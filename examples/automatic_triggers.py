#!/usr/bin/env python3
"""
Sistema di Trigger Automatici per Agenti AI
Questo modulo implementa diversi pattern per far triggerare automaticamente
l'uso del sistema di memoria da parte degli agenti AI.
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class TriggerType(Enum):
    """Tipi di trigger disponibili"""
    KEYWORD = "keyword"           # Parole chiave specifiche
    PATTERN = "pattern"           # Pattern regex
    CONTEXT_LENGTH = "context_length"  # Lunghezza del contesto
    SEMANTIC = "semantic"         # Similarità semantica
    TIME_BASED = "time_based"     # Basato sul tempo
    CONVERSATION_FLOW = "conversation_flow"  # Flusso conversazione

@dataclass
class TriggerRule:
    """Regola di trigger per l'attivazione automatica"""
    name: str
    trigger_type: TriggerType
    condition: Any  # Condizione specifica del trigger
    action: str    # Azione da eseguire
    priority: int = 1  # Priorità (più alto = più importante)
    enabled: bool = True

class AutoMemoryTrigger:
    """Sistema di trigger automatici per la memoria"""
    
    def __init__(self, memory_server_path: str = "main.py"):
        self.memory_server_path = memory_server_path
        self.project_id = "triggered_session"
        self.rules: List[TriggerRule] = []
        self.conversation_history: List[Dict[str, Any]] = []
        self.last_memory_save = None
        
        # Carica regole predefinite
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Carica regole di trigger predefinite"""
        self.rules = [
            # Trigger per parole chiave di memoria
            TriggerRule(
                name="remember_keywords",
                trigger_type=TriggerType.KEYWORD,
                condition=["ricorda", "salva", "memorizza", "importante", "per dopo"],
                action="save_context",
                priority=3
            ),
            
            # Trigger per ricerca
            TriggerRule(
                name="search_keywords", 
                trigger_type=TriggerType.KEYWORD,
                condition=["cosa abbiamo detto", "precedente", "prima", "ricordi", "avevamo parlato"],
                action="search_memory",
                priority=3
            ),
            
            # Trigger per pattern di domande
            TriggerRule(
                name="question_pattern",
                trigger_type=TriggerType.PATTERN,
                condition=r"(come|cosa|quando|dove|perché|quale).{0,50}\?",
                action="search_and_save",
                priority=2
            ),
            
            # Trigger per contesto lungo
            TriggerRule(
                name="long_context",
                trigger_type=TriggerType.CONTEXT_LENGTH,
                condition=500,  # Caratteri
                action="summarize_and_save",
                priority=2
            ),
            
            # Trigger per decisioni
            TriggerRule(
                name="decision_pattern",
                trigger_type=TriggerType.PATTERN,
                condition=r"(decisione|scelgo|opto per|preferisco|raccomando)",
                action="save_decision",
                priority=3
            ),
            
            # Trigger per conoscenze tecniche
            TriggerRule(
                name="technical_knowledge",
                trigger_type=TriggerType.PATTERN,
                condition=r"(API|algoritmo|database|framework|libreria|funzione|metodo|classe)",
                action="save_knowledge",
                priority=2
            )
        ]
    
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
    
    async def process_input(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Processa l'input dell'utente e applica i trigger"""
        # Aggiungi alla storia della conversazione
        self.conversation_history.append({
            "type": "user",
            "content": user_input,
            "timestamp": asyncio.get_event_loop().time(),
            "context": context or {}
        })
        
        # Controlla tutti i trigger
        triggered_actions = await self._check_triggers(user_input, context)
        
        # Esegui azioni triggerate
        for action in triggered_actions:
            await self._execute_action(action, user_input, context)
        
        # Restituisci input eventualmente modificato
        return await self._enhance_input(user_input, triggered_actions)
    
    async def process_output(self, agent_output: str, original_input: str) -> str:
        """Processa l'output dell'agente e salva automaticamente"""
        # Aggiungi alla storia
        self.conversation_history.append({
            "type": "agent",
            "content": agent_output,
            "timestamp": asyncio.get_event_loop().time(),
            "original_input": original_input
        })
        
        # Salva automaticamente la conversazione
        async with self.connect_memory() as client:
            await self._save_conversation_pair(client, original_input, agent_output)
        
        return agent_output
    
    async def _check_triggers(self, text: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Controlla quali trigger sono attivati"""
        triggered_actions = []
        
        for rule in sorted(self.rules, key=lambda r: r.priority, reverse=True):
            if not rule.enabled:
                continue
                
            is_triggered = False
            
            if rule.trigger_type == TriggerType.KEYWORD:
                is_triggered = any(keyword.lower() in text.lower() for keyword in rule.condition)
            
            elif rule.trigger_type == TriggerType.PATTERN:
                is_triggered = bool(re.search(rule.condition, text, re.IGNORECASE))
            
            elif rule.trigger_type == TriggerType.CONTEXT_LENGTH:
                is_triggered = len(text) > rule.condition
            
            elif rule.trigger_type == TriggerType.CONVERSATION_FLOW:
                is_triggered = await self._check_conversation_flow(rule.condition)
            
            if is_triggered:
                triggered_actions.append({
                    "rule": rule,
                    "text": text,
                    "context": context,
                    "priority": rule.priority
                })
        
        return triggered_actions
    
    async def _execute_action(self, action_data: Dict[str, Any], text: str, context: Dict[str, Any]):
        """Esegue un'azione triggerata"""
        rule = action_data["rule"]
        
        async with self.connect_memory() as client:
            try:
                if rule.action == "save_context":
                    await self._save_context(client, text, context)
                
                elif rule.action == "search_memory":
                    return await self._search_memory(client, text)
                
                elif rule.action == "search_and_save":
                    search_results = await self._search_memory(client, text)
                    await self._save_context(client, text, context)
                    return search_results
                
                elif rule.action == "save_decision":
                    await self._save_decision(client, text, context)
                
                elif rule.action == "save_knowledge":
                    await self._save_knowledge(client, text, context)
                
                elif rule.action == "summarize_and_save":
                    await self._summarize_and_save(client, text, context)
                    
            except Exception as e:
                print(f"Errore nell'esecuzione dell'azione {rule.action}: {e}")
    
    async def _enhance_input(self, original_input: str, triggered_actions: List[Dict[str, Any]]) -> str:
        """Arricchisce l'input con memoria rilevante"""
        if not triggered_actions:
            return original_input
        
        # Cerca memoria rilevante
        async with self.connect_memory() as client:
            search_results = await self._search_memory(client, original_input)
            
            if search_results:
                context_section = "\n\n=== CONTESTO DALLA MEMORIA ===\n"
                for i, memory in enumerate(search_results[:3], 1):
                    context_section += f"{i}. {memory['text'][:100]}...\n"
                context_section += "=== FINE CONTESTO ===\n\n"
                
                return context_section + original_input
        
        return original_input
    
    async def _save_context(self, client: ClientSession, text: str, context: Dict[str, Any]):
        """Salva contesto"""
        await client.call_tool(
            "save_memory",
            arguments={
                "text": text,
                "type": "context",
                "project": self.project_id,
                "metadata": context or {},
                "importance": 0.7
            }
        )
    
    async def _save_decision(self, client: ClientSession, text: str, context: Dict[str, Any]):
        """Salva decisione"""
        await client.call_tool(
            "save_memory",
            arguments={
                "text": f"DECISIONE: {text}",
                "type": "decision",
                "project": self.project_id,
                "metadata": {**context, "extracted_from": "decision_pattern"},
                "importance": 0.9
            }
        )
    
    async def _save_knowledge(self, client: ClientSession, text: str, context: Dict[str, Any]):
        """Salva conoscenza tecnica"""
        await client.call_tool(
            "save_memory",
            arguments={
                "text": text,
                "type": "knowledge",
                "project": self.project_id,
                "metadata": {**context, "extracted_from": "technical_pattern"},
                "importance": 0.8
            }
        )
    
    async def _search_memory(self, client: ClientSession, query: str) -> List[Dict[str, Any]]:
        """Cerca nella memoria"""
        result = await client.call_tool(
            "search_memory",
            arguments={
                "query": query,
                "project": self.project_id,
                "limit": 5
            }
        )
        
        response = json.loads(result.content[0].text)
        return response.get("memories", [])
    
    async def _save_conversation_pair(self, client: ClientSession, user_input: str, agent_output: str):
        """Salva una coppia domanda-risposta"""
        conversation_text = f"DOMANDA: {user_input}\nRISPOSTA: {agent_output}"
        
        await client.call_tool(
            "save_memory",
            arguments={
                "text": conversation_text,
                "type": "conversation",
                "project": self.project_id,
                "metadata": {"auto_saved": True},
                "importance": 0.6
            }
        )
    
    async def _check_conversation_flow(self, condition: str) -> bool:
        """Controlla il flusso della conversazione"""
        # Implementa logica per flusso conversazione
        return len(self.conversation_history) > 5
    
    async def _summarize_and_save(self, client: ClientSession, text: str, context: Dict[str, Any]):
        """Riassume e salva testo lungo"""
        # Per ora salva direttamente, in futuro può implementare summarization
        await client.call_tool(
            "save_memory",
            arguments={
                "text": f"RIASSUNTO: {text[:200]}...",
                "type": "context",
                "project": self.project_id,
                "metadata": {**context, "summarized": True},
                "importance": 0.7
            }
        )

class AgentWrapper:
    """Wrapper per agenti AI con trigger automatici"""
    
    def __init__(self, agent_function: Callable, memory_server_path: str = "main.py"):
        self.agent_function = agent_function
        self.trigger_system = AutoMemoryTrigger(memory_server_path)
    
    async def __call__(self, user_input: str, **kwargs) -> str:
        """Chiamata wrapper che integra automaticamente la memoria"""
        # Pre-processing con trigger
        enhanced_input = await self.trigger_system.process_input(user_input, kwargs)
        
        # Chiamata all'agente originale
        if asyncio.iscoroutinefunction(self.agent_function):
            agent_output = await self.agent_function(enhanced_input, **kwargs)
        else:
            agent_output = self.agent_function(enhanced_input, **kwargs)
        
        # Post-processing con salvataggio automatico
        final_output = await self.trigger_system.process_output(agent_output, user_input)
        
        return final_output

# Decoratore per automatizzare l'integrazione
def auto_memory_integration(memory_server_path: str = "main.py"):
    """Decoratore per automatizzare l'integrazione della memoria"""
    def decorator(agent_function):
        return AgentWrapper(agent_function, memory_server_path)
    return decorator

# Esempio di utilizzo con diversi agenti
@auto_memory_integration()
async def my_ai_agent(user_input: str, **kwargs) -> str:
    """Esempio di agente AI con memoria automatica"""
    # Simulazione di elaborazione dell'agente
    if "Python" in user_input:
        return "Python è un linguaggio ottimo per sviluppo rapido e machine learning."
    elif "memoria" in user_input.lower():
        return "Il sistema di memoria ti aiuta a ricordare le conversazioni precedenti."
    else:
        return f"Ho elaborato la tua richiesta: {user_input}"

# Esempi specifici per agenti diversi
class ClaudeMemoryTrigger:
    """Trigger specifici per Claude Desktop"""
    
    @staticmethod
    def get_config():
        return {
            "mcpServers": {
                "memory-server": {
                    "command": "python",
                    "args": ["/path/to/mcp-memory-server/main.py"],
                    "env": {
                        "MONGODB_URL": "mongodb://localhost:27017/memory_db",
                        "AUTO_TRIGGER": "true",
                        "TRIGGER_SENSITIVITY": "medium"
                    }
                }
            }
        }

class CursorMemoryTrigger:
    """Trigger specifici per Cursor AI"""
    
    @staticmethod
    def setup_cursor_hooks():
        """Setup hook per Cursor AI"""
        return """
        // Aggiungi al settings.json di Cursor
        {
            "mcp.autoTrigger": true,
            "mcp.triggerKeywords": ["ricorda", "salva", "memorizza"],
            "mcp.contextLength": 500,
            "mcp.memoryServer": {
                "command": "python",
                "args": ["main.py"],
                "cwd": "/path/to/mcp-memory-server"
            }
        }
        """

async def demo_automatic_triggers():
    """Demo del sistema di trigger automatici"""
    print("🤖 Demo Sistema di Trigger Automatici")
    print("=" * 50)
    
    # Test con agente automatico
    agent = my_ai_agent
    
    test_inputs = [
        "Ricorda che sto lavorando su un progetto Python",
        "Come posso ottimizzare le performance?",
        "Cosa avevamo detto prima sui design pattern?",
        "Prendo la decisione di usare MongoDB per il database",
        "L'API REST è migliore per questo use case"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{i}. INPUT: {user_input}")
        response = await agent(user_input)
        print(f"   OUTPUT: {response}")
    
    print("\n✅ Demo completata!")
    print("📝 Tutte le interazioni sono state automaticamente elaborate con trigger")

if __name__ == "__main__":
    asyncio.run(demo_automatic_triggers()) 