#!/usr/bin/env python3
"""
Test script to verify MCP Memory Server is working
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """Test the MCP server with basic commands"""
    
    print("🧪 Testing MCP Memory Server...")
    
    # Test 1: Initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    # Test 2: List tools request
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }

    # Test 3: List memories request
    list_memories_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "list_memories",
            "arguments": {}
        }
    }

    # Test 4: Memory status request
    memory_status_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "memory_status",
            "arguments": {}
        }
    }

    # Test 5: Save a test memory
    save_memory_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "save_memory",
            "arguments": {
                "content": "Test memory for debugging list_memories issue"
            }
        }
    }
    
    try:
        # Start the server process
        print("🚀 Starting MCP server...")
        process = subprocess.Popen(
            [sys.executable, "mcp_memory_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/Users/awais/Desktop/Upworking/Grieco/mcp-memory-server"
        )
        
        # Send initialize request
        print("📤 Sending initialize request...")
        init_json = json.dumps(init_request) + "\n"
        process.stdin.write(init_json)
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize response: {response}")
        
        # Send list tools request
        print("📤 Sending list tools request...")
        tools_json = json.dumps(list_tools_request) + "\n"
        process.stdin.write(tools_json)
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Tools list response:")
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"   Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description']}")
            else:
                print(f"   Response: {response}")

        # Send memory status request
        print("📤 Sending memory status request...")
        status_json = json.dumps(memory_status_request) + "\n"
        process.stdin.write(status_json)
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Memory status response:")
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                print(f"   {content}")
            else:
                print(f"   Response: {response}")

        # Send save memory request
        print("📤 Sending save memory request...")
        save_json = json.dumps(save_memory_request) + "\n"
        process.stdin.write(save_json)
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Save memory response:")
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                print(f"   {content}")
            else:
                print(f"   Response: {response}")

        # Send list memories request AFTER saving
        print("📤 Sending list memories request (after save)...")
        memories_json = json.dumps(list_memories_request) + "\n"
        process.stdin.write(memories_json)
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ List memories response:")
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                print(f"   {content}")
            else:
                print(f"   Response: {response}")
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
        print("🎉 Server test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.terminate()
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
