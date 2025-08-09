#!/usr/bin/env python3
"""
Auto-download models on first use
This ensures the repository works immediately without large model files
"""

import os
import sys
from pathlib import Path

def ensure_model_downloaded(model_name="all-MiniLM-L6-v2"):
    """Ensure model is downloaded and available"""
    models_dir = Path(__file__).parent
    model_path = models_dir / model_name
    
    # Check if model already exists
    if model_path.exists() and any(model_path.iterdir()):
        print(f"✅ Model {model_name} already available")
        return str(model_path)
    
    print(f"📥 Downloading model {model_name}...")
    print("⏳ This may take a few minutes on first run...")
    
    try:
        # Import here to avoid issues if not installed
        from sentence_transformers import SentenceTransformer
        
        # Download model
        model = SentenceTransformer(model_name)
        
        # Save to local path
        model.save(str(model_path))
        
        print(f"✅ Model downloaded and saved to {model_path}")
        return str(model_path)
        
    except ImportError:
        print("⚠️  Installing sentence-transformers...")
        os.system(f"{sys.executable} -m pip install sentence-transformers")
        
        # Try again
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        model.save(str(model_path))
        
        return str(model_path)
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("💡 Using fallback: model will download to cache")
        return model_name  # Return original name for cache download

if __name__ == "__main__":
    ensure_model_downloaded()
