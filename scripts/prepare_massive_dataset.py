#!/usr/bin/env python3
"""
Prepare Massive Dataset for Hugging Face
Creates 100K+ dataset from multiple sources and uploads to HF Hub
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.comprehensive_dataset_builder import build_and_upload_massive_dataset
from src.utils.logging import get_logger

logger = get_logger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(description="Prepare massive dataset for training")
    
    parser.add_argument(
        "--hf-token",
        type=str,
        required=True,
        help="Hugging Face token for dataset upload"
    )
    
    parser.add_argument(
        "--target-size",
        type=int,
        default=100000,
        help="Target number of examples (default: 100,000)"
    )
    
    parser.add_argument(
        "--repo-name",
        type=str,
        default="mcp-memory-auto-trigger-dataset",
        help="Repository name on Hugging Face"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show configuration without building dataset"
    )
    
    return parser.parse_args()


async def main():
    """Main execution function"""
    
    args = parse_arguments()
    
    print("📊 **MASSIVE DATASET PREPARATION**")
    print("=" * 50)
    
    print(f"🎯 Configuration:")
    print(f"   Target size: {args.target_size:,} examples")
    print(f"   Repository: pigrieco/{args.repo_name}")
    print(f"   HF Token: {'✅ Provided' if args.hf_token else '❌ Missing'}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - Configuration shown, exiting")
        return
    
    try:
        print(f"\n🚀 Building and uploading dataset...")
        
        repo_id = await build_and_upload_massive_dataset(
            hf_token=args.hf_token,
            target_size=args.target_size,
            repo_name=args.repo_name
        )
        
        print(f"\n🎉 SUCCESS!")
        print(f"   Dataset uploaded to: https://huggingface.co/datasets/{repo_id}")
        print(f"   Ready for training on Google Colab!")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Open Google Colab with A100 GPU")
        print(f"   2. Upload the training notebook")
        print(f"   3. Set dataset_repo = '{repo_id}' in config")
        print(f"   4. Run training (~3-4 hours)")
        print(f"   5. Deploy trained model to Hugging Face")
        
    except Exception as e:
        logger.error(f"Dataset preparation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
