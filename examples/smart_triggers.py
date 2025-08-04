#!/usr/bin/env python3
"""
Smart Triggers for Auto-Memory
Detects conversation patterns and automatically triggers memory operations
"""

import re
import asyncio
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class TriggerType(Enum):
    AUTO_SAVE = "auto_save"
    AUTO_SEARCH = "auto_search"
    CONTEXT_ENHANCEMENT = "context_enhancement"
    PATTERN_DETECTION = "pattern_detection"

@dataclass
class MemoryTrigger:
    trigger_type: TriggerType
    confidence: float
    context: str
    action: str
    metadata: Dict

class SmartTriggerSystem:
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.conversation_buffer = []
        self.user_patterns = {}
        self.last_search_time = {}
        
        # Patterns per auto-save
        self.save_triggers = {
            # Preferenze personali (alta priorità)
            "preferences": {
                "patterns": [
                    r"(preferisco|mi piace|odio|detesto)\s+(.+)",
                    r"(il mio .+ preferito è|la mia .+ preferita è)\s+(.+)",
                    r"(uso sempre|uso spesso|non uso mai)\s+(.+)",
                    r"(sono abituato a|sono solito)\s+(.+)"
                ],
                "confidence": 0.9,
                "importance": 0.8
            },
            
            # Informazioni di progetto
            "project_info": {
                "patterns": [
                    r"(sto lavorando su|il progetto si chiama|questo progetto)\s+(.+)",
                    r"(il cliente vuole|il requisito è|dobbiamo)\s+(.+)",
                    r"(la deadline è|entro il|dobbiamo finire)\s+(.+)",
                    r"(stack tecnologico|tecnologie utilizzate|framework)\s*:\s*(.+)"
                ],
                "confidence": 0.8,
                "importance": 0.7
            },
            
            # Soluzioni tecniche
            "solutions": {
                "patterns": [
                    r"(la soluzione è|risolto con|ho risolto usando)\s+(.+)",
                    r"(il problema era|l'errore era causato da)\s+(.+)",
                    r"(funziona meglio se|migliora se|ottimizzato con)\s+(.+)",
                    r"(questo pattern|questo approccio|questa tecnica)\s+(.+)"
                ],
                "confidence": 0.7,
                "importance": 0.6
            },
            
            # Configurazioni e setup
            "configurations": {
                "patterns": [
                    r"(configurazione|setup|installazione)\s*:\s*(.+)",
                    r"(parametri|opzioni|flag)\s*:\s*(.+)",
                    r"(versione|release|build)\s+(.+)",
                    r"(compatibile con|richiede|dipende da)\s+(.+)"
                ],
                "confidence": 0.6,
                "importance": 0.5
            }
        }
        
        # Patterns per auto-search
        self.search_triggers = {
            "questions": [
                r"(come faccio a|come posso|come si fa a)\s+(.+)\?",
                r"(qual è il modo migliore per|quale approccio per)\s+(.+)\?",
                r"(hai qualche suggerimento per|consigli per)\s+(.+)\?",
                r"(ricordi se|hai informazioni su|sai qualcosa di)\s+(.+)\?"
            ],
            "comparisons": [
                r"(meglio .+ o .+|differenza tra .+ e .+)",
                r"(vantaggi di .+|svantaggi di .+)",
                r"(confronto tra .+|paragone .+)"
            ],
            "implementations": [
                r"(implementare|sviluppare|creare)\s+(.+)",
                r"(integrare .+ con .+|collegare .+ a .+)",
                r"(setup di .+|configurare .+)"
            ]
        }

    async def analyze_message(self, message: str, project: str = "auto") -> List[MemoryTrigger]:
        """Analizza un messaggio e determina quali trigger attivare"""
        triggers = []
        message_lower = message.lower()
        
        # 1. Analizza per auto-save
        save_triggers = await self._detect_save_triggers(message, project)
        triggers.extend(save_triggers)
        
        # 2. Analizza per auto-search
        search_triggers = await self._detect_search_triggers(message, project)
        triggers.extend(search_triggers)
        
        # 3. Analizza pattern conversazionali
        pattern_triggers = await self._detect_conversation_patterns(message, project)
        triggers.extend(pattern_triggers)
        
        # 4. Aggiungi a buffer conversazione
        self.conversation_buffer.append({
            "message": message,
            "timestamp": datetime.now(),
            "triggers": triggers,
            "project": project
        })
        
        # Mantieni solo ultime 10 conversazioni
        if len(self.conversation_buffer) > 10:
            self.conversation_buffer.pop(0)
        
        return triggers

    async def _detect_save_triggers(self, message: str, project: str) -> List[MemoryTrigger]:
        """Rileva quando salvare automaticamente informazioni"""
        triggers = []
        
        for category, config in self.save_triggers.items():
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, message.lower())
                for match in matches:
                    full_match = match.group(0)
                    extracted_info = match.groups()[-1] if match.groups() else full_match
                    
                    trigger = MemoryTrigger(
                        trigger_type=TriggerType.AUTO_SAVE,
                        confidence=config["confidence"],
                        context=full_match,
                        action=f"save_{category}",
                        metadata={
                            "category": category,
                            "extracted_info": extracted_info,
                            "importance": config["importance"],
                            "project": project,
                            "pattern": pattern
                        }
                    )
                    triggers.append(trigger)
        
        return triggers

    async def _detect_search_triggers(self, message: str, project: str) -> List[MemoryTrigger]:
        """Rileva quando cercare automaticamente nella memoria"""
        triggers = []
        
        # Evita ricerche troppo frequenti
        last_search = self.last_search_time.get(project, datetime.min)
        if datetime.now() - last_search < timedelta(seconds=30):
            return triggers
        
        for category, patterns in self.search_triggers.items():
            for pattern in patterns:
                matches = re.finditer(pattern, message.lower())
                for match in matches:
                    search_query = match.groups()[-1] if match.groups() else match.group(0)
                    
                    trigger = MemoryTrigger(
                        trigger_type=TriggerType.AUTO_SEARCH,
                        confidence=0.7,
                        context=match.group(0),
                        action=f"search_{category}",
                        metadata={
                            "search_query": search_query,
                            "category": category,
                            "project": project,
                            "pattern": pattern
                        }
                    )
                    triggers.append(trigger)
        
        if triggers:
            self.last_search_time[project] = datetime.now()
        
        return triggers

    async def _detect_conversation_patterns(self, message: str, project: str) -> List[MemoryTrigger]:
        """Rileva pattern conversazionali avanzati"""
        triggers = []
        
        # Pattern: Richiesta di context enhancement
        if any(word in message.lower() for word in ["considera", "tenendo conto", "basandoti su", "ricordando"]):
            trigger = MemoryTrigger(
                trigger_type=TriggerType.CONTEXT_ENHANCEMENT,
                confidence=0.8,
                context=message[:100],
                action="enhance_with_context",
                metadata={
                    "type": "context_request",
                    "project": project
                }
            )
            triggers.append(trigger)
        
        # Pattern: Richiesta di informazioni storiche
        if any(phrase in message.lower() for phrase in ["la volta scorsa", "precedentemente", "prima", "ricordi quando"]):
            trigger = MemoryTrigger(
                trigger_type=TriggerType.AUTO_SEARCH,
                confidence=0.9,
                context=message[:100],
                action="search_historical",
                metadata={
                    "type": "historical_request",
                    "project": project,
                    "search_query": message
                }
            )
            triggers.append(trigger)
        
        return triggers

    async def execute_triggers(self, triggers: List[MemoryTrigger], project: str) -> Dict[str, List]:
        """Esegue i trigger rilevati"""
        results = {
            "saved": [],
            "searched": [],
            "enhanced": [],
            "errors": []
        }
        
        for trigger in triggers:
            try:
                if trigger.trigger_type == TriggerType.AUTO_SAVE:
                    result = await self._execute_save_trigger(trigger, project)
                    results["saved"].append(result)
                
                elif trigger.trigger_type == TriggerType.AUTO_SEARCH:
                    result = await self._execute_search_trigger(trigger, project)
                    results["searched"].append(result)
                
                elif trigger.trigger_type == TriggerType.CONTEXT_ENHANCEMENT:
                    result = await self._execute_enhancement_trigger(trigger, project)
                    results["enhanced"].append(result)
                
            except Exception as e:
                results["errors"].append({
                    "trigger": trigger.action,
                    "error": str(e)
                })
        
        return results

    async def _execute_save_trigger(self, trigger: MemoryTrigger, project: str) -> Dict:
        """Esegue un trigger di salvataggio"""
        metadata = trigger.metadata
        
        save_result = await self.mcp_server.call_tool("save_memory", {
            "text": trigger.context,
            "memory_type": f"auto_{metadata['category']}",
            "project": project,
            "importance": metadata.get("importance", 0.5),
            "tags": [
                "auto_saved",
                "smart_trigger",
                metadata["category"],
                f"confidence_{int(trigger.confidence * 100)}"
            ]
        })
        
        return {
            "trigger": trigger.action,
            "text": trigger.context,
            "confidence": trigger.confidence,
            "result": save_result
        }

    async def _execute_search_trigger(self, trigger: MemoryTrigger, project: str) -> Dict:
        """Esegue un trigger di ricerca"""
        metadata = trigger.metadata
        query = metadata.get("search_query", trigger.context)
        
        search_result = await self.mcp_server.call_tool("search_memory", {
            "query": query,
            "project": project,
            "limit": 5,
            "threshold": 0.3
        })
        
        return {
            "trigger": trigger.action,
            "query": query,
            "confidence": trigger.confidence,
            "memories_found": len(search_result.get("memories", [])),
            "result": search_result
        }

    async def _execute_enhancement_trigger(self, trigger: MemoryTrigger, project: str) -> Dict:
        """Esegue un trigger di enhancement del contesto"""
        
        # Cerca contesto rilevante per l'enhancement
        search_result = await self.mcp_server.call_tool("search_memory", {
            "query": trigger.context,
            "project": project,
            "limit": 3,
            "threshold": 0.4
        })
        
        return {
            "trigger": trigger.action,
            "context_found": len(search_result.get("memories", [])),
            "enhanced_context": search_result.get("memories", [])
        }

    def get_conversation_summary(self, project: str = None) -> Dict:
        """Restituisce un riassunto delle conversazioni e trigger"""
        relevant_conversations = [
            conv for conv in self.conversation_buffer 
            if project is None or conv["project"] == project
        ]
        
        total_triggers = sum(len(conv["triggers"]) for conv in relevant_conversations)
        trigger_types = {}
        
        for conv in relevant_conversations:
            for trigger in conv["triggers"]:
                trigger_type = trigger.trigger_type.value
                trigger_types[trigger_type] = trigger_types.get(trigger_type, 0) + 1
        
        return {
            "total_conversations": len(relevant_conversations),
            "total_triggers": total_triggers,
            "trigger_breakdown": trigger_types,
            "last_conversation": relevant_conversations[-1]["timestamp"].isoformat() if relevant_conversations else None
        }


