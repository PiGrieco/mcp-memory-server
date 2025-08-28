#!/usr/bin/env python3
"""
Simple HTTP server for testing MCP Memory Server functionality
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.config.settings import get_settings
from src.services.memory_service import MemoryService


# Create FastAPI app
app = FastAPI(
    title="MCP Memory Server - HTTP Test",
    description="HTTP interface for testing MCP Memory Server functionality",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global memory service
memory_service: MemoryService = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global memory_service
    
    print("🚀 Starting MCP Memory Server HTTP Test...")
    
    try:
        # Load settings
        settings = get_settings()
        print(f"✅ Settings loaded: {settings.server.name}")
        
        # Initialize memory service
        memory_service = MemoryService(settings)
        await memory_service.initialize()
        
        print("✅ Memory service initialized successfully")
        print("🌐 HTTP server ready at http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MCP Memory Server HTTP Test",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "create_memory": "/memory (POST)",
            "search_memories": "/memory/search (POST)",
            "list_memories": "/memory/list (GET)",
            "get_memory": "/memory/{id} (GET)",
            "auto_save": "/memory/auto-save (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health = await memory_service.health_check()
        return {
            "status": "healthy",
            "memory_service": health,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/status")
async def get_status():
    """Get memory system status"""
    try:
        status = await memory_service.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {e}")


@app.post("/memory")
async def create_memory(memory_data: Dict[str, Any]):
    """Create a new memory"""
    try:
        memory = await memory_service.create_memory(
            content=memory_data["content"],
            project=memory_data.get("project", "default"),
            importance=memory_data.get("importance", 0.5),
            tags=memory_data.get("tags", []),
            metadata=memory_data.get("metadata", {}),
            context=memory_data.get("context", {})
        )
        
        return {
            "success": True,
            "message": "Memory created successfully",
            "memory": {
                "id": memory.id,
                "project": memory.project,
                "content": memory.content,
                "importance": memory.importance,
                "tags": memory.tags,
                "created_at": memory.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create memory: {e}")


@app.post("/memory/search")
async def search_memories(search_data: Dict[str, Any]):
    """Search memories"""
    try:
        results = await memory_service.search_memories(
            query=search_data["query"],
            project=search_data.get("project"),
            max_results=search_data.get("max_results", 20),
            similarity_threshold=search_data.get("similarity_threshold", 0.3),
            tags=search_data.get("tags", [])
        )
        
        return {
            "success": True,
            "count": len(results),
            "memories": [
                {
                    "id": memory.id,
                    "project": memory.project,
                    "content": memory.content,
                    "importance": memory.importance,
                    "similarity_score": getattr(memory, 'similarity_score', None),
                    "created_at": memory.created_at.isoformat()
                }
                for memory in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {e}")


@app.get("/memory/list")
async def list_memories(
    project: str = "default",
    limit: int = 50,
    offset: int = 0
):
    """List memories for a project"""
    try:
        memories = await memory_service.list_memories(
            project=project,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "count": len(memories),
            "memories": [
                {
                    "id": memory.id,
                    "project": memory.project,
                    "content": memory.content,
                    "importance": memory.importance,
                    "created_at": memory.created_at.isoformat()
                }
                for memory in memories
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list memories: {e}")


@app.get("/memory/{memory_id}")
async def get_memory(memory_id: str):
    """Get a specific memory"""
    try:
        memory = await memory_service.get_memory(memory_id)
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "success": True,
            "memory": {
                "id": memory.id,
                "project": memory.project,
                "content": memory.content,
                "importance": memory.importance,
                "tags": memory.tags,
                "metadata": memory.metadata,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {e}")


@app.post("/memory/auto-save")
async def auto_save_memory(auto_save_data: Dict[str, Any]):
    """Auto-save memory if content triggers threshold"""
    try:
        result = await memory_service.auto_save_memory(
            content=auto_save_data["content"],
            context=auto_save_data.get("context", {}),
            project=auto_save_data.get("project", "default")
        )
        
        return {
            "success": True,
            "saved": result["saved"],
            "trigger_type": result.get("trigger_type", "none"),
            "importance": result.get("importance"),
            "memory_id": result.get("memory_id"),
            "threshold": result.get("threshold")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-save memory: {e}")


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        metrics = await memory_service.get_metrics()
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {e}")


if __name__ == "__main__":
    print("🚀 MCP Memory Server - HTTP Test Server")
    print("=" * 50)
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 