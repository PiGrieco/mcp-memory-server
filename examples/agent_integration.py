#!/usr/bin/env python3
"""
Esempio di integrazione automatica per agenti AI
Questo script mostra come integrare il sistema di memoria in modo automatico
durante il processo di generazione degli agenti AI.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class AutoMemoryAgent:
    """Agente AI con integrazione automatica della memoria"""
    
    def __init__(self, memory_server_path: str = "main.py"):
        self.memory_server_path = memory_server_path
        self.project_id = "auto_agent_session"
    
    @asynccontextmanager
    async def connect_memory(self):
        """Connessione al server di memoria"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.memory_server_path],
            env=None
        )
        
        read_stream, write_stream = await stdio_client(server_params)
        client = ClientSession(read_stream, write_stream)
        await client.initialize()
        
        try:
            yield client
        finally:
            await client.close()
    
    async def auto_save_context(self, client: ClientSession, context: str, 
                               memory_type: str = "context", importance: float = 0.7):
        """Salva automaticamente il contesto della conversazione"""
        try:
            await client.call_tool(
                "save_memory",
                arguments={
                    "text": context,
                    "type": memory_type,
                    "project": self.project_id,
                    "importance": importance
                }
            )
        except Exception as e:
            print(f"Errore nel salvataggio automatico: {e}")
    
    async def auto_save_knowledge(self, client: ClientSession, knowledge: str, 
                                 metadata: Optional[Dict[str, Any]] = None):
        """Salva automaticamente nuove conoscenze"""
        try:
            await client.call_tool(
                "save_memory",
                arguments={
                    "text": knowledge,
                    "type": "knowledge",
                    "project": self.project_id,
                    "metadata": metadata or {},
                    "importance": 0.8
                }
            )
        except Exception as e:
            print(f"Errore nel salvataggio conoscenza: {e}")
    
    async def auto_save_decision(self, client: ClientSession, decision: str, 
                                reasoning: str = ""):
        """Salva automaticamente decisioni prese"""
        try:
            full_text = f"Decisione: {decision}"
            if reasoning:
                full_text += f"\nRagionamento: {reasoning}"
            
            await client.call_tool(
                "save_memory",
                arguments={
                    "text": full_text,
                    "type": "decision",
                    "project": self.project_id,
                    "importance": 0.9
                }
            )
        except Exception as e:
            print(f"Errore nel salvataggio decisione: {e}")
    
    async def get_relevant_context(self, client: ClientSession, query: str, 
                                  limit: int = 5) -> List[Dict[str, Any]]:
        """Recupera contesto rilevante per una query"""
        try:
            result = await client.call_tool(
                "search_memory",
                arguments={
                    "query": query,
                    "project": self.project_id,
                    "limit": limit
                }
            )
            
            response = json.loads(result.content[0].text)
            return response.get("memories", [])
            
        except Exception as e:
            print(f"Errore nel recupero contesto: {e}")
            return []
    
    async def get_project_context(self, client: ClientSession) -> Dict[str, Any]:
        """Recupera tutto il contesto del progetto"""
        try:
            result = await client.call_tool(
                "get_context",
                arguments={
                    "project": self.project_id,
                    "types": ["context", "knowledge", "decision"],
                    "limit": 10
                }
            )
            
            return json.loads(result.content[0].text)
            
        except Exception as e:
            print(f"Errore nel recupero contesto progetto: {e}")
            return {"context": {}, "total_memories": 0}

