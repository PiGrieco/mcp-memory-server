#!/bin/bash

echo "🚀 Downloading pre-trained models for MCP Memory Server"
echo "======================================================="

# Create models directory structure
mkdir -p models/all-MiniLM-L6-v2

echo "📥 Downloading all-MiniLM-L6-v2 model files..."

# Model files to download
declare -a files=(
    "config.json"
    "config_sentence_transformers.json" 
    "model.safetensors"
    "modules.json"
    "sentence_bert_config.json"
    "special_tokens_map.json"
    "tokenizer.json"
    "tokenizer_config.json"
    "vocab.txt"
    "README.md"
    "1_Pooling/config.json"
)

# Base URL for HuggingFace model
BASE_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main"

# Download each file
for file in "${files[@]}"; do
    echo "⬇️  Downloading $file..."
    
    # Create directory if needed (for pooling config)
    if [[ "$file" == *"/"* ]]; then
        mkdir -p "models/all-MiniLM-L6-v2/$(dirname "$file")"
    fi
    
    # Download file
    curl -L -o "models/all-MiniLM-L6-v2/$file" "$BASE_URL/$file"
    
    if [ $? -eq 0 ]; then
        echo "✅ Downloaded $file"
    else
        echo "❌ Failed to download $file"
    fi
done

echo ""
echo "📊 Model download summary:"
echo "📁 Location: $(pwd)/models/all-MiniLM-L6-v2"
echo "📏 Size: $(du -sh models/ 2>/dev/null | cut -f1 || echo "Unknown")"
echo "🎯 Purpose: Semantic embeddings for intelligent memory search"

# Create model info file
cat > models/all-MiniLM-L6-v2/MODEL_INFO.md << 'EOF'
# all-MiniLM-L6-v2 Model

**Source:** sentence-transformers/all-MiniLM-L6-v2  
**Purpose:** Generate semantic embeddings for text similarity  
**Size:** ~80MB  
**License:** Apache 2.0  

## Usage:
This model is used by the MCP Memory Server to create semantic embeddings 
for intelligent memory search and auto-trigger functionality.

## Benefits of Pre-Download:
- ✅ Faster startup time
- ✅ Offline functionality  
- ✅ Consistent model version
- ✅ No internet required after first setup
EOF

echo ""
echo "✅ Model download complete!"
echo "🚀 Repository ready with pre-downloaded models"
echo "💡 Benefits: Faster startup, offline usage, better UX"
