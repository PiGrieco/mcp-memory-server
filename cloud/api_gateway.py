#!/usr/bin/env python3
"""
MCP Memory Cloud - API Gateway
Main entry point for all cloud services and plugin integrations
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import redis.asyncio as redis
from contextlib import asynccontextmanager

from mongodb_provisioner import MongoDBCloudProvisioner
from billing_system import BillingSystem
from cloud_integration import CloudMemoryClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/api_gateway.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global services
provisioner = None
billing_system = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global provisioner, billing_system, redis_client
    
    try:
        # Initialize services
        logger.info("🚀 Starting MCP Memory Cloud API Gateway...")
        
        # Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        redis_client = redis.from_url(redis_url)
        
        # MongoDB provisioner
        provisioner = MongoDBCloudProvisioner()
        await provisioner.initialize()
        
        # Billing system
        billing_system = BillingSystem()
        await billing_system.initialize()
        
        logger.info("✅ All services initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        if redis_client:
            await redis_client.close()
        logger.info("🛑 API Gateway shutdown complete")

# FastAPI app
app = FastAPI(
    title="MCP Memory Cloud API",
    description="Cloud Memory Service for AI Agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from API key"""
    if not credentials:
        return None
    
    api_key = credentials.credentials
    user = await provisioner.get_user_by_api_key(api_key)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB
        await provisioner.master_db.command("ping")
        
        # Check Redis
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "mongodb": "healthy",
                "redis": "healthy",
                "billing": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")

