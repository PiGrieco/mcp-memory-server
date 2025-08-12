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
        self.base_dir = Path(__file__).parent.parent
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
            
            # Step 4: Test ML model
            self._test_ml_model()
            
            # Step 5: Configure platform
            self._configure_platform()
            
            # Step 6: Test installation
            self._test_installation()
            
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
        
        # Install core dependencies
        requirements_file = self.base_dir / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([str(self.python_exe), "-m", "pip", "install", "-r", str(requirements_file)], check=True)
            print("✅ Core dependencies installed")
        
        # Install ML dependencies
        ml_deps = [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "sentence-transformers>=2.0.0",
            "scikit-learn>=1.3.0",
            "pyarrow>=12.0.0"
        ]
        
        for dep in ml_deps:
            subprocess.run([str(self.python_exe), "-m", "pip", "install", dep], check=True)
        
        print("✅ ML dependencies installed")
    
    def _test_ml_model(self):
        """Test ML model access"""
        print("🧠 Testing ML model access...")
        
        test_script = f"""
import sys
sys.path.insert(0, '{self.base_dir}/src')

try:
    from huggingface_hub import model_info
    model_name = 'PiGrieco/mcp-memory-auto-trigger-model'
    info = model_info(model_name)
    print(f'✅ ML model accessible: {{info.safetensors.total // (1024*1024)}}MB')
except Exception as e:
    print(f'❌ ML model test failed: {{e}}')
    sys.exit(1)
"""
        
        result = subprocess.run([str(self.python_exe), "-c", test_script], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"ML model test failed: {result.stderr}")
        
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
                        "MONGODB_DATABASE": "mcp_memory",
                        "MONGODB_COLLECTION": "memories",
                        "PLATFORM": self.platform
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
    
    def _test_installation(self):
        """Test the installation"""
        print("🧪 Testing installation...")
        
        test_script = f"""
import sys
sys.path.insert(0, '{self.base_dir}/src')

try:
    from config.settings import get_settings
    from core.server import MCPServer
    
    settings = get_settings()
    server = MCPServer(settings)
    print('✅ Server initialization successful')
except Exception as e:
    print(f'❌ Server test failed: {{e}}')
    sys.exit(1)
"""
        
        result = subprocess.run([str(self.python_exe), "-c", test_script], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Installation test failed: {result.stderr}")
        
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