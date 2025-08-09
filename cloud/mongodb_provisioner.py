#!/usr/bin/env python3
"""
Production-Ready MongoDB Atlas Cloud Provisioner
Automatic cloud database setup with enhanced security, monitoring, and error handling
"""

import os
import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
import httpx
import motor.motor_asyncio
from bson import ObjectId

from ..src.config.settings import get_config
from ..src.utils.logging import get_logger, log_performance
from ..src.utils.exceptions import MCPMemoryError
from ..src.utils.retry import retry_async
from ..src.utils.validation import validate_email


logger = get_logger(__name__)


@dataclass
class UserAccount:
    """Enhanced user account structure for cloud MongoDB"""
    user_id: str
    email: str
    api_key: str
    database_name: str
    connection_string: str
    created_at: datetime
    tier: str = "free"  # free, pro, enterprise
    usage_limit_mb: int = 1000  # MB for free tier
    current_usage_mb: float = 0.0  # MB used
    region: str = "us-east-1"
    cluster_tier: str = "M0"  # Atlas cluster tier
    backup_enabled: bool = True
    encryption_enabled: bool = True
    last_activity: Optional[datetime] = None
    status: str = "active"  # active, suspended, deleted
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with datetime serialization"""
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


@dataclass
class UsageMetrics:
    """Enhanced usage tracking for billing and analytics"""
    user_id: str
    timestamp: datetime
    operation_type: str  # create, search, update, delete, sync
    memory_count: int
    memory_size_mb: float
    api_calls: int
    processing_time_ms: float
    storage_cost_usd: float = 0.0
    compute_cost_usd: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ProvisioningError(MCPMemoryError):
    """Error during MongoDB provisioning"""
    pass


class MongoDBCloudProvisioner:
    """Production-ready MongoDB Atlas provisioner with enhanced features"""
    
    def __init__(self):
        self.config = get_config()
        
        # MongoDB Atlas API credentials
        self.atlas_public_key = os.getenv("MONGODB_ATLAS_PUBLIC_KEY")
        self.atlas_private_key = os.getenv("MONGODB_ATLAS_PRIVATE_KEY")
        self.atlas_project_id = os.getenv("MONGODB_ATLAS_PROJECT_ID")
        
        # Fallback to shared cluster if Atlas not configured
        self.shared_cluster_uri = os.getenv("MONGODB_SHARED_CLUSTER_URI")
        
        # Master database for user management
        self.master_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.master_db = None
        
        # Rate limiting and quotas
        self.rate_limits = {
            "free": {"requests_per_hour": 1000, "storage_mb": 1000},
            "pro": {"requests_per_hour": 10000, "storage_mb": 10000},
            "enterprise": {"requests_per_hour": 100000, "storage_mb": 100000}
        }
        
        # Pricing (USD per MB per month)
        self.pricing = {
            "storage": 0.001,  # $0.001 per MB per month
            "compute": 0.0001  # $0.0001 per operation
        }
    
    @log_performance("provisioner_initialization")
    async def initialize(self):
        """Initialize provisioner with connection validation"""
        try:
            # Connect to master database
            master_uri = (
                self.shared_cluster_uri or 
                self.config.database.uri or 
                f"mongodb://{self.config.database.host}:{self.config.database.port}"
            )
            
            self.master_client = motor.motor_asyncio.AsyncIOMotorClient(
                master_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=10
            )
            
            # Test connection
            await self.master_client.admin.command('ping')
            
            self.master_db = self.master_client.mcp_memory_master
            
            # Create indexes for performance
            await self._create_indexes()
            
            logger.info("MongoDB provisioner initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize provisioner: {e}")
            raise ProvisioningError(f"Provisioner initialization failed: {e}")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # User indexes
            await self.master_db.users.create_index("email", unique=True)
            await self.master_db.users.create_index("api_key", unique=True)
            await self.master_db.users.create_index("user_id", unique=True)
            await self.master_db.users.create_index("tier")
            await self.master_db.users.create_index("status")
            
            # Usage metrics indexes
            await self.master_db.usage_metrics.create_index([
                ("user_id", 1), ("timestamp", -1)
            ])
            await self.master_db.usage_metrics.create_index("timestamp")
            await self.master_db.usage_metrics.create_index("operation_type")
            
            logger.debug("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    @retry_async(max_attempts=3, delay=2.0)
    @log_performance("user_account_creation")
    async def create_user_account(
        self, 
        email: str, 
        tier: str = "free",
        region: str = "us-east-1"
    ) -> UserAccount:
        """Create new user account with cloud database"""
        
        if not validate_email(email):
            raise ValueError(f"Invalid email address: {email}")
        
        if tier not in self.rate_limits:
            raise ValueError(f"Invalid tier: {tier}")
        
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                logger.info(f"User {email} already exists")
                return existing_user
            
            # Generate unique identifiers
            user_id = self._generate_user_id(email)
            api_key = self._generate_api_key()
            database_name = f"mcp_memory_{user_id}"
            
            # Create cloud database
            connection_string = await self._provision_database(
                database_name, tier, region
            )
            
            # Create user account
            account = UserAccount(
                user_id=user_id,
                email=email,
                api_key=api_key,
                database_name=database_name,
                connection_string=connection_string,
                created_at=datetime.now(timezone.utc),
                tier=tier,
                usage_limit_mb=self.rate_limits[tier]["storage_mb"],
                region=region,
                cluster_tier="M0" if tier == "free" else "M10"
            )
            
            # Save to master database
            await self.master_db.users.insert_one(account.to_dict())
            
            # Initialize user database
            await self._initialize_user_database(connection_string)
            
            logger.info(f"Created user account: {email} ({tier})")
            return account
            
        except Exception as e:
            logger.error(f"Failed to create user account for {email}: {e}")
            raise ProvisioningError(f"Account creation failed: {e}")
    
    def _generate_user_id(self, email: str) -> str:
        """Generate unique user ID from email"""
        hash_obj = hashlib.sha256(email.encode())
        return hash_obj.hexdigest()[:16]
    
    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        return f"mcp_{secrets.token_urlsafe(32)}"
    
    async def _provision_database(
        self, 
        database_name: str, 
        tier: str, 
        region: str
    ) -> str:
        """Provision MongoDB database (Atlas or shared cluster)"""
        
        if self.atlas_public_key and self.atlas_private_key:
            # Use MongoDB Atlas API
            return await self._provision_atlas_cluster(database_name, tier, region)
        else:
            # Use shared cluster with separate database
            return await self._provision_shared_database(database_name)
    
    async def _provision_atlas_cluster(
        self, 
        database_name: str, 
        tier: str, 
        region: str
    ) -> str:
        """Provision dedicated Atlas cluster"""
        
        cluster_config = {
            "name": database_name,
            "clusterType": "REPLICASET",
            "providerSettings": {
                "providerName": "AWS",
                "regionName": region.upper().replace("-", "_"),
                "instanceSizeName": "M0" if tier == "free" else "M10"
            },
            "mongoDBMajorVersion": "7.0",
            "backupEnabled": True,
            "encryptionAtRestProvider": "AWS"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                auth = httpx.DigestAuth(self.atlas_public_key, self.atlas_private_key)
                
                response = await client.post(
                    f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{self.atlas_project_id}/clusters",
                    json=cluster_config,
                    auth=auth,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    cluster_data = response.json()
                    # Wait for cluster to be ready
                    connection_string = await self._wait_for_cluster_ready(
                        database_name, cluster_data["connectionStrings"]
                    )
                    return connection_string
                else:
                    raise ProvisioningError(f"Atlas API error: {response.text}")
                    
        except Exception as e:
            logger.error(f"Atlas provisioning failed: {e}")
            # Fallback to shared cluster
            return await self._provision_shared_database(database_name)
    
    async def _provision_shared_database(self, database_name: str) -> str:
        """Provision database on shared cluster"""
        if not self.shared_cluster_uri:
            raise ProvisioningError("No shared cluster URI configured")
        
        # Create connection string with specific database
        if "?" in self.shared_cluster_uri:
            base_uri, params = self.shared_cluster_uri.split("?", 1)
            connection_string = f"{base_uri}/{database_name}?{params}"
        else:
            connection_string = f"{self.shared_cluster_uri}/{database_name}"
        
        return connection_string
    
    async def _wait_for_cluster_ready(
        self, 
        cluster_name: str, 
        connection_strings: Dict
    ) -> str:
        """Wait for Atlas cluster to be ready"""
        max_wait_minutes = 10
        check_interval = 30  # seconds
        
        for _ in range(max_wait_minutes * 2):  # Check every 30 seconds
            try:
                async with httpx.AsyncClient() as client:
                    auth = httpx.DigestAuth(self.atlas_public_key, self.atlas_private_key)
                    
                    response = await client.get(
                        f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{self.atlas_project_id}/clusters/{cluster_name}",
                        auth=auth,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        cluster_data = response.json()
                        if cluster_data.get("stateName") == "IDLE":
                            return connection_strings.get("standardSrv")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.warning(f"Cluster status check failed: {e}")
                await asyncio.sleep(check_interval)
        
        raise ProvisioningError("Cluster provisioning timeout")
    
    async def _initialize_user_database(self, connection_string: str):
        """Initialize user database with collections and indexes"""
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
            db = client.get_default_database()
            
            # Create memory collection with indexes
            await db.memories.create_index([("project", 1), ("created_at", -1)])
            await db.memories.create_index([("embedding", "2dsphere")])
            await db.memories.create_index("importance")
            await db.memories.create_index("memory_type")
            
            # Create metadata collection
            await db.metadata.create_index("key", unique=True)
            
            await client.close()
            logger.debug(f"User database initialized: {connection_string}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize user database: {e}")
    
    async def get_user_by_email(self, email: str) -> Optional[UserAccount]:
        """Get user by email address"""
        try:
            user_data = await self.master_db.users.find_one({"email": email})
            if user_data:
                # Convert datetime strings back to datetime objects
                for field in ["created_at", "last_activity"]:
                    if field in user_data and isinstance(user_data[field], str):
                        user_data[field] = datetime.fromisoformat(user_data[field])
                
                return UserAccount(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    async def get_user_by_api_key(self, api_key: str) -> Optional[UserAccount]:
        """Get user by API key"""
        try:
            user_data = await self.master_db.users.find_one({"api_key": api_key})
            if user_data:
                # Convert datetime strings back to datetime objects
                for field in ["created_at", "last_activity"]:
                    if field in user_data and isinstance(user_data[field], str):
                        user_data[field] = datetime.fromisoformat(user_data[field])
                
                return UserAccount(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by API key: {e}")
            return None
    
    @log_performance("usage_tracking")
    async def track_usage(
        self,
        user_id: str,
        operation_type: str,
        memory_size_mb: float,
        metadata: Optional[Dict] = None,
        timestamp: Optional[datetime] = None
    ):
        """Track user operation for billing and analytics"""
        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
            
            usage_metric = UsageMetrics(
                user_id=user_id,
                timestamp=timestamp,
                operation_type=operation_type,
                memory_count=1,
                memory_size_mb=memory_size_mb,
                api_calls=1,
                processing_time_ms=0,  # Could be calculated from decorator
                storage_cost_usd=memory_size_mb * self.pricing["storage"],
                compute_cost_usd=self.pricing["compute"],
                metadata=metadata or {}
            )
            
            # Insert usage metric
            await self.master_db.usage_metrics.insert_one(asdict(usage_metric))
            
            # Update user current usage
            await self.master_db.users.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"current_usage_mb": memory_size_mb},
                    "$set": {"last_activity": timestamp.isoformat()}
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to track usage for user {user_id}: {e}")
    
    async def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """Get comprehensive user statistics"""
        try:
            # Get user data
            user_data = await self.master_db.users.find_one({"user_id": user_id})
            if not user_data:
                return None
            
            # Get usage metrics for last 30 days
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            
            usage_stats = await self.master_db.usage_metrics.aggregate([
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": thirty_days_ago}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_operations": {"$sum": 1},
                        "total_memory_mb": {"$sum": "$memory_size_mb"},
                        "total_storage_cost": {"$sum": "$storage_cost_usd"},
                        "total_compute_cost": {"$sum": "$compute_cost_usd"}
                    }
                }
            ]).to_list(length=1)
            
            stats = usage_stats[0] if usage_stats else {}
            
            return {
                **user_data,
                "operations_count": stats.get("total_operations", 0),
                "monthly_memory_mb": stats.get("total_memory_mb", 0),
                "monthly_storage_cost": stats.get("total_storage_cost", 0),
                "monthly_compute_cost": stats.get("total_compute_cost", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats for {user_id}: {e}")
            return None
    
    async def sync_memories(self, user_id: str, memories: List[Dict]) -> Dict:
        """Sync memories to user's cloud database"""
        try:
            user = await self.master_db.users.find_one({"user_id": user_id})
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Connect to user's database
            client = motor.motor_asyncio.AsyncIOMotorClient(user["connection_string"])
            db = client.get_default_database()
            
            # Bulk insert/update memories
            operations = []
            for memory in memories:
                operations.append(
                    pymongo.UpdateOne(
                        {"id": memory.get("id")},
                        {"$set": memory},
                        upsert=True
                    )
                )
            
            if operations:
                result = await db.memories.bulk_write(operations)
                
                # Track usage
                total_size_mb = sum(
                    len(str(memory).encode('utf-8')) / (1024 * 1024) 
                    for memory in memories
                )
                
                await self.track_usage(
                    user_id=user_id,
                    operation_type="sync",
                    memory_size_mb=total_size_mb,
                    metadata={"memories_count": len(memories)}
                )
                
                await client.close()
                
                return {
                    "success": True,
                    "inserted": result.upserted_count,
                    "updated": result.modified_count
                }
            
            await client.close()
            return {"success": True, "inserted": 0, "updated": 0}
            
        except Exception as e:
            logger.error(f"Failed to sync memories for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_memories(
        self, 
        user_id: str, 
        project: str = "default",
        limit: int = 100
    ) -> List[Dict]:
        """Get memories from user's cloud database"""
        try:
            user = await self.master_db.users.find_one({"user_id": user_id})
            if not user:
                return []
            
            # Connect to user's database
            client = motor.motor_asyncio.AsyncIOMotorClient(user["connection_string"])
            db = client.get_default_database()
            
            # Query memories
            cursor = db.memories.find(
                {"project": project}
            ).sort("created_at", -1).limit(limit)
            
            memories = await cursor.to_list(length=limit)
            await client.close()
            
            # Convert ObjectId to string
            for memory in memories:
                if "_id" in memory:
                    memory["_id"] = str(memory["_id"])
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get memories for user {user_id}: {e}")
            return []
    
    async def cleanup_expired_accounts(self, days_inactive: int = 90):
        """Clean up inactive free tier accounts"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_inactive)
            
            # Find inactive free tier accounts
            inactive_users = await self.master_db.users.find({
                "tier": "free",
                "last_activity": {"$lt": cutoff_date.isoformat()}
            }).to_list(length=None)
            
            for user in inactive_users:
                logger.info(f"Archiving inactive user: {user['email']}")
                
                # Mark as archived instead of deleting
                await self.master_db.users.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {"status": "archived"}}
                )
            
            logger.info(f"Archived {len(inactive_users)} inactive accounts")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired accounts: {e}")
    
    async def close(self):
        """Close provisioner connections"""
        if self.master_client:
            self.master_client.close()


# CLI interface for provisioner management
async def main():
    """CLI interface for provisioner operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MongoDB Cloud Provisioner")
    parser.add_argument("--init", action="store_true", help="Initialize provisioner")
    parser.add_argument("--create-user", help="Create user account (email)")
    parser.add_argument("--tier", default="free", help="User tier (free/pro/enterprise)")
    parser.add_argument("--stats", help="Get user stats (user_id)")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup inactive accounts")
    
    args = parser.parse_args()
    
    provisioner = MongoDBCloudProvisioner()
    await provisioner.initialize()
    
    try:
        if args.init:
            print("✅ Provisioner initialized successfully")
        
        elif args.create_user:
            account = await provisioner.create_user_account(args.create_user, args.tier)
            print(f"✅ Created account: {account.email}")
            print(f"   User ID: {account.user_id}")
            print(f"   API Key: {account.api_key}")
            print(f"   Database: {account.database_name}")
        
        elif args.stats:
            stats = await provisioner.get_user_stats(args.stats)
            if stats:
                print(f"📊 User Stats for {args.stats}:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ User not found")
        
        elif args.cleanup:
            await provisioner.cleanup_expired_accounts()
            print("✅ Cleanup completed")
        
        else:
            parser.print_help()
    
    finally:
        await provisioner.close()


if __name__ == "__main__":
    asyncio.run(main())
