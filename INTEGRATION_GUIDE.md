# 🔌 MCP Memory Server - Guida Completa alle Integrazioni

Questa guida mostra come integrare il MCP Memory Server con tutti i principali strumenti di sviluppo AI.

## 🚀 Setup Iniziale

### Prerequisiti
```bash
# 1. Avvia il server di memoria
cd /Users/piermatteogrieco/mcp-memory-server
docker compose up -d

# 2. Verifica che funzioni
curl http://localhost:8000/health
```

## 1. 🤖 Claude Desktop (Supporto MCP Nativo)

**Difficoltà**: ⭐ Facile  
**Funzionalità**: ⭐⭐⭐⭐⭐ Complete

### Setup:
1. **Trova il file di configurazione**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

2. **Aggiungi la configurazione**:
```json
{
  "mcpServers": {
    "memory-server": {
      "command": "python",
      "args": ["/Users/piermatteogrieco/mcp-memory-server/main.py"],
      "env": {
        "MONGODB_URL": "mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
      }
    }
  }
}
```

3. **Riavvia Claude Desktop**

### Utilizzo:
```
Claude, salva questa informazione: "Preferisco TypeScript per i progetti React"
Claude, cerca informazioni sui miei progetti React
Claude, mostrami le statistiche della mia memoria
```

---

## 2. 💻 Cursor

**Difficoltà**: ⭐⭐ Medio  
**Funzionalità**: ⭐⭐⭐⭐ Ottime

### Metodo 1: Estensione MCP
1. Installa l'estensione MCP in Cursor
2. Configura in Settings → MCP:
```json
{
  "mcp.servers": {
    "memory-server": {
      "command": "python",
      "args": ["/Users/piermatteogrieco/mcp-memory-server/main.py"],
      "cwd": "/Users/piermatteogrieco/mcp-memory-server"
    }
  }
}
```

### Utilizzo:
```
@memory-server ricorda: "Questo pattern è utile per React hooks"
Cerca nella memoria informazioni su authentication
```

---

## 3. 🧠 GPT/ChatGPT

**Difficoltà**: ⭐⭐⭐ Avanzato  
**Funzionalità**: ⭐⭐⭐ Buone

### Setup API Wrapper:
```bash
# Avvia l'API wrapper per GPT
python examples/gpt_integration.py
```

### Custom GPT Instructions:
Aggiungi alle istruzioni personalizzate di ChatGPT:
```
Hai accesso a un sistema di memoria persistente. Quando condivido informazioni importanti:

1. Salvale con: POST http://localhost:8000/save
2. Cercale con: POST http://localhost:8000/search
3. Controlla sempre la memoria prima di dare consigli

Ricorda le mie preferenze di codifica, dettagli dei progetti e contesto importante.
```

### Utilizzo:
```json
// Salva memoria
POST http://localhost:8000/save
{
  "text": "L'utente preferisce TypeScript per React",
  "memory_type": "preference",
  "project": "gpt"
}

// Cerca memoria
POST http://localhost:8000/search
{
  "query": "TypeScript React",
  "project": "gpt"
}
```

---

## 4. 💖 Lovable

**Difficoltà**: ⭐⭐⭐ Avanzato  
**Funzionalità**: ⭐⭐⭐⭐ Ottime

### Setup Plugin:
1. Crea `lovable_memory.js` nel tuo progetto Lovable
2. Includi il plugin:
```javascript
import { LovableMemoryIntegration } from './examples/lovable_integration.js';

const memory = new LovableMemoryIntegration({
  project: 'mio-progetto-lovable'
});
```

### Funzionalità Automatiche:
- ✅ Salva automaticamente modifiche ai file
- ✅ Ricorda creazione di componenti
- ✅ Memorizza soluzioni ai bug
- ✅ Migliora i prompt AI con contesto

### Utilizzo:
```javascript
// Manuale
await lovable.memory.save("Questo pattern funziona bene", "pattern");
const memories = await lovable.memory.search("React hooks");

// Automatico
// Il plugin salva automaticamente quando modifichi file o crei componenti
```

---

## 5. 🔄 Replit

**Difficoltà**: ⭐⭐ Medio  
**Funzionalità**: ⭐⭐⭐ Buone

### Metodo 1: Deploy Completo
1. **Importa da GitHub**: `https://github.com/AiGotsrl/mcp-memory-server`
2. **Usa MongoDB Atlas** (gratuito)
3. **Configura Secrets**: `MONGODB_URL`

### Metodo 2: Database Replit Semplice
```python
from replit import db
from sentence_transformers import SentenceTransformer

class ReplitMemory:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def save(self, text, type="note"):
        embedding = self.model.encode(text).tolist()
        db[f"mem_{len(db)}"] = {"text": text, "type": type, "embedding": embedding}
    
    def search(self, query):
        # Implementazione ricerca similarità
        pass

memory = ReplitMemory()
```

---

## 📊 Confronto Rapido

| Strumento | Difficoltà | Funzionalità | Setup Time | Note |
|-----------|------------|--------------|------------|------|
| **Claude Desktop** | ⭐ | ⭐⭐⭐⭐⭐ | 5 min | MCP nativo, perfetto |
| **Cursor** | ⭐⭐ | ⭐⭐⭐⭐ | 10 min | Ottima integrazione |
| **GPT/ChatGPT** | ⭐⭐⭐ | ⭐⭐⭐ | 15 min | Richiede API wrapper |
| **Lovable** | ⭐⭐⭐ | ⭐⭐⭐⭐ | 20 min | Auto-save fantastico |
| **Replit** | ⭐⭐ | ⭐⭐⭐ | 15 min | Cloud-ready |

## 🔧 Comandi Rapidi

### Avvio Server
```bash
# Locale con Docker
docker compose up -d

# Solo MongoDB (se hai Python setup)
docker compose up -d mongodb
python main.py

# Verifica funzionamento
curl http://localhost:8000/health
```

### Test Funzionalità
```bash
# Salva memoria
curl -X POST http://localhost:8000/save \
  -H "Content-Type: application/json" \
  -d '{"text": "Test memory", "project": "test"}'

# Cerca memoria
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "project": "test"}'
```

### Monitoring
```bash
# Logs
docker compose logs -f mcp-memory-server

# Statistiche MongoDB
docker compose exec mongodb mongosh --eval "db.memories.countDocuments()"

# UI MongoDB (http://localhost:8081)
docker compose up -d mongo-express
```

## 🚀 Prossimi Passi

1. **Inizia con Claude Desktop** (più facile)
2. **Aggiungi Cursor** per lo sviluppo
3. **Sperimenta con Lovable** per progetti AI
4. **Usa Replit** per condivisione cloud
5. **Integra GPT** per casi specifici

## 🆘 Troubleshooting

### Problemi Comuni:
- **Port 27017 occupato**: `docker compose down && docker compose up -d`
- **Python import errors**: Controlla `PYTHONPATH` in `.env`
- **Embedding model download**: Serve internet stabile
- **Memory search lenta**: Riduci dimensione embedding o usa GPU

### Log Utili:
```bash
# Server logs
docker compose logs mcp-memory-server

# MongoDB logs
docker compose logs mongodb

# Test connessione
python -c "from src.services.database_service import DatabaseService; print('OK')"
```

---

**🎯 Obiettivo**: Dare memoria persistente ai tuoi agenti AI per conversazioni più intelligenti e contestuali!

Per domande o problemi, apri un issue su [GitHub](https://github.com/AiGotsrl/mcp-memory-server/issues). 