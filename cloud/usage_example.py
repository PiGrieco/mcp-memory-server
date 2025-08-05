#!/usr/bin/env python3
"""
Complete demo of MCP Memory Cloud system
Demonstrates automatic user setup and usage-based billing
"""

import asyncio
from cloud_integration import CloudMemoryClient
from billing_system import BillingSystem
from datetime import datetime, timedelta

async def demo_complete_flow():
    """
    Dimostra il flusso completo:
    1. Setup automatico utente (first-time use)
    2. Salvataggio memorie
    3. Ricerche
    4. Calcolo billing
    """
    
    print("🌩️ MCP MEMORY CLOUD - DEMO COMPLETO")
    print("=" * 50)
    
    # 1. Setup automatico utente
    print("\n1️⃣ SETUP AUTOMATICO UTENTE")
    print("-" * 30)
    
    demo_email = "demo@mcpmemory.cloud"
    client = CloudMemoryClient(demo_email)
    
    print(f"📧 Inizializzando per: {demo_email}")
    
    try:
        await client.initialize_cloud()
        print("✅ Utente inizializzato con successo!")
        print(f"   🆔 User ID: {client.user_id}")
        print(f"   🔑 API Key: {client.api_key[:20]}...")
        print(f"   🗄️ Database: {client.database_name}")
        
    except Exception as e:
        print(f"❌ Errore inizializzazione: {e}")
        return
    
    # 2. Simulazione uso normale
    print("\n2️⃣ SIMULAZIONE USO NORMALE")
    print("-" * 30)
    
    memories = [
        {
            "content": "L'utente preferisce Python per l'AI development",
            "context": "conversation_preferences", 
            "tags": ["python", "ai", "development"]
        },
        {
            "content": "Il progetto MCP Memory è stato configurato con MongoDB Atlas",
            "context": "project_setup",
            "tags": ["mcp", "mongodb", "setup"]
        },
        {
            "content": "Stripe configurato per billing automatico",
            "context": "billing_setup", 
            "tags": ["stripe", "billing", "payment"]
        },
        {
            "content": "L'utente lavora su MacOS con VS Code",
            "context": "environment_setup",
            "tags": ["macos", "vscode", "environment"]
        },
        {
            "content": "Preferisce interfacce CLI per automazione",
            "context": "user_preferences",
            "tags": ["cli", "automation", "preferences"]
        }
    ]
    
    # Salva memorie
    for i, memory in enumerate(memories, 1):
        print(f"   💾 Salvando memoria {i}: {memory['content'][:40]}...")
        
        # Simula save tramite MCP (tracked automaticamente)
        await client.track_memory_operation(
            operation_type="save",
            data_size_mb=len(memory['content']) / (1024 * 1024),  # ~KB
            metadata=memory
        )
    
    # Simula ricerche
    searches = [
        "Python AI development",
        "MongoDB setup",
        "billing configuration", 
        "user environment preferences",
        "CLI automation tools"
    ]
    
    for i, search in enumerate(searches, 1):
        print(f"   🔍 Ricerca {i}: {search}")
        
        # Simula search tramite MCP (tracked automaticamente)
        await client.track_memory_operation(
            operation_type="search",
            query=search,
            results_count=3  # Simula 3 risultati
        )
    
    # 3. Real-time usage stats
    print("\n3️⃣ STATISTICHE USO IN TEMPO REALE")
    print("-" * 30)
    
    stats = await client.get_usage_stats()
    if stats:
        print(f"   📊 API Calls: {stats.get('api_calls', 0)}")
        print(f"   💾 Memory Used: {stats.get('memory_usage_mb', 0):.2f} MB")
        print(f"   🔍 Searches: {stats.get('search_operations', 0)}")
        print(f"   🧮 Embeddings: {stats.get('vector_embeddings', 0)}")
        print(f"   💰 Current Tier: {stats.get('tier', 'free')}")
    
    # 4. Calcolo costi fine mese
    print("\n4️⃣ CALCOLO COSTI FINE MESE")
    print("-" * 30)
    
    billing = BillingSystem()
    await billing.initialize()
    
    # Simula billing dashboard per questo utente
    dashboard_data = await billing.get_usage_dashboard_data(client.user_id)
    
    if dashboard_data:
        print(f"   💳 Piano: {dashboard_data['user_tier']}")
        print(f"   📈 Usage corrente:")
        usage = dashboard_data['current_usage']
        for key, value in usage.items():
            print(f"      {key}: {value}")
        
        print(f"   💰 Costo stimato mese: ${dashboard_data.get('estimated_monthly_cost', 0):.2f}")
        
        if dashboard_data.get('overage_costs'):
            print(f"   ⚠️ Costi extra: ${dashboard_data['overage_costs']:.2f}")
    
    print("\n✅ Demo completato con successo!")

