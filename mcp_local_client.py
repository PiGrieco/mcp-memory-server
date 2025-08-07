#!/usr/bin/env python3
"""
Local MCP HTTP Client for Cursor
This script acts as a bridge between Cursor (stdio) and the HTTP server
"""

import sys
import json
import requests
import logging

# Configure logging to be quiet
logging.basicConfig(level=logging.ERROR)

# Server configuration
SERVER_URL = "http://localhost:8000/mcp"
REQUEST_TIMEOUT = 10

def send_request(request_data):
    """Send request to local HTTP server"""
    try:
        response = requests.post(
            SERVER_URL,
            json=request_data,
            timeout=REQUEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "error": {
                "code": -32603,
                "message": f"HTTP server error: {str(e)}"
            }
        }

def main():
    """Main loop - read from stdin, send to HTTP server, write to stdout"""
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request_data = json.loads(line)
                response = send_request(request_data)
                
                if response is not None:
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.stderr.write(f"Fatal error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
