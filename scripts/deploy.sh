#!/bin/bash

# MCP Memory Server - Quick Deployment Script
# Deploy the complete system with one command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🚀 MCP Memory Server - Quick Deployment"
echo "======================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️ No .env file found. Creating from template...${NC}"
    cp config/env.example .env
    echo -e "${GREEN}✅ .env file created from template${NC}"
    echo -e "${YELLOW}📝 Please edit .env file with your configuration before continuing${NC}"
    echo -e "${YELLOW}   Or press Enter to continue with default values${NC}"
    read -p "Press Enter to continue..."
fi

# Check prerequisites
echo -e "\n${BLUE}🔍 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"

# Create necessary directories
echo -e "\n${BLUE}📁 Creating directories...${NC}"
mkdir -p deployment/docker/logs
mkdir -p deployment/docker/data
mkdir -p deployment/docker/exports
mkdir -p deployment/docker/backups
mkdir -p deployment/docker/mongo-init

# Create MongoDB initialization script
echo -e "\n${BLUE}🗄️ Setting up MongoDB...${NC}"
cat > deployment/docker/mongo-init/init.js << 'EOF'
db = db.getSiblingDB('mcp_memory_production');

// Create collections
db.createCollection('memories');
db.createCollection('analytics');
db.createCollection('backups');

// Create indexes
db.memories.createIndex({ "content": "text" });
db.memories.createIndex({ "project": 1 });
db.memories.createIndex({ "created_at": -1 });
db.memories.createIndex({ "user_id": 1 });

// Create user for the application
db.createUser({
  user: "mcp_user",
  pwd: "mcp_password",
  roles: [
    { role: "readWrite", db: "mcp_memory_production" }
  ]
});

print("MongoDB initialization completed");
EOF

echo -e "${GREEN}✅ MongoDB setup completed${NC}"

# Deploy with Docker Compose
echo -e "\n${BLUE}🐳 Starting deployment...${NC}"
cd deployment/docker

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service status
echo -e "\n${BLUE}📊 Service Status:${NC}"
docker-compose ps

echo -e "\n${BLUE}🔍 Health Checks:${NC}"

# Check MongoDB
if docker-compose ps mongodb | grep -q "Up"; then
    echo -e "${GREEN}✅ MongoDB: Running${NC}"
else
    echo -e "${RED}❌ MongoDB: Not running${NC}"
fi

# Check Redis
if docker-compose ps redis | grep -q "Up"; then
    echo -e "${GREEN}✅ Redis: Running${NC}"
else
    echo -e "${RED}❌ Redis: Not running${NC}"
fi

# Check MCP Server
if docker-compose ps mcp-memory-server | grep -q "Up"; then
    echo -e "${GREEN}✅ MCP Server: Running${NC}"
    # Test HTTP endpoint
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ HTTP API: Responding${NC}"
    else
        echo -e "${YELLOW}⚠️ HTTP API: Not responding yet (may take a few minutes)${NC}"
    fi
else
    echo -e "${RED}❌ MCP Server: Not running${NC}"
fi

echo -e "\n${GREEN}🎉 DEPLOYMENT COMPLETED!${NC}"
echo "================================"

echo -e "\n${BLUE}🌐 Access Points:${NC}"
echo -e "  • MCP Server: http://localhost:8000"
echo -e "  • API Docs: http://localhost:8000/docs"
echo -e "  • Health Check: http://localhost:8000/health"
echo -e "  • MongoDB: localhost:27017"
echo -e "  • Redis: localhost:6379"

echo -e "\n${BLUE}🔧 Management Commands:${NC}"
echo -e "  • View logs: docker-compose logs -f"
echo -e "  • Stop services: docker-compose down"
echo -e "  • Restart services: docker-compose restart"
echo -e "  • View status: docker-compose ps"

echo -e "\n${BLUE}📝 Next Steps:${NC}"
echo -e "  1. Test the API: curl http://localhost:8000/health"
echo -e "  2. Check logs: docker-compose logs mcp-memory-server"
echo -e "  3. Configure your IDE (Cursor/Claude) to use the MCP server"
echo -e "  4. Monitor performance: docker stats"

echo -e "\n${GREEN}✅ Your MCP Memory Server is ready! 🧠✨${NC}" 