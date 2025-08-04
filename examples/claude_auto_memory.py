#!/usr/bin/env python3
"""
Claude Desktop Auto-Memory Wrapper
Intercepts and processes conversations automatically with memory
"""

import sys
import json
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.mcp_server import MCPServer
from examples.auto_memory_system import AutoMemorySystem

class ClaudeAutoMemoryWrapper:
    def __init__(self):
        self.mcp_server = None
        self.auto_memory = None
        self.project = "claude"
        
    async def initialize(self):
        """Inizializza il server MCP e il sistema auto-memory"""
        self.mcp_server = MCPServer()
        await self.mcp_server.initialize()
        self.auto_memory = AutoMemorySystem(self.mcp_server)
        print("🧠 Claude Auto-Memory initialized")

    async def handle_mcp_call(self, method: str, params: dict) -> dict:
        """
        Intercetta le chiamate MCP e aggiunge intelligence automatica
        """
        
        # Per tutte le chiamate ai tool, cerca prima contesto rilevante
        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            # Se non è una chiamata esplicita alla memoria, cerca contesto
            if tool_name not in ["save_memory", "search_memory"]:
                # Cerca contesto basato sull'input dell'utente
                if "text" in tool_args or "query" in tool_args:
                    user_input = tool_args.get("text") or tool_args.get("query", "")
                    context = await self.auto_memory._search_relevant_context(
                        user_input, self.project
                    )
                    
                    if context:
                        # Arricchisci i parametri con il contesto
                        tool_args["_context"] = context
                        params["arguments"] = tool_args
                        print(f"🔍 Added context to {tool_name}: {len(context)} memories")
            
            # Esegui il tool originale
            result = await self.mcp_server.call_tool(tool_name, tool_args)
            
            # Auto-save se appropriato
            if tool_name not in ["save_memory", "search_memory", "health_check"]:
                await self._auto_save_interaction(tool_name, tool_args, result)
            
            return result
        
        # Per altri metodi MCP, passa direttamente
        return await self.mcp_server.handle_request(method, params)

    async def _auto_save_interaction(self, tool_name: str, args: dict, result: dict):
        """Salva automaticamente interazioni interessanti"""
        try:
            # Salva il pattern di utilizzo del tool
            interaction_text = f"Used {tool_name} with: {str(args)[:200]}"
            await self.mcp_server.call_tool("save_memory", {
                "text": interaction_text,
                "memory_type": "auto_interaction",
                "project": self.project,
                "importance": 0.5,
                "tags": ["auto_saved", "tool_usage", tool_name]
            })
            
            # Se il risultato contiene informazioni utili, salvale
            if result.get("success") and result.get("data"):
                result_text = f"Result from {tool_name}: {str(result['data'])[:200]}"
                await self.mcp_server.call_tool("save_memory", {
                    "text": result_text,
                    "memory_type": "auto_result",
                    "project": self.project,
                    "importance": 0.4,
                    "tags": ["auto_saved", "tool_result", tool_name]
                })
                
        except Exception as e:
            print(f"⚠️ Auto-save failed: {e}")

    async def enhance_prompt_with_context(self, original_prompt: str) -> str:
        """Migliora un prompt con contesto dalla memoria"""
        context = await self.auto_memory._search_relevant_context(
            original_prompt, self.project
        )
        
        if not context:
            return original_prompt
        
        enhanced_prompt = original_prompt + "\n\n## Relevant Context:\n"
        for i, memory in enumerate(context[:3], 1):
            enhanced_prompt += f"{i}. {memory['text'][:100]}...\n"
        
        enhanced_prompt += "\nPlease use this context to provide a more informed response.\n"
        return enhanced_prompt

# Configurazione per Claude Desktop
claude_config = {
    "mcpServers": {
        "auto-memory-server": {
            "command": "python",
            "args": [str(Path(__file__))],
            "env": {
                "MONGODB_URL": "mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin",
                "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
                "AUTO_MEMORY": "true"
            }
        }
    }
}

async def main():
    """Main entry point quando viene eseguito da Claude"""
    wrapper = ClaudeAutoMemoryWrapper()
    await wrapper.initialize()
    
    print("🚀 Claude Auto-Memory Wrapper ready!")
    print("💡 Now conversations will automatically:")
    print("   - Save important information")
    print("   - Search for relevant context")
    print("   - Enhance responses with memory")
    
    # Loop per gestire le richieste MCP
    try:
        while True:
            # Leggi richiesta MCP da stdin
            line = input()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                
                # Processa con auto-memory
                result = await wrapper.handle_mcp_call(method, params)
                
                # Restituisci risultato
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
                print(json.dumps(response))
                
            except json.JSONDecodeError:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"}
                }))
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": str(e)}
                }))
                
    except KeyboardInterrupt:
        print("🛑 Auto-Memory Wrapper stopped")

if __name__ == "__main__":
    asyncio.run(main()) 