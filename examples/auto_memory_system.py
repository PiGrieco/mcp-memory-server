#!/usr/bin/env python3
"""
Auto-Memory System for MCP Memory Server
Automatically saves and retrieves context during AI conversations
"""

import re
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class AutoMemorySystem:
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.auto_save_patterns = [
            # Preferenze utente
            r"preferisco|mi piace|odio|non mi piace",
            r"il mio\s+\w+\s+è|la mia\s+\w+\s+è",
            r"uso sempre|uso spesso|non uso mai",
            
            # Informazioni tecniche importanti
            r"funziona con|compatibile con|richiede",
            r"installazione:|setup:|configurazione:",
            r"errore|problema|bug|soluzione",
            
            # Progetti e contesto
            r"sto lavorando su|il mio progetto|questo progetto",
            r"il client vuole|il requisito è",
            r"deadline|scadenza|entro il",
            
            # Pattern di codice
            r"questo pattern|questa funzione|questo approccio",
            r"ho implementato|ho creato|ho sviluppato"
        ]
        
        self.context_keywords = [
            "progetto", "cliente", "deadline", "requisiti", "framework",
            "linguaggio", "database", "api", "frontend", "backend",
            "bug", "errore", "soluzione", "implementazione"
        ]

    async def process_conversation_turn(self, 
                                      user_message: str, 
                                      ai_response: str,
                                      project: str = "auto") -> Dict[str, Any]:
        """
        Processa automaticamente un turno di conversazione
        """
        results = {
            "auto_saved": [],
            "context_retrieved": [],
            "enhanced_response": ai_response
        }
        
        # 1. Auto-save informazioni importanti dal messaggio utente
        auto_saved = await self._auto_save_from_message(user_message, project)
        results["auto_saved"].extend(auto_saved)
        
        # 2. Cerca contesto rilevante PRIMA della risposta
        relevant_context = await self._search_relevant_context(user_message, project)
        results["context_retrieved"] = relevant_context
        
        # 3. Migliora la risposta con il contesto (se necessario)
        if relevant_context:
            enhanced_response = await self._enhance_response_with_context(
                ai_response, relevant_context
            )
            results["enhanced_response"] = enhanced_response
        
        # 4. Auto-save anche dalla risposta AI (se contiene info utili)
        ai_saved = await self._auto_save_from_ai_response(ai_response, project)
        results["auto_saved"].extend(ai_saved)
        
        return results

    async def _auto_save_from_message(self, message: str, project: str) -> List[Dict]:
        """Salva automaticamente informazioni importanti dal messaggio"""
        saved_items = []
        
        # Rileva preferenze
        if any(re.search(pattern, message.lower()) for pattern in self.auto_save_patterns):
            # Estrai frasi complete che contengono preferenze
            sentences = re.split(r'[.!?]+', message)
            for sentence in sentences:
                if any(re.search(pattern, sentence.lower()) for pattern in self.auto_save_patterns):
                    try:
                        result = await self.mcp_server.call_tool("save_memory", {
                            "text": sentence.strip(),
                            "memory_type": "auto_preference",
                            "project": project,
                            "importance": 0.8,
                            "tags": ["auto_saved", "preference"]
                        })
                        saved_items.append({
                            "text": sentence.strip(),
                            "type": "preference",
                            "result": result
                        })
                    except Exception as e:
                        logging.error(f"Auto-save failed: {e}")
        
        # Rileva informazioni tecniche
        tech_patterns = [
            r"uso\s+(\w+)\s+per",
            r"lavoro con\s+(\w+)",
            r"il progetto è in\s+(\w+)",
            r"stack:\s*(.+?)(?:\.|$)"
        ]
        
        for pattern in tech_patterns:
            matches = re.finditer(pattern, message.lower())
            for match in matches:
                tech_info = match.group(0)
                try:
                    result = await self.mcp_server.call_tool("save_memory", {
                        "text": tech_info,
                        "memory_type": "auto_tech",
                        "project": project,
                        "importance": 0.7,
                        "tags": ["auto_saved", "technical"]
                    })
                    saved_items.append({
                        "text": tech_info,
                        "type": "technical",
                        "result": result
                    })
                except Exception as e:
                    logging.error(f"Tech auto-save failed: {e}")
        
        return saved_items

    async def _search_relevant_context(self, message: str, project: str) -> List[Dict]:
        """Cerca automaticamente contesto rilevante"""
        relevant_memories = []
        
        # Estrai keywords chiave dal messaggio
        keywords = self._extract_keywords(message)
        
        # Cerca per ogni keyword importante
        for keyword in keywords[:3]:  # Limita a 3 ricerche per performance
            try:
                result = await self.mcp_server.call_tool("search_memory", {
                    "query": keyword,
                    "project": project,
                    "limit": 2,
                    "threshold": 0.4
                })
                
                if result.get("memories"):
                    relevant_memories.extend(result["memories"])
            except Exception as e:
                logging.error(f"Context search failed for '{keyword}': {e}")
        
        # Rimuovi duplicati e ordina per rilevanza
        unique_memories = []
        seen_texts = set()
        for memory in relevant_memories:
            if memory["text"] not in seen_texts:
                unique_memories.append(memory)
                seen_texts.add(memory["text"])
        
        return sorted(unique_memories, key=lambda x: x.get("similarity", 0), reverse=True)[:3]

    async def _enhance_response_with_context(self, response: str, context: List[Dict]) -> str:
        """Migliora la risposta con contesto rilevante"""
        if not context:
            return response
        
        # Aggiungi nota sul contesto utilizzato
        context_note = "\n\n💭 *Basato su informazioni precedenti:*\n"
        for i, memory in enumerate(context[:2], 1):
            context_note += f"   {i}. {memory['text'][:100]}...\n"
        
        return response + context_note

    async def _auto_save_from_ai_response(self, response: str, project: str) -> List[Dict]:
        """Salva soluzioni e consigli importanti dalla risposta AI"""
        saved_items = []
        
        # Rileva soluzioni tecniche
        solution_patterns = [
            r"soluzione:\s*(.+?)(?:\n|$)",
            r"risolvi con:\s*(.+?)(?:\n|$)",
            r"usa\s+(.+?)\s+per\s+(.+?)(?:\.|$)"
        ]
        
        for pattern in solution_patterns:
            matches = re.finditer(pattern, response.lower())
            for match in matches:
                solution = match.group(0)
                try:
                    result = await self.mcp_server.call_tool("save_memory", {
                        "text": f"AI suggerisce: {solution}",
                        "memory_type": "auto_solution",
                        "project": project,
                        "importance": 0.6,
                        "tags": ["auto_saved", "ai_solution"]
                    })
                    saved_items.append({
                        "text": solution,
                        "type": "ai_solution", 
                        "result": result
                    })
                except Exception as e:
                    logging.error(f"AI solution auto-save failed: {e}")
        
        return saved_items

    def _extract_keywords(self, text: str) -> List[str]:
        """Estrae keywords rilevanti dal testo"""
        # Keywords tecniche comuni
        tech_keywords = [
            "react", "vue", "angular", "python", "javascript", "typescript",
            "node", "express", "django", "flask", "mongodb", "mysql",
            "docker", "kubernetes", "aws", "azure", "git", "github"
        ]
        
        keywords = []
        text_lower = text.lower()
        
        # Trova keywords tecniche
        for keyword in tech_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Trova keywords generiche dal contesto
        for keyword in self.context_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Estrai sostantivi importanti (semplificato)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        keywords.extend([w.lower() for w in words[:5]])  # Prime 5 parole lunghe
        
        return list(set(keywords))  # Rimuovi duplicati


