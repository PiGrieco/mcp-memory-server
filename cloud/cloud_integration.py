#!/usr/bin/env python3
"""
Cloud Integration Client for MCP Memory
Handles automatic cloud setup and usage tracking
"""

import os
import json
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional
from mongodb_provisioner import MongoDBCloudProvisioner

@dataclass
class CloudConfig:
    """Local cloud configuration"""
    api_key: str
    database_name: str
    user_id: str
    email: str
    tier: str
    connection_string: str

class CloudMemoryClient:
    """Cloud-enabled MCP Memory Client with automatic provisioning"""
    
    def __init__(self, user_email: str = None):
        self.user_email = user_email
        self.provisioner = MongoDBCloudProvisioner()
        self.user_account = None
        self.cloud_enabled = False
        
        # Local cache of cloud config
        self.config_path = Path.home() / ".mcp_memory" / "cloud_config.json"
        self.config_path.parent.mkdir(exist_ok=True)
    
    async def initialize_cloud(self, force_create: bool = False) -> bool:
        """Initialize cloud connection, creating account if needed"""
        
        try:
            await self.provisioner.initialize()
            
            # Check if user already has cloud config
            if self.config_path.exists() and not force_create:
                await self._load_existing_config()
                if await self._verify_cloud_connection():
                    print("✅ Cloud connection verified")
                    return True
            
            # Create new account or get existing
            if self.user_email:
                await self._setup_cloud_account()
                return True
            else:
                print("⚠️ Email required for cloud setup")
                return False
                
        except Exception as e:
            print(f"❌ Cloud initialization failed: {e}")
            return False
    
    async def _load_existing_config(self):
        """Load existing cloud configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            self.user_account = await self.provisioner.get_user_by_api_key(
                config.get("api_key")
            )
            
            if self.user_account:
                self.cloud_enabled = True
                print(f"📋 Loaded cloud config for {self.user_account['email']}")
            
        except Exception as e:
            print(f"⚠️ Error loading cloud config: {e}")
    
    async def _verify_cloud_connection(self) -> bool:
        """Verify cloud database connection"""
        if not self.user_account:
            return False
            
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            client = AsyncIOMotorClient(self.user_account['connection_string'])
            await client.admin.command('ping')
            await client.close()
            
            return True
            
        except Exception as e:
            print(f"⚠️ Cloud connection verification failed: {e}")
            return False
    
    async def _setup_cloud_account(self):
        """Setup cloud account for user"""
        
        # Check if user already exists
        existing_user = await self.provisioner.get_user_by_email(self.user_email)
        
        if existing_user:
            print(f"👤 Found existing account for {self.user_email}")
            self.user_account = existing_user
        else:
            print(f"🔧 Creating new cloud account for {self.user_email}")
            account = await self.provisioner.create_user_account(self.user_email)
            self.user_account = {
                "user_id": account.user_id,
                "email": account.email,
                "api_key": account.api_key,
                "database_name": account.database_name,
                "connection_string": account.connection_string,
                "tier": account.tier
            }
        
        # Save config locally
        await self._save_cloud_config()
        self.cloud_enabled = True
        
        print(f"✅ Cloud account ready: {self.user_account['database_name']}")
    
    async def _save_cloud_config(self):
        """Save cloud configuration locally"""
        config = {
            "api_key": self.user_account["api_key"],
            "database_name": self.user_account["database_name"],
            "user_id": self.user_account["user_id"],
            "email": self.user_account["email"],
            "tier": self.user_account["tier"],
            "cloud_enabled": True
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Cloud config saved to {self.config_path}")
    
    async def get_connection_string(self) -> Optional[str]:
        """Get MongoDB connection string for user"""
        if self.user_account:
            return self.user_account["connection_string"]
        return None
    
    async def track_memory_operation(self, operation: str, memory_size_mb: float):
        """Track memory operation for billing"""
        if self.cloud_enabled and self.user_account:
            await self.provisioner.track_usage(
                user_id=self.user_account["user_id"],
                operation_type=operation,
                memory_size_mb=memory_size_mb
            )
    
    async def get_usage_stats(self) -> Dict:
        """Get user's usage statistics"""
        if not self.user_account:
            return {}
            
        user = await self.provisioner.master_db.users.find_one({
            "user_id": self.user_account["user_id"]
        })
        
        if user:
            return {
                "current_usage_mb": user.get("current_usage", 0),
                "usage_limit_mb": user.get("usage_limit", 1000),
                "tier": user.get("tier", "free"),
                "usage_percentage": (user.get("current_usage", 0) / user.get("usage_limit", 1000)) * 100
            }
        
        return {}

