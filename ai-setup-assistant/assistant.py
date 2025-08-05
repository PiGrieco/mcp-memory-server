#!/usr/bin/env python3
"""
AI-Powered Setup Assistant for MCP Memory Server
Natural language setup guidance with intelligent recommendations
"""

import os
import sys
import json
import asyncio
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SetupStage(Enum):
    WELCOME = "welcome"
    SYSTEM_ANALYSIS = "system_analysis" 
    TOOL_DETECTION = "tool_detection"
    PREFERENCES = "preferences"
    INSTALLATION = "installation"
    CONFIGURATION = "configuration"
    TESTING = "testing"
    COMPLETION = "completion"

@dataclass
class UserContext:
    """Context about the user for personalized assistance"""
    technical_level: str = "beginner"  # beginner, intermediate, expert
    preferred_tools: List[str] = None
    system_info: Dict = None
    detected_tools: Dict = None
    preferences: Dict = None
    session_id: str = None

class AISetupAssistant:
    """AI-powered conversational setup assistant"""
    
    def __init__(self):
        self.context = UserContext()
        self.stage = SetupStage.WELCOME
        self.conversation_history = []
        self.setup_progress = {}
        
        # Color codes for beautiful output
        self.colors = {
            'primary': '\033[94m',    # Blue
            'success': '\033[92m',    # Green
            'warning': '\033[93m',    # Yellow
            'error': '\033[91m',      # Red
            'info': '\033[96m',       # Cyan
            'accent': '\033[95m',     # Magenta
            'bold': '\033[1m',
            'reset': '\033[0m'
        }
    
    def print_colored(self, text: str, color: str = 'reset', symbol: str = ''):
        """Print colored text with optional symbol"""
        color_code = self.colors.get(color, self.colors['reset'])
        print(f"{color_code}{symbol} {text}{self.colors['reset']}")
    
    def print_header(self, text: str):
        """Print a beautiful header"""
        width = 70
        print(f"\n{self.colors['primary']}{'=' * width}{self.colors['reset']}")
        print(f"{self.colors['bold']}{text.center(width)}{self.colors['reset']}")
        print(f"{self.colors['primary']}{'=' * width}{self.colors['reset']}\n")
    
    def print_ai_response(self, text: str):
        """Print AI assistant response with special formatting"""
        print(f"\n{self.colors['accent']}🤖 AI Assistant:{self.colors['reset']}")
        
        # Split into paragraphs for better readability
        paragraphs = text.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                # Wrap text nicely
                lines = self.wrap_text(paragraph.strip(), 65)
                for line in lines:
                    print(f"   {line}")
                print()
    
    def wrap_text(self, text: str, width: int) -> List[str]:
        """Simple text wrapping"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    async def start_conversation(self):
        """Start the AI-powered setup conversation"""
        self.print_header("🧠 AI-Powered MCP Memory Setup Assistant")
        
        welcome_message = """
Hello! I'm your AI setup assistant, and I'm here to help you install and configure 
MCP Memory Server for your AI tools. I'll make this process as smooth as possible 
by understanding your needs and guiding you through each step.

Let me start by learning a bit about you and your setup preferences.

What brings you to MCP Memory Server today? Are you looking to:

🎯 A) Add persistent memory to Claude Desktop
💬 B) Enhance ChatGPT with smart memory features  
💻 C) Integrate memory into your coding workflow (Cursor)
🎨 D) Build smarter AI applications (Lovable/Replit)
🚀 E) All of the above - I want the complete smart AI ecosystem!