class EnhancedMCPServer:
    """MCP Server con memoria automatica integrata"""
    
    def __init__(self, base_mcp_server):
        self.base_server = base_mcp_server
        self.auto_memory = AutoMemorySystem(base_mcp_server)
        self.conversation_history = []

    async def process_user_message(self, 
                                 user_message: str, 
                                 project: str = "auto") -> Dict[str, Any]:
        """
        Processa un messaggio utente con memoria automatica
        """
        print(f"🧠 Processing message with auto-memory...")
        
        # 1. Cerca contesto rilevante PRIMA di generare risposta
        relevant_context = await self.auto_memory._search_relevant_context(
            user_message, project
        )
        
        # 2. Costruisci prompt migliorato per l'AI
        enhanced_prompt = self._build_enhanced_prompt(user_message, relevant_context)
        
        # 3. [Qui l'AI genererebbe la risposta usando enhanced_prompt]
        # Per questo esempio, simulo una risposta
        ai_response = await self._simulate_ai_response(enhanced_prompt)
        
        # 4. Processa il turno completo con auto-memory
        memory_results = await self.auto_memory.process_conversation_turn(
            user_message, ai_response, project
        )
        
        # 5. Salva nella cronologia conversazione
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "ai_response": memory_results["enhanced_response"],
            "auto_saved": memory_results["auto_saved"],
            "context_used": memory_results["context_retrieved"]
        })
        
        return {
            "response": memory_results["enhanced_response"],
            "context_used": memory_results["context_retrieved"],
            "auto_saved": memory_results["auto_saved"],
            "enhanced_prompt": enhanced_prompt
        }

    def _build_enhanced_prompt(self, user_message: str, context: List[Dict]) -> str:
        """Costruisce un prompt migliorato con contesto"""
        prompt = f"User message: {user_message}\n"
        
        if context:
            prompt += "\nRelevant context from memory:\n"
            for i, memory in enumerate(context, 1):
                prompt += f"{i}. {memory['text']} (type: {memory.get('memory_type', 'unknown')})\n"
            prompt += "\nPlease use this context to provide a more personalized and informed response.\n"
        
        return prompt

    async def _simulate_ai_response(self, prompt: str) -> str:
        """Simula una risposta AI (in implementazione reale, qui chiameresti l'AI)"""
        # Questa è solo una simulazione
        if "typescript" in prompt.lower():
            return "Based on your preference for TypeScript, I recommend setting up your React project with TypeScript from the start using create-react-app with the TypeScript template."
        elif "react" in prompt.lower():
            return "For React development, I suggest using functional components with hooks for better performance and code organization."
        else:
            return "I'll help you with that. Let me provide a solution based on your context."