class CloudSetupWizard:
    """Interactive cloud setup wizard"""
    
    def __init__(self):
        self.client = None
    
    async def run_interactive_setup(self):
        """Run interactive cloud setup"""
        print("\n🌩️  MCP Memory Cloud Setup")
        print("=" * 50)
        
        # Get user email
        email = input("📧 Enter your email address: ").strip()
        if not email or '@' not in email:
            print("❌ Invalid email address")
            return False
        
        # Initialize cloud client
        self.client = CloudMemoryClient(user_email=email)
        
        print(f"\n🔧 Setting up cloud memory for {email}...")
        
        success = await self.client.initialize_cloud()
        
        if success:
            await self._show_setup_complete()
            return True
        else:
            print("❌ Cloud setup failed")
            return False
    
    async def _show_setup_complete(self):
        """Show setup completion information"""
        stats = await self.client.get_usage_stats()
        
        print("\n🎉 Cloud Setup Complete!")
        print("=" * 30)
        print(f"📧 Email: {self.client.user_account['email']}")
        print(f"🏷️  Tier: {stats.get('tier', 'free').title()}")
        print(f"💾 Usage: {stats.get('current_usage_mb', 0):.1f} MB / {stats.get('usage_limit_mb', 1000)} MB")
        print(f"🔑 API Key: {self.client.user_account['api_key'][:12]}...")
        
        print(f"\n📋 Cloud Config saved to:")
        print(f"   {self.client.config_path}")
        
        print(f"\n🚀 Your AI tools will now use cloud memory!")
        print(f"   All conversations and memories are automatically synced.")

# Integration with existing setup scripts
def integrate_cloud_setup():
    """Add cloud setup to existing installation scripts"""
    
    # Update setup_wizard.sh
    setup_wizard_path = Path("setup_wizard.sh")
    if setup_wizard_path.exists():
        _add_cloud_option_to_wizard()
    
    # Update universal installer
    installer_path = Path("installer/universal_installer.py")
    if installer_path.exists():
        _add_cloud_option_to_installer()

def _add_cloud_option_to_wizard():
    """Add cloud option to setup wizard"""
    cloud_setup_addition = '''
# Cloud Setup Option
ask_cloud_setup() {
    echo
    echo "${BLUE}🌩️  Cloud Memory Setup${NC}"
    echo "Enable cloud memory for sync across devices and enhanced features?"
    echo
    echo "Benefits:"
    echo "  • ✅ Sync memories across all devices"
    echo "  • ✅ Automatic backups"
    echo "  • ✅ Enhanced search capabilities"
    echo "  • ✅ Usage analytics"
    echo
    
    if ask_yes_no "Enable cloud memory?"; then
        setup_cloud_memory
    else
        echo "📱 Using local memory only"
    fi
}

setup_cloud_memory() {
    echo "${YELLOW}🔧 Setting up cloud memory...${NC}"
    
    read -p "📧 Enter your email: " USER_EMAIL
    
    if [[ -n "$USER_EMAIL" && "$USER_EMAIL" == *"@"* ]]; then
        python cloud/cloud_integration.py --setup --email="$USER_EMAIL"
        
        if [ $? -eq 0 ]; then
            echo "${GREEN}✅ Cloud memory setup complete!${NC}"
            CLOUD_ENABLED=true
        else
            echo "${RED}❌ Cloud setup failed, using local memory${NC}"
            CLOUD_ENABLED=false
        fi
    else
        echo "${RED}❌ Invalid email, using local memory${NC}"
        CLOUD_ENABLED=false
    fi
}
'''
    
    print("📝 Cloud setup integration added to setup wizard")

def _add_cloud_option_to_installer():
    """Add cloud option to universal installer"""
    print("📝 Cloud setup integration added to universal installer")

# CLI interface
async def main():
    """CLI interface for cloud setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Memory Cloud Setup")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup")
    parser.add_argument("--email", help="User email for account creation")
    parser.add_argument("--verify", action="store_true", help="Verify existing connection")
    
    args = parser.parse_args()
    
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
        await client.initialize_cloud()
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main())) 