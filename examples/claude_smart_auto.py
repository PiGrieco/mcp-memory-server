#!/usr/bin/env python3
"""
Claude Desktop Smart Auto-Memory Integration
Full automation with intelligent triggers, context enhancement, and proactive suggestions
"""

import sys
import json
import asyncio
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.mcp_server import MCPServer
from examples.smart_triggers import SmartTriggerSystem, TriggerType
from examples.auto_memory_system import AutoMemorySystem

class ClaudeSmartAutoMemory:
    def __init__(self):
        self.mcp_server = None
        self.smart_triggers = None
        self.auto_memory = None
        self.project = "claude"
        self.conversation_context = []
        
    async def initialize(self):
        """Inizializza tutti i sistemi di memoria automatica"""
        print("🧠 Initializing Claude Smart Auto-Memory...")
        
        self.mcp_server = MCPServer()
        await self.mcp_server.initialize()
        
        self.smart_triggers = SmartTriggerSystem(self.mcp_server)
        self.auto_memory = AutoMemorySystem(self.mcp_server)
        
        print("✅ Claude Smart Auto-Memory ready!")
        print("🎯 Features enabled:")
        print("   - Automatic preference detection and saving")
        print("   - Smart context search before responses")
        print("   - Proactive information suggestions")
        print("   - Learning from conversation patterns")

    async def process_conversation(self, user_message: str, context: Dict = None) -> Dict[str, Any]:
        """
        Processa una conversazione con automazione completa
        """
        results = {
            "triggers_detected": [],
            "auto_saved": [],
            "context_retrieved": [],
            "enhanced_prompt": "",
            "proactive_suggestions": [],
            "conversation_analysis": {}
        }
        
        # 1. Analizza trigger intelligenti
        print(f"🔍 Analyzing message: {user_message[:100]}...")
        triggers = await self.smart_triggers.analyze_message(user_message, self.project)
        results["triggers_detected"] = [
            {
                "type": t.trigger_type.value,
                "action": t.action,
                "confidence": t.confidence,
                "context": t.context[:100]
            } for t in triggers
        ]
        
        # 2. Esegui trigger automatici
        if triggers:
            trigger_results = await self.smart_triggers.execute_triggers(triggers, self.project)
            results["auto_saved"] = trigger_results["saved"]
            
        # 3. Cerca contesto rilevante automaticamente
        relevant_context = await self.auto_memory._search_relevant_context(
            user_message, self.project
        )
        results["context_retrieved"] = relevant_context
        
        # 4. Costruisci prompt migliorato
        enhanced_prompt = await self._build_enhanced_prompt(
            user_message, relevant_context, triggers
        )
        results["enhanced_prompt"] = enhanced_prompt
        
        # 5. Genera suggerimenti proattivi
        proactive_suggestions = await self._generate_proactive_suggestions(
            user_message, relevant_context
        )
        results["proactive_suggestions"] = proactive_suggestions
        
        # 6. Analizza conversazione per pattern
        conversation_analysis = await self._analyze_conversation_patterns()
        results["conversation_analysis"] = conversation_analysis
        
        # 7. Salva contesto conversazione
        self.conversation_context.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "triggers": len(triggers),
            "context_used": len(relevant_context),
            "auto_saved": len(results["auto_saved"])
        })
        
        # Mantieni solo ultime 20 conversazioni
        if len(self.conversation_context) > 20:
            self.conversation_context.pop(0)
            
        return results

    async def _build_enhanced_prompt(self, 
                                   user_message: str, 
                                   context: List[Dict], 
                                   triggers: List) -> str:
        """Costruisce un prompt super-enhanced con tutto il contesto"""
        
        prompt_parts = [f"User message: {user_message}"]
        
        # Aggiungi contesto dalla memoria
        if context:
            prompt_parts.append("\n🧠 RELEVANT MEMORY CONTEXT:")
            for i, memory in enumerate(context[:3], 1):
                memory_type = memory.get('memory_type', 'unknown')
                confidence = memory.get('similarity', 0)
                prompt_parts.append(
                    f"   {i}. [{memory_type}] {memory['text']} "
                    f"(relevance: {confidence:.2f})"
                )
        
        # Aggiungi informazioni sui trigger rilevati
        if triggers:
            high_confidence_triggers = [t for t in triggers if t.confidence > 0.7]
            if high_confidence_triggers:
                prompt_parts.append("\n🎯 DETECTED PATTERNS:")
                for trigger in high_confidence_triggers:
                    prompt_parts.append(
                        f"   - {trigger.action}: {trigger.context[:50]}... "
                        f"(confidence: {trigger.confidence:.1f})"
                    )
        
        # Aggiungi contesto conversazione recente
        recent_context = self._get_recent_conversation_context()
        if recent_context:
            prompt_parts.append(f"\n💬 RECENT CONVERSATION CONTEXT:\n{recent_context}")
        
        prompt_parts.append(
            "\nPlease provide a response that:\n"
            "1. Uses the memory context to be more personalized\n"
            "2. Acknowledges detected patterns when relevant\n"
            "3. Builds on recent conversation history\n"
            "4. Suggests saving important new information when appropriate"
        )
        
        return "\n".join(prompt_parts)

    async def _generate_proactive_suggestions(self, 
                                            user_message: str, 
                                            context: List[Dict]) -> List[Dict]:
        """Genera suggerimenti proattivi basati su pattern e contesto"""
        suggestions = []
        
        # Suggerimenti basati su pattern mancanti
        if "setup" in user_message.lower() or "configure" in user_message.lower():
            # Cerca configurazioni simili
            similar_setups = await self.mcp_server.call_tool("search_memory", {
                "query": "configuration setup install",
                "project": self.project,
                "limit": 3,
                "threshold": 0.3
            })
            
            if similar_setups.get("memories"):
                suggestions.append({
                    "type": "similar_setup",
                    "message": "Found similar configurations from your past projects",
                    "memories": similar_setups["memories"][:2]
                })
        
        # Suggerimenti per pattern di preferenze
        if any(word in user_message.lower() for word in ["recommend", "suggest", "best"]):
            preferences = await self.mcp_server.call_tool("search_memory", {
                "query": "preferisco uso sempre",
                "project": self.project,
                "limit": 5,
                "threshold": 0.4
            })
            
            if preferences.get("memories"):
                suggestions.append({
                    "type": "preference_based",
                    "message": "Based on your stated preferences",
                    "memories": preferences["memories"][:3]
                })
        
        # Suggerimenti per problemi simili
        if any(word in user_message.lower() for word in ["error", "problem", "issue", "bug"]):
            solutions = await self.mcp_server.call_tool("search_memory", {
                "query": "soluzione risolto problema errore",
                "project": self.project,
                "limit": 3,
                "threshold": 0.3
            })
            
            if solutions.get("memories"):
                suggestions.append({
                    "type": "similar_problem",
                    "message": "You've solved similar problems before",
                    "memories": solutions["memories"][:2]
                })
        
        return suggestions

    async def _analyze_conversation_patterns(self) -> Dict[str, Any]:
        """Analizza pattern nelle conversazioni recenti"""
        if len(self.conversation_context) < 3:
            return {}
        
        recent = self.conversation_context[-10:]  # Ultime 10 conversazioni
        
        # Analizza frequenza di trigger
        total_triggers = sum(conv["triggers"] for conv in recent)
        avg_triggers = total_triggers / len(recent) if recent else 0
        
        # Analizza utilizzo del contesto
        total_context = sum(conv["context_used"] for conv in recent)
        avg_context = total_context / len(recent) if recent else 0
        
        # Analizza auto-save
        total_saved = sum(conv["auto_saved"] for conv in recent)
        
        # Rileva pattern di domande frequenti
        frequent_topics = await self._detect_frequent_topics(recent)
        
        return {
            "conversation_count": len(recent),
            "avg_triggers_per_conversation": round(avg_triggers, 2),
            "avg_context_usage": round(avg_context, 2),
            "total_auto_saved": total_saved,
            "frequent_topics": frequent_topics,
            "memory_efficiency": "high" if avg_context > 1 else "medium" if avg_context > 0 else "low"
        }

    async def _detect_frequent_topics(self, conversations: List[Dict]) -> List[str]:
        """Rileva argomenti frequenti nelle conversazioni"""
        # Estrai parole chiave tecniche comuni
        tech_words = []
        for conv in conversations:
            message = conv.get("user_message", "").lower()
            words = re.findall(r'\b(react|python|javascript|typescript|docker|api|database|frontend|backend|deployment|auth|error|setup|config)\b', message)
            tech_words.extend(words)
        
        # Conta frequenze
        word_count = {}
        for word in tech_words:
            word_count[word] = word_count.get(word, 0) + 1
        
        # Restituisci i 5 più frequenti
        frequent = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
        return [word for word, count in frequent if count >= 2]

    def _get_recent_conversation_context(self) -> str:
        """Ottieni contesto delle conversazioni recenti"""
        if len(self.conversation_context) < 2:
            return ""
        
        recent = self.conversation_context[-3:]  # Ultime 3 conversazioni
        context_parts = []
        
        for i, conv in enumerate(recent, 1):
            context_parts.append(
                f"{i}. {conv['user_message'][:80]}... "
                f"(triggers: {conv['triggers']}, context: {conv['context_used']})"
            )
        
        return "\n".join(context_parts)

    async def handle_mcp_request(self, method: str, params: dict) -> dict:
        """Gestisce richieste MCP con automazione completa"""
        
        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            # Processa automaticamente se è una richiesta di conversazione
            if tool_name not in ["save_memory", "search_memory", "health_check"]:
                # Cerca input dell'utente
                user_input = ""
                for key in ["text", "query", "message", "prompt"]:
                    if key in tool_args:
                        user_input = tool_args[key]
                        break
                
                if user_input:
                    # Processa con automazione completa
                    auto_results = await self.process_conversation(user_input)
                    
                    # Arricchisci i parametri del tool
                    if auto_results["context_retrieved"]:
                        tool_args["_auto_context"] = auto_results["context_retrieved"]
                    
                    if auto_results["proactive_suggestions"]:
                        tool_args["_auto_suggestions"] = auto_results["proactive_suggestions"]
                    
                    # Aggiorna parametri
                    params["arguments"] = tool_args
                    
                    print(f"🚀 Enhanced {tool_name} with:")
                    print(f"   - {len(auto_results['context_retrieved'])} context memories")
                    print(f"   - {len(auto_results['auto_saved'])} auto-saved items")
                    print(f"   - {len(auto_results['proactive_suggestions'])} suggestions")
            
            # Esegui il tool originale
            result = await self.mcp_server.call_tool(tool_name, tool_args)
            return result
        
        # Per altri metodi, passa direttamente
        return await self.mcp_server.handle_request(method, params)

    def get_system_status(self) -> Dict[str, Any]:
        """Ottieni status del sistema di automazione"""
        trigger_summary = self.smart_triggers.get_conversation_summary(self.project)
        
        return {
            "auto_memory_active": True,
            "conversation_count": len(self.conversation_context),
            "trigger_system": trigger_summary,
            "recent_activity": self.conversation_context[-5:] if self.conversation_context else [],
            "features": [
                "Smart Trigger Detection",
                "Automatic Context Search", 
                "Proactive Suggestions",
                "Conversation Pattern Analysis",
                "Memory-Enhanced Responses"
            ]
        }

