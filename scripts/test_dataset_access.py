#!/usr/bin/env python3
"""
Test Dataset Access
Verify access to all required datasets before building
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from datasets import load_dataset
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False

from src.utils.logging import get_logger

logger = get_logger(__name__)


def test_dataset_access():
    """Test access to all required datasets"""
    
    if not HAS_DATASETS:
        print("❌ datasets library not installed")
        print("Run: pip install datasets")
        return False
    
    print("🔍 **DATASET ACCESS TEST**")
    print("=" * 50)
    
    # Dataset list with priorities
    datasets_to_test = [
        # Public datasets (should work immediately)
        {
            "id": "banking77",
            "name": "BANKING77",
            "access": "Public", 
            "priority": "Medium",
            "target_samples": 4000
        },
        {
            "id": "snips_built_in_intents", 
            "name": "SNIPS",
            "access": "Public",
            "priority": "Medium", 
            "target_samples": 3000
        },
        {
            "id": "clinc_oos",
            "name": "CLINC150",
            "access": "Public",
            "priority": "High",
            "target_samples": 15000,
            "config": "imbalanced"  # Required config
        },
        {
            "id": "hwu_64",
            "name": "HWU64", 
            "access": "Public",
            "priority": "Medium",
            "target_samples": 2000
        },
        {
            "id": "persona_chat",
            "name": "PersonaChat",
            "access": "Public",
            "priority": "Low",
            "target_samples": 1000
        },
        {
            "id": "daily_dialog",
            "name": "DailyDialog",
            "access": "Public", 
            "priority": "Low",
            "target_samples": 1000
        },
        
        # Approval required datasets
        {
            "id": "AmazonScience/massive",
            "name": "MASSIVE",
            "access": "Approval Required",
            "priority": "Very High",
            "target_samples": 25000
        },
        {
            "id": "facebook/top_v2",
            "name": "TOP",
            "access": "Approval Required", 
            "priority": "High",
            "target_samples": 5000
        },
        {
            "id": "multi_woz_v22",
            "name": "MultiWOZ",
            "access": "Approval Required",
            "priority": "High", 
            "target_samples": 10000
        }
    ]
    
    # Test results
    successful = []
    failed = []
    total_available_samples = 0
    
    # Get HF token
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        print(f"🔑 HF Token: ✅ Found")
    else:
        print(f"🔑 HF Token: ⚠️ Not found (some datasets may fail)")
    
    print(f"\n📊 Testing {len(datasets_to_test)} datasets...\n")
    
    for dataset_info in datasets_to_test:
        dataset_id = dataset_info["id"]
        name = dataset_info["name"]
        access = dataset_info["access"]
        priority = dataset_info["priority"]
        target_samples = dataset_info["target_samples"]
        
        print(f"🔍 {name} ({dataset_id})")
        print(f"   Access: {access}, Priority: {priority}")
        
        try:
            # Try to load dataset
            config = dataset_info.get("config")
            if hf_token:
                if config:
                    dataset = load_dataset(dataset_id, config, use_auth_token=hf_token)
                else:
                    dataset = load_dataset(dataset_id, use_auth_token=hf_token)
            else:
                if config:
                    dataset = load_dataset(dataset_id, config)
                else:
                    dataset = load_dataset(dataset_id)
            
            # Get dataset info
            splits = list(dataset.keys())
            total_size = sum(len(dataset[split]) for split in splits)
            
            print(f"   ✅ SUCCESS")
            print(f"   Splits: {splits}")
            print(f"   Total size: {total_size:,} examples")
            print(f"   Target samples: {target_samples:,}")
            
            successful.append({
                "name": name,
                "id": dataset_id,
                "size": total_size,
                "target": target_samples,
                "priority": priority
            })
            
            total_available_samples += min(total_size, target_samples)
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ FAILED: {error_msg}")
            
            # Categorize error
            if "doesn't exist" in error_msg or "not found" in error_msg:
                error_type = "Dataset not found"
            elif "private" in error_msg or "permission" in error_msg or "authentication" in error_msg:
                error_type = "Access denied (approval required)"
            else:
                error_type = "Unknown error"
            
            failed.append({
                "name": name,
                "id": dataset_id,
                "error": error_type,
                "priority": priority,
                "target": target_samples
            })
        
        print()
    
    # Summary
    print("📋 **TEST SUMMARY**")
    print("=" * 50)
    
    print(f"✅ **Successful Datasets ({len(successful)}):**")
    public_samples = 0
    for dataset in successful:
        print(f"   • {dataset['name']}: {dataset['size']:,} examples (target: {dataset['target']:,})")
        public_samples += min(dataset['size'], dataset['target'])
    
    print(f"\n❌ **Failed Datasets ({len(failed)}):**")
    blocked_samples = 0
    for dataset in failed:
        print(f"   • {dataset['name']}: {dataset['error']} (target: {dataset['target']:,})")
        blocked_samples += dataset['target']
    
    print(f"\n📊 **Dataset Availability:**")
    print(f"   Available samples: {public_samples:,}")
    print(f"   Blocked samples: {blocked_samples:,}")
    print(f"   Total potential: {public_samples + blocked_samples:,}")
    print(f"   Coverage: {(public_samples / (public_samples + blocked_samples)) * 100:.1f}%")
    
    # Recommendations
    print(f"\n💡 **Recommendations:**")
    
    if public_samples >= 50000:
        print(f"   🎯 EXCELLENT: {public_samples:,} samples available")
        print(f"   You can build a high-quality 50K+ dataset immediately!")
        
    elif public_samples >= 30000:
        print(f"   ✅ GOOD: {public_samples:,} samples available") 
        print(f"   Sufficient for initial training. Consider requesting approvals for more.")
        
    else:
        print(f"   ⚠️ LIMITED: Only {public_samples:,} samples available")
        print(f"   Recommend requesting dataset approvals before training.")
    
    # High priority failed datasets
    high_priority_failed = [d for d in failed if d['priority'] in ['Very High', 'High']]
    if high_priority_failed:
        print(f"\n🔐 **Priority Approval Requests:**")
        for dataset in high_priority_failed:
            print(f"   1. {dataset['name']} ({dataset['priority']} priority)")
            print(f"      → https://huggingface.co/datasets/{dataset['id']}")
    
    # Next steps
    print(f"\n🚀 **Next Steps:**")
    
    if public_samples >= 30000:
        print(f"   1. ✅ Build initial dataset with available sources")
        print(f"   2. 🚀 Start training on Google Colab")
        print(f"   3. 🔐 Request approvals for premium datasets")
        print(f"   4. 📈 Retrain with larger dataset when approved")
        
        print(f"\n💻 **Build Command:**")
        print(f"   python scripts/prepare_massive_dataset.py \\")
        print(f"     --hf-token YOUR_TOKEN \\")
        print(f"     --target-size {min(public_samples, 100000)} \\")
        print(f"     --repo-name mcp-memory-auto-trigger-dataset")
        
    else:
        print(f"   1. 🔐 Request approvals for high-priority datasets")
        print(f"   2. ⏳ Wait for approval (usually 1-3 days)")
        print(f"   3. 🔄 Re-run this test script")
        print(f"   4. 📊 Build complete dataset when ready")
    
    return len(successful) > 0


def main():
    """Main execution"""
    
    print("This script tests access to all datasets needed for training.\n")
    
    # Check if HF token is set
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("⚠️ Warning: HF_TOKEN environment variable not set")
        print("Some datasets may require authentication.")
        print("Set token with: export HF_TOKEN='your_token_here'")
        print()
    
    try:
        success = test_dataset_access()
        
        if success:
            print("\n🎉 **Ready to build dataset!**")
            print("At least some datasets are accessible.")
        else:
            print("\n❌ **No datasets accessible**")
            print("Check your internet connection and HF token.")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
