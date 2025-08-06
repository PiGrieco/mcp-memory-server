#!/usr/bin/env python3
"""
Simple test script to debug embedding service issues
"""
import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path for proper imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def test_embedding_service():
    """Test the embedding service directly"""
    try:
        print("Testing embedding service...")
        
        # Import and initialize
        from src.services.embedding_service import embedding_service
        print("✅ Imported embedding service")
        
        # Initialize
        print("Initializing embedding service...")
        await embedding_service.initialize()
        print("✅ Embedding service initialized")
        
        # Test embedding generation
        print("Generating test embedding...")
        test_text = "This is a test for embedding generation"
        embedding = await embedding_service.generate_embedding(test_text)
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        print(f"First 5 values: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_embedding_service())
    sys.exit(0 if success else 1)
