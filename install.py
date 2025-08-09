#!/usr/bin/env python3
"""
One-Click Installer for MCP Memory Server with Auto-Trigger
Simple, automated installation that works everywhere
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
import shutil
import urllib.request

def print_step(step, msg):
    """Print installation step"""
    print(f"\n🔸 Step {step}: {msg}")

def run_command(cmd, description=""):
    """Run shell command with error handling"""
    try:
        print(f"   Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ❌ Error: {result.stderr}")
            return False
        print(f"   ✅ {description}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    dependencies = [
        "mcp>=1.0.0",
        "sentence-transformers",
        "asyncio",
        "python-dotenv",
        "motor",
        "pydantic",
        "uvicorn",
        "fastapi"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installed {dep}"):
            print(f"❌ Failed to install {dep}")
            return False
    return True

def create_cursor_config():
    """Create Cursor IDE configuration"""
    cursor_dir = Path.home() / ".cursor"
    cursor_dir.mkdir(exist_ok=True)
    
    config = {
        "mcpServers": {
            "mcp-memory-auto": {
                "command": "python",
                "args": [str(Path.cwd() / "main_simple.py")],
                "env": {
                    "AUTO_TRIGGER": "true",
                    "KEYWORDS": "ricorda,nota,importante,salva,memorizza,remember",
                    "PATTERNS": "risolto,solved,fixed,bug fix,solution,tutorial"
                }
            }
        }
    }
    
    config_file = cursor_dir / "mcp_settings.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Cursor config created: {config_file}")
    return True

def create_claude_config():
    """Create Claude Desktop configuration"""
    claude_dir = Path.home() / ".config" / "claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "mcpServers": {
            "mcp-memory-auto": {
                "command": "python",
                "args": [str(Path.cwd() / "main_simple.py")],
                "env": {
                    "AUTO_TRIGGER": "true",
                    "CLAUDE_MODE": "true"
                }
            }
        }
    }
    
    config_file = claude_dir / "claude_desktop_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Claude config created: {config_file}")
    return True

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    # Test import
    try:
        import asyncio
        print("✅ asyncio import OK")
    except ImportError:
        print("❌ asyncio import failed")
        return False
    
    # Test server file
    if not Path("main_simple.py").exists():
        print("❌ main_simple.py not found")
        return False
    print("✅ Server file found")
    
    # Test auto-trigger
    if run_command("python test_auto_trigger.py", "Auto-trigger test"):
        print("✅ Auto-trigger system working")
        return True
    else:
        print("❌ Auto-trigger test failed")
        return False

def main():
    """Main installation process"""
    print("🚀 MCP Memory Server Auto-Trigger Installer")
    print("=" * 50)
    
    # Step 1: Check Python
    print_step(1, "Checking Python version")
    if not check_python():
        sys.exit(1)
    
    # Step 2: Install dependencies
    print_step(2, "Installing dependencies")
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Step 3: Create configurations
    print_step(3, "Creating configurations")
    create_cursor_config()
    create_claude_config()
    
    # Step 4: Test installation
    print_step(4, "Testing installation")
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Success message
    print("\n🎉 INSTALLATION COMPLETED!")
    print("=" * 30)
    print("✅ MCP Memory Server installed")
    print("✅ Auto-trigger system configured")
    print("✅ Cursor IDE integration ready")
    print("✅ Claude Desktop integration ready")
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. Start the server:")
    print("   python main_simple.py")
    print("\n2. Open Cursor IDE:")
    print("   - Press Cmd+L (macOS) or Ctrl+L (Windows/Linux)")
    print("   - Try: 'Ricorda che Python è case-sensitive'")
    print("\n3. Open Claude Desktop:")
    print("   - Restart Claude Desktop")
    print("   - Auto-trigger system will be active")
    
    print(f"\n📋 Files created:")
    print(f"   • {Path.home() / '.cursor' / 'mcp_settings.json'}")
    print(f"   • {Path.home() / '.config' / 'claude' / 'claude_desktop_config.json'}")
    
    print(f"\n🎯 Test the system:")
    print("   Use keywords: ricorda, importante, risolto")
    print("   Your AI will automatically save memories!")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Installation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)