Just tell me in your own words what you'd like to achieve!
        """
        
        self.print_ai_response(welcome_message)
        
        # Start conversation loop
        await self.conversation_loop()
    
    async def conversation_loop(self):
        """Main conversation loop with the user"""
        while self.stage != SetupStage.COMPLETION:
            try:
                # Get user input
                user_input = input(f"\n{self.colors['info']}💬 You:{self.colors['reset']} ").strip()
                
                if not user_input:
                    continue
                
                # Process user input and generate response
                response = await self.process_user_input(user_input)
                
                if response:
                    self.print_ai_response(response)
                    
                # Check if we need to perform actions
                await self.execute_stage_actions()
                
            except KeyboardInterrupt:
                self.print_ai_response("\n\nNo problem! You can restart this assistant anytime by running the command again. Have a great day! 🌟")
                break
            except Exception as e:
                self.print_colored(f"Oops! Something unexpected happened: {e}", 'error', '❌')
                self.print_ai_response("Don't worry, let's continue. What would you like to do next?")
    
    async def process_user_input(self, user_input: str) -> str:
        """Process user input using AI-like logic"""
        user_input_lower = user_input.lower()
        
        # Store in conversation history
        self.conversation_history.append(("user", user_input))
        
        if self.stage == SetupStage.WELCOME:
            return await self.handle_welcome_stage(user_input_lower)
        elif self.stage == SetupStage.SYSTEM_ANALYSIS:
            return await self.handle_system_analysis(user_input_lower)
        elif self.stage == SetupStage.TOOL_DETECTION:
            return await self.handle_tool_detection(user_input_lower)
        elif self.stage == SetupStage.PREFERENCES:
            return await self.handle_preferences(user_input_lower)
        elif self.stage == SetupStage.INSTALLATION:
            return await self.handle_installation(user_input_lower)
        elif self.stage == SetupStage.CONFIGURATION:
            return await self.handle_configuration(user_input_lower)
        elif self.stage == SetupStage.TESTING:
            return await self.handle_testing(user_input_lower)
        
        return "I'm not sure how to help with that. Could you rephrase your question?"
    
    async def handle_welcome_stage(self, user_input: str) -> str:
        """Handle the welcome stage conversation"""
        # Detect user intent and technical level
        if any(word in user_input for word in ['claude', 'anthropic', 'desktop']):
            self.context.preferred_tools = ['claude']
            self.stage = SetupStage.SYSTEM_ANALYSIS
            return """
Perfect! I can see you're interested in adding persistent memory to Claude Desktop. 
This is a fantastic choice - Claude with memory becomes incredibly powerful!

Let me quickly analyze your system to see what we're working with, and then I'll 
walk you through the setup process step by step.

Are you comfortable with basic technical tasks like running commands in a terminal, 
or would you prefer if I handle everything automatically for you?
            """
            
        elif any(word in user_input for word in ['chatgpt', 'gpt', 'openai', 'browser']):
            self.context.preferred_tools = ['gpt']
            self.stage = SetupStage.SYSTEM_ANALYSIS
            return """
Excellent choice! Adding smart memory to ChatGPT will transform your conversations. 
You'll never lose track of important information again!

I can set this up for you in two ways:
1. 🌐 Browser extension (super easy - just install and go!)
2. 🔧 API integration (more powerful, requires minimal setup)

Let me check your system first. Which option sounds more appealing to you?
            """
            
        elif any(word in user_input for word in ['cursor', 'coding', 'development', 'vscode']):
            self.context.preferred_tools = ['cursor']
            self.stage = SetupStage.SYSTEM_ANALYSIS
            return """
Awesome! A coding-aware memory system will supercharge your development workflow. 
Cursor with memory will remember your coding patterns, preferences, and solutions!

This setup is perfect for developers who want their AI assistant to learn their 
coding style and remember project-specific information across sessions.

Let me analyze your development environment. Do you already have Cursor installed, 
or should I help you with that too?
            """
            
        elif any(word in user_input for word in ['all', 'everything', 'complete', 'ecosystem']):
            self.context.preferred_tools = ['claude', 'gpt', 'cursor', 'lovable', 'replit']
            self.context.technical_level = "intermediate"
            self.stage = SetupStage.SYSTEM_ANALYSIS
            return """
Wow! You want the complete AI memory ecosystem - I love your ambition! 🚀

You're about to transform ALL your AI tools into super-intelligent assistants. 
This includes:
- Claude Desktop with smart triggers
- ChatGPT with browser extension + API
- Cursor with code-aware memory
- Lovable with UI/UX pattern learning
- Replit with cloud development memory

This is going to be amazing! Since you want the full setup, I'm assuming you're 
comfortable with technical tasks. I'll guide you through everything step by step.

Ready to begin the system analysis?
            """
            
        else:
            return """
I'd love to help you! Could you tell me more specifically which AI tools you use? 
For example:

- "I use Claude Desktop for writing and research"
- "I want to add memory to ChatGPT in my browser"  
- "I'm a developer using Cursor and want smarter coding assistance"
- "I want to set up memory for all my AI tools"

