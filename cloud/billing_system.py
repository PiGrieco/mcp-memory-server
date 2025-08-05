#!/usr/bin/env python3
"""
Billing and Monetization System for MCP Memory Server
Usage-based billing with Stripe integration and automatic tier management
"""

import os
import asyncio
import stripe
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from cloud.mongodb_provisioner import MongoDBCloudProvisioner
import httpx
import json

@dataclass
class BillingPlan:
    """Billing plan structure"""
    name: str
    monthly_cost: float
    memory_limit_mb: int
    api_calls_limit: int
    overage_cost_per_mb: float
    features: List[str]

@dataclass
class Invoice:
    """Invoice structure"""
    user_id: str
    invoice_id: str
    billing_period_start: datetime
    billing_period_end: datetime
    base_cost: float
    usage_costs: Dict[str, float]
    total_cost: float
    stripe_invoice_id: str
    status: str  # pending, paid, failed, cancelled

class BillingSystem:
    """Complete billing system with Stripe integration"""
    
    def __init__(self):
        # Stripe configuration
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        # MongoDB provisioner for user management
        self.provisioner = MongoDBCloudProvisioner()
        
        # Billing plans
        self.billing_plans = {
            "free": BillingPlan(
                name="Free",
                monthly_cost=0.0,
                memory_limit_mb=1000,  # 1GB
                api_calls_limit=10000,
                overage_cost_per_mb=0.0,  # No overage for free
                features=[
                    "1GB Memory Storage",
                    "10,000 API calls/month",
                    "Basic search",
                    "Community support"
                ]
            ),
            "pro": BillingPlan(
                name="Pro",
                monthly_cost=29.99,
                memory_limit_mb=10000,  # 10GB
                api_calls_limit=100000,
                overage_cost_per_mb=0.001,  # $0.001 per MB
                features=[
                    "10GB Memory Storage",
                    "100,000 API calls/month",
                    "Advanced search & analytics",
                    "Priority support",
                    "Team collaboration",
                    "API integrations"
                ]
            ),
            "enterprise": BillingPlan(
                name="Enterprise",
                monthly_cost=99.99,
                memory_limit_mb=-1,  # Unlimited
                api_calls_limit=-1,  # Unlimited
                overage_cost_per_mb=0.0005,  # $0.0005 per MB (for tracking)
                features=[
                    "Unlimited Memory Storage",
                    "Unlimited API calls",
                    "Advanced analytics dashboard",
                    "24/7 premium support",
                    "Multi-tenant architecture",
                    "Custom integrations",
                    "SLA guarantees"
                ]
            )
        }
        
        # Usage tracking rates
        self.usage_rates = {
            "memory_storage": 0.001,  # $0.001 per MB
            "api_call": 0.0001,       # $0.0001 per API call
            "search_operation": 0.0005, # $0.0005 per search
            "vector_embedding": 0.001   # $0.001 per embedding generation
        }
    
    async def initialize(self):
        """Initialize billing system"""
        await self.provisioner.initialize()
        print("✅ Billing system initialized")
    
    async def create_stripe_customer(self, user_id: str, email: str, name: str = "") -> str:
        """Create Stripe customer for user"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "user_id": user_id,
                    "service": "mcp_memory_server"
                }
            )
            
            # Save Stripe customer ID to user record
            await self.provisioner.master_db.users.update_one(
                {"user_id": user_id},
                {"$set": {"stripe_customer_id": customer.id}}
            )
            
            print(f"✅ Stripe customer created: {customer.id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            print(f"❌ Stripe customer creation failed: {e}")
            raise
    
    async def setup_subscription(self, user_id: str, plan_name: str) -> Dict:
        """Setup subscription for user"""
        
        if plan_name not in self.billing_plans:
            raise ValueError(f"Invalid plan: {plan_name}")
        
        user = await self.provisioner.master_db.users.find_one({"user_id": user_id})
        if not user:
            raise ValueError("User not found")
        
        plan = self.billing_plans[plan_name]
        
        # Free plan doesn't need Stripe subscription
        if plan_name == "free":
            await self.provisioner.upgrade_user_tier(user_id, "free")
            return {"status": "active", "plan": "free"}
        
        # Get or create Stripe customer
        stripe_customer_id = user.get("stripe_customer_id")
        if not stripe_customer_id:
            stripe_customer_id = await self.create_stripe_customer(
                user_id, user["email"], user.get("full_name", "")
            )
        
        try:
            # Create Stripe subscription
            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"MCP Memory {plan.name}",
                            "description": f"Memory storage and AI features - {plan.name} tier"
                        },
                        "unit_amount": int(plan.monthly_cost * 100),  # Convert to cents
                        "recurring": {"interval": "month"}
                    }
                }],
                metadata={
                    "user_id": user_id,
                    "plan": plan_name
                }
            )
            
            # Update user record
            await self.provisioner.master_db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "stripe_subscription_id": subscription.id,
                        "subscription_status": subscription.status,
                        "plan_name": plan_name
                    }
                }
            )
            
            # Upgrade user tier
            await self.provisioner.upgrade_user_tier(user_id, plan_name)
            
            print(f"✅ Subscription created: {subscription.id}")
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "plan": plan_name,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None
            }
            
        except stripe.error.StripeError as e:
            print(f"❌ Subscription creation failed: {e}")
            raise
    
    async def calculate_usage_based_billing(self, user_id: str, 
                                          billing_period_start: datetime,
                                          billing_period_end: datetime) -> Dict:
        """Calculate usage-based billing for a period"""
        
        # Get usage records for the period
        usage_records = await self.provisioner.master_db.usage_logs.find({
            "user_id": user_id,
            "timestamp": {
                "$gte": billing_period_start,
                "$lt": billing_period_end
            }
        }).to_list(None)
        
        user = await self.provisioner.master_db.users.find_one({"user_id": user_id})
        plan = self.billing_plans[user.get("tier", "free")]
        
        # Calculate usage totals
        usage_totals = {
            "memory_storage_mb": 0,
            "api_calls": 0,
            "search_operations": 0,
            "vector_embeddings": 0
        }
        
        for record in usage_records:
            usage_totals["memory_storage_mb"] += record.get("memory_size_mb", 0)
            usage_totals["api_calls"] += record.get("api_calls", 0)
            
            if record.get("operation_type") == "search":
                usage_totals["search_operations"] += 1
            elif record.get("operation_type") == "save":
                usage_totals["vector_embeddings"] += 1
        
        # Calculate costs
        costs = {
            "base_subscription": plan.monthly_cost,
            "memory_overage": 0,
            "api_overage": 0,
            "additional_usage": 0
        }
        
        # Memory overage
        if plan.memory_limit_mb > 0:  # -1 means unlimited
            memory_overage = max(0, usage_totals["memory_storage_mb"] - plan.memory_limit_mb)
            costs["memory_overage"] = memory_overage * plan.overage_cost_per_mb
        
        # API overage
        if plan.api_calls_limit > 0:  # -1 means unlimited
            api_overage = max(0, usage_totals["api_calls"] - plan.api_calls_limit)
            costs["api_overage"] = api_overage * self.usage_rates["api_call"]
        
        # Additional usage costs (searches, embeddings)
        costs["additional_usage"] = (
            usage_totals["search_operations"] * self.usage_rates["search_operation"] +
            usage_totals["vector_embeddings"] * self.usage_rates["vector_embedding"]
        )
        
        total_cost = sum(costs.values())
        
        billing_details = {
            "user_id": user_id,
            "billing_period": {
                "start": billing_period_start,
                "end": billing_period_end
            },
            "plan": user.get("tier", "free"),
            "usage_totals": usage_totals,
            "costs": costs,
            "total_cost": total_cost,
            "calculated_at": datetime.utcnow()
        }
        
        return billing_details
    
    async def generate_invoice(self, user_id: str, month: int, year: int) -> Invoice:
        """Generate invoice for user for specific month"""
        
        # Calculate billing period
        billing_start = datetime(year, month, 1)
        if month == 12:
            billing_end = datetime(year + 1, 1, 1)
        else:
            billing_end = datetime(year, month + 1, 1)
        
        # Calculate usage
        billing_details = await self.calculate_usage_based_billing(
            user_id, billing_start, billing_end
        )
        
        user = await self.provisioner.master_db.users.find_one({"user_id": user_id})
        
        # Create Stripe invoice for overages (base subscription is handled separately)
        overage_total = (
            billing_details["costs"]["memory_overage"] +
            billing_details["costs"]["api_overage"] +
            billing_details["costs"]["additional_usage"]
        )
        
        stripe_invoice_id = None
        if overage_total > 0 and user.get("stripe_customer_id"):
            try:
                # Create invoice item for overages
                stripe.InvoiceItem.create(
                    customer=user["stripe_customer_id"],
                    amount=int(overage_total * 100),  # Convert to cents
                    currency="usd",
                    description=f"Usage overages for {billing_start.strftime('%B %Y')}"
                )
                
                # Create and finalize invoice
                stripe_invoice = stripe.Invoice.create(
                    customer=user["stripe_customer_id"],
                    auto_advance=True
                )
                stripe_invoice.finalize()
                stripe_invoice_id = stripe_invoice.id
                
            except stripe.error.StripeError as e:
                print(f"⚠️ Stripe invoice creation failed: {e}")
        
        # Create invoice record
        invoice = Invoice(
            user_id=user_id,
            invoice_id=f"inv_{user_id}_{year}{month:02d}",
            billing_period_start=billing_start,
            billing_period_end=billing_end,
            base_cost=billing_details["costs"]["base_subscription"],
            usage_costs=billing_details["costs"],
            total_cost=billing_details["total_cost"],
            stripe_invoice_id=stripe_invoice_id,
            status="pending"
        )
        
        # Save invoice to database
        await self.provisioner.master_db.invoices.insert_one({
            "invoice_id": invoice.invoice_id,
            "user_id": invoice.user_id,
            "billing_period_start": invoice.billing_period_start,
            "billing_period_end": invoice.billing_period_end,
            "base_cost": invoice.base_cost,
            "usage_costs": invoice.usage_costs,
            "total_cost": invoice.total_cost,
            "stripe_invoice_id": invoice.stripe_invoice_id,
            "status": invoice.status,
            "generated_at": datetime.utcnow(),
            "billing_details": billing_details
        })
        
        return invoice
    
    async def handle_stripe_webhook(self, payload: str, signature: str) -> bool:
        """Handle Stripe webhooks"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.stripe_webhook_secret
            )
            
            if event["type"] == "invoice.payment_succeeded":
                await self._handle_payment_success(event["data"]["object"])
            
            elif event["type"] == "invoice.payment_failed":
                await self._handle_payment_failed(event["data"]["object"])
            
            elif event["type"] == "customer.subscription.deleted":
                await self._handle_subscription_cancelled(event["data"]["object"])
            
            return True
            
        except stripe.error.SignatureVerificationError:
            print("❌ Invalid Stripe webhook signature")
            return False
        except Exception as e:
            print(f"❌ Webhook handling error: {e}")
            return False
    
    async def _handle_payment_success(self, stripe_invoice):
        """Handle successful payment"""
        invoice_id = stripe_invoice.get("metadata", {}).get("invoice_id")
        
        if invoice_id:
            await self.provisioner.master_db.invoices.update_one(
                {"invoice_id": invoice_id},
                {
                    "$set": {
                        "status": "paid",
                        "paid_at": datetime.utcnow()
                    }
                }
            )
            print(f"✅ Payment successful for invoice {invoice_id}")
    
    async def _handle_payment_failed(self, stripe_invoice):
        """Handle failed payment"""
        invoice_id = stripe_invoice.get("metadata", {}).get("invoice_id")
        
        if invoice_id:
            await self.provisioner.master_db.invoices.update_one(
                {"invoice_id": invoice_id},
                {
                    "$set": {
                        "status": "failed",
                        "failed_at": datetime.utcnow()
                    }
                }
            )
            print(f"⚠️ Payment failed for invoice {invoice_id}")
    
    async def _handle_subscription_cancelled(self, subscription):
        """Handle subscription cancellation"""
        user_id = subscription.get("metadata", {}).get("user_id")
        
        if user_id:
            # Downgrade to free tier
            await self.provisioner.upgrade_user_tier(user_id, "free")
            
            await self.provisioner.master_db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "subscription_status": "cancelled",
                        "cancelled_at": datetime.utcnow()
                    }
                }
            )
            print(f"📉 Subscription cancelled for user {user_id}")
    
    async def get_usage_dashboard_data(self, user_id: str) -> Dict:
        """Get usage data for dashboard"""
        user = await self.provisioner.master_db.users.find_one({"user_id": user_id})
        plan = self.billing_plans[user.get("tier", "free")]
        
        # Get current month usage
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        billing_details = await self.calculate_usage_based_billing(
            user_id, month_start, now
        )
        
        return {
            "user": {
                "email": user["email"],
                "tier": user.get("tier", "free"),
                "subscription_status": user.get("subscription_status", "active")
            },
            "plan": {
                "name": plan.name,
                "monthly_cost": plan.monthly_cost,
                "memory_limit_mb": plan.memory_limit_mb,
                "api_calls_limit": plan.api_calls_limit,
                "features": plan.features
            },
            "current_usage": billing_details["usage_totals"],
            "current_costs": billing_details["costs"],
            "billing_period": {
                "start": month_start,
                "end": now
            }
        }

# FastAPI endpoints for billing dashboard
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="MCP Memory Billing Dashboard")
billing_system = BillingSystem()

@app.on_event("startup")
async def startup():
    await billing_system.initialize()

@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """Get billing dashboard data"""
    try:
        data = await billing_system.get_usage_dashboard_data(user_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/subscribe/{user_id}")
async def create_subscription(user_id: str, plan: str):
    """Create subscription for user"""
    try:
        result = await billing_system.setup_subscription(user_id, plan)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    success = await billing_system.handle_stripe_webhook(
        payload.decode(), signature
    )
    
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Webhook processing failed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 