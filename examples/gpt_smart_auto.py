#!/usr/bin/env python3
"""
GPT/ChatGPT Smart Auto-Memory Integration
Advanced automation with intelligent triggers, context enhancement, and proactive learning
"""

import asyncio
import json
import re
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.mcp_server import MCPServer
from examples.smart_triggers import SmartTriggerSystem
from examples.auto_memory_system import AutoMemorySystem

app = FastAPI(title="GPT Smart Auto-Memory API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
mcp_server = None
smart_triggers = None
auto_memory = None
conversation_sessions = {}

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"
    user_id: str = "gpt_user"
    context: Optional[Dict] = None

class SmartResponse(BaseModel):
    enhanced_message: str
    auto_saved: List[Dict]
    context_used: List[Dict]
    proactive_suggestions: List[Dict]
    conversation_analysis: Dict
    system_actions: List[str]

class MemoryOperation(BaseModel):
    text: str
    memory_type: str = "knowledge"
    project: str = "gpt"
    importance: float = 0.5
    tags: Optional[List[str]] = None

class SmartSearch(BaseModel):
    query: str
    project: str = "gpt"
    limit: int = 5
    include_analysis: bool = True

class GPTSmartAutoMemory:
    def __init__(self):
        self.session_contexts = {}
        self.user_profiles = {}
        
    async def initialize(self):
        """Inizializza tutti i sistemi di automazione"""
        global mcp_server, smart_triggers, auto_memory
        
        print("🧠 Initializing GPT Smart Auto-Memory...")
        
        mcp_server = MCPServer()
        await mcp_server.initialize()
        
        smart_triggers = SmartTriggerSystem(mcp_server)
        auto_memory = AutoMemorySystem(mcp_server)
        
        print("✅ GPT Smart Auto-Memory ready!")

    async def process_chat_message(self, chat: ChatMessage) -> SmartResponse:
        """Processa un messaggio chat con automazione completa"""
        
        project = f"gpt_{chat.user_id}"
        session_key = f"{chat.user_id}_{chat.session_id}"
        
        # Inizializza sessione se nuova
        if session_key not in self.session_contexts:
            self.session_contexts[session_key] = {
                "messages": [],
                "auto_saves": 0,
                "context_retrievals": 0,
                "start_time": datetime.now().isoformat()
            }
        
        session = self.session_contexts[session_key]
        
        # 1. Analizza trigger intelligenti
        triggers = await smart_triggers.analyze_message(chat.message, project)
        
        # 2. Esegui trigger automatici
        trigger_results = {"saved": [], "searched": [], "enhanced": []}
        if triggers:
            trigger_results = await smart_triggers.execute_triggers(triggers, project)
            session["auto_saves"] += len(trigger_results["saved"])
        
        # 3. Cerca contesto rilevante automaticamente
        relevant_context = await auto_memory._search_relevant_context(
            chat.message, project
        )
        if relevant_context:
            session["context_retrievals"] += 1
        
        # 4. Genera suggerimenti proattivi avanzati
        proactive_suggestions = await self._generate_advanced_suggestions(
            chat.message, relevant_context, project, session
        )
        
        # 5. Analizza pattern utente
        user_analysis = await self._analyze_user_patterns(chat.user_id, chat.message)
        
        # 6. Costruisci messaggio enhanced
        enhanced_message = await self._build_enhanced_message(
            chat.message, relevant_context, triggers, proactive_suggestions
        )
        
        # 7. Aggiorna sessione
        session["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "message": chat.message,
            "triggers": len(triggers),
            "context_used": len(relevant_context),
            "suggestions": len(proactive_suggestions)
        })
        
        # 8. Azioni di sistema automatiche
        system_actions = await self._execute_system_actions(
            chat, triggers, relevant_context
        )
        
        return SmartResponse(
            enhanced_message=enhanced_message,
            auto_saved=trigger_results["saved"],
            context_used=relevant_context,
            proactive_suggestions=proactive_suggestions,
            conversation_analysis=user_analysis,
            system_actions=system_actions
        )

    async def _generate_advanced_suggestions(self, 
                                           message: str, 
                                           context: List[Dict], 
                                           project: str,
                                           session: Dict) -> List[Dict]:
        """Genera suggerimenti proattivi avanzati"""
        suggestions = []
        
        # Analisi pattern temporali
        session_messages = session.get("messages", [])
        if len(session_messages) >= 3:
            # Rileva pattern ricorrenti
            recent_topics = [msg["message"] for msg in session_messages[-5:]]
            topic_analysis = await self._analyze_topic_patterns(recent_topics)
            
            if topic_analysis["recurring_themes"]:
                suggestions.append({
                    "type": "recurring_pattern",
                    "message": f"I notice you often discuss: {', '.join(topic_analysis['recurring_themes'])}",
                    "action": "create_topic_memory",
                    "confidence": 0.8
                })
        
        # Suggerimenti basati su gap di conoscenza
        knowledge_gaps = await self._detect_knowledge_gaps(message, context)
        if knowledge_gaps:
            suggestions.extend(knowledge_gaps)
        
        # Suggerimenti di workflow optimization
        if "same" in message.lower() or "again" in message.lower():
            workflow_suggestions = await self._suggest_workflow_optimization(
                message, project
            )
            suggestions.extend(workflow_suggestions)
        
        # Suggerimenti predittivi
        if len(session_messages) >= 2:
            predictive = await self._generate_predictive_suggestions(
                session_messages, message
            )
            suggestions.extend(predictive)
        
        return suggestions

    async def _analyze_user_patterns(self, user_id: str, message: str) -> Dict[str, Any]:
        """Analizza pattern dell'utente per personalizzazione"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "total_messages": 0,
                "preferred_topics": {},
                "communication_style": "unknown",
                "expertise_level": "unknown",
                "last_active": datetime.now().isoformat()
            }
        
        profile = self.user_profiles[user_id]
        profile["total_messages"] += 1
        profile["last_active"] = datetime.now().isoformat()
        
        # Analizza argomenti preferiti
        tech_keywords = re.findall(
            r'\b(react|vue|python|javascript|typescript|node|api|database|docker|kubernetes|aws|azure|git)\b', 
            message.lower()
        )
        for keyword in tech_keywords:
            profile["preferred_topics"][keyword] = profile["preferred_topics"].get(keyword, 0) + 1
        
        # Rileva stile di comunicazione
        if any(word in message.lower() for word in ["please", "could you", "would you"]):
            profile["communication_style"] = "polite"
        elif "?" in message:
            profile["communication_style"] = "inquisitive"
        elif any(word in message.lower() for word in ["fix", "solve", "debug"]):
            profile["communication_style"] = "problem_solver"
        
        # Rileva livello di expertise
        technical_indicators = len(re.findall(r'\b(implementation|architecture|optimization|scalability|performance)\b', message.lower()))
        if technical_indicators >= 2:
            profile["expertise_level"] = "advanced"
        elif technical_indicators >= 1:
            profile["expertise_level"] = "intermediate"
        else:
            profile["expertise_level"] = "beginner"
        
        return {
            "user_profile": profile,
            "session_analysis": {
                "message_complexity": len(message.split()),
                "technical_density": technical_indicators,
                "question_type": self._classify_question_type(message)
            }
        }

    async def _analyze_topic_patterns(self, messages: List[str]) -> Dict[str, Any]:
        """Analizza pattern negli argomenti discussi"""
        all_text = " ".join(messages).lower()
        
        # Estrai temi ricorrenti
        tech_topics = re.findall(
            r'\b(frontend|backend|database|api|authentication|deployment|testing|debugging|optimization)\b',
            all_text
        )
        
        topic_counts = {}
        for topic in tech_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        recurring_themes = [topic for topic, count in topic_counts.items() if count >= 2]
        
        return {
            "recurring_themes": recurring_themes,
            "topic_diversity": len(set(tech_topics)),
            "focus_areas": sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        }

    async def _detect_knowledge_gaps(self, message: str, context: List[Dict]) -> List[Dict]:
        """Rileva gap di conoscenza e suggerisce approfondimenti"""
        suggestions = []
        
        # Rileva richieste di spiegazione
        explanation_patterns = [
            r"what is\s+(\w+)",
            r"how does\s+(\w+)\s+work",
            r"explain\s+(\w+)",
            r"difference between\s+(\w+)\s+and\s+(\w+)"
        ]
        
        for pattern in explanation_patterns:
            matches = re.finditer(pattern, message.lower())
            for match in matches:
                concept = match.group(1)
                
                # Cerca se abbiamo già informazioni su questo concetto
                concept_info = await mcp_server.call_tool("search_memory", {
                    "query": concept,
                    "project": "gpt_knowledge",
                    "limit": 3,
                    "threshold": 0.5
                })
                
                if not concept_info.get("memories"):
                    suggestions.append({
                        "type": "knowledge_gap",
                        "message": f"Consider saving detailed explanation of '{concept}' for future reference",
                        "action": "save_explanation",
                        "target": concept,
                        "confidence": 0.7
                    })
        
        return suggestions

    async def _suggest_workflow_optimization(self, message: str, project: str) -> List[Dict]:
        """Suggerisce ottimizzazioni del workflow"""
        suggestions = []
        
        # Cerca pattern ripetitivi
        repetitive_actions = await mcp_server.call_tool("search_memory", {
            "query": "setup configure install deploy",
            "project": project,
            "limit": 10,
            "threshold": 0.3
        })
        
        if repetitive_actions.get("memories") and len(repetitive_actions["memories"]) >= 3:
            suggestions.append({
                "type": "workflow_optimization",
                "message": "You seem to repeat similar setup processes. Consider creating templates or scripts.",
                "action": "create_template",
                "memories": repetitive_actions["memories"][:3],
                "confidence": 0.6
            })
        
        return suggestions

    async def _generate_predictive_suggestions(self, 
                                             session_messages: List[Dict], 
                                             current_message: str) -> List[Dict]:
        """Genera suggerimenti predittivi basati su pattern"""
        suggestions = []
        
        # Analizza sequenze di azioni
        if len(session_messages) >= 3:
            last_messages = [msg["message"] for msg in session_messages[-3:]]
            
            # Pattern: setup -> configure -> test
            if any("setup" in msg.lower() for msg in last_messages):
                if "configure" in current_message.lower():
                    suggestions.append({
                        "type": "predictive_next_step",
                        "message": "After configuration, you'll likely want to test. I can help prepare testing guidelines.",
                        "action": "prepare_testing_info",
                        "confidence": 0.7
                    })
        
        return suggestions

    def _classify_question_type(self, message: str) -> str:
        """Classifica il tipo di domanda"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["how to", "how do", "how can"]):
            return "how_to"
        elif any(word in message_lower for word in ["what is", "what are", "what does"]):
            return "definition"
        elif any(word in message_lower for word in ["why", "because", "reason"]):
            return "explanation"
        elif any(word in message_lower for word in ["best", "better", "recommend", "suggest"]):
            return "recommendation"
        elif any(word in message_lower for word in ["error", "problem", "issue", "bug"]):
            return "troubleshooting"
        else:
            return "general"

    async def _build_enhanced_message(self, 
                                    message: str, 
                                    context: List[Dict], 
                                    triggers: List,
                                    suggestions: List[Dict]) -> str:
        """Costruisce un messaggio enhanced per GPT"""
        
        enhanced_parts = [f"Original message: {message}"]
        
        # Aggiungi contesto dalla memoria
        if context:
            enhanced_parts.append("\n🧠 RELEVANT CONTEXT FROM YOUR MEMORY:")
            for i, memory in enumerate(context[:3], 1):
                enhanced_parts.append(f"   {i}. {memory['text'][:150]}...")
        
        # Aggiungi informazioni sui trigger
        if triggers:
            auto_save_triggers = [t for t in triggers if t.trigger_type.value == "auto_save"]
            if auto_save_triggers:
                enhanced_parts.append("\n💾 AUTO-SAVED INFORMATION:")
                for trigger in auto_save_triggers[:2]:
                    enhanced_parts.append(f"   - {trigger.context[:100]}...")
        
        # Aggiungi suggerimenti proattivi
        if suggestions:
            high_confidence = [s for s in suggestions if s.get("confidence", 0) > 0.6]
            if high_confidence:
                enhanced_parts.append("\n💡 PROACTIVE SUGGESTIONS:")
                for sugg in high_confidence[:2]:
                    enhanced_parts.append(f"   - {sugg['message']}")
        
        enhanced_parts.append(
            "\nPlease respond considering the context and suggestions above. "
            "Mention when you're using remembered information."
        )
        
        return "\n".join(enhanced_parts)

    async def _execute_system_actions(self, 
                                    chat: ChatMessage, 
                                    triggers: List,
                                    context: List[Dict]) -> List[str]:
        """Esegue azioni di sistema automatiche"""
        actions = []
        
        # Auto-save definizioni importanti
        if any(word in chat.message.lower() for word in ["define", "definition", "means"]):
            actions.append("auto_save_definition")
        
        # Auto-create collegamenti tra concetti
        if len(context) >= 2:
            actions.append("create_concept_links")
        
        # Auto-suggest templates per pattern ripetitivi
        repetitive_count = len([t for t in triggers if "setup" in t.context.lower()])
        if repetitive_count >= 2:
            actions.append("suggest_template_creation")
        
        return actions

