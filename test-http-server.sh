#!/bin/bash

# =============================================================================
# Test HTTP MCP Memory Server
# =============================================================================

echo "🧪 Testing HTTP MCP Memory Server"
echo "================================="

SERVER_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() { echo -e "${BLUE}🔍 Test: $1${NC}"; }
print_pass() { echo -e "${GREEN}✅ $1${NC}"; }
print_fail() { echo -e "${RED}❌ $1${NC}"; }

# Test 1: Health Check
print_test "Health Check"
if curl -s -f "${SERVER_URL}/health" > /dev/null; then
    print_pass "Health check passed"
    curl -s "${SERVER_URL}/health" | python3 -m json.tool
else
    print_fail "Health check failed"
fi

echo ""

# Test 2: Server Info
print_test "Server Info"
if curl -s -f "${SERVER_URL}/info" > /dev/null; then
    print_pass "Server info retrieved"
    curl -s "${SERVER_URL}/info" | python3 -m json.tool
else
    print_fail "Server info failed"
fi

echo ""

# Test 3: MCP Initialize
print_test "MCP Initialize"
response=$(curl -s -X POST "${SERVER_URL}/mcp" \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
  }')

if echo "$response" | grep -q '"result"'; then
    print_pass "MCP Initialize successful"
    echo "$response" | python3 -m json.tool
else
    print_fail "MCP Initialize failed"
    echo "$response"
fi

echo ""

# Test 4: List Tools
print_test "List Tools"
response=$(curl -s -X POST "${SERVER_URL}/mcp" \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }')

if echo "$response" | grep -q '"tools"'; then
    print_pass "Tools list retrieved"
    echo "$response" | python3 -c "
import json, sys
data = json.load(sys.stdin)
tools = data.get('result', {}).get('tools', [])
print(f'Found {len(tools)} tools:')
for tool in tools:
    print(f'  - {tool[\"name\"]}: {tool[\"description\"]}')
"
else
    print_fail "Tools list failed"
    echo "$response"
fi

echo ""

# Test 5: Save Memory
print_test "Save Memory"
response=$(curl -s -X POST "${SERVER_URL}/mcp" \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "save_memory",
      "arguments": {
        "content": "HTTP test memory - remote server deployment successful",
        "importance": 0.9
      }
    }
  }')

if echo "$response" | grep -q '"result"'; then
    print_pass "Memory saved successfully"
    echo "$response" | python3 -m json.tool
else
    print_fail "Save memory failed"
    echo "$response"
fi

echo ""

# Test 6: List Memories
print_test "List Memories"
response=$(curl -s -X POST "${SERVER_URL}/mcp" \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "list_memories",
      "arguments": {}
    }
  }')

if echo "$response" | grep -q '"result"'; then
    print_pass "Memories listed successfully"
    echo "$response" | python3 -c "
import json, sys
data = json.load(sys.stdin)
content = data.get('result', {}).get('content', '')
print(content)
"
else
    print_fail "List memories failed"
    echo "$response"
fi

echo ""

# Test 7: Search Memories
print_test "Search Memories"
response=$(curl -s -X POST "${SERVER_URL}/mcp" \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "search_memories",
      "arguments": {
        "query": "HTTP test",
        "max_results": 3
      }
    }
  }')

if echo "$response" | grep -q '"result"'; then
    print_pass "Memory search successful"
    echo "$response" | python3 -m json.tool
else
    print_fail "Memory search failed"
    echo "$response"
fi

echo ""

# Test 8: Memory Status
print_test "Memory Status"
response=$(curl -s -X POST "${SERVER_URL}/mcp" \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "memory_status",
      "arguments": {}
    }
  }')

if echo "$response" | grep -q '"result"'; then
    print_pass "Memory status retrieved"
    echo "$response" | python3 -c "
import json, sys
data = json.load(sys.stdin)
content = data.get('result', {}).get('content', '')
print(content)
"
else
    print_fail "Memory status failed"
    echo "$response"
fi

echo ""
echo "🎉 HTTP MCP Memory Server testing completed!"
echo ""
echo "📋 Next steps:"
echo "1. Configure Cursor IDE with the HTTP endpoint"
echo "2. Test from Cursor IDE"
echo "3. Deploy to remote server if needed"
