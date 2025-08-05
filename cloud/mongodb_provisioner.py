#!/usr/bin/env python3
"""
MongoDB Atlas Cloud Provisioner
Automatic cloud database setup with multi-tenant architecture and usage tracking
"""

import os
import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
import httpx
import pymongo
from pymongo import MongoClient
import motor.motor_asyncio
from bson import ObjectId

@dataclass
class UserAccount:
    """User account structure for cloud MongoDB"""
    user_id: str
    email: str
    api_key: str
    database_name: str
    connection_string: str
    created_at: datetime
    tier: str = "free"  # free, pro, enterprise
    usage_limit: int = 1000  # MB for free tier
    current_usage: float = 0.0  # MB used

@dataclass
class UsageMetrics:
    """Usage tracking for monetization"""
    user_id: str
    date: datetime
    memories_stored: int
    memory_size_mb: float
    api_calls: int
    search_operations: int
    storage_cost: float
    compute_cost: float

class MongoDBCloudProvisioner:
    """Automatic MongoDB Atlas provisioner with multi-tenant support"""
    
    def __init__(self):
        # Your MongoDB Atlas API credentials
        self.atlas_public_key = os.getenv("MONGODB_ATLAS_PUBLIC_KEY")
        self.atlas_private_key = os.getenv("MONGODB_ATLAS_PRIVATE_KEY")
        self.atlas_project_id = os.getenv("MONGODB_ATLAS_PROJECT_ID")
        
        # Master database for user management
        self.master_connection = os.getenv("MONGODB_MASTER_CONNECTION")
        self.master_db = None
        
        # Pricing tiers
        self.pricing_tiers = {
            "free": {
                "memory_limit_mb": 500,  # 500MB instead of 1GB
                "monthly_cost": 0,
                "cost_per_mb": 0,
                "api_calls_limit": 5000  # 5K instead of 10K
            },
            "starter": {
                "memory_limit_mb": 2000,  # 2GB - NEW TIER
                "monthly_cost": 9.99,
                "cost_per_mb": 0.0008,
                "api_calls_limit": 25000  # 25K
            },
            "pro": {
                "memory_limit_mb": 10000,  # 10GB
                "monthly_cost": 29.99,
                "cost_per_mb": 0.0008,  # Optimized rate
                "api_calls_limit": 100000
            },
            "enterprise": {
                "memory_limit_mb": -1,  # Unlimited
                "monthly_cost": 99.99,
                "cost_per_mb": 0.0005,
                "api_calls_limit": -1  # Unlimited
            }
        }
        
    async def initialize(self):
        """Initialize the provisioner with master database connection"""
        if self.master_connection:
            self.master_client = motor.motor_asyncio.AsyncIOMotorClient(self.master_connection)
            self.master_db = self.master_client.mcp_memory_master
            
            # Create indexes for efficient queries
            await self.master_db.users.create_index("email", unique=True)
            await self.master_db.users.create_index("api_key", unique=True)
            await self.master_db.usage_metrics.create_index([("user_id", 1), ("date", -1)])
            
            print("✅ MongoDB Master Database initialized")
        else:
            raise ValueError("MONGODB_MASTER_CONNECTION environment variable required")
    
    async def create_user_account(self, email: str, full_name: str = "") -> UserAccount:
        """Create a new user account with dedicated MongoDB database"""
        
        # Generate unique identifiers
        user_id = self._generate_user_id(email)
        api_key = self._generate_api_key()
        database_name = f"mcp_memory_{user_id}"
        
        print(f"🔧 Creating account for {email}...")
        
        # Create MongoDB Atlas cluster/database
        connection_string = await self._provision_atlas_database(user_id, database_name)
        
        # Create user account record
        user_account = UserAccount(
            user_id=user_id,
            email=email,
            api_key=api_key,
            database_name=database_name,
            connection_string=connection_string,
            created_at=datetime.utcnow(),
            tier="free"
        )
        
        # Save to master database
        await self.master_db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "api_key": api_key,
            "database_name": database_name,
            "connection_string": connection_string,
            "created_at": user_account.created_at,
            "tier": user_account.tier,
            "usage_limit": user_account.usage_limit,
            "current_usage": user_account.current_usage,
            "status": "active"
        })
        
        # Initialize user's memory database
        await self._initialize_user_database(connection_string)
        
        print(f"✅ Account created successfully for {email}")
        print(f"📊 Database: {database_name}")
        print(f"🔑 API Key: {api_key[:8]}...")
        
        return user_account
    
    async def _provision_atlas_database(self, user_id: str, database_name: str) -> str:
        """Provision a new MongoDB Atlas database"""
        
        if not all([self.atlas_public_key, self.atlas_private_key, self.atlas_project_id]):
            # Fallback to shared cluster for development
            print("⚠️ MongoDB Atlas credentials not found, using shared cluster")
            return await self._create_shared_cluster_database(user_id, database_name)
        
        try:
            # MongoDB Atlas API call to create database
            headers = {
                "Content-Type": "application/json"
            }
            
            auth = httpx.DigestAuth(self.atlas_public_key, self.atlas_private_key)
            
            # Create database user
            user_data = {
                "username": f"user_{user_id}",
                "password": secrets.token_urlsafe(16),
                "roles": [
                    {
                        "roleName": "readWrite",
                        "databaseName": database_name
                    }
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{self.atlas_project_id}/databaseUsers",
                    json=user_data,
                    headers=headers,
                    auth=auth,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    user_info = response.json()
                    cluster_endpoint = await self._get_cluster_endpoint()
                    
                    connection_string = f"mongodb+srv://{user_data['username']}:{user_data['password']}@{cluster_endpoint}/{database_name}?retryWrites=true&w=majority"
                    
                    print(f"✅ MongoDB Atlas database created: {database_name}")
                    return connection_string
                else:
                    print(f"⚠️ Atlas API error: {response.status_code}")
                    return await self._create_shared_cluster_database(user_id, database_name)
                    
        except Exception as e:
            print(f"⚠️ Error provisioning Atlas database: {e}")
            return await self._create_shared_cluster_database(user_id, database_name)
    
    async def _create_shared_cluster_database(self, user_id: str, database_name: str) -> str:
        """Create database in shared cluster (fallback)"""
        
        # Use your existing MongoDB connection but create isolated database
        base_connection = self.master_connection.rsplit('/', 1)[0]  # Remove database name
        connection_string = f"{base_connection}/{database_name}"
        
        print(f"📝 Created shared cluster database: {database_name}")
        return connection_string
    
    async def _get_cluster_endpoint(self) -> str:
        """Get MongoDB Atlas cluster endpoint"""
        try:
            headers = {"Content-Type": "application/json"}
            auth = httpx.DigestAuth(self.atlas_public_key, self.atlas_private_key)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{self.atlas_project_id}/clusters",
                    headers=headers,
                    auth=auth,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    clusters = response.json().get("results", [])
                    if clusters:
                        return clusters[0]["mongoURI"].split("//")[1].split("/")[0]
                        
        except Exception as e:
            print(f"Error getting cluster endpoint: {e}")
            
        return "your-cluster.mongodb.net"
    
    async def _initialize_user_database(self, connection_string: str):
        """Initialize user's database with required collections and indexes"""
        
        client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
        db = client.get_default_database()
        
        # Create collections with indexes
        collections_config = {
            "memories": [
                ("text", "text"),  # Text search index
                ("embedding", "2dsphere"),  # Vector search index
                ("created_at", -1),
                ("importance", -1),
                ("memory_type", 1)
            ],
            "usage_logs": [
                ("timestamp", -1),
                ("operation_type", 1)
            ],
            "user_preferences": [
                ("key", 1)
            ]
        }
        
        for collection_name, indexes in collections_config.items():
            collection = db[collection_name]
            
            for index in indexes:
                if isinstance(index, tuple):
                    await collection.create_index([index])
                else:
                    await collection.create_index(index)
        
        # Insert initial user preferences
        await db.user_preferences.insert_one({
            "key": "system_initialized",
            "value": True,
            "created_at": datetime.utcnow()
        })
        
        await client.close()
        print("✅ User database initialized with collections and indexes")
    
    def _generate_user_id(self, email: str) -> str:
        """Generate unique user ID from email"""
        return hashlib.sha256(email.encode()).hexdigest()[:16]
    
    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        return f"mcp_{secrets.token_urlsafe(32)}"
    
    async def get_user_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Get user account by API key"""
        return await self.master_db.users.find_one({"api_key": api_key})
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user account by email"""
        return await self.master_db.users.find_one({"email": email})
    
    async def track_usage(self, user_id: str, operation_type: str, 
                         memory_size_mb: float = 0, api_calls: int = 1):
        """Track usage for billing purposes"""
        
        usage_record = {
            "user_id": user_id,
            "date": datetime.utcnow(),
            "operation_type": operation_type,  # save, search, retrieve, etc.
            "memory_size_mb": memory_size_mb,
            "api_calls": api_calls,
            "timestamp": datetime.utcnow()
        }
        
        # Log usage
        await self.master_db.usage_logs.insert_one(usage_record)
        
        # Update user's current usage
        await self.master_db.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {"current_usage": memory_size_mb},
                "$set": {"last_activity": datetime.utcnow()}
            }
        )
        
        # Check if user exceeded limits
        user = await self.master_db.users.find_one({"user_id": user_id})
        if user:
            await self._check_usage_limits(user)
    
    async def _check_usage_limits(self, user: Dict):
        """Check if user has exceeded their tier limits"""
        tier_info = self.pricing_tiers[user["tier"]]
        
        if tier_info["memory_limit_mb"] > 0:  # -1 means unlimited
            if user["current_usage"] > tier_info["memory_limit_mb"]:
                await self._handle_usage_exceeded(user)
    
    async def _handle_usage_exceeded(self, user: Dict):
        """Handle when user exceeds usage limits"""
        print(f"⚠️ User {user['email']} exceeded usage limits")
        
        # For now, just log. Later we'll implement:
        # - Email notifications
        # - Automatic tier upgrades
        # - Usage restrictions
        
        await self.master_db.notifications.insert_one({
            "user_id": user["user_id"],
            "type": "usage_limit_exceeded",
            "message": f"You have exceeded your {user['tier']} tier limits",
            "created_at": datetime.utcnow(),
            "read": False
        })
    
    async def calculate_monthly_bill(self, user_id: str, month: int, year: int) -> Dict:
        """Calculate monthly bill for a user"""
        
        # Get usage for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        usage_records = await self.master_db.usage_logs.find({
            "user_id": user_id,
            "date": {"$gte": start_date, "$lt": end_date}
        }).to_list(None)
        
        user = await self.master_db.users.find_one({"user_id": user_id})
        tier_info = self.pricing_tiers[user["tier"]]
        
        # Calculate costs
        total_memory_mb = sum(record["memory_size_mb"] for record in usage_records)
        total_api_calls = sum(record["api_calls"] for record in usage_records)
        
        base_cost = tier_info["monthly_cost"]
        overage_memory = max(0, total_memory_mb - tier_info["memory_limit_mb"])
        overage_cost = overage_memory * tier_info["cost_per_mb"]
        
        total_cost = base_cost + overage_cost
        
        bill = {
            "user_id": user_id,
            "month": month,
            "year": year,
            "tier": user["tier"],
            "base_cost": base_cost,
            "total_memory_mb": total_memory_mb,
            "memory_limit_mb": tier_info["memory_limit_mb"],
            "overage_memory_mb": overage_memory,
            "overage_cost": overage_cost,
            "total_api_calls": total_api_calls,
            "total_cost": total_cost,
            "generated_at": datetime.utcnow()
        }
        
        return bill
    
    async def upgrade_user_tier(self, user_id: str, new_tier: str):
        """Upgrade user to a new tier"""
        
        if new_tier not in self.pricing_tiers:
            raise ValueError(f"Invalid tier: {new_tier}")
        
        await self.master_db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "tier": new_tier,
                    "usage_limit": self.pricing_tiers[new_tier]["memory_limit_mb"],
                    "upgraded_at": datetime.utcnow()
                }
            }
        )
        
        print(f"✅ User {user_id} upgraded to {new_tier} tier")

# Usage example and CLI interface
async def main():
    """Example usage of the MongoDB Cloud Provisioner"""
    
    provisioner = MongoDBCloudProvisioner()
    await provisioner.initialize()
    
    # Example: Create a new user account
    try:
        user_account = await provisioner.create_user_account(
            email="user@example.com",
            full_name="Example User"
        )
        
        print(f"\n🎉 Account created successfully!")
        print(f"📧 Email: {user_account.email}")
        print(f"🔑 API Key: {user_account.api_key}")
        print(f"🗄️ Database: {user_account.database_name}")
        print(f"🔗 Connection: {user_account.connection_string[:50]}...")
        
    except Exception as e:
        print(f"❌ Error creating account: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 