#!/usr/bin/env python3
"""
Cost Analysis Tool for MCP Memory Cloud
Detailed breakdown for pricing optimization
"""

def analyze_costs():
    """Analisi dettagliata dei costi operativi"""
    
    print("💰 MCP MEMORY CLOUD - COST ANALYSIS")
    print("=" * 50)
    
    # COSTI OPERATIVI (stimati)
    operational_costs = {
        "mongodb_atlas_m10": 57.0,      # $57/month per cluster M10 (2GB RAM, 10GB storage)
        "mongodb_atlas_m20": 120.0,     # $120/month per cluster M20 (4GB RAM, 20GB storage)  
        "stripe_processing": 0.029,     # 2.9% + $0.30 per transaction
        "server_hosting": 50.0,         # $50/month per server (DigitalOcean/AWS)
        "embedding_compute": 0.0001,    # $0.0001 per embedding (sentence-transformers)
        "backup_storage": 10.0,         # $10/month per 100GB backup
    }
    
    # UNIT ECONOMICS
    print("\n📊 UNIT ECONOMICS")
    print("-" * 20)
    
    # Stima costi per operazione
    costs_per_operation = {
        "save_memory": {
            "mongodb_write": 0.000001,      # ~$0.000001 per write operation
            "embedding_generation": 0.0001,  # $0.0001 per embedding
            "storage_per_mb": 0.000015,     # ~$0.000015 per MB stored/month
            "total": 0.000116
        },
        "search_memory": {
            "mongodb_query": 0.000002,       # ~$0.000002 per query
            "vector_search": 0.00001,       # ~$0.00001 per vector search
            "total": 0.000012
        },
        "api_call": {
            "server_processing": 0.00001,   # $0.00001 per API call
            "bandwidth": 0.000001,          # $0.000001 per call (bandwidth)
            "total": 0.000011
        }
    }
    
    for operation, breakdown in costs_per_operation.items():
        print(f"\n🔧 {operation.upper()}:")
        for component, cost in breakdown.items():
            if component != "total":
                print(f"   • {component}: ${cost:.6f}")
        print(f"   ⚡ TOTAL: ${breakdown['total']:.6f}")
    
    # PROFITABILITY ANALYSIS
    print("\n💡 PROFITABILITY ANALYSIS")
    print("-" * 25)
    
    current_pricing = {
        "memory_storage_per_mb": 0.0024,    # $0.0024 per MB (tripled from 0.0008)
        "search_operation": 0.0009,         # $0.0009 per search (tripled from 0.0003)
        "api_call": 0.00024,                # $0.00024 per API call (tripled from 0.00008)
        "vector_embedding": 0.0024          # $0.0024 per embedding (tripled from 0.0008)
    }
    
    # Calcola margins
    margins = {
        "memory_storage": {
            "revenue": current_pricing["memory_storage_per_mb"],
            "cost": costs_per_operation["save_memory"]["storage_per_mb"],
            "margin": current_pricing["memory_storage_per_mb"] - costs_per_operation["save_memory"]["storage_per_mb"]
        },
        "search": {
            "revenue": current_pricing["search_operation"], 
            "cost": costs_per_operation["search_memory"]["total"],
            "margin": current_pricing["search_operation"] - costs_per_operation["search_memory"]["total"]
        },
        "api": {
            "revenue": current_pricing["api_call"],
            "cost": costs_per_operation["api_call"]["total"],
            "margin": current_pricing["api_call"] - costs_per_operation["api_call"]["total"]
        }
    }
    
    for service, data in margins.items():
        margin_pct = (data["margin"] / data["revenue"]) * 100
        print(f"\n💰 {service.upper()}:")
        print(f"   Revenue: ${data['revenue']:.6f}")
        print(f"   Cost: ${data['cost']:.6f}")
        print(f"   Margin: ${data['margin']:.6f} ({margin_pct:.1f}%)")
    
    # COMPETITIVE ANALYSIS
    print("\n🏆 COMPETITIVE ANALYSIS")
    print("-" * 22)
    
    competitors = {
        "Pinecone": {
            "storage_per_mb": 0.002,        # $2 per 1M vectors (~1GB)
            "queries_per_1k": 0.0004,      # $0.4 per 1K queries
        },
        "Weaviate Cloud": {
            "storage_per_mb": 0.0015,      # ~$1.5 per GB
            "queries_per_1k": 0.0003,     # ~$0.3 per 1K queries
        },
        "Redis Enterprise": {
            "storage_per_mb": 0.001,       # $1 per GB
            "queries_per_1k": 0.0002,     # ~$0.2 per 1K queries
        }
    }
    
    for competitor, pricing in competitors.items():
        print(f"\n🔥 {competitor}:")
        print(f"   Storage: ${pricing['storage_per_mb']:.4f}/MB")
        print(f"   Queries: ${pricing['queries_per_1k']:.4f}/1K")
    
    print(f"\n🎯 OUR PRICING:")
    print(f"   Storage: ${current_pricing['memory_storage_per_mb']:.4f}/MB")
    print(f"   Searches: ${current_pricing['search_operation'] * 1000:.4f}/1K")
    
    # SCALING PROJECTIONS
    print("\n📈 SCALING PROJECTIONS")
    print("-" * 20)
    
    user_scenarios = [
        {"users": 100, "avg_monthly_revenue": 15},
        {"users": 1000, "avg_monthly_revenue": 25}, 
        {"users": 10000, "avg_monthly_revenue": 35},
        {"users": 50000, "avg_monthly_revenue": 45}
    ]
    
    for scenario in user_scenarios:
        users = scenario["users"]
        revenue_per_user = scenario["avg_monthly_revenue"]
        total_revenue = users * revenue_per_user
        
        # Stima costi operativi (con scaling)
        if users <= 1000:
            infra_cost = 500  # Basic infrastructure
        elif users <= 10000:
            infra_cost = 2000  # Medium infrastructure  
        else:
            infra_cost = 8000  # Large infrastructure
        
        variable_costs = users * 2  # $2 per user variabile costs
        total_costs = infra_cost + variable_costs
        profit = total_revenue - total_costs
        profit_margin = (profit / total_revenue) * 100
        
        print(f"\n👥 {users:,} Users:")
        print(f"   Revenue: ${total_revenue:,}/month")
        print(f"   Costs: ${total_costs:,}/month")
        print(f"   Profit: ${profit:,}/month ({profit_margin:.1f}%)")