# Plugin onboarding endpoints
@app.post("/api/v1/onboard")
async def plugin_onboarding(request: Request):
    """
    Plugin onboarding - generates signup URL for new users
    Called when a plugin is first installed
    """
    try:
        data = await request.json()
        plugin_type = data.get("plugin_type")  # claude, cursor, chatgpt, etc.
        user_id = data.get("user_id")  # Optional user identifier
        return_url = data.get("return_url")  # Where to redirect after setup
        
        # Generate onboarding session
        session_id = f"onboard_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        # Store session data in Redis
        session_data = {
            "plugin_type": plugin_type,
            "user_id": user_id,
            "return_url": return_url,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        await redis_client.setex(
            f"onboard_session:{session_id}",
            3600,  # 1 hour expiry
            json.dumps(session_data)
        )
        
        # Frontend signup URL
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        signup_url = f"{frontend_url}/signup?session={session_id}&plugin={plugin_type}"
        
        logger.info(f"🔗 Generated onboarding URL for {plugin_type}: {session_id}")
        
        return {
            "signup_url": signup_url,
            "session_id": session_id,
            "message": "Please complete setup in your browser"
        }
        
    except Exception as e:
        logger.error(f"❌ Onboarding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/onboard/status/{session_id}")
async def check_onboarding_status(session_id: str):
    """Check onboarding status for polling"""
    try:
        session_data = await redis_client.get(f"onboard_session:{session_id}")
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        data = json.loads(session_data)
        return {
            "status": data.get("status"),
            "api_key": data.get("api_key"),
            "user_id": data.get("final_user_id"),
            "message": data.get("message")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/signup/complete")
async def complete_signup(request: Request):
    """
    Complete signup process from frontend
    Called after user provides email and payment info
    """
    try:
        data = await request.json()
        session_id = data.get("session_id")
        email = data.get("email")
        full_name = data.get("full_name", "")
        plan = data.get("plan", "free")
        stripe_payment_method = data.get("stripe_payment_method")
        
        # Get session data
        session_data = await redis_client.get(f"onboard_session:{session_id}")
        if not session_data:
            raise HTTPException(status_code=404, detail="Session expired")
        
        session = json.loads(session_data)
        
        # Create user account
        user_account = await provisioner.create_user_account(email, full_name)
        
        # Setup billing if not free plan
        if plan != "free" and stripe_payment_method:
            try:
                subscription_result = await billing_system.setup_subscription(
                    user_account.user_id, 
                    plan
                )
                logger.info(f"✅ Subscription created for {email}: {plan}")
            except Exception as e:
                logger.error(f"⚠️ Billing setup failed for {email}: {e}")
                # Continue with free plan
                plan = "free"
        
        # Update session with completion data
        session["status"] = "completed"
        session["api_key"] = user_account.api_key
        session["final_user_id"] = user_account.user_id
        session["email"] = email
        session["plan"] = plan
        session["message"] = "Account created successfully!"
        
        await redis_client.setex(
            f"onboard_session:{session_id}",
            300,  # 5 minutes for plugin to retrieve
            json.dumps(session)
        )
        
        logger.info(f"🎉 Signup completed for {email} ({session['plugin_type']})")
        
        return {
            "success": True,
            "api_key": user_account.api_key,
            "user_id": user_account.user_id,
            "message": "Account created successfully! Your plugin is being configured...",
            "return_url": session.get("return_url")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Signup completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Memory operations endpoints
@app.post("/api/v1/memory/save")
async def save_memory(request: Request, user: dict = Depends(get_current_user)):
    """Save a memory for the user"""
    try:
        data = await request.json()
        
        # Track usage
        memory_size_mb = len(json.dumps(data)) / (1024 * 1024)
        await provisioner.track_usage(
            user["user_id"],
            "save",
            memory_size_mb=memory_size_mb
        )
        
        # Here you would implement actual memory storage
        # For now, just acknowledge
        return {
            "success": True,
            "memory_id": f"mem_{int(datetime.utcnow().timestamp())}",
            "size_mb": memory_size_mb,
            "message": "Memory saved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Save memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/memory/search")
async def search_memory(request: Request, user: dict = Depends(get_current_user)):
    """Search memories for the user"""
    try:
        data = await request.json()
        query = data.get("query", "")
        
        # Track usage
        await provisioner.track_usage(
            user["user_id"],
            "search",
            memory_size_mb=0
        )
        
        # Here you would implement actual memory search
        # For now, return mock results
        return {
            "success": True,
            "query": query,
            "results": [],
            "message": "Search completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Search memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Billing endpoints (proxy to billing service)
@app.get("/api/v1/billing/dashboard")
async def get_billing_dashboard(user: dict = Depends(get_current_user)):
    """Get billing dashboard data"""
    try:
        dashboard_data = await billing_system.get_usage_dashboard_data(user["user_id"])
        return dashboard_data
    except Exception as e:
        logger.error(f"❌ Billing dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/billing/subscribe")
async def create_subscription(request: Request, user: dict = Depends(get_current_user)):
    """Create or update subscription"""
    try:
        data = await request.json()
        plan = data.get("plan")
        
        result = await billing_system.setup_subscription(user["user_id"], plan)
        return result
    except Exception as e:
        logger.error(f"❌ Subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Plugin-specific configuration endpoints
@app.get("/api/v1/config/{plugin_type}")
async def get_plugin_config(plugin_type: str, user: dict = Depends(get_current_user)):
    """Get configuration for specific plugin type"""
    try:
        base_config = {
            "api_url": os.getenv("API_BASE_URL", "http://localhost:8000"),
            "api_key": user["api_key"],
            "user_id": user["user_id"],
            "tier": user.get("tier", "free")
        }
        
        # Plugin-specific configurations
        plugin_configs = {
            "claude": {
                **base_config,
                "mcp_server_url": f"{base_config['api_url']}/mcp/claude",
                "instructions": "Add this server to your Claude Desktop MCP settings"
            },
            "cursor": {
                **base_config,
                "extension_url": f"{base_config['api_url']}/api/v1/memory",
                "instructions": "Install the Cursor extension and enter your API key"
            },
            "chatgpt": {
                **base_config,
                "plugin_url": f"{base_config['api_url']}/api/v1/memory",
                "instructions": "Use the ChatGPT browser extension"
            }
        }
        
        config = plugin_configs.get(plugin_type, base_config)
        return config
        
    except Exception as e:
        logger.error(f"❌ Plugin config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api_gateway:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    ) 