# Demo del sistema
async def demo_smart_triggers():
    """Demo del sistema di trigger intelligenti"""
    
    # Mock MCP server per test
    class MockMCPServer:
        def __init__(self):
            self.memories = []
        
        async def call_tool(self, tool_name: str, params: Dict) -> Dict:
            if tool_name == "save_memory":
                memory = {
                    "id": len(self.memories),
                    "text": params["text"],
                    "memory_type": params["memory_type"],
                    "project": params["project"],
                    "saved": True
                }
                self.memories.append(memory)
                return {"success": True, "memory_id": memory["id"]}
            
            elif tool_name == "search_memory":
                # Ricerca mock
                query = params["query"].lower()
                results = [mem for mem in self.memories if query in mem["text"].lower()]
                return {"memories": results[:params.get("limit", 5)]}
    
    # Test del sistema
    mock_server = MockMCPServer()
    smart_triggers = SmartTriggerSystem(mock_server)
    
    print("🎯 Testing Smart Trigger System\n")
    
    # Test messages
    test_messages = [
        "Preferisco usare TypeScript per i progetti React perché offre type safety",
        "Come posso implementare authentication in React?",
        "Il mio progetto si chiama e-commerce-app e usa Next.js",
        "La soluzione è usare Redux Toolkit per state management",
        "Ricordi se abbiamo parlato di deployment su Vercel?",
        "Qual è il modo migliore per gestire le API calls?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"📝 Message {i}: {message}")
        
        # Analizza trigger
        triggers = await smart_triggers.analyze_message(message, "demo")
        print(f"🔍 Detected {len(triggers)} triggers:")
        
        for trigger in triggers:
            print(f"   - {trigger.action} (confidence: {trigger.confidence:.1f})")
        
        # Esegui trigger
        if triggers:
            results = await smart_triggers.execute_triggers(triggers, "demo")
            print(f"✅ Executed: {len(results['saved'])} saves, {len(results['searched'])} searches")
        
        print()
    
    # Riassunto finale
    summary = smart_triggers.get_conversation_summary("demo")
    print("📊 Conversation Summary:")
    print(f"   Total conversations: {summary['total_conversations']}")
    print(f"   Total triggers: {summary['total_triggers']}")
    print(f"   Trigger breakdown: {summary['trigger_breakdown']}")

if __name__ == "__main__":
    asyncio.run(demo_smart_triggers()) 