def pricing_recommendations():
    """Raccomandazioni per pricing ottimale"""
    
    print("\n\n🎯 PRICING RECOMMENDATIONS")
    print("=" * 30)
    
    # Sweet spot pricing basato su analisi
    recommended_pricing = {
        "free_tier": {
            "memory_limit_mb": 500,         # 500MB
            "api_calls_limit": 5000,        # 5K
            "monthly_cost": 0
        },
        "light_user_tier": {
            "memory_limit_mb": 2000,        # 2GB
            "api_calls_limit": 25000,       # 25K
            "monthly_cost": 3.99            # Light User
        },
        "power_user_tier": {
            "memory_limit_mb": 10000,       # 10GB
            "api_calls_limit": 100000,      # 100K
            "monthly_cost": 9.99            # Power User
        },
        "enterprise_tier": {
            "memory_limit_mb": -1,          # Unlimited
            "api_calls_limit": -1,          # Unlimited
            "monthly_cost": 99.99           # Enterprise
        }
    }
    
    # Usage-based pricing (tutti triplicati)
    usage_based_pricing = {
        "memory_storage": 0.0024,       # $0.0024/MB (tripled)
        "search_operations": 0.0009,    # $0.0009/search (tripled)
        "api_calls": 0.00024,           # $0.00024/call (tripled)
        "vector_embeddings": 0.0024     # $0.0024/embedding (tripled)
    }
    
    print("💰 RECOMMENDED MONTHLY TIERS:")
    for tier, details in recommended_pricing.items():
        print(f"\n{tier.replace('_', ' ').title()}:")
        print(f"   Memory: {details['memory_limit_mb'] if details['memory_limit_mb'] > 0 else 'Unlimited'}")
        print(f"   API Calls: {details['api_calls_limit'] if details['api_calls_limit'] > 0 else 'Unlimited'}")  
        print(f"   Price: ${details['monthly_cost']}/month")
    
    print(f"\n💡 RECOMMENDED USAGE PRICING:")
    for metric, price in usage_based_pricing.items():
        print(f"   {metric.replace('_', ' ').title()}: ${price:.6f}")
    
    # ROI Calculation
    print(f"\n📊 EXPECTED ROI:")
    print(f"   1K Memory Operations: ${usage_based_pricing['memory_storage'] * 500:.3f}")  # Assuming 500KB avg
    print(f"   1K Search Operations: ${usage_based_pricing['search_operations'] * 1000:.3f}")
    print(f"   1MB Storage: ${usage_based_pricing['memory_storage']:.3f}")

if __name__ == "__main__":
    analyze_costs()
    pricing_recommendations() 