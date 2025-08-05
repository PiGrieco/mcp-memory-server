#!/usr/bin/env python3
"""
Interactive Setup Guide for MongoDB Atlas + Stripe
Step-by-step configuration with validation
"""

import os
import asyncio
import json
import requests
from pathlib import Path

class InteractiveSetup:
    """Interactive setup wizard for cloud services"""
    
    def __init__(self):
        self.config = {}
        self.env_file = Path("cloud/.env")
        
    def print_header(self, title):
        print(f"\n{'=' * 60}")
        print(f"🚀 {title}")
        print(f"{'=' * 60}")
    
    def print_step(self, step, title):
        print(f"\n{step} {title}")
        print("-" * 40)
    
    async def setup_mongodb_atlas(self):
        """Setup MongoDB Atlas configuration"""
        
        self.print_header("MONGODB ATLAS SETUP")
        
        print("""
📋 MongoDB Atlas Setup Requirements:
1. Account su MongoDB Atlas (https://cloud.mongodb.com)
2. Progetto creato
3. API Keys generate (Project Settings > Access Manager > API Keys)
4. Cluster esistente (shared cluster OK per iniziare)
        """)
        
        # Step 1: API Keys
        self.print_step("1️⃣", "API Keys Configuration")
        
        has_atlas = input("Hai già un account MongoDB Atlas? (y/n): ").lower() == 'y'
        
        if not has_atlas:
            print("""
🔧 CREA ACCOUNT MONGODB ATLAS:
1. Vai su https://cloud.mongodb.com
2. Crea account gratuito
3. Crea un nuovo progetto
4. Segui i prossimi step...
            """)
            input("Premi ENTER quando hai creato l'account...")
        
        print("""
🔑 GENERA API KEYS:
1. Nel tuo progetto MongoDB Atlas
2. Vai in: Project Settings > Access Manager > API Keys
3. Clicca "Create API Key"
4. Seleziona permissions: "Project Data Access Admin"
5. Copia Public Key e Private Key
        """)
        
        public_key = input("📝 MongoDB Atlas Public Key: ").strip()
        private_key = input("📝 MongoDB Atlas Private Key: ").strip()
        
        # Step 2: Project ID
        self.print_step("2️⃣", "Project ID")
        print("""
🔍 TROVA PROJECT ID:
1. Nella dashboard MongoDB Atlas
2. L'URL sarà tipo: https://cloud.mongodb.com/v2/PROJECT_ID#/overview
3. Copia il PROJECT_ID dall'URL
        """)
        
        project_id = input("📝 MongoDB Atlas Project ID: ").strip()
        
        # Step 3: Master Database Connection
        self.print_step("3️⃣", "Master Database Connection")
        print("""
🗄️ SETUP MASTER DATABASE:
1. Nel tuo cluster, clicca "Connect"
2. Scegli "Connect your application"  
3. Copia la connection string
4. Sostituisci <password> con la password reale
5. Aggiungi database name: mcp_memory_master
        """)
        
        connection_string = input("📝 Master Connection String: ").strip()
        
        # Validation
        print("\n🧪 Validating MongoDB configuration...")
        
        if await self._validate_mongodb_config(public_key, private_key, project_id, connection_string):
            print("✅ MongoDB Atlas configuration valid!")
            
            self.config.update({
                "MONGODB_ATLAS_PUBLIC_KEY": public_key,
                "MONGODB_ATLAS_PRIVATE_KEY": private_key, 
                "MONGODB_ATLAS_PROJECT_ID": project_id,
                "MONGODB_MASTER_CONNECTION": connection_string
            })
            return True
        else:
            print("❌ MongoDB configuration validation failed!")
            return False
    
    async def setup_stripe(self):
        """Setup Stripe configuration"""
        
        self.print_header("STRIPE SETUP")
        
        print("""
💳 Stripe Setup Requirements:
1. Account Stripe (https://dashboard.stripe.com)
2. API Keys (test + eventualmente live)
3. Webhook endpoint configurato
        """)
        
        # Step 1: Account creation
        self.print_step("1️⃣", "Stripe Account")
        
        has_stripe = input("Hai già un account Stripe? (y/n): ").lower() == 'y'
        
        if not has_stripe:
            print("""
🔧 CREA ACCOUNT STRIPE:
1. Vai su https://dashboard.stripe.com/register
2. Crea account (anche solo test per ora)
3. Completa setup base
            """)
            input("Premi ENTER quando hai creato l'account...")
        
        # Step 2: API Keys
        self.print_step("2️⃣", "API Keys")
        print("""
🔑 OTTIENI API KEYS:
1. Nella Stripe Dashboard
2. Vai in: Developers > API Keys
3. Copia "Publishable key" e "Secret key" (test mode)
        """)
        
        publishable_key = input("📝 Stripe Publishable Key (pk_test_...): ").strip()
        secret_key = input("📝 Stripe Secret Key (sk_test_...): ").strip()
        
        # Step 3: Webhook setup
        self.print_step("3️⃣", "Webhook Configuration")
        print("""
🔗 SETUP WEBHOOK (opzionale per ora):
1. Vai in: Developers > Webhooks
2. Clicca "Add endpoint"
3. URL: https://your-domain.com/webhook/stripe (o localhost per test)
4. Eventi: invoice.payment_succeeded, invoice.payment_failed, customer.subscription.deleted
5. Copia il "Signing secret"
        """)
        
        setup_webhook = input("Vuoi configurare webhook ora? (y/n): ").lower() == 'y'
        webhook_secret = ""
        
        if setup_webhook:
            webhook_secret = input("📝 Webhook Signing Secret (whsec_...): ").strip()
        else:
            print("⚠️ Webhook verrà configurato successivamente")
            webhook_secret = "whsec_placeholder_for_later"
        
        # Validation
        print("\n🧪 Validating Stripe configuration...")
        
        if self._validate_stripe_config(publishable_key, secret_key):
            print("✅ Stripe configuration valid!")
            
            self.config.update({
                "STRIPE_PUBLISHABLE_KEY": publishable_key,
                "STRIPE_SECRET_KEY": secret_key,
                "STRIPE_WEBHOOK_SECRET": webhook_secret
            })
            return True
        else:
            print("❌ Stripe configuration validation failed!")
            return False
    
    async def _validate_mongodb_config(self, public_key, private_key, project_id, connection_string):
        """Validate MongoDB Atlas configuration"""
        try:
            # Test Atlas API
            import httpx
            auth = httpx.DigestAuth(public_key, private_key)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}",
                    auth=auth,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(f"❌ Atlas API error: {response.status_code}")
                    return False
            
            # Test connection string
            from motor.motor_asyncio import AsyncIOMotorClient
            
            client = AsyncIOMotorClient(connection_string)
            await client.admin.command('ping')
            await client.close()
            
            print("✅ MongoDB Atlas API and connection validated")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB validation error: {e}")
            return False
    
    def _validate_stripe_config(self, publishable_key, secret_key):
        """Validate Stripe configuration"""
        try:
            import stripe
            stripe.api_key = secret_key
            
            # Test API call
            stripe.Account.retrieve()
            
            # Validate key formats
            if not publishable_key.startswith('pk_'):
                print("❌ Invalid publishable key format")
                return False
                
            if not secret_key.startswith('sk_'):
                print("❌ Invalid secret key format")
                return False
            
            print("✅ Stripe API validated")
            return True
            
        except Exception as e:
            print(f"❌ Stripe validation error: {e}")
            return False
    
    def save_configuration(self):
        """Save configuration to .env file"""
        
        self.print_step("💾", "Saving Configuration")
        
        # Load template
        template_path = Path("cloud/.env.example")
        if template_path.exists():
            with open(template_path, 'r') as f:
                template_content = f.read()
        else:
            template_content = ""
        
        # Update with real values
        env_content = template_content
        for key, value in self.config.items():
            # Replace template values
            old_pattern = f"{key}=your_"
            if old_pattern in env_content:
                env_content = env_content.replace(f"{key}=your_{key.lower()}", f"{key}={value}")
            else:
                # Add new line if not exists
                env_content += f"\n{key}={value}"
        
        # Save to .env
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Configuration saved to {self.env_file}")
        
        # Show summary
        print(f"\n📋 CONFIGURATION SUMMARY:")
        for key, value in self.config.items():
            if "SECRET" in key or "PRIVATE" in key:
                print(f"   {key}: {value[:8]}...")
            else:
                print(f"   {key}: {value}")
    
    async def test_complete_setup(self):
        """Test the complete setup"""
        
        self.print_step("🧪", "Testing Complete Setup")
        
        # Load environment
        from dotenv import load_dotenv
        load_dotenv(self.env_file)
        
        try:
            # Test MongoDB provisioner
            print("Testing MongoDB provisioner...")
            from cloud.mongodb_provisioner import MongoDBCloudProvisioner
            
            provisioner = MongoDBCloudProvisioner()
            await provisioner.initialize()
            print("✅ MongoDB provisioner initialized")
            
            # Test billing system
            print("Testing billing system...")
            from cloud.billing_system import BillingSystem
            
            billing = BillingSystem()
            await billing.initialize()
            print("✅ Billing system initialized")
            
            # Test user creation (demo)
            print("Testing user creation...")
            demo_user = await provisioner.create_user_account(
                email="test@example.com",
                full_name="Test User"
            )
            print(f"✅ Demo user created: {demo_user.database_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Setup test failed: {e}")
            return False
    
    async def run_complete_setup(self):
        """Run complete interactive setup"""
        
        print("🌩️ MCP MEMORY CLOUD - INTERACTIVE SETUP")
        print("Setting up MongoDB Atlas + Stripe for production use")
        
        # MongoDB Atlas Setup
        mongodb_success = await self.setup_mongodb_atlas()
        if not mongodb_success:
            print("❌ MongoDB setup failed. Please check your configuration.")
            return False
        
        # Stripe Setup  
        stripe_success = await self.setup_stripe()
        if not stripe_success:
            print("❌ Stripe setup failed. Please check your configuration.")
            return False
        
        # Save configuration
        self.save_configuration()
        
        # Test complete setup
        test_success = await self.test_complete_setup()
        
        if test_success:
            self.print_header("🎉 SETUP COMPLETED SUCCESSFULLY!")
            print("""
✅ MongoDB Atlas configured and tested
✅ Stripe configured and tested  
✅ Environment file created
✅ Services initialized successfully

🚀 NEXT STEPS:
1. Run: python cloud/usage_example.py (to test everything)
2. Deploy to production server
3. Update webhook URLs in Stripe dashboard
4. Start onboarding users!

💰 Your cloud monetization system is ready!
            """)
        else:
            print("❌ Setup validation failed. Please check the errors above.")
        
        return test_success

async def main():
    """Main setup function"""
    setup = InteractiveSetup()
    await setup.run_complete_setup()

if __name__ == "__main__":
    asyncio.run(main()) 