#!/usr/bin/env python3
"""
GPT Integration for MCP Memory Server
Creates a REST API wrapper that can be used with ChatGPT via Custom GPTs or API calls
"""

import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.mcp_server import MCPServer

app = FastAPI(title="MCP Memory Server API", version="1.0.0")

# Add CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class SaveMemoryRequest(BaseModel):
    text: str
    memory_type: str = "knowledge"
    project: str = "gpt"
    importance: float = 0.5
    tags: Optional[List[str]] = None

class SearchMemoryRequest(BaseModel):
    query: str
    project: str = "gpt"
    limit: int = 5
    threshold: float = 0.3

class MemoryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# Global MCP server instance
mcp_server = None

@app.on_startup
async def startup():
    global mcp_server
    mcp_server = MCPServer()
    await mcp_server.initialize()

@app.post("/save", response_model=MemoryResponse)
async def save_memory(request: SaveMemoryRequest):
    """Save a memory - callable from GPT"""
    try:
        # Call the MCP server's save_memory tool
        result = await mcp_server.call_tool(
            "save_memory",
            {
                "text": request.text,
                "memory_type": request.memory_type,
                "project": request.project,
                "importance": request.importance,
                "tags": request.tags or []
            }
        )
        
        return MemoryResponse(
            success=True,
            message="Memory saved successfully",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=MemoryResponse)
async def search_memories(request: SearchMemoryRequest):
    """Search memories - callable from GPT"""
    try:
        result = await mcp_server.call_tool(
            "search_memory",
            {
                "query": request.query,
                "project": request.project,
                "limit": request.limit,
                "threshold": request.threshold
            }
        )
        
        return MemoryResponse(
            success=True,
            message=f"Found {len(result.get('memories', []))} memories",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/context/{project}")
async def get_context(project: str):
    """Get project context - callable from GPT"""
    try:
        result = await mcp_server.call_tool(
            "get_context",
            {"project": project}
        )
        
        return MemoryResponse(
            success=True,
            message="Context retrieved successfully",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/{project}")
async def get_stats(project: str):
    """Get memory statistics - callable from GPT"""
    try:
        result = await mcp_server.call_tool(
            "get_memory_stats",
            {"project": project}
        )
        
        return MemoryResponse(
            success=True,
            message="Statistics retrieved successfully",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        result = await mcp_server.call_tool("health_check", {})
        return MemoryResponse(
            success=True,
            message="Server is healthy",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting MCP Memory Server API for GPT integration...")
    print("📝 API will be available at: http://localhost:8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("\n🤖 GPT Usage Examples:")
    print("  Save: POST http://localhost:8000/save")
    print("  Search: POST http://localhost:8000/search")
    print("  Context: GET http://localhost:8000/context/gpt")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 