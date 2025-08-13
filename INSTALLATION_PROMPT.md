# 🧠 MCP Memory Server - Installazione Automatica

## Prompt di Installazione

Per installare automaticamente il **MCP Memory Server** con tutte le funzionalità SAM, usa questo prompt:

```
Install this: https://github.com/PiGrieco/mcp-memory-server.git on macos
```

## Cosa Fa l'Installazione Automatica

L'installer configurerà automaticamente:

### ✅ **Database MongoDB**
- Installa MongoDB via Homebrew (macOS) o package manager (Linux)
- Avvia il servizio MongoDB automaticamente
- Configura database `mcp_memory_dev` per le memorie

### ✅ **Dipendenze Python**
- Crea virtual environment dedicato
- Installa tutte le dipendenze ML (PyTorch, Transformers, etc.)
- Configura SentenceTransformer per embeddings

### ✅ **Tool MCP per SAM**
- `save_memory` - Salva memorie con embeddings
- `search_memory` - Ricerca semantica nelle memorie  
- `analyze_message` - Analisi automatica dei messaggi
- `get_memory_stats` - Statistiche del sistema
- `list_memories` - Lista tutte le memorie

### ✅ **Test Completo**
- Testa connessione database
- Verifica salvataggio memorie
- Testa analisi automatica messaggi
- Conferma tutti i tool SAM funzionanti

### ✅ **Configurazione Piattaforma**
- **Cursor**: Configura `~/.cursor/mcp_settings.json`
- **Claude**: Configura `~/.config/claude/claude_desktop_config.json`  
- **Universal**: Crea configurazione locale

## Entry Point Corretto

L'installer usa il **server MCP corretto** per la compatibilità SAM:

- **File**: `main.py` (non i vecchi server legacy)
- **Implementazione**: `src/core/server.py` con tutti i tool SAM
- **Database**: MongoDB con salvataggio reale (non in-memory)

## Variabili Ambiente Configurate

```bash
ENVIRONMENT=development
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=mcp_memory_dev
MONGODB_COLLECTION=memories
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
ML_TRIGGER_MODE=hybrid
AUTO_SAVE_ENABLED=true
PLATFORM=cursor  # o claude, universal
```

## Dopo l'Installazione

1. **Restart** la tua piattaforma (Cursor/Claude)
2. **Test** con questi comandi:
   ```
   Ricorda che per CORS serve Access-Control-Allow-Origin
   Cosa sai sui bug di rendering in React?
   ```
3. **Verifica** che le memorie vengano salvate e recuperate

## Risoluzione Problemi

Se l'installazione fallisce:

1. **MongoDB**: Verifica che MongoDB sia in esecuzione
   ```bash
   brew services start mongodb/brew/mongodb-community
   ```

2. **Dipendenze**: Reinstalla requirements
   ```bash
   pip install -r requirements.txt
   ```

3. **Test Manuale**: Esegui test completo
   ```bash
   python -c "
   import sys; sys.path.insert(0, 'src')
   from src.config.settings import get_settings
   from src.core.server import MCPServer
   import asyncio
   async def test(): 
       s = get_settings(); 
       server = MCPServer(s); 
       await server.initialize(); 
       print('✅ Setup OK')
   asyncio.run(test())
   "
   ```

## Supporto

- **GitHub**: https://github.com/PiGrieco/mcp-memory-server
- **Issues**: Per problemi specifici
- **Docs**: `/docs/` nella repository

---

**🎯 Risultato**: Server MCP completamente funzionale con tutte le capacità SAM per gestione intelligente della memoria.