# Configurazione per Claude Desktop
CLAUDE_CONFIG = {
    "mcpServers": {
        "claude-smart-auto": {
            "command": "python",
            "args": [str(Path(__file__))],
            "env": {
                "MONGODB_URL": "mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin",
                "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
                "AUTO_MEMORY": "advanced",
                "SMART_TRIGGERS": "true"
            }
        }
    }
}

async def main():
    """Main entry point per Claude Desktop"""
    claude_smart = ClaudeSmartAutoMemory()
    await claude_smart.initialize()
    
    # MCP protocol loop
    try:
        while True:
            line = input()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                
                result = await claude_smart.handle_mcp_request(method, params)
                
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
        print("🛑 Claude Smart Auto-Memory stopped")

# Demo per test
async def demo_claude_smart():
    """Demo del sistema Claude Smart Auto-Memory"""
    
    # Mock server per test
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
                    "timestamp": datetime.now().isoformat()
                }
                self.memories.append(memory)
                return {"success": True, "memory_id": memory["id"]}
            
            elif tool_name == "search_memory":
                query = params["query"].lower()
                results = []
                for memory in self.memories:
                    if query in memory["text"].lower():
                        results.append({
                            **memory,
                            "similarity": 0.8
                        })
                return {"memories": results[:params.get("limit", 5)]}
        
        async def initialize(self):
            pass
    
    # Test
    print("🎯 Testing Claude Smart Auto-Memory\n")
    
    claude_smart = ClaudeSmartAutoMemory()
    claude_smart.mcp_server = MockMCPServer()
    await claude_smart.mcp_server.initialize()
    
    claude_smart.smart_triggers = SmartTriggerSystem(claude_smart.mcp_server)
    claude_smart.auto_memory = AutoMemorySystem(claude_smart.mcp_server)
    
    # Test conversazioni
    test_messages = [
        "Preferisco usare TypeScript per tutti i miei progetti React",
        "Come dovrei configurare ESLint per TypeScript?",
        "Ricordi quale setup avevamo usato per il progetto precedente?",
        "Ho un errore di CORS quando faccio API calls",
        "Qual è il modo migliore per gestire state management?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"💬 Message {i}: {message}")
        
        results = await claude_smart.process_conversation(message)
        
        print(f"🔍 Triggers detected: {len(results['triggers_detected'])}")
        print(f"💾 Auto-saved: {len(results['auto_saved'])}")
        print(f"🧠 Context retrieved: {len(results['context_retrieved'])}")
        print(f"💡 Suggestions: {len(results['proactive_suggestions'])}")
        print()
    
    # Status finale
    status = claude_smart.get_system_status()
    print("📊 Final System Status:")
    print(f"   Conversations: {status['conversation_count']}")
    print(f"   Features active: {len(status['features'])}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(demo_claude_smart())
    else:
        asyncio.run(main()) 