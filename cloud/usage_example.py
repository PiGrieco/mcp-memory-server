#!/usr/bin/env python3
"""
Complete Usage Example - MCP Memory Cloud System
Shows real-world setup and usage patterns
"""

import asyncio
from cloud.cloud_integration import CloudMemoryClient
from cloud.billing_system import BillingSystem

async def demo_complete_flow():
    """Dimostra il flow completo dal setup all'uso"""
    
    print("🌩️ MCP Memory Cloud - Complete Demo")
    print("=" * 50)
    
    # STEP 1: Setup utente automatico
    print("\n1️⃣ USER SETUP")
    client = CloudMemoryClient(user_email="demo@example.com")
    
    # Questo crea automaticamente:
    # ✅ Account utente unico
    # ✅ Database MongoDB isolato  
    # ✅ API key sicura
    # ✅ Config locale
    success = await client.initialize_cloud()
    
    if not success:
        print("❌ Setup failed")
        return
    
    # STEP 2: Uso normale (quello che faranno i plugin)
    print("\n2️⃣ NORMAL USAGE")
    
    # Simula utilizzo di Claude/ChatGPT/Cursor
    memories_saved = [
        ("Come configurare FastAPI con async", "technical_solution", 0.5),
        ("Preferenze utente per dark mode", "user_preference", 0.1), 
        ("Bug fix per memory leak in Python", "debugging_solution", 0.8),
        ("Setup MongoDB Atlas connection", "configuration", 0.3),
        ("Stripe webhook implementation guide", "technical_solution", 1.2)
    ]
    
    total_memory_mb = 0
    for i, (text, memory_type, size_mb) in enumerate(memories_saved, 1):
        # Ogni volta che il plugin salva una memoria
        await client.track_memory_operation("save", size_mb)
        total_memory_mb += size_mb
        print(f"   💾 Memory {i}: {text[:40]}... ({size_mb}MB)")
    
    # Simula ricerche (search operations)
    searches = [
        "Come configurare FastAPI?",
        "Bug memory leak Python",
        "Setup MongoDB", 
        "Stripe webhook",
        "Dark mode preferences"
    ]
    
    for i, search in enumerate(searches, 1):
        await client.track_memory_operation("search", 0)  # Le ricerche non aggiungono memoria
        print(f"   🔍 Search {i}: {search}")
    
    # STEP 3: Mostra usage stats
    print("\n3️⃣ USAGE STATS")
    stats = await client.get_usage_stats()
    print(f"   💾 Memory Used: {stats['current_usage_mb']:.2f} MB / {stats['usage_limit_mb']} MB")
    print(f"   📈 Usage: {stats['usage_percentage']:.1f}%")
    print(f"   🏷️ Tier: {stats['tier'].title()}")
    
    # STEP 4: Simula billing (fine mese)
    print("\n4️⃣ BILLING CALCULATION")
    billing = BillingSystem()
    await billing.initialize()
    
    # Calcola costi per questo utente
    user_id = client.user_account["user_id"]
    from datetime import datetime
    now = datetime.utcnow()
    
    dashboard_data = await billing.get_usage_dashboard_data(user_id)
    current_costs = dashboard_data["current_costs"]
    
    print(f"   💰 Base Cost: ${current_costs['base_subscription']:.2f}")
    print(f"   💰 Memory Overage: ${current_costs['memory_overage']:.4f}")
    print(f"   💰 Search Costs: ${current_costs['additional_usage']:.4f}")
    print(f"   💰 Total: ${sum(current_costs.values()):.2f}")
    
    return {
        "memories_saved": len(memories_saved),
        "total_memory_mb": total_memory_mb,
        "searches_performed": len(searches),
        "total_cost": sum(current_costs.values()),
        "user_stats": stats
    }

async def estimate_real_usage():
    """Stima usage patterns realistici"""
    
    print("\n📊 REAL USAGE ESTIMATES")
    print("=" * 30)
    
    # Patterns di utilizzo realistici
    usage_patterns = {
        "Light User (Claude Desktop)": {
            "memories_per_day": 10,
            "avg_memory_size_mb": 0.2,  # 200KB media
            "searches_per_day": 5,
            "days_per_month": 20
        },
        "Power User (Cursor + ChatGPT)": {
            "memories_per_day": 50,
            "avg_memory_size_mb": 0.5,  # 500KB media
            "searches_per_day": 25,
            "days_per_month": 25
        },
        "Team/Enterprise": {
            "memories_per_day": 200,
            "avg_memory_size_mb": 0.8,  # 800KB media
            "searches_per_day": 100,
            "days_per_month": 30
        }
    }
    
    for user_type, pattern in usage_patterns.items():
        monthly_memories = pattern["memories_per_day"] * pattern["days_per_month"]
        monthly_memory_mb = monthly_memories * pattern["avg_memory_size_mb"]
        monthly_searches = pattern["searches_per_day"] * pattern["days_per_month"]
        
        # Calcola costi con pricing attuale
        memory_cost = monthly_memory_mb * 0.001  # $0.001 per MB
        search_cost = monthly_searches * 0.0005   # $0.0005 per search
        total_usage_cost = memory_cost + search_cost
        
        print(f"\n👤 {user_type}:")
        print(f"   📝 Memories/month: {monthly_memories:,}")
        print(f"   💾 Memory MB/month: {monthly_memory_mb:.1f} MB")
        print(f"   🔍 Searches/month: {monthly_searches:,}")
        print(f"   💰 Usage Cost: ${total_usage_cost:.2f}/month")
        
        # Proiezioni 1K calls e 1MB
        memories_per_1k = 1000
        cost_per_1k_memories = memories_per_1k * pattern["avg_memory_size_mb"] * 0.001
        cost_per_1mb = 1.0 * 0.001  # $0.001 per MB
        
        print(f"   📊 Cost per 1K memories: ${cost_per_1k_memories:.3f}")
        print(f"   📊 Cost per 1MB: ${cost_per_1mb:.3f}")

if __name__ == "__main__":
    async def main():
        # Demo completo
        demo_results = await demo_complete_flow()
        
        # Stime realistiche
        await estimate_real_usage()
        
        print(f"\n🎯 DEMO COMPLETED")
        print(f"Demo saved {demo_results['memories_saved']} memories")
        print(f"Total cost for demo: ${demo_results['total_cost']:.4f}")
    
    asyncio.run(main()) 