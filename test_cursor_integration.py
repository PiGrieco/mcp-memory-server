#!/usr/bin/env python3
"""
Test immediato per integrazione Cursor con Auto-Trigger
"""

import json
import os
from pathlib import Path

def setup_cursor_config():
    """Setup della configurazione Cursor"""
    print("🔧 SETUP CURSOR INTEGRATION")
    print("=" * 40)
    
    # Path della configurazione Cursor
    cursor_config_dir = Path.home() / ".cursor"
    cursor_config_file = cursor_config_dir / "mcp_settings.json"
    
    # Crea directory se non esiste
    cursor_config_dir.mkdir(exist_ok=True)
    
    # Configurazione per Cursor
    config = {
        "mcpServers": {
            "mcp-memory-auto": {
                "command": "python",
                "args": [str(Path.cwd() / "main.py")],
                "env": {
                    "AUTO_TRIGGER_ENABLED": "true",
                    "TRIGGER_KEYWORDS": "ricorda,nota,importante,salva,memorizza",
                    "SOLUTION_PATTERNS": "risolto,solved,fixed,bug fix,solution",
                    "AUTO_SAVE_THRESHOLD": "0.7"
                }
            }
        }
    }
    
    # Salva configurazione
    with open(cursor_config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Config salvata in: {cursor_config_file}")
    print("✅ Server: mcp-memory-auto")
    print("✅ Auto-trigger: ENABLED")
    
    return cursor_config_file

def create_test_instructions():
    """Crea istruzioni per il test"""
    instructions = """
🎯 ISTRUZIONI PER TEST IN CURSOR

1. APRI CURSOR IDE
   - Assicurati che la configurazione sia caricata
   - Verifica che il server MCP sia attivo

2. APRI UNA NUOVA CONVERSAZIONE
   - Premi Cmd+L (macOS) o Ctrl+L (Windows/Linux)

3. TESTA I TRIGGER AUTOMATICI:

   📝 Test Keyword Trigger:
   "Ricorda che per fixare i CORS devi aggiungere Access-Control-Allow-Origin nel backend"
   
   → Dovrebbe auto-salvare la memoria!

   🔍 Test Pattern Trigger:
   "Ho risolto il bug di autenticazione aumentando il timeout a 30 secondi"
   
   → Dovrebbe auto-salvare come solution!

   🎯 Test Search Trigger:
   "Ho un problema di timeout simile a quello di prima"
   
   → Dovrebbe auto-cercare memories rilevanti!

4. VERIFICA I RISULTATI:
   - Cursor dovrebbe mostrare che ha salvato automaticamente
   - Le conversazioni successive dovrebbero avere contesto dalle memories
   - I trigger dovrebbero essere trasparenti ma efficaci

5. TEST AVANZATI:
   "Importante: questa configurazione Docker funziona perfettamente"
   "Come posso ottimizzare le query del database?"
   "Nota bene: il pattern Observer va usato con attenzione"

RISULTATI ATTESI:
✅ Memories salvate automaticamente
✅ Contesto iniettato nelle conversazioni
✅ AI più intelligente e contestuale
✅ Zero effort dall'utente
"""
    
    with open("CURSOR_TEST_INSTRUCTIONS.md", 'w') as f:
        f.write(instructions)
    
    print("\n📋 Istruzioni salvate in: CURSOR_TEST_INSTRUCTIONS.md")
    return "CURSOR_TEST_INSTRUCTIONS.md"

def check_system_requirements():
    """Verifica requisiti di sistema"""
    print("\n🔍 SYSTEM CHECK")
    print("-" * 20)
    
    # Check Python
    import sys
    print(f"✅ Python: {sys.version.split()[0]}")
    
    # Check dependencies
    try:
        import mcp
        print("✅ MCP library: available")
    except ImportError:
        print("❌ MCP library: missing (run: pip install mcp)")
        return False
    
    # Check main.py
    if os.path.exists("main.py"):
        print("✅ main.py: found")
    else:
        print("❌ main.py: missing")
        return False
    
    # Check Cursor config directory
    cursor_dir = Path.home() / ".cursor"
    if cursor_dir.exists():
        print("✅ Cursor config directory: found")
    else:
        print("⚠️  Cursor config directory: will be created")
    
    return True

def main():
    """Setup completo per test Cursor"""
    print("🚀 CURSOR AUTO-TRIGGER INTEGRATION SETUP")
    print("=" * 50)
    
    # Check system
    if not check_system_requirements():
        print("\n❌ System check failed. Please install missing dependencies.")
        return
    
    # Setup config
    config_file = setup_cursor_config()
    
    # Create instructions
    instructions_file = create_test_instructions()
    
    print(f"\n🎉 SETUP COMPLETATO!")
    print("=" * 30)
    print(f"📁 Config: {config_file}")
    print(f"📋 Instructions: {instructions_file}")
    print("\n🚀 NEXT STEPS:")
    print("1. Apri Cursor IDE")
    print("2. Inizia una nuova conversazione (Cmd+L)")
    print("3. Prova: 'Ricorda che Python è case-sensitive'")
    print("4. Osserva l'auto-trigger in azione!")
    
    print(f"\n💡 TIP: Monitora il server con:")
    print("   tail -f logs/mcp_server.log")
    
    return True

if __name__ == "__main__":
    main()
