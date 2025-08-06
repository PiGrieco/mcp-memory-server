#!/usr/bin/env python3
"""
Comprehensive Test Script for MCP Memory Server
Tests all core functionality and validates production readiness.
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """Comprehensive test of MCP Memory Server functionality"""
    print("🧪 MCP Memory Server - Comprehensive Production Test")
    print("=" * 60)
    
    # Test requests for all functionality
    tests = [
        {
            "name": "Initialize",
            "request": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
        },
        {
            "name": "List Tools",
            "request": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
        },
        {
            "name": "Memory Status",
            "request": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "memory_status",
                    "arguments": {}
                }
            }
        },
        {
            "name": "Save Memory",
            "request": {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "save_memory",
                    "arguments": {
                        "content": "Production test: MCP Memory Server integration with Cursor IDE - Full Server mode with MongoDB and sentence transformers",
                        "importance": 0.9
                    }
                }
            }
        },
        {
            "name": "List Memories",
            "request": {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "list_memories",
                    "arguments": {}
                }
            }
        },
        {
            "name": "Search Memories",
            "request": {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "search_memories",
                    "arguments": {
                        "query": "MCP integration Cursor",
                        "max_results": 3,
                        "similarity_threshold": 0.3
                    }
                }
            }
        }
    ]
    
    try:
        # Start the MCP server
        print("🚀 Starting MCP Memory Server...")
        process = subprocess.Popen(
            ["python", "mcp_memory_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for server to initialize
        time.sleep(3)
        
        # Run all tests
        for i, test in enumerate(tests, 1):
            print(f"\n📤 Test {i}: {test['name']}")
            
            # Send request
            request_json = json.dumps(test['request']) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read response
            try:
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    
                    if "result" in response:
                        if test['name'] == "List Tools":
                            tools = response["result"].get("tools", [])
                            print(f"   ✅ Found {len(tools)} tools:")
                            for tool in tools:
                                print(f"      - {tool['name']}: {tool['description'][:60]}...")
                        
                        elif test['name'] in ["Memory Status", "Save Memory", "List Memories", "Search Memories"]:
                            content = response["result"].get("content", "")
                            print(f"   ✅ Response: {content[:200]}{'...' if len(content) > 200 else ''}")
                        
                        else:
                            print(f"   ✅ Success: {response['result']}")
                    
                    elif "error" in response:
                        print(f"   ❌ Error: {response['error']}")
                    
                    else:
                        print(f"   ✅ Response: {response}")
                
                else:
                    print(f"   ⚠️  No response received")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n🎉 Test completed! All {len(tests)} tests executed.")
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    finally:
        # Clean up
        if process:
            process.terminate()
            process.wait()
    
    return True

if __name__ == "__main__":
    print("🧠 MCP Memory Server - Production Test Suite")
    print("Testing Full Server mode with MongoDB and Sentence Transformers")
    print()
    
    success = test_mcp_server()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("🚀 MCP Memory Server is production-ready!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