class AgentMemoryHooks:
    """Hook per integrazione automatica con agenti AI"""
    
    def __init__(self, memory_agent: AutoMemoryAgent):
        self.memory_agent = memory_agent
    
    async def before_generation(self, prompt: str, user_context: str = "") -> str:
        """Hook chiamato prima della generazione della risposta"""
        async with self.memory_agent.connect_memory() as client:
            # Salva il contesto dell'utente
            if user_context:
                await self.memory_agent.auto_save_context(client, user_context)
            
            # Recupera contesto rilevante
            relevant_memories = await self.memory_agent.get_relevant_context(client, prompt)
            
            # Costruisci prompt arricchito
            enhanced_prompt = self._build_enhanced_prompt(prompt, relevant_memories)
            
            return enhanced_prompt
    
    async def after_generation(self, response: str, prompt: str, 
                              response_type: str = "conversation"):
        """Hook chiamato dopo la generazione della risposta"""
        async with self.memory_agent.connect_memory() as client:
            # Salva la risposta come contesto
            await self.memory_agent.auto_save_context(
                client, 
                f"Risposta a: {prompt}\n{response}",
                importance=0.6
            )
    
    async def on_knowledge_extraction(self, knowledge: str, source: str = ""):
        """Hook per estrazione di conoscenze"""
        async with self.memory_agent.connect_memory() as client:
            metadata = {"source": source} if source else {}
            await self.memory_agent.auto_save_knowledge(client, knowledge, metadata)
    
    async def on_decision_made(self, decision: str, reasoning: str = ""):
        """Hook per decisioni prese dall'agente"""
        async with self.memory_agent.connect_memory() as client:
            await self.memory_agent.auto_save_decision(client, decision, reasoning)
    
    def _build_enhanced_prompt(self, original_prompt: str, 
                              memories: List[Dict[str, Any]]) -> str:
        """Costruisce un prompt arricchito con memorie rilevanti"""
        if not memories:
            return original_prompt
        
        context_section = "\n\n=== CONTESTO RILEVANTE ===\n"
        for i, memory in enumerate(memories, 1):
            context_section += f"{i}. {memory['text']}\n"
        
        context_section += "\n=== FINE CONTESTO ===\n\n"
        
        return context_section + original_prompt

# Esempio di utilizzo
async def demo_agent_integration():
    """Dimostrazione dell'integrazione automatica"""
    print("🤖 Demo Integrazione Automatica Agente AI")
    print("=" * 50)
    
    # Crea agente con memoria
    memory_agent = AutoMemoryAgent()
    hooks = AgentMemoryHooks(memory_agent)
    
    # Simula una conversazione
    user_prompt = "Come posso ottimizzare le performance di un'applicazione Python?"
    
    print(f"\n1. Prompt utente: {user_prompt}")
    
    # Hook pre-generazione
    enhanced_prompt = await hooks.before_generation(
        user_prompt, 
        "L'utente sta lavorando su un'applicazione Python e vuole migliorare le performance"
    )
    
    print(f"\n2. Prompt arricchito:\n{enhanced_prompt}")
    
    # Simula risposta dell'agente
    agent_response = """
    Per ottimizzare le performance di un'applicazione Python:
    1. Usa profiling (cProfile, line_profiler)
    2. Ottimizza algoritmi e strutture dati
    3. Considera Cython per parti critiche
    4. Usa multiprocessing per operazioni CPU-intensive
    5. Implementa caching appropriato
    """
    
    print(f"\n3. Risposta agente:\n{agent_response}")
    
    # Hook post-generazione
    await hooks.after_generation(agent_response, user_prompt)
    
    # Estrai conoscenza
    knowledge = "Le performance Python si ottimizzano con profiling, algoritmi efficienti, Cython, multiprocessing e caching"
    await hooks.on_knowledge_extraction(knowledge, "performance_optimization")
    
    # Simula decisione
    decision = "Raccomandare profiling come primo passo per ottimizzazione"
    reasoning = "Il profiling identifica i bottleneck specifici prima di implementare ottimizzazioni"
    await hooks.on_decision_made(decision, reasoning)
    
    print("\n✅ Integrazione automatica completata!")
    print("📝 Tutte le informazioni sono state salvate automaticamente nella memoria")

if __name__ == "__main__":
    asyncio.run(demo_agent_integration()) 