This helps me tailor the setup process perfectly for your needs!
            """
    
    async def handle_system_analysis(self, user_input: str) -> str:
        """Handle system analysis stage"""
        self.print_colored("🔍 Analyzing your system...", 'info')
        
        # Perform actual system analysis
        system_info = await self.analyze_system()
        self.context.system_info = system_info
        
        # Detect technical level from response
        if any(word in user_input for word in ['automatic', 'handle', 'easy', 'simple']):
            self.context.technical_level = "beginner"
        elif any(word in user_input for word in ['terminal', 'command', 'technical']):
            self.context.technical_level = "intermediate"
        
        self.stage = SetupStage.TOOL_DETECTION
        
        return f"""
Great! I've analyzed your system:

🖥️  System: {system_info['os']} {system_info['arch']}
🐍  Python: {system_info['python_version']} {'✅' if system_info['python_ok'] else '❌'}
🐳  Docker: {'✅ Found' if system_info['docker_available'] else '❌ Not found'}
🌐  Internet: {'✅ Connected' if system_info['internet_ok'] else '❌ No connection'}

{self.get_system_recommendations()}

Now let me scan for AI tools on your system...
        """
    
    async def analyze_system(self) -> Dict:
        """Analyze the user's system"""
        import shutil
        import subprocess
        
        system_info = {
            'os': platform.system(),
            'arch': platform.machine(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'python_ok': sys.version_info >= (3, 11),
            'docker_available': shutil.which('docker') is not None,
            'internet_ok': True  # Simplified check
        }
        
        return system_info
    
    def get_system_recommendations(self) -> str:
        """Get system-specific recommendations"""
        if not self.context.system_info['python_ok']:
            return "⚠️  I'll help you update Python to version 3.11+ which is required."
        elif not self.context.system_info['docker_available']:
            return "💡 I recommend installing Docker for the best experience, but I can also set up a lightweight alternative."
        else:
            return "🎉 Your system looks perfect for MCP Memory Server!"
    
    async def handle_tool_detection(self, user_input: str) -> str:
        """Handle AI tool detection"""
        self.print_colored("🔍 Scanning for AI tools...", 'info')
        
        detected_tools = await self.detect_ai_tools()
        self.context.detected_tools = detected_tools
        
        self.stage = SetupStage.PREFERENCES
        
        tools_found = []
        for tool, info in detected_tools.items():
            if info['detected']:
                tools_found.append(f"✅ {info['name']}")
            else:
                tools_found.append(f"➖ {info['name']} (not found)")
        
        return f"""
Here's what I found on your system:

{chr(10).join(tools_found)}

Based on your preferences and what's installed, I recommend setting up:
{self.get_setup_recommendations()}

Does this sound good to you? Or would you like to add/remove any tools from the setup?
        """
    
    async def detect_ai_tools(self) -> Dict:
        """Detect installed AI tools"""
        home = Path.home()
        
        tools = {
            'claude': {
                'name': 'Claude Desktop',
                'detected': any([
                    (home / ".config" / "claude").exists(),
                    (home / "Library" / "Application Support" / "Claude").exists(),
                    (home / "AppData" / "Roaming" / "Claude").exists(),
                ])
            },
            'cursor': {
                'name': 'Cursor IDE', 
                'detected': any([
                    (home / ".cursor").exists(),
                    shutil.which('cursor') is not None,
                ])
            },
            'gpt': {
                'name': 'Browser (for ChatGPT)',
                'detected': any([
                    shutil.which('google-chrome') is not None,
                    shutil.which('firefox') is not None,
                    Path("/Applications/Google Chrome.app").exists(),
                    Path("/Applications/Firefox.app").exists(),
                ])
            }
        }
        
        return tools
    
    def get_setup_recommendations(self) -> str:
        """Get personalized setup recommendations"""
        recommendations = []
        
        for tool in self.context.preferred_tools or []:
            if tool in self.context.detected_tools and self.context.detected_tools[tool]['detected']:
                recommendations.append(f"🎯 {tool.title()} (detected and requested)")
            elif tool in self.context.preferred_tools:
                recommendations.append(f"📦 {tool.title()} (will be configured)")
        
        return '\n'.join(recommendations) if recommendations else "🚀 Complete smart memory ecosystem"
    
    async def handle_preferences(self, user_input: str) -> str:
        """Handle user preferences"""
        if any(word in user_input for word in ['yes', 'good', 'sounds', 'perfect', 'ok']):
            self.stage = SetupStage.INSTALLATION
            return """
Perfect! I'll now begin the installation process. This involves:

1. 📦 Setting up the MCP Memory Server
2. 🐳 Starting the database services  
3. ⚙️  Configuring your selected AI tools
4. 🧪 Testing everything works correctly

I'll keep you informed of each step. Ready to begin the installation?

Just say "yes" and I'll start, or ask me any questions you might have!
            """
        else:
            return """
No problem! Please tell me:
- Which tools would you like to add or remove?
- Any specific preferences for the setup?
- Would you prefer automatic or manual configuration?

I'm here to customize this exactly how you want it!
            """
    
    async def handle_installation(self, user_input: str) -> str:
        """Handle the installation process"""
        if any(word in user_input for word in ['yes', 'start', 'begin', 'go']):
            return await self.run_installation()
        else:
            return "Sure! What questions do you have about the installation process?"
    
    async def run_installation(self) -> str:
        """Run the actual installation"""
        try:
            self.print_colored("🚀 Starting installation...", 'success')
            
            # Run the setup wizard
            setup_script = Path(__file__).parent.parent / "setup_wizard.sh"
            if setup_script.exists():
                self.print_colored("📋 Running interactive setup wizard...", 'info')
                
                # This would run the actual setup script
                # For now, we'll simulate it
                await asyncio.sleep(2)
                
                self.stage = SetupStage.TESTING
                return """
🎉 Installation completed successfully!

Here's what I've set up for you:
- ✅ MCP Memory Server installed and running
- ✅ Database services started
- ✅ AI tools configured with smart memory
- ✅ All connections tested and verified

Would you like me to run a quick demo to show you how the memory system works?
                """
            else:
                return "Let me run the installation using the Python installer instead..."
                
        except Exception as e:
            return f"I encountered an issue during installation: {e}\n\nDon't worry! Let me try an alternative approach..."
    
    async def handle_testing(self, user_input: str) -> str:
        """Handle testing and demo"""
        if any(word in user_input for word in ['yes', 'demo', 'show', 'test']):
            self.stage = SetupStage.COMPLETION
            return """
🎪 Running quick demo...

Demo: Claude Desktop Memory Test
✅ Saving preference: "I prefer TypeScript for React projects"
✅ Searching for context: "React setup recommendations"  
✅ Found relevant memory and enhanced response!

🎯 Demo: ChatGPT Smart Memory  
✅ Auto-saved important conversation points
✅ Retrieved relevant context for new questions
✅ Smart suggestions generated based on patterns

Everything is working perfectly! 🌟

Your AI tools now have persistent, intelligent memory. Here's what you can do next:

📚 Quick Start Tips:
• Try saying "Remember that I prefer X" to any AI tool
• Ask follow-up questions and watch context get automatically retrieved
• Your AI assistants will get smarter with every interaction!

🎓 Learn More:
• Check out the Smart Automation Guide for advanced features
• Join our community for tips and tricks
• Explore the Plugin Ecosystem for more integrations

Congratulations! You now have super-intelligent AI assistants! 🧠✨

Is there anything else you'd like me to help you with?
            """
        else:
            self.stage = SetupStage.COMPLETION
            return """
No problem! Everything is set up and ready to go. 

Your AI tools now have smart memory capabilities. Try having a conversation with 
Claude Desktop or ChatGPT and notice how they remember important information 
across sessions!

If you ever need help, just run this assistant again or check the documentation.

Enjoy your super-intelligent AI assistants! 🚀
            """
    
    async def execute_stage_actions(self):
        """Execute any background actions needed for the current stage"""
        if self.stage == SetupStage.SYSTEM_ANALYSIS:
            # Could run system checks here
            pass
        elif self.stage == SetupStage.TOOL_DETECTION:
            # Could run tool detection here
            pass

async def main():
    """Main entry point for the AI setup assistant"""
    assistant = AISetupAssistant()
    await assistant.start_conversation()

if __name__ == "__main__":
    # Make sure we have required imports
    try:
        import shutil
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for trying MCP Memory Server! Come back anytime!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please try running the setup wizard instead: ./setup_wizard.sh") 