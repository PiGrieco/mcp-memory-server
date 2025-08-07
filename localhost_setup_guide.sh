#!/bin/bash

# 🏠 MCP Memory Server - Localhost Setup & Testing Guide

echo "🏠 MCP Memory Server - Localhost Configuration"
echo "============================================="

# Start the local server
echo ""
echo "🚀 STEP 1: Start Local Server"
echo "------------------------------"
echo "Run this command in a separate terminal:"
echo ""
echo "python mcp_memory_server_http.py"
echo ""
echo "Or with specific host/port:"
echo "python mcp_memory_server_http.py --host localhost --port 8000"
echo ""

# Cursor Configuration
echo "🔧 STEP 2: Cursor Configuration"
echo "--------------------------------"
echo "Use this configuration in your Cursor mcp.json:"
echo ""
cat << 'EOF'
{
  "mcpServers": {
    "memory-server": {
      "transport": "http",
      "url": "http://localhost:8000/mcp",
      "timeout": 30000,
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
EOF
echo ""

# Test Commands
echo "🧪 STEP 3: Test Commands"
echo "-------------------------"
echo ""

echo "1. Test Server Health:"
echo "curl http://localhost:8000/health"
echo ""

echo "2. Test MCP Tools List:"
echo 'curl -X POST http://localhost:8000/mcp \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'\'
echo ""

echo "3. Test Memory Status:"
echo 'curl -X POST http://localhost:8000/mcp \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{'
echo '    "jsonrpc": "2.0",'
echo '    "id": 2,'
echo '    "method": "tools/call",'
echo '    "params": {'
echo '      "name": "memory_status"'
echo '    }'
echo '  }'\'''
echo ""

echo "4. Test Save Memory:"
echo 'curl -X POST http://localhost:8000/mcp \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{'
echo '    "jsonrpc": "2.0",'
echo '    "id": 3,'
echo '    "method": "tools/call",'
echo '    "params": {'
echo '      "name": "save_memory",'
echo '      "arguments": {'
echo '        "content": "Testing localhost MCP Memory Server setup",'
echo '        "metadata": {"source": "localhost_test"}'
echo '      }'
echo '    }'
echo '  }'\'''
echo ""

echo "5. Test Search Memories:"
echo 'curl -X POST http://localhost:8000/mcp \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{'
echo '    "jsonrpc": "2.0",'
echo '    "id": 4,'
echo '    "method": "tools/call",'
echo '    "params": {'
echo '      "name": "search_memories",'
echo '      "arguments": {'
echo '        "query": "localhost test",'
echo '        "max_results": 5'
echo '      }'
echo '    }'
echo '  }'\'''
echo ""

echo "6. Test List Memories:"
echo 'curl -X POST http://localhost:8000/mcp \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{'
echo '    "jsonrpc": "2.0",'
echo '    "id": 5,'
echo '    "method": "tools/call",'
echo '    "params": {'
echo '      "name": "list_memories",'
echo '      "arguments": {'
echo '        "limit": 10'
echo '      }'
echo '    }'
echo '  }'\'''
echo ""

echo "✅ VERIFICATION"
echo "---------------"
echo "Expected responses:"
echo "• Health check: {\"status\": \"healthy\", ...}"
echo "• Tools list: {\"result\": {\"tools\": [...]}}"
echo "• Memory status: Shows database connection and memory count"
echo "• Save memory: Returns memory ID"
echo "• Search/List: Returns memory arrays with content"
echo ""

echo "🎯 NEXT STEPS"
echo "-------------"
echo "1. Start the server: python mcp_memory_server_http.py"
echo "2. Run health check: curl http://localhost:8000/health"
echo "3. Update Cursor config with localhost URL"
echo "4. Restart Cursor IDE"
echo "5. Test memory tools in Cursor chat"