def estimate_real_usage():
    """
    Stima usage realistico per diverse tipologie di utenti
    """
    
    print("\n" + "=" * 60)
    print("📊 STIME USAGE REALISTICO")
    print("=" * 60)
    
    user_profiles = {
        "Light User": {
            "monthly_memories": 100,
            "monthly_searches": 200, 
            "monthly_api_calls": 500,
            "avg_memory_size_kb": 2  # 2KB per memoria
        },
        "Power User": {
            "monthly_memories": 1000,
            "monthly_searches": 2000,
            "monthly_api_calls": 5000,
            "avg_memory_size_kb": 5  # 5KB per memoria
        },
        "Enterprise": {
            "monthly_memories": 10000,
            "monthly_searches": 20000,
            "monthly_api_calls": 50000,
            "avg_memory_size_kb": 10  # 10KB per memoria
        }
    }
    
    # Pricing corrente (da billing_system.py) - tutti triplicati
    pricing = {
        "memory_per_mb": 0.0024,  # $0.0024/MB (triplicato da 0.0008)
        "api_call": 0.00024,      # $0.00024/call (triplicato da 0.00008)
        "search": 0.0009,         # $0.0009/search (triplicato da 0.0003)
        "embedding": 0.0024       # $0.0024/embedding (triplicato da 0.0008)
    }
    
    for profile, usage in user_profiles.items():
        print(f"\n📋 {profile}")
        print("-" * 40)
        
        # Calcoli
        total_memory_mb = (usage["monthly_memories"] * usage["avg_memory_size_kb"]) / 1024
        
        costs = {
            "memory": total_memory_mb * pricing["memory_per_mb"],
            "api_calls": usage["monthly_api_calls"] * pricing["api_call"],
            "searches": usage["monthly_searches"] * pricing["search"],
            "embeddings": usage["monthly_memories"] * pricing["embedding"]  # 1 embedding per memoria
        }
        
        total_cost = sum(costs.values())
        
        print(f"   Memory usage: {total_memory_mb:.1f} MB → ${costs['memory']:.2f}")
        print(f"   API calls: {usage['monthly_api_calls']} → ${costs['api_calls']:.2f}")
        print(f"   Searches: {usage['monthly_searches']} → ${costs['searches']:.2f}")
        print(f"   Embeddings: {usage['monthly_memories']} → ${costs['embeddings']:.2f}")
        print(f"   🎯 TOTAL: ${total_cost:.2f}/month")
    
    # Proiezioni per 1K e 1MB
    print(f"\n💡 UNIT COSTS:")
    print(f"   1K memories (~5MB): ${(5 * pricing['memory_per_mb'] + 1000 * pricing['embedding']):.2f}")
    print(f"   1MB storage: ${pricing['memory_per_mb']:.3f}")
    print(f"   1K API calls: ${(1000 * pricing['api_call']):.2f}")
    print(f"   1K searches: ${(1000 * pricing['search']):.2f}")

async def main():
    """Main demo function"""
    try:
        # Demo completo
        await demo_complete_flow()
        
        # Stime realistiche
        estimate_real_usage()
        
    except Exception as e:
        print(f"❌ Errore durante demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 