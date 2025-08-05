# 🌩️ MCP Memory Server - Cloud Setup Guide

## 📋 **Overview**

Il sistema Cloud di MCP Memory Server offre:

- ✅ **MongoDB automatico multi-tenant** (ogni utente ha il suo database)
- ✅ **Billing automatico basato sull'usage** (Stripe integration)
- ✅ **Monitoraggio usage in tempo reale**
- ✅ **Tier automatici** (Free, Pro, Enterprise)
- ✅ **Provisioning automatico** (zero setup manuale)

---

## 🚀 **Quick Start**

### **Step 1: Setup Cloud Environment**

```bash
# 1. Copia il file di configurazione
cp cloud/.env.example cloud/.env

# 2. Modifica con le tue credenziali
nano cloud/.env
```

### **Step 2: Setup MongoDB Atlas (opzionale)**

Se vuoi cluster dedicati per ogni utente:

```bash
# Vai su MongoDB Atlas (cloud.mongodb.com)
# 1. Crea un progetto
# 2. Genera API Keys (Project Settings > Access Manager > API Keys)
# 3. Aggiungi le credenziali in .env
```

### **Step 3: Setup Stripe per Billing**

```bash
# Vai su Stripe Dashboard (dashboard.stripe.com)
# 1. Crea account/ottieni API keys
# 2. Setup webhook endpoint: https://your-domain.com/webhook/stripe
# 3. Aggiungi credenziali in .env
```

### **Step 4: Avvia il Sistema Cloud**

```bash
# Installa dependencies
pip install stripe httpx motor

# Avvia il provisioner
python cloud/mongodb_provisioner.py

# Avvia il billing system
python cloud/billing_system.py
```

---

## 🏗️ **Architettura del Sistema**

### **Multi-Tenant Database Structure**

```
Master Database (mcp_memory_master)
├── users                    # User accounts e billing info  
├── usage_logs              # Tracking per ogni operazione
├── invoices                # Fatture generate
├── notifications           # Sistema di notifiche
└── analytics               # Metriche aggregate

User Database (mcp_memory_{user_id})
├── memories                # Le memorie dell'utente
├── usage_logs             # Log locali dell'utente  
├── user_preferences       # Preferenze utente
└── sessions               # Sessioni attive
```

### **Pricing Tiers**

| Tier | Prezzo | Memory Limit | API Calls | Features |
|------|--------|--------------|-----------|----------|
| **Free** | $0/mese | 1GB | 10,000/mese | Basic search, Community support |
| **Pro** | $29.99/mese | 10GB | 100,000/mese | Advanced search, Priority support, Team collaboration |
| **Enterprise** | $99.99/mese | Unlimited | Unlimited | Analytics dashboard, 24/7 support, Custom integrations |

### **Usage-Based Billing**

- 💾 **Memory Storage**: $0.001 per MB oltre il limite
- 🔍 **Search Operations**: $0.0005 per ricerca
- 🧠 **Vector Embeddings**: $0.001 per embedding generato
- 📡 **API Calls**: $0.0001 per call oltre il limite

---

## 🔧 **Integrazione Automatica**

### **1. Setup Utente Automatico**

```python
from cloud.cloud_integration import CloudMemoryClient

# Inizializza client cloud
client = CloudMemoryClient(user_email="user@example.com")

# Setup automatico account + database
await client.initialize_cloud()

# Il sistema crea automaticamente:
# ✅ User account unico
# ✅ Database MongoDB dedicato  
# ✅ API key sicura
# ✅ Configurazione locale
```

### **2. Tracking Usage Automatico**

```python
# Ogni operazione viene tracciata automaticamente
await client.track_memory_operation(
    operation="save",
    memory_size_mb=2.5  # 2.5MB di memoria salvata
)

# Il sistema aggiorna:
# ✅ Usage totale utente
# ✅ Billing data
# ✅ Limits checking
# ✅ Notifiche se necessario
```

### **3. Billing Automatico**

