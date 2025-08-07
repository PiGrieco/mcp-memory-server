#!/usr/bin/env python3
"""
MCP HTTP Bridge - Connects Cursor IDE to Remote MCP Memory Server
Bridges stdio (Cursor) to HTTP (Remote Server)
"""

import sys
import json
import requests
import logging
from typing import Dict, Any, Optional

# Configure logging to suppress unnecessary output
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Remote server configuration
REMOTE_SERVER_URL = "http://134.122.75.246:8000/mcp"
REQUEST_TIMEOUT = 30

class MCPHTTPBridge:
    """Bridge between Cursor IDE (stdio) and Remote MCP Server (HTTP)"""

    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MCP-HTTP-Bridge/1.0'
        })

    def send_request(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send request to remote MCP server"""
        try:
            response = self.session.post(
                self.server_url,
                json=request_data,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            return self.create_error_response(
                request_data.get("id"),
                -32603,
                "Request timeout - remote server not responding"
            )
        except requests.exceptions.ConnectionError:
            return self.create_error_response(
                request_data.get("id"),
                -32603,
                "Connection error - cannot reach remote server"
            )
        except requests.exceptions.HTTPError as e:
            return self.create_error_response(
                request_data.get("id"),
                -32603,
                f"HTTP error: {e}"
            )
        except Exception as e:
            return self.create_error_response(
                request_data.get("id"),
                -32603,
                f"Unexpected error: {str(e)}"
            )

    def create_error_response(self, request_id: Optional[str], code: int, message: str) -> Dict[str, Any]:
        """Create MCP error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def run(self):
        """Main bridge loop - read from stdin, send to HTTP, write to stdout"""
        try:
            # Process each line from Cursor IDE
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse MCP request from Cursor
                    request_data = json.loads(line)

                    # Send to remote server and get response
                    response_data = self.send_request(request_data)

                    if response_data:
                        # Send response back to Cursor
                        print(json.dumps(response_data))
                        sys.stdout.flush()

                except json.JSONDecodeError:
                    # Invalid JSON from Cursor - skip silently
                    continue
                except Exception as e:
                    # Unexpected error - send error response
                    error_response = self.create_error_response(None, -32700, f"Parse error: {str(e)}")
                    print(json.dumps(error_response))
                    sys.stdout.flush()

        except KeyboardInterrupt:
            # Clean shutdown
            logger.info("Bridge shutting down...")
        except Exception as e:
            logger.error(f"Bridge fatal error: {e}")
            sys.exit(1)

def main():
    """Entry point"""
    bridge = MCPHTTPBridge(REMOTE_SERVER_URL)
    bridge.run()

if __name__ == "__main__":
    main()