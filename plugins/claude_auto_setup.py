#!/usr/bin/env python3
"""
Claude Plugin Auto-Setup
Handles automatic onboarding when MCP Memory Server is added to Claude Desktop
"""

import os
import json
import asyncio
import time
import webbrowser
import httpx
from pathlib import Path
from typing import Dict, Optional

class ClaudeAutoSetup:
    """Automatic setup for Claude Desktop integration"""
    
    def __init__(self):
        self.api_base = os.getenv("MCP_MEMORY_API_URL", "https://api.mcpmemory.cloud")
        self.config_path = Path.home() / ".mcp_memory" / "claude_config.json"
        self.session_id = None
        self.user_config = None
        
    async def start_onboarding(self) -> bool:
        """Start the onboarding process"""
        print("🌩️ MCP Memory Cloud - Claude Setup")
        print("=" * 50)
        
        # Check if already configured
        if await self.check_existing_config():
            print("✅ Claude plugin already configured!")
            return True
        
        print("🔧 Starting automatic setup...")
        
        try:
            # Request onboarding session
            session_data = await self.request_onboarding_session()
            if not session_data:
                return False
            
            self.session_id = session_data["session_id"]
            signup_url = session_data["signup_url"]
            
            print(f"🔗 Opening browser for account setup...")
            print(f"   URL: {signup_url}")
            
            # Open browser
            webbrowser.open(signup_url)
            
            # Wait for completion
            print("⏳ Waiting for account setup completion...")
            print("   (Complete the signup in your browser)")
            
            success = await self.wait_for_completion()
            
            if success:
                print("🎉 Setup completed successfully!")
                await self.save_config()
                return True
            else:
                print("❌ Setup failed or timed out")
                return False
                
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return False
    
    async def check_existing_config(self) -> bool:
        """Check if plugin is already configured"""
        if not self.config_path.exists():
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            api_key = config.get("api_key")
            if not api_key:
                return False
            
            # Verify API key is still valid
            valid = await self.verify_api_key(api_key)
            if valid:
                self.user_config = config
                return True
            else:
                # Remove invalid config
                self.config_path.unlink()
                return False
                
        except Exception:
            return False
    
    async def verify_api_key(self, api_key: str) -> bool:
        """Verify API key is valid"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/api/v1/config/claude",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def request_onboarding_session(self) -> Optional[Dict]:
        """Request onboarding session from API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/api/v1/onboard",
                    json={
                        "plugin_type": "claude",
                        "user_id": None,
                        "return_url": "claude://plugin-configured"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"❌ Onboarding request failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ Network error: {e}")
            return None
    
    async def wait_for_completion(self, timeout: int = 600) -> bool:
        """Wait for signup completion (10 minutes timeout)"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.api_base}/api/v1/onboard/status/{self.session_id}",
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        
                        if status == "completed":
                            self.user_config = {
                                "api_key": data.get("api_key"),
                                "user_id": data.get("user_id"),
                                "plugin_type": "claude",
                                "configured_at": time.time()
                            }
                            return True
                        elif status == "failed":
                            print("❌ Signup failed")
                            return False
                    
                    # Print progress dots
                    print(".", end="", flush=True)
                    
            except Exception:
                pass
            
            await asyncio.sleep(5)  # Check every 5 seconds
        
        return False
    
    async def save_config(self):
        """Save configuration to local file"""
        if not self.user_config:
            return
        
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get additional config from API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/api/v1/config/claude",
                    headers={"Authorization": f"Bearer {self.user_config['api_key']}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    api_config = response.json()
                    self.user_config.update(api_config)
        except Exception:
            pass
        
        # Save to file
        with open(self.config_path, 'w') as f:
            json.dump(self.user_config, f, indent=2)
        
        print(f"💾 Configuration saved to: {self.config_path}")
    
    def get_claude_mcp_config(self) -> Dict:
        """Generate Claude MCP configuration"""
        if not self.user_config:
            return {}
        
        return {
            "mcpServers": {
                "memory-server": {
                    "command": "python",
                    "args": ["-m", "mcp_memory_server"],
                    "env": {
                        "MCP_MEMORY_API_KEY": self.user_config["api_key"],
                        "MCP_MEMORY_API_URL": self.api_base,
                        "MCP_MEMORY_USER_ID": self.user_config["user_id"]
                    }
                }
            }
        }
    
    async def update_claude_config(self):
        """Update Claude Desktop configuration"""
        try:
            # Claude Desktop config paths
            config_paths = [
                Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",  # macOS
                Path.home() / ".config" / "claude" / "claude_desktop_config.json",  # Linux
                Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"  # Windows
            ]
            
            claude_config_path = None
            for path in config_paths:
                if path.parent.exists():
                    claude_config_path = path
                    break
            
            if not claude_config_path:
                print("⚠️ Claude Desktop config directory not found")
                print("   Please manually add the MCP server configuration")
                return False
            
            # Load existing config
            existing_config = {}
            if claude_config_path.exists():
                with open(claude_config_path, 'r') as f:
                    existing_config = json.load(f)
            
            # Add MCP server config
            mcp_config = self.get_claude_mcp_config()
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
            
            existing_config["mcpServers"].update(mcp_config["mcpServers"])
            
            # Save updated config
            with open(claude_config_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            
            print(f"✅ Claude Desktop configuration updated: {claude_config_path}")
            print("🔄 Please restart Claude Desktop to load the memory server")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update Claude config: {e}")
            return False

async def main():
    """Main entry point for Claude auto-setup"""
    setup = ClaudeAutoSetup()
    
    success = await setup.start_onboarding()
    
    if success:
        await setup.update_claude_config()
        print("\n🎉 Claude Memory Plugin Setup Complete!")
        print("   Your AI conversations will now have persistent memory")
        print("   across all your Claude Desktop sessions.")
    else:
        print("\n❌ Setup failed. Please try again or contact support.")

if __name__ == "__main__":
    asyncio.run(main()) 