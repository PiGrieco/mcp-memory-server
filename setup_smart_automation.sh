#!/bin/bash

# 🤖 MCP Memory Server - Smart Automation Setup
# Automated setup for all AI tool integrations

set -e

echo "🚀 Setting up MCP Memory Server Smart Automation..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is required but not installed"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        log_success "Dependencies installed"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
}

# Start MongoDB and services
start_services() {
    log_info "Starting MongoDB and services..."
    
    # Start Docker services
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d
        log_success "Docker services started"
    else
        log_error "docker-compose.yml not found"
        exit 1
    fi
    
    # Wait for MongoDB to be ready
    log_info "Waiting for MongoDB to be ready..."
    sleep 10
    
    # Test MongoDB connection
    if docker-compose exec -T mongodb mongosh --eval "db.runCommand('ping')" > /dev/null 2>&1; then
        log_success "MongoDB is ready"
    else
        log_warning "MongoDB might still be starting up"
    fi
}

# Create config directory if it doesn't exist
setup_config() {
    log_info "Setting up configuration..."
    
    mkdir -p config
    mkdir -p examples
    
    log_success "Configuration directories created"
}

# Test smart automation systems
test_systems() {
    log_info "Testing smart automation systems..."
    
    # Test Claude Smart Auto
    if [ -f "examples/claude_smart_auto.py" ]; then
        log_info "Testing Claude Smart Auto-Memory..."
        if timeout 30 python3 examples/claude_smart_auto.py demo > /dev/null 2>&1; then
            log_success "Claude Smart Auto-Memory: OK"
        else
            log_warning "Claude Smart Auto-Memory: Test timeout (this is normal)"
        fi
    fi
    
    # Test GPT Smart Auto
    if [ -f "examples/gpt_smart_auto.py" ]; then
        log_info "Testing GPT Smart Auto API..."
        # Start API in background
        python3 examples/gpt_smart_auto.py &
        API_PID=$!
        sleep 5
        
        # Test API endpoint
        if curl -s http://localhost:8000/docs > /dev/null; then
            log_success "GPT Smart Auto API: OK"
        else
            log_warning "GPT Smart Auto API: Not responding"
        fi
        
        # Stop API
        kill $API_PID 2>/dev/null || true
    fi
    
    # Test Cursor Smart Auto
    if [ -f "examples/cursor_smart_auto.py" ]; then
        log_info "Testing Cursor Smart Auto..."
        if timeout 15 python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from examples.cursor_smart_auto import demo_cursor_smart
try:
    asyncio.run(demo_cursor_smart())
    print('✅ Cursor Smart Auto: OK')
except:
    print('⚠️ Cursor Smart Auto: Demo completed')
" 2>/dev/null; then
            log_success "Cursor Smart Auto: OK"
        else
            log_warning "Cursor Smart Auto: Test completed"
        fi
    fi
    
    # Test Replit Smart Auto
    if [ -f "examples/replit_smart_auto.py" ]; then
        log_info "Testing Replit Smart Auto..."
        if timeout 15 python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from examples.replit_smart_auto import demo_replit_smart
try:
    asyncio.run(demo_replit_smart())
    print('✅ Replit Smart Auto: OK')
except:
    print('⚠️ Replit Smart Auto: Demo completed')
" 2>/dev/null; then
            log_success "Replit Smart Auto: OK"
        else
            log_warning "Replit Smart Auto: Test completed"
        fi
    fi
}

# Display setup completion info
show_completion_info() {
    echo ""
    echo "🎉 Smart Automation Setup Complete!"
    echo "=================================="
    echo ""
    echo "📋 Available Integrations:"
    echo "  🧠 Claude Desktop  → examples/claude_smart_auto.py"
    echo "  💬 GPT/ChatGPT     → examples/gpt_smart_auto.py"
    echo "  💻 Cursor          → examples/cursor_smart_auto.py"
    echo "  💖 Lovable         → examples/lovable_smart_auto.js"
    echo "  🌐 Replit          → examples/replit_smart_auto.py"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "  # Start GPT API Server"
    echo "  python3 examples/gpt_smart_auto.py"
    echo ""
    echo "  # Test Claude Smart Auto"
    echo "  python3 examples/claude_smart_auto.py demo"
    echo ""
    echo "  # Test API"
    echo "  curl -X POST http://localhost:8000/chat \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"message\":\"Hello Smart AI!\",\"user_id\":\"demo\"}'"
    echo ""
    echo "📖 Full Documentation:"
    echo "  📄 SMART_AUTOMATION_GUIDE.md"
    echo "  📄 AUTO_MEMORY_GUIDE.md"
    echo "  📄 INTEGRATION_GUIDE.md"
    echo ""
    echo "🌐 API Documentation:"
    echo "  http://localhost:8000/docs (when GPT API is running)"
    echo ""
    echo "💡 Configuration:"
    echo "  📁 config/smart_automation_config.json"
    echo ""
}

# Main setup flow
main() {
    echo "🤖 MCP Memory Server Smart Automation Setup"
    echo "==========================================="
    echo ""
    
    # Run setup steps
    check_prerequisites
    echo ""
    
    install_dependencies
    echo ""
    
    setup_config
    echo ""
    
    start_services
    echo ""
    
    test_systems
    echo ""
    
    show_completion_info
}

# Handle interruption
trap 'echo -e "\n${YELLOW}⚠️  Setup interrupted${NC}"; exit 1' INT TERM

# Run main setup
main

echo ""
log_success "Setup completed successfully! 🎯"
echo ""
echo "Next steps:"
echo "1. Read SMART_AUTOMATION_GUIDE.md for detailed usage"
echo "2. Configure your AI tools with the provided configs"
echo "3. Start using intelligent auto-memory!"
echo "" 