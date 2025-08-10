# 🔧 Test MCP Tools in Cursor

## ✅ **Configurazione Completata**

La configurazione di Cursor è stata aggiornata per usare il server MCP completo con tutti i tool visibili.

**📁 Server:** `main_full_simple.py`  
**📍 Config:** `~/.cursor/mcp_settings.json`

## 🧪 **Come Testare i Tool MCP**

### **STEP 1: Riavvia Cursor**
1. Chiudi completamente Cursor
2. Riapri Cursor
3. Aspetta che si connetta al server MCP

### **STEP 2: Verifica Tool Disponibili**
Dovresti vedere questi **4 tool MCP** nella UI di Cursor:

#### **1. 💾 save_memory**
- **Descrizione:** Save important information to memory
- **Test:** Prova a salvare qualcosa

#### **2. 🔍 search_memories** 
- **Descrizione:** Search through saved memories
- **Test:** Cerca nei ricordi salvati

#### **3. 📋 get_memory_context**
- **Descrizione:** Get recent memory context for a project
- **Test:** Ottieni il contesto recente

#### **4. 🗑️ delete_memory**
- **Descrizione:** Delete a specific memory
- **Test:** Elimina un ricordo specifico

## 🎯 **Test Sequence**

### **Test 1: Salva Memory**
```
Usa il tool "save_memory" con:
- content: "React usa JSX per il rendering"
- project: "test_project"
- importance: 0.8
```

### **Test 2: Cerca Memories**
```
Usa il tool "search_memories" con:
- query: "React"
- project: "test_project"
```

### **Test 3: Ottieni Contesto**
```
Usa il tool "get_memory_context" con:
- project: "test_project"
- limit: 5
```

### **Test 4: Elimina Memory**
```
Usa il tool "delete_memory" con:
- memory_id: "mem_001" (o l'ID che vedi dal test precedente)
```

## 🔧 **Troubleshooting**

### **❌ Non vedo i tool MCP:**
1. Controlla che Cursor sia riavviato
2. Verifica che la configurazione sia corretta:
   ```bash
   cat ~/.cursor/mcp_settings.json
   ```
3. Controlla i log di Cursor per errori

### **❌ Errori di connessione:**
1. Testa il server manualmente:
   ```bash
   python main_full_simple.py
   ```
2. Verifica che non ci siano errori di import

### **❌ Tool non funzionano:**
1. Controlla i log del server
2. Verifica che i parametri siano corretti

## 🎉 **Risultato Atteso**

Dovresti vedere tutti i 4 tool MCP nella UI di Cursor e essere in grado di:
- ✅ Salvare memories
- ✅ Cercare memories 
- ✅ Ottenere contesto del progetto
- ✅ Eliminare memories specifiche

## 📊 **Vantaggi del Server Completo**

- **🔧 Tool MCP Visibili:** Tutti i 4 tool disponibili nella UI
- **💾 In-Memory DB:** Nessuna dipendenza esterna richiesta  
- **⚡ Performance:** Startup immediato con modelli pre-scaricati
- **🛠️ Debug:** Log dettagliati per troubleshooting

---

**🚀 Ora testa in Cursor e fammi sapere se vedi tutti i tool MCP!**
