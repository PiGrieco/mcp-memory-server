#!/bin/bash

# =============================================================================
# MCP Memory Server - Production Setup Script
# =============================================================================

echo "🧠 MCP Memory Server - Production Setup"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .myenv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .myenv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
python -m pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your MongoDB credentials."
    echo "   See README.md for configuration details."
else
    echo "✅ .env file found"
fi

# Test installation
echo "🧪 Testing installation..."
python comprehensive_test.py

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your .env file with MongoDB credentials"
echo "2. Add MCP server configuration to Cursor IDE"
echo "3. Restart Cursor IDE"
echo "4. Test with: python comprehensive_test.py"
echo ""
echo "🚀 Your MCP Memory Server is ready for production!"
