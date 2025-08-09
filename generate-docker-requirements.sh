#!/bin/bash

# =============================================================================
# Generate requirements.txt from .myenv for Docker
# =============================================================================

echo "🐳 Generating Docker requirements.txt from .myenv"
echo "================================================="

# Check if .myenv exists
if [ ! -d ".myenv" ]; then
    echo "❌ .myenv virtual environment not found!"
    echo "   Please create it first with: python -m venv .myenv"
    echo "   Then install dependencies and run this script"
    exit 1
fi

# Check if .myenv/bin/pip exists
if [ ! -f ".myenv/bin/pip" ]; then
    echo "❌ .myenv/bin/pip not found!"
    echo "   Virtual environment seems incomplete"
    exit 1
fi

echo "✅ Found .myenv virtual environment"

# Generate requirements.txt
echo "📦 Generating requirements.txt from .myenv packages..."

# Get all installed packages with exact versions using python -m pip
.myenv/bin/python -m pip freeze > requirements_temp.txt

# Filter and format for Docker
echo "# =============================================================================" > requirements.txt
echo "# MCP Memory Server - Docker Requirements (Generated from .myenv)" >> requirements.txt
echo "# Generated on: $(date)" >> requirements.txt
echo "# =============================================================================" >> requirements.txt
echo "" >> requirements.txt

# Add packages, filtering out unnecessary ones
grep -v "^-e " requirements_temp.txt | \
grep -v "^pkg-resources" | \
grep -v "^setuptools" | \
grep -v "^wheel" | \
sort >> requirements.txt

# Clean up
rm requirements_temp.txt

# Show results
echo ""
echo "✅ requirements.txt generated successfully!"
echo "📄 Generated $(grep -v "^#" requirements.txt | grep -v "^$" | wc -l) package dependencies"
echo ""
echo "📋 First 10 packages:"
grep -v "^#" requirements.txt | grep -v "^$" | head -10

echo ""
echo "🐳 Ready for Docker build!"
echo "   Next: docker-compose build"