```python
from cloud.billing_system import BillingSystem

billing = BillingSystem()

# Genera fattura automatica mensile
invoice = await billing.generate_invoice(
    user_id="user123",
    month=12,
    year=2024
)

# Stripe processo automatico:
# ✅ Calcolo usage-based costs
# ✅ Creazione invoice Stripe
# ✅ Gestione pagamenti
# ✅ Upgrade/downgrade automatici
```

---

## 🛠️ **Configurazione Avanzata**

### **Environment Variables**

```bash
# MongoDB Atlas (opzionale - per cluster dedicati)
MONGODB_ATLAS_PUBLIC_KEY=your_public_key
MONGODB_ATLAS_PRIVATE_KEY=your_private_key  
MONGODB_ATLAS_PROJECT_ID=your_project_id

# Master MongoDB (obbligatorio)
MONGODB_MASTER_CONNECTION=mongodb+srv://user:pass@cluster.net/master

# Stripe (obbligatorio per billing)
STRIPE_SECRET_KEY=sk_live_or_test_key
STRIPE_WEBHOOK_SECRET=whsec_webhook_secret

# Opzionali
SENDGRID_API_KEY=for_email_notifications
JWT_SECRET_KEY=for_api_authentication
```

### **Customizza Pricing**

```python
# In cloud/billing_system.py
billing_plans = {
    "startup": BillingPlan(
        name="Startup",
        monthly_cost=9.99,
        memory_limit_mb=5000,  # 5GB
        api_calls_limit=50000,
        overage_cost_per_mb=0.0008,
        features=["5GB Storage", "Advanced search", "Email support"]
    )
}
```

---

## 🧪 **Testing del Sistema**

### **Test User Creation**

```bash
# Test creazione utente
python cloud/cloud_integration.py --setup --email="test@example.com"

# Verifica database
python cloud/cloud_integration.py --verify
```

### **Test Billing**

```bash
# Test calcolo billing
python -c "
from cloud.billing_system import BillingSystem
import asyncio

async def test():
    billing = BillingSystem()
    await billing.initialize()
    
    # Simula usage
    dashboard = await billing.get_usage_dashboard_data('test_user')
    print(dashboard)

asyncio.run(test())
"
```

### **Test Complete Flow**

```bash
# Test completo: user creation + usage tracking + billing
python cloud/test_cloud_system.py
```

---

## 📊 **Monitoring & Analytics**

### **Usage Dashboard**

```python
# Get real-time user analytics
stats = await client.get_usage_stats()

print(f"""
📊 Usage Stats:
  💾 Memory Used: {stats['current_usage_mb']:.1f} MB / {stats['usage_limit_mb']} MB
  📈 Usage: {stats['usage_percentage']:.1f}%
  🏷️ Tier: {stats['tier'].title()}
""")
```

### **Billing Dashboard API**

```bash
# Avvia billing dashboard
python cloud/billing_system.py

# Access dashboard
curl http://localhost:8001/dashboard/{user_id}

# Create subscription  
curl -X POST http://localhost:8001/subscribe/{user_id} \
  -H "Content-Type: application/json" \
  -d '{"plan": "pro"}'
```

---

## 🔐 **Security & Best Practices**

### **API Key Security**

- ✅ API keys generate con `secrets.token_urlsafe(32)`
- ✅ Stored encrypted nel database
- ✅ Rate limiting per user (1000 req/hour default)
- ✅ JWT tokens per authentication

### **Database Security**

- ✅ User isolation completa (database separati)
- ✅ Connection strings uniche per user
- ✅ MongoDB Atlas security (quando usato)
- ✅ Backup automatici

### **Billing Security**

- ✅ Stripe webhook signature verification
- ✅ Idempotent operations
- ✅ Failed payment handling
- ✅ Fraud protection

---

## 🚀 **Deployment**

### **Local Development**

```bash
# Setup completo locale
./setup_wizard.sh
# Seleziona "Enable cloud memory" quando richiesto
```

### **Production Deployment**

```bash
# 1. Setup environment
export MONGODB_MASTER_CONNECTION="your_production_db"
export STRIPE_SECRET_KEY="sk_live_your_key"

# 2. Deploy services
docker-compose -f docker-compose.cloud.yml up -d

# 3. Setup load balancer/reverse proxy
# Nginx/Cloudflare per gestire traffic
```

