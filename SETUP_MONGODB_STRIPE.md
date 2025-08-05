# 🚀 Setup MongoDB Atlas + Stripe - Guida Completa

## 📋 **Overview**

Configureremo insieme:
1. **MongoDB Atlas** (database cloud multi-tenant)
2. **Stripe** (billing e pagamenti)
3. **Test completo** del sistema

**Tempo stimato**: 15-20 minuti

---

## 🗄️ **STEP 1: MongoDB Atlas Setup**

### **1.1 Crea Account**

1. Vai su [MongoDB Atlas](https://cloud.mongodb.com)
2. Clicca **"Try Free"**
3. Registrati con email (suggerisco Google/GitHub per speed)
4. Completa verifica email

### **1.2 Crea Progetto**

1. Dopo login, clicca **"New Project"**
2. Nome progetto: `MCP Memory Production`
3. Clicca **"Next"** → **"Create Project"**

### **1.3 Crea Cluster**

1. Clicca **"Build a Database"**
2. Scegli **"Shared"** (gratis per iniziare)
3. Provider: **AWS** (consigliato)
4. Region: **N. Virginia (us-east-1)** (consigliato)
5. Nome cluster: `mcp-memory-cluster`
6. Clicca **"Create"**

⏰ **Attendi 3-5 minuti** per il provisioning...

### **1.4 Configura Accesso**

**Database User:**
1. Vai in **"Database Access"**
2. Clicca **"Add New Database User"**
3. Username: `mcpmemory`
4. Password: **Genera sicura** (salva!)
5. Database User Privileges: **"Atlas admin"**
6. Clicca **"Add User"**

**Network Access:**
1. Vai in **"Network Access"**
2. Clicca **"Add IP Address"**
3. Clicca **"Allow Access from Anywhere"** (0.0.0.0/0)
4. Clicca **"Confirm"**

### **1.5 Ottieni Connection String**

1. Vai in **"Database"**
2. Clicca **"Connect"** sul tuo cluster
3. Scegli **"Connect your application"**
4. Driver: **Python 3.11+**
5. Copia la **connection string**
6. Sostituisci `<password>` con la password vera
7. Aggiungi alla fine: `/mcp_memory_master`

**Esempio:**
```
mongodb+srv://mcpmemory:YOUR_PASSWORD@mcp-memory-cluster.abc123.mongodb.net/mcp_memory_master?retryWrites=true&w=majority
```

### **1.6 Genera API Keys**

1. Vai in **"Project Settings"** (ingranaggio in alto)
2. **"Access Manager"** → **"API Keys"**
3. Clicca **"Create API Key"**
4. Description: `MCP Memory Production`
5. Permissions: **"Project Data Access Admin"**
6. Clicca **"Next"**
7. **SALVA** Public Key e Private Key (non li rivedrai!)
8. Whitelist IP: **"0.0.0.0/0"** (o il tuo IP)

### **1.7 Trova Project ID**

1. Nell'URL della dashboard vedrai:
   ```
   https://cloud.mongodb.com/v2/PROJECT_ID_QUI#/overview
   ```
2. Copia il **PROJECT_ID** dall'URL

---

## 💳 **STEP 2: Stripe Setup**

### **2.1 Crea Account**

1. Vai su [Stripe Dashboard](https://dashboard.stripe.com/register)
2. Registrati (email + password)
3. Completa verifica email
4. **Skip business details** per ora (puoi compilare dopo)

### **2.2 Attiva Test Mode**

1. In dashboard, assicurati di essere in **"Test mode"** (toggle in alto)
2. Vedrai **"Test mode"** attivo

### **2.3 Ottieni API Keys**

1. Vai in **"Developers"** → **"API Keys"**
2. Troverai:
   - **Publishable key**: `pk_test_...`
   - **Secret key**: `sk_test_...` (clicca "Reveal")
3. **COPIA** entrambe le keys

### **2.4 Setup Webhook (Opzionale)**

Per ora saltiamo - lo configureremo dopo il deploy.

**Placeholder per ora:**
```
whsec_placeholder_for_later
```

---

## 🔧 **STEP 3: Configurazione Automatica**

### **3.1 Applica Pricing Ottimizzato**

Prima di tutto, applichiamo il pricing competitivo:

```bash
cd /Users/piermatteogrieco/mcp-memory-server
python cloud/optimized_pricing.py
```

Quando chiede: **"Apply optimized pricing? (y/n):"** → digita `y`

### **3.2 Esegui Setup Interattivo**

```bash
python cloud/setup_guide.py
```

Il setup ti chiederà:

**MongoDB Atlas:**
- Hai già account? → `y`
- Public Key → `[incolla la tua]`
- Private Key → `[incolla la tua]`
- Project ID → `[incolla il tuo]`  
- Connection String → `[incolla la tua con password]`

**Stripe:**
- Hai già account? → `y`
- Publishable Key → `pk_test_...`
- Secret Key → `sk_test_...`
- Setup webhook ora? → `n` (per ora)

### **3.3 Validazione Automatica**

Il setup farà:
- ✅ Test MongoDB Atlas API
- ✅ Test connessione database
- ✅ Test Stripe API
- ✅ Creazione file `.env`
- ✅ Test provisioner + billing
- ✅ Creazione utente demo

---

## 🧪 **STEP 4: Test Completo**

### **4.1 Test Sistema Cloud**

```bash
python cloud/usage_example.py
```

Questo dovrebbe mostrare:
- ✅ User setup automatico
- ✅ Salvataggio memories
- ✅ Search operations  
- ✅ Usage tracking
- ✅ Billing calculation

### **4.2 Test Billing Dashboard**

Avvia il server billing:

```bash
python cloud/billing_system.py
```

In un altro terminale:

```bash
# Test dashboard
curl http://localhost:8001/dashboard/[USER_ID_FROM_PREVIOUS_TEST]

# Test subscription creation
curl -X POST http://localhost:8001/subscribe/[USER_ID] \
  -H "Content-Type: application/json" \
  -d '{"plan": "starter"}'
```

---

## ✅ **STEP 5: Verifica Tutto Funziona**

### **5.1 Check Environment**

```bash
cat cloud/.env
```

Dovresti vedere tutte le tue credenziali popolate.

### **5.2 Check Database**

1. Vai nella tua **MongoDB Atlas Dashboard**
2. **"Browse Collections"**
3. Dovresti vedere:
   - Database: `mcp_memory_master`
   - Collections: `users`, `usage_logs`, etc.
   - Documenti con dati di test

### **5.3 Check Stripe**

1. Vai nella **Stripe Dashboard**
2. **"Customers"** → dovresti vedere customer di test
3. **"Logs"** → dovresti vedere API calls

---

## 🎯 **STEP 6: Pricing Finale**

Il sistema ora usa il **pricing ottimizzato**:

| **Tier** | **Prezzo** | **Memory** | **API Calls** |
|----------|------------|------------|---------------|
| **Free** | $0 | 500MB | 5,000/mese |
| **🆕 Starter** | **$9.99** | 2GB | 25,000/mese |
| **Pro** | $29.99 | 10GB | 100,000/mese |
| **Enterprise** | $99.99 | Unlimited | Unlimited |

**Usage-based (oltre i limiti):**
- 💾 Memory: $0.0008/MB (era $0.001)
- 🔍 Search: $0.0003/search (era $0.0005)  
- 📡 API: $0.00008/call (era $0.0001)

---

## 🚀 **STEP 7: Production Ready!**

Se tutto funziona:

### **7.1 Commit Changes**

```bash
git add .
git commit -m "feat: production MongoDB Atlas + Stripe configuration

✅ Optimized pricing with new Starter tier ($9.99)
✅ Interactive setup guide with validation
✅ Complete cloud infrastructure tested
✅ Ready for production deployment"

git push origin main
```

### **7.2 Next Steps**

1. **Deploy su server** (DigitalOcean/AWS)
2. **Switch Stripe a Live Mode** quando pronto
3. **Setup webhook URL** reale
4. **Start onboarding** primi utenti!

---

## ❓ **Troubleshooting**

### **MongoDB Connection Issues**
```bash
# Test manuale connessione
python -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
async def test():
    client = AsyncIOMotorClient('YOUR_CONNECTION_STRING')
    await client.admin.command('ping')
    print('✅ MongoDB connected!')
asyncio.run(test())
"
```

### **Stripe API Issues**
```bash
# Test manuale Stripe
python -c "
import stripe
stripe.api_key = 'sk_test_YOUR_KEY'
print(stripe.Account.retrieve())
"
```

### **Reset Setup**
```bash
rm cloud/.env
python cloud/setup_guide.py
```

---

## 🎉 **Success!**

Quando vedi questo messaggio, sei **production-ready**:

```
🎉 SETUP COMPLETED SUCCESSFULLY!

✅ MongoDB Atlas configured and tested
✅ Stripe configured and tested  
✅ Environment file created
✅ Services initialized successfully

💰 Your cloud monetization system is ready!
```

**Il tuo "Redis for AI Agents" è ora completamente operativo con billing automatico!** 🚀 