# Global instance
gpt_smart = GPTSmartAutoMemory()

@app.on_startup
async def startup():
    await gpt_smart.initialize()

@app.post("/chat", response_model=SmartResponse)
async def smart_chat(chat: ChatMessage, background_tasks: BackgroundTasks):
    """Endpoint principale per chat con automazione completa"""
    try:
        result = await gpt_smart.process_chat_message(chat)
        
        # Aggiungi task in background per ottimizzazioni
        background_tasks.add_task(optimize_memory_usage, chat.user_id)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save")
async def smart_save(memory: MemoryOperation):
    """Salva memoria con analisi automatica"""
    try:
        # Analizza automaticamente il tipo di memoria
        detected_type = await analyze_memory_type(memory.text)
        if detected_type != memory.memory_type:
            memory.memory_type = detected_type
        
        result = await mcp_server.call_tool("save_memory", {
            "text": memory.text,
            "memory_type": memory.memory_type,
            "project": memory.project,
            "importance": memory.importance,
            "tags": memory.tags or []
        })
        
        return {"success": True, "result": result, "detected_type": detected_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def smart_search(search: SmartSearch):
    """Ricerca intelligente con analisi automatica"""
    try:
        # Ricerca base
        result = await mcp_server.call_tool("search_memory", {
            "query": search.query,
            "project": search.project,
            "limit": search.limit,
            "threshold": 0.3
        })
        
        if search.include_analysis:
            # Aggiungi analisi dei risultati
            analysis = await analyze_search_results(result.get("memories", []), search.query)
            result["analysis"] = analysis
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Ottieni profilo utente con pattern analysis"""
    profile = gpt_smart.user_profiles.get(user_id, {})
    
    if profile:
        # Aggiungi analisi avanzata
        profile["insights"] = await generate_user_insights(user_id, profile)
    
    return profile

@app.get("/analytics/conversation/{session_id}")
async def get_conversation_analytics(session_id: str, user_id: str = "gpt_user"):
    """Analytics dettagliati per una sessione"""
    session_key = f"{user_id}_{session_id}"
    session = gpt_smart.session_contexts.get(session_key, {})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    analytics = await analyze_conversation_session(session)
    return analytics

# Helper functions
async def analyze_memory_type(text: str) -> str:
    """Analizza automaticamente il tipo di memoria"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["preferisco", "mi piace", "uso sempre"]):
        return "preference"
    elif any(word in text_lower for word in ["progetto", "client", "deadline"]):
        return "project_info"
    elif any(word in text_lower for word in ["soluzione", "risolto", "errore"]):
        return "solution"
    elif any(word in text_lower for word in ["configurazione", "setup", "install"]):
        return "configuration"
    else:
        return "knowledge"

async def analyze_search_results(memories: List[Dict], query: str) -> Dict[str, Any]:
    """Analizza risultati di ricerca per insights"""
    if not memories:
        return {"insight": "No memories found", "suggestions": []}
    
    # Analizza distribuzione tipi
    types = [mem.get("memory_type", "unknown") for mem in memories]
    type_distribution = {t: types.count(t) for t in set(types)}
    
    # Analizza rilevanza media
    similarities = [mem.get("similarity", 0) for mem in memories]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    
    suggestions = []
    if avg_similarity < 0.5:
        suggestions.append("Consider refining your search query for better results")
    
    if len(set(types)) == 1:
        suggestions.append(f"All results are {types[0]} type. Try broader search terms for variety")
    
    return {
        "total_results": len(memories),
        "type_distribution": type_distribution,
        "average_relevance": round(avg_similarity, 2),
        "suggestions": suggestions
    }

async def generate_user_insights(user_id: str, profile: Dict) -> Dict[str, Any]:
    """Genera insights avanzati per l'utente"""
    insights = {}
    
    # Analizza preferenze tecniche
    preferred_topics = profile.get("preferred_topics", {})
    if preferred_topics:
        top_topic = max(preferred_topics.items(), key=lambda x: x[1])
        insights["primary_interest"] = top_topic[0]
        insights["expertise_focus"] = "frontend" if top_topic[0] in ["react", "vue", "javascript"] else "backend"
    
    # Suggerimenti personalizzati
    total_messages = profile.get("total_messages", 0)
    if total_messages > 10:
        insights["engagement_level"] = "high"
        insights["recommendation"] = "Consider creating project templates based on your frequent patterns"
    elif total_messages > 5:
        insights["engagement_level"] = "medium"
        insights["recommendation"] = "Keep building your knowledge base with more specific preferences"
    else:
        insights["engagement_level"] = "new"
        insights["recommendation"] = "Share more about your preferences to get personalized suggestions"
    
    return insights

async def analyze_conversation_session(session: Dict) -> Dict[str, Any]:
    """Analizza una sessione di conversazione"""
    messages = session.get("messages", [])
    
    if not messages:
        return {"error": "No messages in session"}
    
    analytics = {
        "duration": "calculated_duration",
        "message_count": len(messages),
        "avg_triggers_per_message": sum(msg.get("triggers", 0) for msg in messages) / len(messages),
        "context_utilization": sum(msg.get("context_used", 0) for msg in messages),
        "learning_efficiency": session.get("auto_saves", 0) / len(messages) if messages else 0,
        "interaction_pattern": "determined_pattern"
    }
    
    return analytics

async def optimize_memory_usage(user_id: str):
    """Ottimizza l'utilizzo della memoria per un utente (background task)"""
    # Implementa logica di ottimizzazione
    print(f"🔧 Optimizing memory usage for user {user_id}")

if __name__ == "__main__":
    print("🚀 Starting GPT Smart Auto-Memory API...")
    print("📝 API available at: http://localhost:8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("\n🤖 Advanced Features:")
    print("   - Intelligent trigger detection")
    print("   - Proactive suggestions")
    print("   - User pattern analysis")
    print("   - Conversation analytics")
    print("   - Automatic workflow optimization")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 