### **Scalability**

- 🔄 **Horizontal scaling**: Ogni user ha database isolato
- ⚡ **Performance**: Connection pooling e caching
- 📈 **Auto-scaling**: MongoDB Atlas auto-scaling
- 🌍 **Global**: Multi-region deployment ready

---

## 💡 **Usage Examples**

### **Integrazione nei Plugin Esistenti**

```python
# examples/claude_cloud_auto.py
from cloud.cloud_integration import CloudMemoryClient

class CloudClaudeMemory:
    def __init__(self, user_email):
        self.cloud_client = CloudMemoryClient(user_email)
    
    async def initialize(self):
        # Setup automatico cloud
        await self.cloud_client.initialize_cloud()
        
        # Get connection string per questo user
        connection = await self.cloud_client.get_connection_string()
        
        # Usa connection per MCP server
        self.mcp_server = MCPServer(connection)
    
    async def save_memory(self, text, memory_type):
        # Salva nella memoria utente
        result = await self.mcp_server.save_memory(text, memory_type)
        
        # Track usage per billing
        memory_size = len(text.encode('utf-8')) / (1024 * 1024)  # MB
        await self.cloud_client.track_memory_operation("save", memory_size)
        
        return result
```

### **Browser Extension con Cloud**

```javascript
// browser-extension/cloud-content.js
class CloudChatGPTMemory {
    async initializeCloud() {
        // Check se user ha cloud config
        const response = await fetch('http://localhost:8000/cloud/status');
        
        if (response.ok) {
            const data = await response.json();
            this.cloudEnabled = data.cloud_enabled;
            this.userTier = data.tier;
            this.usageStats = data.usage;
        }
    }
    
    async saveToCloud(message) {
        if (!this.cloudEnabled) return;
        
        const response = await fetch('http://localhost:8000/cloud/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                text: message,
                memory_type: 'chatgpt_conversation'
            })
        });
        
        // Update usage display
        this.updateUsageUI();
    }
}
```

---

## ❓ **FAQ**

### **Q: Come funziona il multi-tenancy?**
A: Ogni utente ottiene un database MongoDB completamente isolato con nome `mcp_memory_{user_id}`. Zero condivisione dati.

### **Q: Cosa succede se supero i limiti?**
A: 
- **Free tier**: Operazioni bloccate fino al mese successivo
- **Pro/Enterprise**: Addebito automatico overage costs

### **Q: Come funziona il billing?**
A: Stripe gestisce subscriptions mensili + invoice separate per usage overages.

### **Q: Posso usare il mio MongoDB?**
A: Sì! Basta configurare `MONGODB_MASTER_CONNECTION` con il tuo cluster.

### **Q: È secure?**
A: Sì! Database isolation, API keys criptate, Stripe security, rate limiting.

---

## 🆘 **Support**

- 📧 **Email**: cloud-support@mcp-memory.ai
- 📚 **Docs**: [Cloud Documentation](https://docs.mcp-memory.ai/cloud)
- 🐛 **Issues**: [GitHub Issues](https://github.com/AiGotsrl/mcp-memory-server/issues)
- 💬 **Discord**: [Community Chat](https://discord.gg/mcp-memory)

---

## 🎯 **Roadmap Cloud**

### **Q1 2024**
- ✅ MongoDB auto-provisioning
- ✅ Stripe billing integration
- ✅ Multi-tenant architecture
- ✅ Usage tracking & limits

### **Q2 2024**
- 🔄 Advanced analytics dashboard
- 🔄 Team collaboration features
- 🔄 API rate limiting avanzato
- 🔄 Multi-region deployment

### **Q3 2024**
- 📦 Enterprise SSO integration
- 📦 Advanced security features
- 📦 Custom integrations
- 📦 White-label solutions

---

**🌟 Il tuo "Redis for AI Agents" ora è completamente cloud-ready con monetizzazione automatica!** 🚀 