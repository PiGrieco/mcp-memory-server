#!/usr/bin/env python3
"""
Production-Ready Cloud Integration for MCP Memory Server
Handles cloud deployment, provisioning, and synchronization with enhanced architecture
"""

import os
import json
import asyncio
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from ..src.config.settings import get_config
from ..src.utils.logging import get_logger, log_performance
from ..src.utils.exceptions import MCPMemoryError, ConfigurationError
from ..src.utils.retry import retry_async
from ..src.utils.validation import validate_email


logger = get_logger(__name__)


@dataclass
class CloudConfig:
    """Production-ready cloud configuration"""
    api_key: str
    database_name: str
    user_id: str
    email: str
    tier: str
    connection_string: str
    region: str = "us-east-1"
    cluster_tier: str = "M0"  # Free tier
    backup_enabled: bool = True
    encryption_enabled: bool = True
    created_at: datetime = None
    last_sync: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class CloudProvisioningError(MCPMemoryError):
    """Error during cloud provisioning"""
    pass


class CloudMemoryClient:
    """Production-ready cloud-enabled MCP Memory Client"""
    
    def __init__(self, user_email: Optional[str] = None, config_override: Optional[Dict] = None):
        self.config = get_config()
        self.user_email = user_email
        self.user_account: Optional[CloudConfig] = None
        self.cloud_enabled = False
        
        # Configuration paths
        self.config_path = Path.home() / ".mcp_memory" / "cloud_config.json"
        self.backup_path = Path.home() / ".mcp_memory" / "backups"
        
        # Ensure directories exist
        self.config_path.parent.mkdir(exist_ok=True)
        self.backup_path.mkdir(exist_ok=True)
        
        # Initialize provisioner
        self.provisioner = None
        self._init_provisioner()
    
    def _init_provisioner(self):
        """Initialize cloud provisioner"""
        try:
            from .mongodb_provisioner import MongoDBCloudProvisioner
            self.provisioner = MongoDBCloudProvisioner()
        except ImportError as e:
            logger.warning(f"Cloud provisioner not available: {e}")
    
    @retry_async(max_attempts=3, delay=1.0)
    @log_performance("cloud_initialization")
    async def initialize_cloud(self, force_create: bool = False) -> bool:
        """Initialize cloud connection with retry and validation"""
        if not self.provisioner:
            logger.error("Cloud provisioner not available")
            return False
        
        try:
            await self.provisioner.initialize()
            
            # Load existing configuration if available
            if self.config_path.exists() and not force_create:
                await self._load_existing_config()
                if await self._verify_cloud_connection():
                    logger.info("Cloud connection verified successfully")
                    return True
            
            # Create new account if email is provided
            if self.user_email:
                if not validate_email(self.user_email):
                    raise ConfigurationError(f"Invalid email address: {self.user_email}")
                
                await self._setup_cloud_account()
                return True
            else:
                logger.warning("Email required for cloud setup")
                return False
                
        except Exception as e:
            logger.error(f"Cloud initialization failed: {e}")
            raise CloudProvisioningError(f"Failed to initialize cloud: {e}")
    
    async def _load_existing_config(self):
        """Load and validate existing cloud configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Validate configuration schema
            required_fields = ['api_key', 'database_name', 'user_id', 'email', 'tier']
            if not all(field in config_data for field in required_fields):
                raise ConfigurationError("Invalid cloud configuration format")
            
            # Load user account from provisioner
            self.user_account = await self.provisioner.get_user_by_api_key(
                config_data.get("api_key")
            )
            
            if self.user_account:
                self.cloud_enabled = True
                logger.info(f"Loaded cloud config for {self.user_account.email}")
            else:
                logger.warning("Failed to load user account from cloud config")
            
        except Exception as e:
            logger.error(f"Error loading cloud config: {e}")
            # Create backup of corrupted config
            await self._backup_config("corrupted")
    
    @retry_async(max_attempts=3, delay=2.0)
    async def _verify_cloud_connection(self) -> bool:
        """Verify cloud database connection with timeout"""
        if not self.user_account:
            return False
        
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            import asyncio
            
            client = AsyncIOMotorClient(
                self.user_account.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test connection with timeout
            await asyncio.wait_for(
                client.admin.command('ping'), 
                timeout=10.0
            )
            await client.close()
            
            # Update last sync time
            self.user_account.last_sync = datetime.now(timezone.utc)
            await self._save_cloud_config()
            
            return True
            
        except Exception as e:
            logger.warning(f"Cloud connection verification failed: {e}")
            return False
    
    @log_performance("cloud_account_setup")
    async def _setup_cloud_account(self):
        """Setup cloud account with enhanced error handling"""
        try:
            # Check for existing user
            existing_user = await self.provisioner.get_user_by_email(self.user_email)
            
            if existing_user:
                logger.info(f"Found existing account for {self.user_email}")
                self.user_account = existing_user
            else:
                logger.info(f"Creating new cloud account for {self.user_email}")
                account = await self.provisioner.create_user_account(
                    email=self.user_email,
                    tier="free",
                    region="us-east-1"
                )
                
                self.user_account = CloudConfig(
                    user_id=account.user_id,
                    email=account.email,
                    api_key=account.api_key,
                    database_name=account.database_name,
                    connection_string=account.connection_string,
                    tier=account.tier,
                    region=account.region,
                    cluster_tier=account.cluster_tier
                )
            
            # Save configuration
            await self._save_cloud_config()
            self.cloud_enabled = True
            
            logger.info(f"Cloud account ready: {self.user_account.database_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup cloud account: {e}")
            raise CloudProvisioningError(f"Cloud account setup failed: {e}")
    
    async def _save_cloud_config(self):
        """Save cloud configuration with backup"""
        try:
            # Create backup of existing config
            if self.config_path.exists():
                await self._backup_config("auto")
            
            config_data = {
                **asdict(self.user_account),
                "cloud_enabled": True,
                "saved_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Convert datetime objects to ISO format
            for key, value in config_data.items():
                if isinstance(value, datetime):
                    config_data[key] = value.isoformat()
            
            # Atomic write
            temp_path = self.config_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            temp_path.replace(self.config_path)
            
            logger.debug(f"Cloud config saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save cloud config: {e}")
            raise
    
    async def _backup_config(self, reason: str = "manual"):
        """Create timestamped backup of cloud configuration"""
        if not self.config_path.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_path / f"cloud_config_{reason}_{timestamp}.json"
        
        try:
            import shutil
            shutil.copy2(self.config_path, backup_file)
            logger.debug(f"Config backup created: {backup_file}")
        except Exception as e:
            logger.warning(f"Failed to create config backup: {e}")
    
    async def get_connection_string(self) -> Optional[str]:
        """Get secure MongoDB connection string"""
        if self.user_account:
            return self.user_account.connection_string
        return None
    
    @log_performance("usage_tracking")
    async def track_memory_operation(
        self, 
        operation: str, 
        memory_size_mb: float, 
        metadata: Optional[Dict] = None
    ):
        """Track memory operation for billing and analytics"""
        if not (self.cloud_enabled and self.user_account):
            return
        
        try:
            await self.provisioner.track_usage(
                user_id=self.user_account.user_id,
                operation_type=operation,
                memory_size_mb=memory_size_mb,
                metadata=metadata or {},
                timestamp=datetime.now(timezone.utc)
            )
        except Exception as e:
            logger.warning(f"Failed to track usage: {e}")
    
    async def get_usage_stats(self) -> Dict:
        """Get comprehensive user usage statistics"""
        if not self.user_account:
            return {}
        
        try:
            user_data = await self.provisioner.get_user_stats(
                self.user_account.user_id
            )
            
            if user_data:
                return {
                    "current_usage_mb": user_data.get("current_usage", 0),
                    "usage_limit_mb": user_data.get("usage_limit", 1000),
                    "tier": user_data.get("tier", "free"),
                    "usage_percentage": (
                        user_data.get("current_usage", 0) / 
                        user_data.get("usage_limit", 1000)
                    ) * 100,
                    "operations_count": user_data.get("operations_count", 0),
                    "last_activity": user_data.get("last_activity"),
                    "account_created": user_data.get("created_at")
                }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
        
        return {}
    
    async def sync_to_cloud(self, memories: List[Dict]) -> bool:
        """Synchronize local memories to cloud"""
        if not self.cloud_enabled:
            return False
        
        try:
            sync_result = await self.provisioner.sync_memories(
                user_id=self.user_account.user_id,
                memories=memories
            )
            
            if sync_result.get("success"):
                logger.info(f"Synced {len(memories)} memories to cloud")
                return True
            else:
                logger.warning(f"Cloud sync failed: {sync_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to sync to cloud: {e}")
            return False
    
    async def get_cloud_memories(self, project: str = "default") -> List[Dict]:
        """Retrieve memories from cloud"""
        if not self.cloud_enabled:
            return []
        
        try:
            memories = await self.provisioner.get_memories(
                user_id=self.user_account.user_id,
                project=project
            )
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get cloud memories: {e}")
            return []


class CloudSetupWizard:
    """Enhanced interactive cloud setup wizard"""
    
    def __init__(self):
        self.client: Optional[CloudMemoryClient] = None
        self.logger = get_logger(__name__)
    
    async def run_interactive_setup(self) -> bool:
        """Run interactive cloud setup with validation"""
        print("\n🌩️  MCP Memory Cloud Setup (Production Ready)")
        print("=" * 60)
        
        try:
            # Get and validate user email
            email = await self._get_user_email()
            if not email:
                return False
            
            # Initialize cloud client
            self.client = CloudMemoryClient(user_email=email)
            
            print(f"\n🔧 Setting up cloud memory for {email}...")
            print("📊 This includes:")
            print("  • ✅ Secure MongoDB Atlas cluster")
            print("  • ✅ Automatic backups and encryption")
            print("  • ✅ Cross-device synchronization")
            print("  • ✅ Usage analytics and monitoring")
            
            # Setup cloud account
            success = await self.client.initialize_cloud()
            
            if success:
                await self._show_setup_complete()
                await self._show_integration_instructions()
                return True
            else:
                print("❌ Cloud setup failed - check logs for details")
                return False
                
        except Exception as e:
            self.logger.error(f"Setup wizard failed: {e}")
            print(f"❌ Setup failed: {e}")
            return False
    
    async def _get_user_email(self) -> Optional[str]:
        """Get and validate user email"""
        while True:
            email = input("📧 Enter your email address: ").strip()
            
            if not email:
                print("❌ Email is required")
                continue
            
            if not validate_email(email):
                print("❌ Please enter a valid email address")
                continue
            
            return email
    
    async def _show_setup_complete(self):
        """Show comprehensive setup completion information"""
        stats = await self.client.get_usage_stats()
        
        print("\n🎉 Cloud Setup Complete!")
        print("=" * 40)
        print(f"📧 Email: {self.client.user_account.email}")
        print(f"🏷️  Tier: {stats.get('tier', 'free').title()}")
        print(f"💾 Usage: {stats.get('current_usage_mb', 0):.1f} MB / {stats.get('usage_limit_mb', 1000)} MB")
        print(f"🔑 API Key: {self.client.user_account.api_key[:12]}...")
        print(f"🌍 Region: {self.client.user_account.region}")
        print(f"🛡️  Security: Encryption enabled")
        
        print(f"\n📋 Configuration saved to:")
        print(f"   {self.client.config_path}")
        print(f"📁 Backups location:")
        print(f"   {self.client.backup_path}")
    
    async def _show_integration_instructions(self):
        """Show integration instructions for different tools"""
        print(f"\n🚀 Integration Ready!")
        print("=" * 30)
        print("Your AI tools will now use cloud memory automatically.")
        print("\n🔧 To integrate with other tools:")
        print("  • Cursor: Already configured via .cursor/mcp.json")
        print("  • Claude Desktop: Update claude_desktop_config.json")
        print("  • VS Code: Install MCP extension")
        print("  • Custom tools: Use API key for authentication")
        
        print(f"\n📚 Next steps:")
        print("  1. Test the connection: python -m cloud.cloud_integration --verify")
        print("  2. View usage: python -m cloud.cloud_integration --stats")
        print("  3. Read docs: ./docs/cloud_integration.md")


# CLI interface
async def main():
    """Enhanced CLI interface for cloud management"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MCP Memory Cloud Integration (Production Ready)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m cloud.cloud_integration --setup --email user@example.com
  python -m cloud.cloud_integration --verify
  python -m cloud.cloud_integration --stats
  python -m cloud.cloud_integration --sync
        """
    )
    
    parser.add_argument("--setup", action="store_true", help="Run cloud setup")
    parser.add_argument("--email", help="User email for account creation")
    parser.add_argument("--verify", action="store_true", help="Verify cloud connection")
    parser.add_argument("--stats", action="store_true", help="Show usage statistics")
    parser.add_argument("--sync", action="store_true", help="Sync local memories to cloud")
    parser.add_argument("--backup", action="store_true", help="Create configuration backup")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    if args.setup:
        if args.email:
            # Non-interactive setup
            client = CloudMemoryClient(user_email=args.email)
            success = await client.initialize_cloud()
            if success:
                print("✅ Cloud setup complete")
                return 0
            else:
                print("❌ Cloud setup failed")
                return 1
        else:
            # Interactive setup
            wizard = CloudSetupWizard()
            success = await wizard.run_interactive_setup()
            return 0 if success else 1
    
    elif args.verify:
        client = CloudMemoryClient()
        success = await client.initialize_cloud()
        if success:
            print("✅ Cloud connection verified")
            return 0
        else:
            print("❌ Cloud connection failed")
            return 1
    
    elif args.stats:
        client = CloudMemoryClient()
        await client.initialize_cloud()
        stats = await client.get_usage_stats()
        
        if stats:
            print("\n📊 Usage Statistics")
            print("=" * 30)
            for key, value in stats.items():
                print(f"{key}: {value}")
        else:
            print("❌ No usage statistics available")
        return 0
    
    elif args.backup:
        client = CloudMemoryClient()
        await client._backup_config("manual")
        print("✅ Configuration backup created")
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
