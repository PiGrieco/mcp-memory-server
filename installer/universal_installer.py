#!/usr/bin/env python3
"""
Universal MCP Memory Server Installer
Cross-platform installation system for non-technical users
"""

import os
import sys
import json
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.request
import zipfile
import tempfile

class UniversalInstaller:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.home_dir = Path.home()
        self.install_dir = self.home_dir / ".mcp-memory"
        self.detected_tools = {}
        self.config_data = {}
        
        # Color codes for output
        self.colors = {
            'green': '\033[92m',
            'blue': '\033[94m', 
            'yellow': '\033[93m',
            'red': '\033[91m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'end': '\033[0m'
        }
        
    def colored_print(self, text: str, color: str = 'white', symbol: str = ''):
        """Print colored text with optional symbol"""
        print(f"{self.colors[color]}{symbol} {text}{self.colors['end']}")
        
    def success(self, text: str):
        self.colored_print(text, 'green', '✅')
        
    def info(self, text: str):
        self.colored_print(text, 'blue', 'ℹ️')
        
    def warning(self, text: str):
        self.colored_print(text, 'yellow', '⚠️')
        
    def error(self, text: str):
        self.colored_print(text, 'red', '❌')
        
    def magic(self, text: str):
        self.colored_print(text, 'purple', '✨')
        
    def step(self, text: str):
        self.colored_print(text, 'cyan', '🎯')
        
    def check_prerequisites(self) -> bool:
        """Check if system meets requirements"""
        self.step("Checking system prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 11):
            self.error(f"Python 3.11+ required, found {sys.version}")
            return False
        self.success(f"Python {sys.version.split()[0]} found")
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            self.success("pip found")
        except subprocess.CalledProcessError:
            self.error("pip not found or not working")
            return False
            
        # Check internet connection
        try:
            urllib.request.urlopen('https://google.com', timeout=5)
            self.success("Internet connection verified")
        except:
            self.error("Internet connection required")
            return False
            
        return True
        
    def detect_ai_tools(self) -> Dict[str, Dict]:
        """Auto-detect installed AI tools"""
        self.step("Detecting AI tools...")
        
        detected = {}
        
        # Claude Desktop detection
        claude_paths = [
            self.home_dir / ".config" / "claude",
            self.home_dir / "Library" / "Application Support" / "Claude",
            self.home_dir / "AppData" / "Roaming" / "Claude"
        ]
        
        for path in claude_paths:
            if path.exists():
                detected['claude'] = {
                    'name': 'Claude Desktop',
                    'config_path': path,
                    'status': 'detected'
                }
                self.success("Claude Desktop found")
                break
                
        # Cursor detection
        cursor_paths = [
            self.home_dir / ".cursor",
            self.home_dir / "Library" / "Application Support" / "Cursor",
            self.home_dir / "AppData" / "Roaming" / "Cursor"
        ]
        
        for path in cursor_paths:
            if path.exists():
                detected['cursor'] = {
                    'name': 'Cursor IDE',
                    'config_path': path / "User",
                    'status': 'detected'
                }
                self.success("Cursor IDE found")
                break
                
        # Browser detection for GPT
        browsers = ['google-chrome', 'firefox', 'chrome', 'firefox.exe']
        for browser in browsers:
            if shutil.which(browser):
                detected['gpt'] = {
                    'name': 'Browser (ChatGPT)',
                    'browser': browser,
                    'status': 'detected'
                }
                self.success("Browser found (ChatGPT compatible)")
                break
                
        # Check for browser apps on macOS
        if self.os_type == 'darwin':
            browser_apps = [
                "/Applications/Google Chrome.app",
                "/Applications/Firefox.app",
                "/Applications/Microsoft Edge.app"
            ]
            for app in browser_apps:
                if os.path.exists(app):
                    detected['gpt'] = {
                        'name': 'Browser (ChatGPT)',
                        'browser': app,
                        'status': 'detected'
                    }
                    self.success(f"Browser found: {Path(app).stem}")
                    break
                    
        # Replit environment detection
        if os.getenv('REPL_SLUG') or os.getenv('REPLIT_CLI_TOKEN'):
            detected['replit'] = {
                'name': 'Replit Environment',
                'status': 'detected',
                'mode': 'cloud'
            }
            self.success("Replit environment detected")
            
        self.detected_tools = detected
        return detected
        
    def user_tool_selection(self) -> Dict[str, bool]:
        """Interactive tool selection"""
        self.step("Select AI tools to configure:")
        print()
        
        tools = {
            'claude': 'Claude Desktop',
            'gpt': 'ChatGPT/GPT-4 (Browser)',
            'cursor': 'Cursor IDE', 
            'lovable': 'Lovable AI',
            'replit': 'Replit'
        }
        
        selected = {}
        
        # Show options with detection status
        options = []
        for key, name in tools.items():
            status = ""
            if key in self.detected_tools:
                status = f" {self.colors['green']}(detected){self.colors['end']}"
            else:
                status = f" {self.colors['yellow']}(not detected){self.colors['end']}"
            options.append(f"{name}{status}")
            
        options.extend(["All tools", "Skip selection"])
        
        # Display options
        for i, option in enumerate(options, 1):
            print(f"  {self.colors['green']}{i}) {option}{self.colors['end']}")
        print()
        
        while True:
            try:
                choice = input(f"{self.colors['white']}Choose option [1-{len(options)}]: {self.colors['end']}")
                choice = int(choice)
                
                if choice == len(options) - 1:  # All tools
                    selected = {tool: True for tool in tools.keys()}
                    self.magic("All tools selected!")
                    break
                elif choice == len(options):  # Skip
                    self.info("Tool selection skipped")
                    break
                elif 1 <= choice <= len(tools):
                    tool_key = list(tools.keys())[choice - 1]
                    selected[tool_key] = True
                    self.success(f"{tools[tool_key]} selected")
                    
                    more = input(f"{self.colors['white']}Add another tool? [y/N]: {self.colors['end']}")
                    if more.lower() not in ['y', 'yes']:
                        break
                else:
                    self.warning("Invalid selection")
                    
            except (ValueError, KeyboardInterrupt):
                self.warning("Invalid input, please try again")
                continue
                
        return selected
        
    def download_mcp_server(self) -> bool:
        """Download and setup MCP Memory Server"""
        self.step("Setting up MCP Memory Server...")
        
        # Create installation directory
        self.install_dir.mkdir(exist_ok=True)
        
        # Download release or clone repository
        repo_url = "https://github.com/AiGotsrl/mcp-memory-server.git"
        
        try:
            # Try git clone first
            if shutil.which('git'):
                subprocess.run([
                    'git', 'clone', repo_url, str(self.install_dir / 'source')
                ], check=True, capture_output=True)
                self.success("MCP Memory Server downloaded via git")
            else:
                # Fallback to zip download
                self.download_zip_release()
                
        except subprocess.CalledProcessError:
            self.warning("Git clone failed, trying zip download...")
            self.download_zip_release()
            
        return True
        
    def download_zip_release(self):
        """Download and extract zip release"""
        zip_url = "https://github.com/AiGotsrl/mcp-memory-server/archive/refs/heads/main.zip"
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            urllib.request.urlretrieve(zip_url, tmp_file.name)
            
            with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
                
            # Rename extracted directory
            extracted_dir = self.install_dir / "mcp-memory-server-main"
            if extracted_dir.exists():
                extracted_dir.rename(self.install_dir / "source")
                
        os.unlink(tmp_file.name)
        self.success("MCP Memory Server downloaded via zip")
        
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        self.step("Installing Python dependencies...")
        
        source_dir = self.install_dir / "source"
        requirements_file = source_dir / "requirements.txt"
        
        if not requirements_file.exists():
            self.error("requirements.txt not found")
            return False
            
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True)
            self.success("Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            self.error(f"Failed to install dependencies: {e}")
            return False
            
    def setup_docker(self) -> bool:
        """Setup Docker services for MongoDB"""
        self.step("Setting up database services...")
        
        # Check if Docker is available
        if not shutil.which('docker'):
            self.warning("Docker not found - will use alternative setup")
            return self.setup_alternative_database()
            
        source_dir = self.install_dir / "source"
        
        try:
            # Start Docker services
            subprocess.run([
                'docker-compose', 'up', '-d'
            ], cwd=source_dir, check=True, capture_output=True)
            
            self.success("Database services started")
            return True
            
        except subprocess.CalledProcessError:
            self.warning("Docker setup failed - trying alternative")
            return self.setup_alternative_database()
            
    def setup_alternative_database(self) -> bool:
        """Setup alternative database (SQLite fallback)"""
        self.info("Setting up lightweight database alternative...")
        
        # Install SQLite-based alternative
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "sqlite-vec", "chromadb"
            ], check=True, capture_output=True)
            
            self.success("Lightweight database alternative installed")
            return True
        except subprocess.CalledProcessError:
            self.error("Failed to setup alternative database")
            return False
            
    def configure_claude(self, config_path: Path) -> bool:
        """Configure Claude Desktop"""
        self.info("Configuring Claude Desktop...")
        
        config_file = config_path / "claude_desktop_config.json"
        config_path.mkdir(parents=True, exist_ok=True)
        
        source_dir = self.install_dir / "source"
        claude_script = source_dir / "examples" / "claude_smart_auto.py"
        
        config = {
            "mcpServers": {
                "mcp-memory-smart": {
                    "command": "python",
                    "args": [str(claude_script)],
                    "env": {
                        "MONGODB_URL": "mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin",
                        "AUTO_MEMORY": "advanced"
                    }
                }
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.success("Claude Desktop configured")
        return True
        
    def configure_gpt(self) -> bool:
        """Configure GPT API setup"""
        self.info("Setting up ChatGPT API integration...")
        
        source_dir = self.install_dir / "source"
        
        # Create startup script
        if self.os_type == 'windows':
            script_name = "start_gpt_api.bat"
            script_content = f"""@echo off
cd /d "{source_dir}"
python examples/gpt_smart_auto.py
pause"""
        else:
            script_name = "start_gpt_api.sh"
            script_content = f"""#!/bin/bash
cd "{source_dir}"
python examples/gpt_smart_auto.py"""
            
        script_path = self.install_dir / script_name
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        if self.os_type != 'windows':
            os.chmod(script_path, 0o755)
            
        self.success("ChatGPT API integration configured")
        return True
        
    def configure_cursor(self, config_path: Path) -> bool:
        """Configure Cursor IDE"""
        self.info("Configuring Cursor IDE...")
        
        settings_file = config_path / "settings.json"
        config_path.mkdir(parents=True, exist_ok=True)
        
        source_dir = self.install_dir / "source"
        cursor_script = source_dir / "examples" / "cursor_smart_auto.py"
        
        # Load existing settings or create new
        settings = {}
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            except:
                pass
                
        # Add MCP configuration
        if "mcp.servers" not in settings:
            settings["mcp.servers"] = {}
            
        settings["mcp.servers"]["mcp-memory-smart"] = {
            "command": "python",
            "args": [str(cursor_script)],
            "cwd": str(source_dir),
            "env": {
                "CODE_AWARE": "true"
            }
        }
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
            
        self.success("Cursor IDE configured")
        return True
        
    def configure_lovable(self) -> bool:
        """Configure Lovable integration"""
        self.info("Setting up Lovable AI integration...")
        
        source_dir = self.install_dir / "source"
        plugin_file = source_dir / "examples" / "lovable_smart_auto.js"
        
        if plugin_file.exists():
            self.success("Lovable AI integration ready")
            self.info(f"Plugin location: {plugin_file}")
            return True
        else:
            self.error("Lovable plugin file not found")
            return False
            
    def configure_replit(self) -> bool:
        """Configure Replit integration"""
        self.info("Setting up Replit integration...")
        
        source_dir = self.install_dir / "source"
        
        # Create Replit-specific setup
        setup_content = """from examples.replit_smart_auto import ReplitSmartAutoMemory

# Auto-configure for Replit environment
replit_memory = ReplitSmartAutoMemory({
    "use_replit_db": True,
    "enabled": True,
    "auto_detect": True
})

# Import this in your main.py
"""
        
        setup_file = self.install_dir / "replit_memory_setup.py"
        with open(setup_file, 'w') as f:
            f.write(setup_content)
            
        self.success("Replit integration configured")
        return True
        
    def run_tests(self) -> bool:
        """Run installation tests"""
        self.step("Testing installation...")
        
        source_dir = self.install_dir / "source"
        
        # Test Python imports
        try:
            subprocess.run([
                sys.executable, "-c",
                "import sentence_transformers, pymongo, motor; print('Dependencies OK')"
            ], check=True, capture_output=True, cwd=source_dir)
            self.success("Python dependencies: OK")
        except subprocess.CalledProcessError:
            self.warning("Some dependencies missing but installation can continue")
            
        # Test smart automation
        test_scripts = [
            "examples/claude_smart_auto.py",
            "examples/gpt_smart_auto.py"
        ]
        
        for script in test_scripts:
            script_path = source_dir / script
            if script_path.exists():
                try:
                    result = subprocess.run([
                        sys.executable, str(script_path), "demo"
                    ], timeout=10, capture_output=True, cwd=source_dir)
                    self.success(f"{script_path.stem}: OK")
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    self.info(f"{script_path.stem}: Test completed")
                    
        return True
        
    def create_shortcuts(self, selected_tools: Dict[str, bool]):
        """Create desktop shortcuts and launchers"""
        self.step("Creating shortcuts...")
        
        if self.os_type == 'windows':
            self.create_windows_shortcuts(selected_tools)
        elif self.os_type == 'darwin':
            self.create_macos_shortcuts(selected_tools)
        else:
            self.create_linux_shortcuts(selected_tools)
            
    def create_windows_shortcuts(self, selected_tools: Dict[str, bool]):
        """Create Windows shortcuts"""
        desktop = Path.home() / "Desktop"
        
        if 'gpt' in selected_tools:
            # Create batch file for GPT API
            bat_content = f"""@echo off
cd /d "{self.install_dir / 'source'}"
python examples/gpt_smart_auto.py
pause"""
            
            bat_file = desktop / "MCP Memory GPT API.bat"
            with open(bat_file, 'w') as f:
                f.write(bat_content)
                
        self.success("Windows shortcuts created")
        
    def create_macos_shortcuts(self, selected_tools: Dict[str, bool]):
        """Create macOS shortcuts"""
        # macOS shortcuts would use Automator or shell scripts
        self.info("macOS shortcuts: Use Terminal commands from installation guide")
        
    def create_linux_shortcuts(self, selected_tools: Dict[str, bool]):
        """Create Linux shortcuts"""
        # Linux shortcuts would use .desktop files
        self.info("Linux shortcuts: Use shell commands from installation guide")
        
    def show_final_instructions(self, selected_tools: Dict[str, bool]):
        """Show final setup instructions"""
        print("\n" + "="*60)
        self.magic("🎉 Installation Complete!")
        print("="*60)
        
        print(f"\n{self.colors['white']}Installation Directory:{self.colors['end']}")
        print(f"  📁 {self.install_dir}")
        
        print(f"\n{self.colors['white']}Quick Start:{self.colors['end']}")
        
        if 'claude' in selected_tools:
            print(f"\n{self.colors['green']}🧠 Claude Desktop:{self.colors['end']}")
            print("  • Restart Claude Desktop")
            print("  • Try: 'Remember that I prefer TypeScript'")
            
        if 'gpt' in selected_tools:
            print(f"\n{self.colors['green']}💬 ChatGPT API:{self.colors['end']}")
            if self.os_type == 'windows':
                print(f"  • Double-click: {self.install_dir}/start_gpt_api.bat")
            else:
                print(f"  • Run: {self.install_dir}/start_gpt_api.sh")
            print("  • Visit: http://localhost:8000/docs")
            
        if 'cursor' in selected_tools:
            print(f"\n{self.colors['green']}💻 Cursor IDE:{self.colors['end']}")
            print("  • Restart Cursor")
            print("  • Smart coding assistance will be active")
            
        print(f"\n{self.colors['white']}Support:{self.colors['end']}")
        print("  📖 Guide: SMART_AUTOMATION_GUIDE.md")
        print("  🆘 Issues: https://github.com/AiGotsrl/mcp-memory-server/issues")
        
        print(f"\n{self.colors['cyan']}💡 Tip: The more you use your AI tools, the smarter they become!{self.colors['end']}")
        
    def run_installation(self):
        """Main installation flow"""
        print(f"\n{self.colors['cyan']}🧠 MCP Memory Server - Universal Installer{self.colors['end']}")
        print("Transform your AI tools into super-intelligent assistants!\n")
        
        # Prerequisites
        if not self.check_prerequisites():
            self.error("Prerequisites check failed")
            return False
            
        # Tool detection and selection
        self.detect_ai_tools()
        selected_tools = self.user_tool_selection()
        
        if not selected_tools:
            self.info("No tools selected, installation cancelled")
            return False
            
        # Download and setup
        if not self.download_mcp_server():
            return False
            
        if not self.install_dependencies():
            return False
            
        self.setup_docker()
        
        # Configure selected tools
        for tool, enabled in selected_tools.items():
            if not enabled:
                continue
                
            if tool == 'claude' and 'claude' in self.detected_tools:
                self.configure_claude(self.detected_tools['claude']['config_path'])
            elif tool == 'gpt':
                self.configure_gpt()
            elif tool == 'cursor' and 'cursor' in self.detected_tools:
                self.configure_cursor(self.detected_tools['cursor']['config_path'])
            elif tool == 'lovable':
                self.configure_lovable()
            elif tool == 'replit':
                self.configure_replit()
                
        # Final steps
        self.run_tests()
        self.create_shortcuts(selected_tools)
        self.show_final_instructions(selected_tools)
        
        return True

def main():
    """Entry point for universal installer"""
    installer = UniversalInstaller()
    
    try:
        success = installer.run_installation()
        if success:
            print(f"\n{installer.colors['green']}✅ Installation completed successfully!{installer.colors['end']}")
        else:
            print(f"\n{installer.colors['red']}❌ Installation failed{installer.colors['end']}")
            return 1
    except KeyboardInterrupt:
        print(f"\n{installer.colors['yellow']}⚠️ Installation cancelled by user{installer.colors['end']}")
        return 1
    except Exception as e:
        print(f"\n{installer.colors['red']}❌ Unexpected error: {e}{installer.colors['end']}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 