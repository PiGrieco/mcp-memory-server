#!/usr/bin/env python3
"""
Unified Installation Script for MCP Memory Server
Supports all platforms: Cursor, Claude, Universal, etc.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Installer:
    """Unified installer for all platforms"""
    
    def __init__(self, platform: str = "universal"):
        self.platform = platform
        self.base_dir = Path(__file__).parent.parent.parent  # Go up to project root from scripts/install/
        self.config_dir = self.base_dir / "config"
        self.scripts_dir = self.base_dir / "scripts"
        
        # Platform configurations
        self.platform_configs = {
            "cursor": {
                "name": "Cursor IDE",
                "config_dir": Path.home() / ".cursor",
                "config_file": "mcp_settings.json",
                "auto_trigger": True,
                "ide_integration": True
            },
            "claude": {
                "name": "Claude Desktop",
                "config_dir": Path.home() / ".config" / "claude",
                "config_file": "claude_desktop_config.json",
                "auto_trigger": True,
                "conversation_mode": True
            },
            "universal": {
                "name": "Universal",
                "config_dir": self.base_dir,
                "config_file": "universal_config.json",
                "auto_trigger": True,
                "http_api": True
            }
        }
        
        self.config = self.platform_configs.get(platform, self.platform_configs["universal"])
    
    def install(self):
        """Main installation process"""
        print(f"🚀 Installing MCP Memory Server for {self.config['name']}")
        print("=" * 50)
        
        try:
            # Step 1: Check prerequisites
            self._check_prerequisites()
            
            # Step 2: Setup environment
            self._setup_environment()
            
            # Step 3: Install dependencies
            self._install_dependencies()
            
            # Step 4: Setup MongoDB
            self._setup_mongodb()
            
            # Step 5: Test ML model
            self._test_ml_model()
            
            # Step 6: Configure platform
            self._configure_platform()
            
            # Step 7: Test complete installation
            self._test_complete_installation()
            
            print("\n✅ Installation completed successfully!")
            self._print_next_steps()
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            sys.exit(1)
    
    def _check_prerequisites(self):
        """Check system prerequisites"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            raise RuntimeError(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check if we're in the right directory
        if not (self.base_dir / "src").exists():
            raise RuntimeError("Must run installer from project root directory")
        
        print("✅ Project structure verified")
    
    def _setup_environment(self):
        """Setup Python environment"""
        print("🐍 Setting up Python environment...")
        
        # Create virtual environment if it doesn't exist
        venv_dir = self.base_dir / "venv"
        if not venv_dir.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            print("✅ Virtual environment created")
        else:
            print("✅ Virtual environment already exists")
        
        # Get Python executable from venv
        if os.name == "nt":  # Windows
            self.python_exe = venv_dir / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            self.python_exe = venv_dir / "bin" / "python"
        
        if not self.python_exe.exists():
            raise RuntimeError(f"Python executable not found: {self.python_exe}")
        
        print(f"✅ Python executable: {self.python_exe}")
    
    def _install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        
        # Upgrade pip
        subprocess.run([str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install core MCP dependencies first
        core_deps = [
            "mcp>=1.0.0",
            "pydantic>=2.0.0,<3.0.0",
            "python-dotenv>=1.0.0",
            "PyYAML>=6.0.0",
            "motor>=3.0.0",  # MongoDB async driver
            "pymongo>=4.0.0",
            "aiohttp>=3.8.0"
        ]
        
        for dep in core_deps:
            try:
                subprocess.run([str(self.python_exe), "-m", "pip", "install", dep], check=True)
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Warning: Failed to install {dep}: {e}")
        
        print("✅ Core dependencies installed")
        
        # Install ML dependencies with compatible versions for Python 3.10
        ml_deps = [
            "torch>=2.0.0,<2.3.0",
            "transformers>=4.30.0,<5.0.0",
            "sentence-transformers>=2.0.0,<3.0.0",
            "scikit-learn>=1.2.0,<1.4.0",
            "numpy>=1.21.0,<1.25.0",
            "scipy>=1.9.0,<1.12.0",
            "networkx>=3.0.0,<3.3.0",
            "pyarrow>=12.0.0"
        ]
        
        for dep in ml_deps:
            subprocess.run([str(self.python_exe), "-m", "pip", "install", dep], check=True)
        
        print("✅ ML dependencies installed")
    
    def _setup_mongodb(self):
        """Setup MongoDB for the memory database"""
        print("🗄️ Setting up MongoDB...")
        
        import platform
        system = platform.system().lower()
        
        try:
            # Check if MongoDB is already running
            result = subprocess.run(["mongosh", "--eval", "db.runCommand('ping')"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ MongoDB is already running")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Install MongoDB based on platform
        if system == "darwin":  # macOS
            self._install_mongodb_macos()
        elif system == "linux":
            self._install_mongodb_linux()
        elif system == "windows":
            self._install_mongodb_windows()
        else:
            print(f"⚠️ Unsupported platform: {system}")
            print("Please install MongoDB manually from: https://www.mongodb.com/try/download/community")
            return
        
        # Start MongoDB service
        self._start_mongodb()
        print("✅ MongoDB setup completed")
    
    def _install_mongodb_macos(self):
        """Install MongoDB on macOS using Homebrew"""
        print("📦 Installing MongoDB on macOS...")
        
        # Check if Homebrew is installed
        try:
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("❌ Homebrew not found. Installing Homebrew first...")
            install_brew = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            subprocess.run(install_brew, shell=True, check=True)
        
        # Install MongoDB
        subprocess.run(["brew", "tap", "mongodb/brew"], check=True)
        subprocess.run(["brew", "install", "mongodb-community"], check=True)
        print("✅ MongoDB installed via Homebrew")
    
    def _install_mongodb_linux(self):
        """Install MongoDB on Linux"""
        print("📦 Installing MongoDB on Linux...")
        
        # Try to detect the distribution
        try:
            with open("/etc/os-release") as f:
                os_release = f.read().lower()
            
            if "ubuntu" in os_release or "debian" in os_release:
                # Ubuntu/Debian
                subprocess.run([
                    "wget", "-qO", "-", "https://www.mongodb.org/static/pgp/server-7.0.asc",
                    "|", "sudo", "apt-key", "add", "-"
                ], shell=True, check=True)
                
                subprocess.run([
                    "echo", '"deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse"',
                    "|", "sudo", "tee", "/etc/apt/sources.list.d/mongodb-org-7.0.list"
                ], shell=True, check=True)
                
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "mongodb-org"], check=True)
                
            elif "centos" in os_release or "rhel" in os_release or "fedora" in os_release:
                # CentOS/RHEL/Fedora
                mongo_repo = """[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-7.0.asc"""
                
                subprocess.run(["sudo", "tee", "/etc/yum.repos.d/mongodb-org-7.0.repo"], 
                             input=mongo_repo, text=True, check=True)
                subprocess.run(["sudo", "yum", "install", "-y", "mongodb-org"], check=True)
            
            print("✅ MongoDB installed via package manager")
            
        except Exception as e:
            print(f"❌ Could not install MongoDB automatically: {e}")
            print("Please install MongoDB manually from: https://www.mongodb.com/try/download/community")
            raise
    
    def _install_mongodb_windows(self):
        """Install MongoDB on Windows"""
        print("📦 Installing MongoDB on Windows...")
        print("Please download and install MongoDB from:")
        print("https://www.mongodb.com/try/download/community")
        print("Then restart this installer.")
        raise RuntimeError("Manual MongoDB installation required on Windows")
    
    def _start_mongodb(self):
        """Start MongoDB service"""
        print("🚀 Starting MongoDB service...")
        
        import platform
        system = platform.system().lower()
        
        try:
            if system == "darwin":  # macOS
                subprocess.run(["brew", "services", "start", "mongodb/brew/mongodb-community"], check=True)
            elif system == "linux":
                subprocess.run(["sudo", "systemctl", "start", "mongod"], check=True)
                subprocess.run(["sudo", "systemctl", "enable", "mongod"], check=True)
            
            # Wait a moment for MongoDB to start
            import time
            time.sleep(3)
            
            # Test connection
            result = subprocess.run(["mongosh", "--eval", "db.runCommand('ping')"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ MongoDB service started successfully")
            else:
                raise RuntimeError("MongoDB failed to start")
                
        except Exception as e:
            print(f"❌ Failed to start MongoDB: {e}")
            print("Please start MongoDB manually")
            raise
    
    def _test_ml_model(self):
        """Download and test ML model"""
        print("🧠 Downloading and testing ML model...")
        
        test_script = f"""
import sys
sys.path.insert(0, '{self.base_dir}/src')

try:
    from transformers import pipeline
    model_name = 'PiGrieco/mcp-memory-auto-trigger-model'
    print(f'📥 Downloading ML model: {{model_name}}')
    
    # This will download the model to local cache
    classifier = pipeline(
        'text-classification',
        model=model_name,
        tokenizer=model_name,
        return_all_scores=True
    )
    
    # Test the model with a sample
    test_result = classifier('This is an important note to remember')
    print(f'✅ ML model downloaded and tested successfully')
    print(f'   Test prediction: {{test_result[0][0]["label"]}} (confidence: {{test_result[0][0]["score"]:.3f}})')
    
    from huggingface_hub import model_info
    info = model_info(model_name)
    print(f'   Model size: ~{{info.safetensors.total // (1024*1024)}}MB')
    
except Exception as e:
    print(f'❌ ML model download failed: {{e}}')
    print('Model will be downloaded on first use')
    # Don't fail installation for model issues
"""
        
        result = subprocess.run([str(self.python_exe), "-c", test_script], 
                              capture_output=True, text=True)
        
        # Don't fail installation if model download fails
        if result.returncode != 0:
            print(f"⚠️ ML model download failed: {result.stderr}")
            print("Model will be downloaded on first use")
        else:
            print(result.stdout.strip())
    
    def _configure_platform(self):
        """Configure platform-specific settings"""
        print(f"⚙️ Configuring {self.config['name']}...")
        
        # Create config directory if it doesn't exist
        self.config['config_dir'].mkdir(parents=True, exist_ok=True)
        
        # Generate platform-specific configuration
        config = self._generate_platform_config()
        
        # Write configuration file
        config_file = self.config['config_dir'] / self.config['config_file']
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to: {config_file}")
    
    def _generate_platform_config(self) -> Dict[str, Any]:
        """Generate platform-specific configuration"""
        base_config = {
            "mcpServers": {
                "mcp-memory": {
                    "command": str(self.python_exe),
                    "args": [str(self.base_dir / "main.py")],
                    "env": {
                        "ENVIRONMENT": "development",
                        "MONGODB_URI": "mongodb://localhost:27017",
                        "MONGODB_DATABASE": "mcp_memory_dev",
                        "MONGODB_COLLECTION": "memories",
                        "PLATFORM": self.platform,
                        "EMBEDDING_PROVIDER": "sentence_transformers",
                        "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
                        "ML_TRIGGER_MODE": "hybrid",
                        "AUTO_SAVE_ENABLED": "true"
                    }
                }
            }
        }
        
        # Add platform-specific settings
        if self.platform == "cursor":
            base_config["mcpServers"]["mcp-memory"]["env"].update({
                "AUTO_TRIGGER_ENABLED": "true",
                "IDE_INTEGRATION": "true"
            })
        elif self.platform == "claude":
            base_config["mcpServers"]["mcp-memory"]["env"].update({
                "AUTO_TRIGGER_ENABLED": "true",
                "CONVERSATION_MODE": "true"
            })
        
        return base_config
    
    def _test_complete_installation(self):
        """Test the complete installation with all components"""
        print("🧪 Testing complete installation...")
        
        test_script = f"""
import sys
import asyncio
import json
sys.path.insert(0, '{self.base_dir}/src')

async def test_installation():
    try:
        # Test 1: Basic imports
        from src.config.settings import get_settings
        from src.core.server import MCPServer
        print('✅ 1. Imports successful')
        
        # Test 2: Settings and server creation
        settings = get_settings()
        server = MCPServer(settings)
        print('✅ 2. Server creation successful')
        
        # Test 3: Server initialization
        await server.initialize()
        print('✅ 3. Server initialization successful')
        
        # Test 4: Test save_memory functionality
        test_args = {{
            "content": "Test installation memory",
            "context": {{"category": "test", "importance": 0.8}},
            "project": "installation_test"
        }}
        
        result = await server._handle_save_memory(test_args)
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print(f'✅ 4. Memory save test successful (ID: {{result_data.get("memory_id")}})')
        else:
            print(f'❌ 4. Memory save test failed: {{result_data.get("error")}}')
            return False
        
        # Test 5: Test analyze_message functionality  
        analyze_args = {{
            "message": "This is an important test message",
            "platform_context": {{"platform": "test"}}
        }}
        
        result = await server._handle_analyze_message(analyze_args)
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print(f'✅ 5. Message analysis test successful (Triggers: {{result_data.get("triggers")}})')
        else:
            print(f'❌ 5. Message analysis test failed: {{result_data.get("error")}}')
            return False
        
        # Test 6: Test get_memory_stats functionality
        result = await server._handle_get_memory_stats({{"random_string": "test"}})
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print(f'✅ 6. Memory stats test successful (DB: {{result_data.get("database_status")}})')
        else:
            print(f'❌ 6. Memory stats test failed: {{result_data.get("error")}}')
            return False
        
        print('🎉 All tests passed! Installation is fully functional.')
        return True
        
    except Exception as e:
        print(f'❌ Installation test failed: {{e}}')
        import traceback
        traceback.print_exc()
        return False

# Run the test
success = asyncio.run(test_installation())
sys.exit(0 if success else 1)
"""
        
        result = subprocess.run([str(self.python_exe), "-c", test_script], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Complete installation test failed!")
            print(f"Error: {result.stderr}")
            print(f"Output: {result.stdout}")
            raise RuntimeError(f"Complete installation test failed")
        
        print(result.stdout.strip())
    
    def _print_next_steps(self):
        """Print next steps for the user"""
        print("\n🎯 Next Steps:")
        print("=" * 30)
        
        if self.platform == "cursor":
            print("1. Restart Cursor IDE")
            print("2. Open a chat and test: 'Ricorda que para resolver CORS preciso adicionar Access-Control-Allow-Origin'")
            print("3. Ask: 'O que sabes sobre CORS?' to test memory retrieval")
        
        elif self.platform == "claude":
            print("1. Restart Claude Desktop")
            print("2. Start a conversation and test memory features")
        
        else:
            print("1. Run: python main.py")
            print("2. Test HTTP API: curl http://localhost:8000/health")
        
        print(f"\n📁 Configuration: {self.config['config_dir'] / self.config['config_file']}")
        print(f"🐍 Python: {self.python_exe}")
        print(f"📦 Project: {self.base_dir}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python install.py <platform>")
        print("Platforms: cursor, claude, universal")
        sys.exit(1)
    
    platform = sys.argv[1].lower()
    if platform not in ["cursor", "claude", "universal"]:
        print("Invalid platform. Use: cursor, claude, or universal")
        sys.exit(1)
    
    installer = Installer(platform)
    installer.install()


if __name__ == "__main__":
    main() 