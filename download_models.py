#!/usr/bin/env python3
"""
Download and cache models for offline usage
This script pre-downloads the sentence transformer model for faster startup
"""

import os
import sys
from pathlib import Path

def download_models():
    """Download models for offline usage"""
    print("🚀 MCP Memory Server - Model Download")
    print("=" * 50)
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    try:
        print("📦 Installing required packages...")
        os.system(f"{sys.executable} -m pip install sentence-transformers torch")
        
        print("\n📥 Downloading sentence transformer model...")
        from sentence_transformers import SentenceTransformer
        
        # Download the model
        model_name = 'all-MiniLM-L6-v2'
        print(f"⬇️  Downloading {model_name}...")
        model = SentenceTransformer(model_name)
        
        # Save to models directory
        model_path = models_dir / model_name
        print(f"💾 Saving to {model_path}...")
        model.save(str(model_path))
        
        print(f"\n✅ SUCCESS!")
        print(f"📁 Model saved to: {model_path.absolute()}")
        print(f"📏 Model size: {get_dir_size(model_path):.1f} MB")
        print("\n🎯 Benefits:")
        print("   • Faster startup (no download needed)")
        print("   • Offline usage")
        print("   • Consistent model version")
        
        return True
        
    except ImportError as e:
        print(f"\n⚠️  Import Error: {e}")
        print("💡 Installing dependencies...")
        os.system(f"{sys.executable} -m pip install sentence-transformers torch")
        return False
        
    except Exception as e:
        print(f"\n❌ Error downloading model: {e}")
        print("💡 Model will be downloaded automatically on first use.")
        return False

def get_dir_size(path):
    """Get directory size in MB"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)  # Convert to MB
    except:
        return 0

def create_model_info():
    """Create model info file"""
    info_content = """# Pre-downloaded Models

This directory contains pre-downloaded machine learning models for the MCP Memory Server.

## Included Models:

### all-MiniLM-L6-v2
- **Purpose**: Semantic similarity and text embeddings
- **Size**: ~80MB
- **Source**: sentence-transformers/all-MiniLM-L6-v2
- **License**: Apache 2.0

## Benefits:
- ✅ **Faster startup** - No download needed on first run
- ✅ **Offline usage** - Works without internet connection
- ✅ **Consistent version** - Same model for all users
- ✅ **Better UX** - Immediate functionality

## Automatic Fallback:
If models are missing, the server will automatically download them on first use.
"""
    
    with open("models/README.md", "w") as f:
        f.write(info_content)

if __name__ == "__main__":
    success = download_models()
    create_model_info()
    
    if success:
        print("\n🎉 Models ready! Repository size will be larger but startup will be faster.")
    else:
        print("\n⚠️  Model download failed. Server will download on first use.")
    
    print("\n🚀 Ready to commit to repository!")
