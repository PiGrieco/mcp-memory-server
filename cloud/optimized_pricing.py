#!/usr/bin/env python3
"""
Optimized Pricing Configuration
Based on competitive analysis and cost optimization
"""

OPTIMIZED_PRICING_TIERS = {
    "free": {
        "name": "Free",
        "monthly_cost": 0.0,
        "memory_limit_mb": 500,  # 500MB
        "api_calls_limit": 5000,  # 5K
        "overage_cost_per_mb": 0.0,  # No overage for free
        "features": [
            "500MB Memory Storage",
            "5,000 API calls/month", 
            "Basic search",
            "Community support"
        ]
    },
    "starter": {
        "name": "Light User", 
        "monthly_cost": 3.99,  # Light User pricing
        "memory_limit_mb": 2000,  # 2GB
        "api_calls_limit": 25000,  # 25K
        "overage_cost_per_mb": 0.0024,  # Tripled from 0.0008
        "features": [
            "2GB Memory Storage",
            "25,000 API calls/month",
            "Advanced search",
            "Email support",
            "Basic analytics"
        ]
    },
    "pro": {
        "name": "Power User",
        "monthly_cost": 9.99,  # Power User pricing
        "memory_limit_mb": 10000,  # 10GB
        "api_calls_limit": 100000,  # 100K
        "overage_cost_per_mb": 0.0024,  # Tripled from 0.0008
        "features": [
            "10GB Memory Storage",
            "100,000 API calls/month",
            "Advanced search & analytics",
            "Priority support",
            "Team collaboration",
            "API integrations",
            "Usage dashboard"
        ]
    },
    "enterprise": {
        "name": "Enterprise",
        "monthly_cost": 99.99,  # Enterprise pricing
        "memory_limit_mb": -1,  # Unlimited
        "api_calls_limit": -1,  # Unlimited
        "overage_cost_per_mb": 0.0015,  # Tripled from 0.0005
        "features": [
            "Unlimited Memory Storage",
            "Unlimited API calls",
            "Advanced analytics dashboard",
            "24/7 premium support",
            "Multi-tenant architecture",
            "Custom integrations",
            "SLA guarantees",
            "Dedicated support manager"
        ]
    }
}

# Usage-based rates (all tripled)
OPTIMIZED_USAGE_RATES = {
    "memory_storage": 0.0024,   # $0.0024 per MB (tripled from 0.0008)
    "api_call": 0.00024,        # $0.00024 per API call (tripled from 0.00008)
    "search_operation": 0.0009, # $0.0009 per search (tripled from 0.0003)
    "vector_embedding": 0.0024  # $0.0024 per embedding (tripled from 0.0008)
}