# Esempio di utilizzo
async def demo_auto_memory():
    """Demo del sistema di memoria automatica"""
    
    # Simula MCP server (in realtà useresti il tuo server)
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
                # Ricerca semplificata
                query = params["query"].lower()
                results = []
                for memory in self.memories:
                    if query in memory["text"].lower():
                        results.append({
                            **memory,
                            "similarity": 0.8  # Simulato
                        })
                return {"memories": results[:params.get("limit", 5)]}
    
    # Test del sistema
    mock_server = MockMCPServer()
    enhanced_server = EnhancedMCPServer(mock_server)
    
    print("🎯 Testing Auto-Memory System\n")
    
    # Conversazione 1: Stabilisce preferenze
    result1 = await enhanced_server.process_user_message(
        "Preferisco usare TypeScript per i miei progetti React perché offre type safety",
        project="test"
    )
    print(f"Response 1: {result1['response']}")
    print(f"Auto-saved: {len(result1['auto_saved'])} items\n")
    
    # Conversazione 2: Dovrebbe usare il contesto
    result2 = await enhanced_server.process_user_message(
        "Come dovrei setup un nuovo progetto React?",
        project="test"
    )
    print(f"Response 2: {result2['response']}")
    print(f"Context used: {len(result2['context_used'])} memories")
    print(f"Auto-saved: {len(result2['auto_saved'])} items\n")

if __name__ == "__main__":
    asyncio.run(demo_auto_memory()) 