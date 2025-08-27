#!/usr/bin/env python3
"""
HTTP Proxy Server for MCP Memory Server
Intercepts AI platform messages for auto-trigger analysis
"""

import asyncio
import json
import logging
import sys
import os
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

import aiohttp
import yaml
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.config.settings import get_settings
from src.core.server import MCPServer
from src.utils.exceptions import MCPMemoryError


class ProxyServer:
    """HTTP Proxy Server for auto-trigger message interception"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load proxy configuration
        if config_path is None:
            config_path = Path(project_root) / "config" / "proxy_config.yaml"
        
        with open(config_path, 'r') as f:
            self.proxy_config = yaml.safe_load(f)
        
        # Load MCP settings
        self.settings = get_settings()
        
        # Initialize MCP server
        self.mcp_server = MCPServer(self.settings)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize FastAPI app
        self.app = self._create_app()
        
        # HTTP session for platform requests
        self.session: Optional[aiohttp.ClientSession] = None
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.proxy_config.get('proxy', {}).get('logging', {})
        
        level = getattr(logging, log_config.get('level', 'INFO'))
        format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=level,
            format=format_str,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_config.get('file', 'logs/proxy.log'))
            ]
        )
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        proxy_settings = self.proxy_config.get('proxy', {})
        
        app = FastAPI(
            title=proxy_settings.get('name', 'MCP Memory Proxy Server'),
            description="HTTP Proxy for MCP Memory Server auto-trigger functionality",
            version=proxy_settings.get('version', '1.0.0'),
            debug=proxy_settings.get('debug', False)
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add request logging middleware
        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            
            # Log request
            self.logger.info(f"📥 {request.method} {request.url.path} from {request.client.host}")
            
            # Process request
            response = await call_next(request)
            
            # Log response
            duration = time.time() - start_time
            self.logger.info(f"📤 {response.status_code} in {duration:.3f}s")
            
            return response
        
        # Setup routes
        self._setup_routes(app)
        
        return app
    
    def _setup_routes(self, app: FastAPI):
        """Setup proxy routes"""
        
        @app.on_event("startup")
        async def startup_event():
            """Initialize services on startup"""
            await self.initialize()
        
        @app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup on shutdown"""
            await self.cleanup()
        
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "message": "MCP Memory Proxy Server",
                "version": self.proxy_config.get('proxy', {}).get('version', '1.0.0'),
                "status": "running",
                "timestamp": datetime.utcnow().isoformat(),
                "mcp_server": "initialized" if self.mcp_server else "not_initialized"
            }
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                # Check MCP server health
                mcp_health = await self._check_mcp_health()
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "mcp_server": mcp_health,
                    "proxy_config": {
                        "auto_trigger_enabled": self.proxy_config.get('proxy', {}).get('auto_trigger', {}).get('enabled', False),
                        "platforms_enabled": [
                            platform for platform, config in self.proxy_config.get('proxy', {}).get('platforms', {}).items()
                            if config.get('enabled', False)
                        ]
                    }
                }
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                return JSONResponse(
                    status_code=503,
                    content={"status": "unhealthy", "error": str(e)}
                )
        
        @app.post("/proxy/cursor")
        async def proxy_cursor(request: Request):
            """Proxy endpoint for Cursor AI Platform"""
            return await self._handle_platform_request(request, "cursor")
        
        @app.post("/proxy/claude")
        async def proxy_claude(request: Request):
            """Proxy endpoint for Claude AI Platform"""
            return await self._handle_platform_request(request, "claude")
        
        @app.post("/proxy/universal")
        async def proxy_universal(request: Request):
            """Proxy endpoint for Universal AI Platform"""
            return await self._handle_platform_request(request, "universal")
        
        @app.post("/proxy/{platform}")
        async def proxy_dynamic(request: Request, platform: str):
            """Dynamic proxy endpoint for any platform"""
            return await self._handle_platform_request(request, platform)
    
    async def initialize(self):
        """Initialize proxy server"""
        try:
            self.logger.info("🚀 Initializing MCP Memory Proxy Server...")
            
            # Initialize MCP server
            await self.mcp_server.initialize()
            self.logger.info("✅ MCP Server initialized")
            
            # Initialize HTTP session
            timeout = aiohttp.ClientTimeout(
                total=self.proxy_config.get('proxy', {}).get('performance', {}).get('request_timeout', 60)
            )
            self.session = aiohttp.ClientSession(timeout=timeout)
            self.logger.info("✅ HTTP Session initialized")
            
            self.logger.info("🌐 Proxy Server ready for message interception")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize proxy server: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
                self.logger.info("✅ HTTP Session closed")
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")
    
    async def _check_mcp_health(self) -> Dict[str, Any]:
        """Check MCP server health"""
        try:
            # Try to call a simple MCP tool
            result = await self.mcp_server._handle_get_memory_stats({})
            stats = json.loads(result)
            
            return {
                "status": "healthy",
                "memory_count": stats.get("memory_count", 0),
                "ml_system": "enabled" if self.mcp_server.ml_trigger_system else "disabled"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _handle_platform_request(self, request: Request, platform: str) -> Response:
        """Handle platform request with auto-trigger analysis"""
        try:
            # Parse request body
            body = await request.body()
            if body:
                request_data = json.loads(body)
            else:
                request_data = {}
            
            self.logger.info(f"🔍 Processing {platform} request: {request_data.get('method', 'unknown')}")
            
            # Extract message for analysis
            message = self._extract_message(request_data)
            
            if message and self._should_analyze(platform):
                # Perform auto-trigger analysis
                enhanced_request = await self._analyze_and_enhance(message, request_data, platform)
            else:
                enhanced_request = request_data
            
            # Forward to AI platform
            if platform in ['cursor', 'claude'] and self.proxy_config.get('proxy', {}).get('platforms', {}).get(platform, {}).get('enabled', False):
                response = await self._forward_to_platform(enhanced_request, platform, request)
            else:
                # For universal or unknown platforms, just return enhanced request
                self.logger.info(f"⚠️ Platform {platform} not configured, returning enhanced request")
                response = JSONResponse(content=enhanced_request)
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Platform request error: {e}")
            import traceback
            traceback.print_exc()
            
            raise HTTPException(
                status_code=500,
                detail=f"Proxy error: {str(e)}"
            )
    
    def _extract_message(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Extract message content from request data"""
        # Try common message fields
        message_fields = ['message', 'prompt', 'input', 'text', 'content', 'query']
        
        for field in message_fields:
            if field in request_data:
                message = request_data[field]
                if isinstance(message, str) and message.strip():
                    return message.strip()
        
        # Try nested structures
        if 'data' in request_data and isinstance(request_data['data'], dict):
            for field in message_fields:
                if field in request_data['data']:
                    message = request_data['data'][field]
                    if isinstance(message, str) and message.strip():
                        return message.strip()
        
        return None
    
    def _should_analyze(self, platform: str) -> bool:
        """Check if we should analyze messages for this platform"""
        auto_trigger_config = self.proxy_config.get('proxy', {}).get('auto_trigger', {})
        
        if not auto_trigger_config.get('enabled', False):
            return False
        
        platform_config = self.proxy_config.get('proxy', {}).get('platforms', {}).get(platform, {})
        return platform_config.get('enabled', False)
    
    async def _analyze_and_enhance(self, message: str, request_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Analyze message and enhance request with memory context"""
        try:
            self.logger.info(f"🧠 Analyzing message for auto-triggers: {message[:100]}...")
            
            # Prepare analyze_message arguments
            analyze_args = {
                "message": message,
                "platform_context": {
                    "platform": platform,
                    "user_id": request_data.get("user_id", "unknown"),
                    "session_id": request_data.get("session_id", "unknown"),
                    "project": request_data.get("project", "default")
                },
                "auto_execute": self.proxy_config.get('proxy', {}).get('auto_trigger', {}).get('auto_execute', True)
            }
            
            # Call MCP analyze_message
            result = await self.mcp_server._handle_analyze_message(analyze_args)
            analysis = json.loads(result)
            
            self.logger.info(f"📊 Analysis complete: confidence={analysis.get('confidence', 0):.3f}")
            
            # Enhance request with analysis results
            enhanced_request = request_data.copy()
            
            # Add memory context if available
            executed_actions = analysis.get('executed_actions', [])
            memory_context = []
            
            for action in executed_actions:
                if action.get('status') == 'success' and action.get('action') == 'search_memory':
                    search_result = action.get('result', {})
                    if isinstance(search_result, list):
                        memory_context.extend(search_result)
                    elif isinstance(search_result, dict) and 'memories' in search_result:
                        memory_context.extend(search_result['memories'])
            
            # Enhance the original message with memory context
            if memory_context:
                context_text = "\n\nRelevant context from memory:\n"
                for memory in memory_context[:3]:  # Limit to top 3 memories
                    if isinstance(memory, dict) and 'content' in memory:
                        context_text += f"- {memory['content']}\n"
                
                # Enhance the message field
                original_message = self._extract_message(enhanced_request)
                if original_message:
                    enhanced_message = original_message + context_text
                    # Update the message in the request
                    for field in ['message', 'prompt', 'input', 'text', 'content', 'query']:
                        if field in enhanced_request:
                            enhanced_request[field] = enhanced_message
                            break
                    
                    self.logger.info(f"✅ Enhanced message with {len(memory_context)} memory contexts")
            
            # Add analysis metadata
            enhanced_request['_mcp_analysis'] = {
                "confidence": analysis.get('confidence', 0),
                "triggers": analysis.get('triggers', []),
                "executed_actions": len(executed_actions),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return enhanced_request
            
        except Exception as e:
            self.logger.error(f"❌ Analysis error: {e}")
            # Return original request if analysis fails
            return request_data
    
    async def _forward_to_platform(self, request_data: Dict[str, Any], platform: str, original_request: Request) -> Response:
        """Forward enhanced request to AI platform"""
        try:
            platform_config = self.proxy_config.get('proxy', {}).get('platforms', {}).get(platform, {})
            base_url = platform_config.get('base_url')
            
            if not base_url:
                self.logger.warning(f"⚠️ No base_url configured for platform {platform}")
                return JSONResponse(content=request_data)
            
            # Prepare headers
            headers = platform_config.get('headers', {}).copy()
            
            # Copy relevant headers from original request
            for header_name in ['Authorization', 'X-API-Key', 'User-Agent']:
                if header_name in original_request.headers:
                    headers[header_name] = original_request.headers[header_name]
            
            # Forward request
            url = f"{base_url.rstrip('/')}{original_request.url.path.replace('/proxy/' + platform, '')}"
            timeout = platform_config.get('timeout', 30)
            
            self.logger.info(f"🌐 Forwarding to {platform}: {url}")
            
            async with self.session.post(
                url,
                json=request_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response_data = await response.json()
                
                self.logger.info(f"✅ Platform response: {response.status}")
                
                return JSONResponse(
                    content=response_data,
                    status_code=response.status
                )
                
        except aiohttp.ClientTimeout:
            self.logger.error(f"⏰ Timeout forwarding to {platform}")
            raise HTTPException(status_code=504, detail="Platform request timeout")
        
        except Exception as e:
            self.logger.error(f"❌ Forward error: {e}")
            raise HTTPException(status_code=502, detail=f"Platform forward error: {str(e)}")
    
    async def run(self, host: str = None, port: int = None):
        """Run the proxy server"""
        proxy_settings = self.proxy_config.get('proxy', {})
        
        host = host or proxy_settings.get('host', '0.0.0.0')
        port = port or proxy_settings.get('port', 8080)
        
        self.logger.info(f"🚀 Starting MCP Memory Proxy Server on {host}:{port}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level=proxy_settings.get('logging', {}).get('level', 'info').lower(),
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Memory Proxy Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--config", help="Path to proxy configuration file")
    
    args = parser.parse_args()
    
    try:
        proxy = ProxyServer(config_path=args.config)
        await proxy.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n👋 Proxy server stopped")
    except Exception as e:
        print(f"❌ Proxy server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