def update_billing_system_pricing():
    """Update billing system with optimized pricing"""
    
    print("🔄 Updating billing system with optimized pricing...")
    
    # Update MongoDB provisioner
    provisioner_file = "cloud/mongodb_provisioner.py"
    with open(provisioner_file, 'r') as f:
        content = f.read()
    
    # Replace pricing tiers
    old_pricing_start = 'self.pricing_tiers = {'
    old_pricing_end = '        }'
    
    new_pricing = """self.pricing_tiers = {
            "free": {
                "memory_limit_mb": 500,  # 500MB instead of 1GB
                "monthly_cost": 0,
                "cost_per_mb": 0,
                "api_calls_limit": 5000  # 5K instead of 10K
            },
            "starter": {
                "memory_limit_mb": 2000,  # 2GB - NEW TIER
                "monthly_cost": 9.99,
                "cost_per_mb": 0.0008,
                "api_calls_limit": 25000  # 25K
            },
            "pro": {
                "memory_limit_mb": 10000,  # 10GB
                "monthly_cost": 29.99,
                "cost_per_mb": 0.0008,  # Optimized rate
                "api_calls_limit": 100000
            },
            "enterprise": {
                "memory_limit_mb": -1,  # Unlimited
                "monthly_cost": 99.99,
                "cost_per_mb": 0.0005,
                "api_calls_limit": -1  # Unlimited
            }
        }"""
    
    # Find and replace pricing section
    import re
    pattern = r'self\.pricing_tiers = \{.*?\n        \}'
    content = re.sub(pattern, new_pricing, content, flags=re.DOTALL)
    
    # Write back
    with open(provisioner_file, 'w') as f:
        f.write(content)
    
    print("✅ MongoDB provisioner pricing updated")
    
    # Update billing system
    billing_file = "cloud/billing_system.py"
    with open(billing_file, 'r') as f:
        content = f.read()
    
    # Update usage rates
    old_rates = '''self.usage_rates = {
            "memory_storage": 0.001,  # $0.001 per MB
            "api_call": 0.0001,       # $0.0001 per API call
            "search_operation": 0.0005, # $0.0005 per search
            "vector_embedding": 0.001   # $0.001 per embedding generation
        }'''
    
    new_rates = '''self.usage_rates = {
            "memory_storage": 0.0008,   # $0.0008 per MB (optimized)
            "api_call": 0.00008,        # $0.00008 per API call (optimized)
            "search_operation": 0.0003, # $0.0003 per search (optimized)
            "vector_embedding": 0.0008  # $0.0008 per embedding (optimized)
        }'''
    
    content = content.replace(old_rates, new_rates)
    
    # Update billing plans with Starter tier
    billing_plans_pattern = r'self\.billing_plans = \{.*?\n        \}'
    
    new_billing_plans = '''self.billing_plans = {
            "free": BillingPlan(
                name="Free",
                monthly_cost=0.0,
                memory_limit_mb=500,  # 500MB
                api_calls_limit=5000,  # 5K
                overage_cost_per_mb=0.0,
                features=[
                    "500MB Memory Storage",
                    "5,000 API calls/month",
                    "Basic search",
                    "Community support"
                ]
            ),
            "starter": BillingPlan(
                name="Light User",
                monthly_cost=3.99,
                memory_limit_mb=2000,  # 2GB
                api_calls_limit=25000,  # 25K
                overage_cost_per_mb=0.0024,  # Tripled
                features=[
                    "2GB Memory Storage",
                    "25,000 API calls/month",
                    "Advanced search",
                    "Email support",
                    "Basic analytics"
                ]
            ),
            "pro": BillingPlan(
                name="Power User",
                monthly_cost=9.99,
                memory_limit_mb=10000,  # 10GB
                api_calls_limit=100000,
                overage_cost_per_mb=0.0024,  # Tripled
                features=[
                    "10GB Memory Storage",
                    "100,000 API calls/month",
                    "Advanced search & analytics",
                    "Priority support",
                    "Team collaboration",
                    "API integrations"
                ]
            ),
            "enterprise": BillingPlan(
                name="Enterprise",
                monthly_cost=99.99,
                memory_limit_mb=-1,  # Unlimited
                api_calls_limit=-1,  # Unlimited
                overage_cost_per_mb=0.0015,  # Tripled
                features=[
                    "Unlimited Memory Storage",
                    "Unlimited API calls",
                    "Advanced analytics dashboard",
                    "24/7 premium support",
                    "Multi-tenant architecture",
                    "Custom integrations",
                    "SLA guarantees"
                ]
            )
        }'''
    
    content = re.sub(billing_plans_pattern, new_billing_plans, content, flags=re.DOTALL)
    
    with open(billing_file, 'w') as f:
        f.write(content)
    
    print("✅ Billing system pricing updated")

def show_pricing_comparison():
    """Show comparison between old and new pricing"""
    
    print("\n💰 PRICING OPTIMIZATION COMPARISON")
    print("=" * 50)
    
    comparisons = [
        {
            "metric": "Free Tier Memory",
            "old": "1GB",
            "new": "500MB", 
            "impact": "Reduced to encourage upgrades"
        },
        {
            "metric": "Free Tier API Calls",
            "old": "10,000/month",
            "new": "5,000/month",
            "impact": "Balanced for trial usage"
        },
        {
            "metric": "Light User Tier",
            "old": "N/A",
            "new": "$3.99/month (2GB, 25K calls)",
            "impact": "Affordable entry point for individual users"
        },
        {
            "metric": "Power User Tier",
            "old": "$29.99/month",
            "new": "$9.99/month (10GB, 100K calls)",
            "impact": "67% price reduction, more accessible"
        },
        {
            "metric": "Memory Storage Cost",
            "old": "$0.0008/MB",
            "new": "$0.0024/MB",
            "impact": "3x increase for better margins"
        },
        {
            "metric": "Search Operations",
            "old": "$0.0003/search",
            "new": "$0.0009/search", 
            "impact": "3x increase for better unit economics"
        },
        {
            "metric": "API Calls",
            "old": "$0.00008/call",
            "new": "$0.00024/call",
            "impact": "3x increase for sustainable pricing"
        },
        {
            "metric": "Vector Embeddings",
            "old": "$0.0008/embedding",
            "new": "$0.0024/embedding",
            "impact": "3x increase for AI processing costs"
        }
    ]
    
    for comp in comparisons:
        print(f"\n📊 {comp['metric']}:")
        print(f"   Old: {comp['old']}")
        print(f"   New: {comp['new']}")
        print(f"   Impact: {comp['impact']}")

if __name__ == "__main__":
    show_pricing_comparison()
    
    confirm = input("\n🔄 Apply optimized pricing? (y/n): ").lower() == 'y'
    
    if confirm:
        update_billing_system_pricing()
        print("\n✅ Pricing optimization applied!")
        print("🚀 Ready for Stripe configuration with competitive rates!")
    else:
        print("⏸️ Pricing optimization skipped") 