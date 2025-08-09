#!/usr/bin/env python3
"""
Main Entry Point for MCP Memory Server with Auto-Trigger System
Enhanced version that includes intelligent automatic triggering
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.mcp_server_enhanced import create_enhanced_mcp_server
from src.config.settings import get_config
from src.utils.logging import setup_logging


def setup_environment():
    """Setup environment for auto-trigger system"""
    # Set auto-trigger environment variables
    os.environ.setdefault("AUTO_TRIGGER_ENABLED", "true")
    os.environ.setdefault("TRIGGER_PLATFORMS", "cursor,claude,chatgpt,browser")
    os.environ.setdefault("AUTO_SAVE_THRESHOLD", "0.7")
    os.environ.setdefault("SEMANTIC_THRESHOLD", "0.8")
    os.environ.setdefault("TRIGGER_COOLDOWN", "30")
    
    # Set logging level for auto-trigger debugging
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    print("🔄 Auto-Trigger Environment Configured")
    print(f"   • Auto-Trigger: {os.getenv('AUTO_TRIGGER_ENABLED')}")
    print(f"   • Platforms: {os.getenv('TRIGGER_PLATFORMS')}")
    print(f"   • Save Threshold: {os.getenv('AUTO_SAVE_THRESHOLD')}")
    print(f"   • Semantic Threshold: {os.getenv('SEMANTIC_THRESHOLD')}")


async def main():
    """Main entry point with auto-trigger support"""
    print("🚀 Starting MCP Memory Server with Auto-Trigger System")
    print("=" * 60)
    
    try:
        # Setup environment
        setup_environment()
        
        # Setup logging
        config = get_config()
        setup_logging(config)
        
        # Create enhanced server
        print("\n🔧 Initializing Enhanced MCP Server...")
        server = create_enhanced_mcp_server()
        
        print("✅ Enhanced MCP Server created")
        print("   • Standard MCP tools available")
        print("   • Auto-trigger system enabled")
        print("   • Intelligent conversation monitoring")
        print("   • Multi-platform support")
        
        # Start server
        print(f"\n🌐 Starting server on {config.server.host}:{config.server.port}")
        print("📡 Auto-triggers active for:")
        print("   • Cursor IDE (.cursor/mcp.json)")
        print("   • Claude Desktop (claude_desktop_config.json)")
        print("   • Browser Extension (ChatGPT, Claude, etc.)")
        print("   • Direct API calls")
        
        print(f"\n🧠 Auto-Trigger Features:")
        print("   • 🔤 Keyword-based triggers (ricorda, importante, etc.)")
        print("   • 🔍 Pattern recognition (risolto, bug fix, etc.)")
        print("   • 🎯 Semantic similarity search")
        print("   • ⭐ Importance threshold detection")
        print("   • 📏 Conversation length triggers")
        print("   • 🔄 Context change detection")
        print("   • ⏰ Time-based periodic search")
        
        print(f"\n📊 Monitoring:")
        print("   • Real-time trigger analysis")
        print("   • Conversation buffer management")
        print("   • Cross-platform memory sync")
        print("   • Automatic importance scoring")
        
        print(f"\n🎯 Ready for auto-triggered conversations!")
        print("   Try saying: 'Ricorda questa soluzione importante'")
        print("   Or: 'Ho risolto il bug con questa fix'")
        print("   The system will automatically save memories!")
        
        print("\n" + "=" * 60)
        print("🟢 Server starting... Press Ctrl+C to stop")
        
        # Start the enhanced server
        await server.start_server()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server interrupted by user")
        print("✅ Shutting down gracefully...")
        
    except Exception as e:
        print(f"\n\n❌ Server error: {e}")
        logging.error(f"Server startup failed: {e}")
        sys.exit(1)
        
    finally:
        print("👋 MCP Memory Server with Auto-Trigger stopped")


def print_usage_examples():
    """Print usage examples for auto-trigger system"""
    print("\n📚 AUTO-TRIGGER EXAMPLES:")
    print("=" * 40)
    
    print("\n🔤 Keyword Triggers:")
    print('   "Ricorda che il bug era nel database"')
    print('   "Importante: usare sempre HTTPS"')
    print('   "Nota bene: questo pattern funziona bene"')
    
    print("\n🔍 Pattern Triggers:")
    print('   "Ho risolto l\'errore di timeout"')
    print('   "Ecco come fixare il problema CORS"')
    print('   "Tutorial: come configurare Docker"')
    
    print("\n🎯 Semantic Triggers:")
    print('   "Ho un problema di autenticazione"')
    print('   → Auto-searches for auth-related memories')
    
    print("\n⭐ Importance Triggers:")
    print('   "Critical bug in production login"')
    print('   → Auto-saves with high importance')
    
    print("\n📏 Length Triggers:")
    print('   [5+ message technical discussion]')
    print('   → Auto-saves conversation summary')
    
    print("\n🔄 Context Triggers:")
    print('   "Ora lavoriamo su un nuovo progetto React"')
    print('   → Auto-loads React-related memories')


if __name__ == "__main__":
    # Print usage examples
    print_usage_examples()
    
    # Run the enhanced server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        sys.exit(1)

