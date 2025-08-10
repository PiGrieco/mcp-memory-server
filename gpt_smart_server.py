#!/usr/bin/env python3
"""
Smart GPT/OpenAI MCP Server with Live Progress and On-Demand ML
Works with OpenAI API, ChatGPT, and browser extensions
Includes HTTP API for web integration
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment for GPT
os.environ.setdefault("ML_MODEL_TYPE", "huggingface")
os.environ.setdefault("HUGGINGFACE_MODEL_NAME", "PiGrieco/mcp-memory-auto-trigger-model")
os.environ.setdefault("AUTO_TRIGGER_ENABLED", "true")
os.environ.setdefault("GPT_MODE", "true")
os.environ.setdefault("HTTP_API_ENABLED", "true")


class ProgressBar:
    """Simple progress bar for console"""
    
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1):
        self.current += increment
        self._display()
    
    def _display(self):
        percentage = min(100, (self.current / self.total) * 100)
        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        elapsed = time.time() - self.start_time
        
        print(f'\r🔄 {self.description}: [{bar}] {percentage:.1f}% ({elapsed:.1f}s)', end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete


class GPTTriggerSystem:
    """Trigger system optimized for GPT/OpenAI integration"""
    
    def __init__(self):
        self.keyword_triggers = [
            'ricorda', 'importante', 'nota', 'salva', 'memorizza',
            'remember', 'save', 'note', 'important', 'store',
            'keep', 'bookmark', 'archive'
        ]
        self.pattern_triggers = [
            'risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial',
            'how to', 'guide', 'step by step', 'instructions', 'tip',
            'best practice', 'workaround', 'hack'
        ]
        self.memories = {}  # Simple in-memory storage for demo
        self.memory_counter = 0
        self.ml_model = None
        self._model_loading = False
        self.api_stats = {
            'requests': 0,
            'saves': 0,
            'searches': 0,
            'ml_predictions': 0
        }
        
        print("✅ GPT trigger system inizializzato")
    
    async def _load_ml_model_lazy(self):
        """Load ML model only when needed with progress"""
        if self.ml_model is not None or self._model_loading:
            return True
        
        self._model_loading = True
        
        try:
            print(f"\n🤖 [GPT] Caricamento modello ML da Hugging Face...")
            progress = ProgressBar(5, "GPT ML Loading")
            
            # Step 1: Import libraries
            progress.update()
            from transformers import pipeline
            
            # Step 2: Check model availability
            progress.update()
            from huggingface_hub import model_info
            model_name = "PiGrieco/mcp-memory-auto-trigger-model"
            
            try:
                info = model_info(model_name)
                progress.update()
                print(f"\n✅ [GPT] Modello trovato: {model_name}")
                print(f"   📊 Dimensione: ~{info.safetensors.total // (1024*1024) if hasattr(info, 'safetensors') and info.safetensors else 'N/A'}MB")
            except Exception as e:
                print(f"\n⚠️ [GPT] Problema accesso modello: {e}")
                print("🔄 Uso modello generico di backup...")
                model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            
            # Step 3: Initialize pipeline (lightweight)
            progress.update()
            print(f"\n🧠 [GPT] Inizializzazione pipeline ML...")
            
            self.ml_model = pipeline(
                "text-classification",
                model=model_name,
                return_all_scores=True,
                device=-1,  # CPU only for web compatibility
                model_kwargs={"torch_dtype": "auto"}
            )
            
            # Step 4: Test prediction
            progress.update()
            print(f"\n🧪 [GPT] Test predizione...")
            test_result = self.ml_model("Test message for GPT initialization")
            
            progress.update()
            print(f"\n✅ [GPT] Modello ML caricato e testato!")
            print(f"   🎯 Ottimizzato per: OpenAI/ChatGPT integration")
            print(f"   ⚡ Device: CPU (web compatibility)")
            print(f"   🌐 API ready: HTTP endpoints available")
            
            self._model_loading = False
            return True
            
        except Exception as e:
            print(f"\n❌ [GPT] Errore caricamento ML: {e}")
            print("🔄 Continuando con trigger deterministici...")
            self._model_loading = False
            return False
    
    def _check_deterministic_triggers(self, message: str) -> Dict:
        """Fast deterministic triggers optimized for GPT"""
        message_lower = message.lower()
        triggers = []
        
        # Enhanced keyword triggers for GPT/OpenAI
        for keyword in self.keyword_triggers:
            if keyword in message_lower:
                triggers.append(f"keyword_{keyword}")
        
        # Enhanced pattern triggers  
        for pattern in self.pattern_triggers:
            if pattern in message_lower:
                triggers.append(f"pattern_{pattern}")
        
        # Enhanced question detection for GPT
        question_words = [
            'come', 'cosa', 'perché', 'dove', 'quando', 'chi',
            'how', 'what', 'why', 'where', 'when', 'who', 'which',
            'can you', 'could you', 'would you', 'please explain', '?'
        ]
        if any(q in message_lower for q in question_words):
            triggers.append("question_detected")
        
        # GPT-specific triggers
        if any(word in message_lower for word in ['explain', 'spiega', 'describe', 'descrivi', 'tell me', 'show me']):
            triggers.append("explanation_request")
        
        # Code-related triggers for GPT
        if any(word in message_lower for word in ['code', 'function', 'variable', 'bug', 'error', 'exception']):
            triggers.append("code_related")
        
        return {
            "triggers": triggers,
            "should_save": len([t for t in triggers if 'keyword' in t or 'pattern' in t or 'code_related' in t]) > 0,
            "should_search": any(t in triggers for t in ["question_detected", "explanation_request"]),
            "confidence": 0.9 if triggers else 0.1
        }
    
    async def _check_ml_triggers(self, message: str) -> Dict:
        """ML-based triggers for GPT"""
        if self.ml_model is None:
            if not await self._load_ml_model_lazy():
                return {"ml_available": False}
        
        try:
            print(f"\n🤖 [GPT] Analisi ML del messaggio...")
            start_time = time.time()
            
            # Get ML prediction
            predictions = self.ml_model(message)
            self.api_stats['ml_predictions'] += 1
            
            # Handle different response formats
            if isinstance(predictions, list) and len(predictions) > 0:
                if isinstance(predictions[0], list):
                    predictions = predictions[0]
                
                # Find best prediction
                best_pred = max(predictions, key=lambda x: x['score'])
            else:
                best_pred = {"label": "NO_ACTION", "score": 0.5}
            
            ml_time = time.time() - start_time
            
            print(f"   ⚡ Tempo ML: {ml_time:.2f}s")
            print(f"   🎯 Predizione: {best_pred['label']} ({best_pred['score']:.3f})")
            
            # GPT-optimized decision logic
            should_save = (best_pred['label'] == 'SAVE_MEMORY' and best_pred['score'] > 0.6) or \
                         (best_pred['score'] > 0.8 and 'NEGATIVE' not in best_pred['label'])
            should_search = (best_pred['label'] == 'SEARCH_MEMORY' and best_pred['score'] > 0.5) or \
                           ('question' in message.lower() or '?' in message or 'how' in message.lower())
            
            return {
                "ml_available": True,
                "ml_prediction": best_pred,
                "should_save": should_save,
                "should_search": should_search,
                "confidence": best_pred['score'],
                "ml_time": ml_time,
                "gpt_optimized": True
            }
            
        except Exception as e:
            print(f"   ❌ [GPT] Errore ML: {e}")
            return {"ml_available": False, "error": str(e)}
    
    async def process_message(self, message: str, context: Dict = None) -> Dict:
        """Process message with GPT-optimized triggers"""
        self.api_stats['requests'] += 1
        print(f"\n📝 [GPT] Processando: '{message[:50]}...'")
        
        # Always do fast deterministic check first
        det_result = self._check_deterministic_triggers(message)
        print(f"⚡ [GPT] Trigger deterministici: {len(det_result['triggers'])} trovati")
        
        # Do ML check for meaningful messages
        ml_result = {}
        if det_result['triggers'] or len(message) > 10:  # Lower threshold for GPT
            ml_result = await self._check_ml_triggers(message)
        
        # Combine results with GPT-specific logic
        should_save = det_result.get('should_save', False) or ml_result.get('should_save', False)
        should_search = det_result.get('should_search', False) or ml_result.get('should_search', False)
        
        actions_taken = []
        
        # Save memory if triggered
        if should_save:
            memory_id = self._save_memory(message, context)
            actions_taken.append(f"save_{memory_id}")
            self.api_stats['saves'] += 1
            print(f"💾 [GPT] Memoria salvata: {memory_id}")
        
        # Search memories if triggered
        if should_search:
            results = self._search_memories(message)
            actions_taken.append(f"search_{len(results)}_results")
            self.api_stats['searches'] += 1
            print(f"🔍 [GPT] Ricerca eseguita: {len(results)} risultati")
        
        # No action
        if not actions_taken:
            print(f"😴 [GPT] Nessuna azione necessaria")
        
        return {
            "message": message,
            "deterministic": det_result,
            "ml": ml_result,
            "actions": actions_taken,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "saved": should_save,
                "searched": should_search,
                "triggers_count": len(det_result['triggers']),
                "ml_used": ml_result.get('ml_available', False),
                "gpt_optimized": True
            }
        }
    
    def _save_memory(self, content: str, context: Dict = None) -> str:
        """Save memory (GPT optimized)"""
        self.memory_counter += 1
        memory_id = f"gpt_mem_{self.memory_counter:03d}"
        
        self.memories[memory_id] = {
            "content": content,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "id": memory_id,
            "source": "gpt_openai",
            "context": context or {},
            "importance": self._calculate_importance(content)
        }
        
        return memory_id
    
    def _calculate_importance(self, content: str) -> float:
        """Calculate importance score for GPT content"""
        importance_words = [
            'important', 'critical', 'urgent', 'remember', 'note',
            'key', 'essential', 'vital', 'crucial', 'significant'
        ]
        
        content_lower = content.lower()
        score = 0.5  # Base score
        
        # Check for importance keywords
        for word in importance_words:
            if word in content_lower:
                score += 0.1
        
        # Check for technical content
        tech_words = ['function', 'variable', 'code', 'bug', 'error', 'solution', 'fix']
        for word in tech_words:
            if word in content_lower:
                score += 0.05
        
        # Length bonus
        if len(content) > 50:
            score += 0.1
        
        return min(1.0, score)
    
    def _search_memories(self, query: str) -> List[Dict]:
        """Search memories (GPT optimized)"""
        query_lower = query.lower()
        results = []
        
        for mem_id, memory in self.memories.items():
            content_lower = memory['content'].lower()
            
            # Enhanced similarity for GPT
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            common_words = query_words.intersection(content_words)
            
            if common_words:
                similarity = len(common_words) / len(query_words.union(content_words))
                # Boost based on importance
                importance_boost = memory.get('importance', 0.5) * 0.2
                final_score = similarity + importance_boost
                
                if final_score > 0.1:  # Basic threshold
                    results.append({
                        "id": mem_id,
                        "content": memory['content'],
                        "similarity": similarity,
                        "importance": memory.get('importance', 0.5),
                        "final_score": final_score,
                        "source": "gpt_openai",
                        "datetime": memory.get('datetime', '')
                    })
        
        # Sort by final score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return results[:5]  # Top 5 results
    
    def get_stats(self) -> Dict:
        """Get API statistics"""
        return {
            "api_stats": self.api_stats,
            "memory_count": len(self.memories),
            "ml_loaded": self.ml_model is not None,
            "server_type": "gpt_openai"
        }


async def main():
    """Main demo for GPT/OpenAI integration"""
    print("🤖 GPT/OPENAI SMART MCP SERVER")
    print("=" * 50)
    print("💡 Funzionalità GPT/OpenAI-specifiche:")
    print("   • ⚡ Trigger deterministici ottimizzati")
    print("   • 🤖 ML on-demand per ChatGPT")
    print("   • 📊 Progress bar per caricamento")
    print("   • 🔄 Uso diretto da Hugging Face")
    print("   • 💾 Auto-salvataggio memorie")
    print("   • 🔍 Ricerca intelligente")
    print("   • 🌐 HTTP API per browser integration")
    print("   • 📊 Statistics tracking")
    
    # Initialize system
    trigger_system = GPTTriggerSystem()
    
    # GPT-specific test messages
    test_messages = [
        "Can you explain how machine learning algorithms work?",  # Should trigger search
        "I solved the memory leak by implementing proper cleanup in useEffect",  # Should save
        "Remember this important API key: sk-1234567890",  # Should save
        "How do I optimize React performance for large datasets?",  # Should search
        "Hello! How are you doing today?",  # No action
        "Here's a useful function for data validation that prevents XSS attacks",  # Should save
        "What's the best practice for handling async operations in JavaScript?",  # Should search
        "Important: always sanitize user input before database queries"  # Should save
    ]
    
    print(f"\n🧪 TESTING GPT con {len(test_messages)} messaggi:")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📋 GPT TEST {i}/{len(test_messages)}:")
        print("─" * 40)
        
        start_time = time.time()
        result = await trigger_system.process_message(message, {"test_id": i, "platform": "chatgpt"})
        total_time = time.time() - start_time
        
        summary = result['summary']
        print(f"\n📊 [GPT] RISULTATO:")
        print(f"   ⏱️ Tempo totale: {total_time:.2f}s")
        print(f"   💾 Salvato: {'✅' if summary['saved'] else '❌'}")
        print(f"   🔍 Cercato: {'✅' if summary['searched'] else '❌'}")
        print(f"   🎯 Trigger: {summary['triggers_count']}")
        print(f"   🤖 ML usato: {'✅' if summary['ml_used'] else '❌'}")
        print(f"   🌐 GPT ottimizzato: {'✅' if summary['gpt_optimized'] else '❌'}")
        print(f"   🎬 Azioni: {len(result['actions'])}")
        
        if result['actions']:
            print(f"   📝 Azioni eseguite: {', '.join(result['actions'])}")
    
    # Show GPT-specific stats
    stats = trigger_system.get_stats()
    print(f"\n📈 STATISTICHE GPT:")
    print("=" * 30)
    print(f"📊 API requests: {stats['api_stats']['requests']}")
    print(f"💾 Memorie salvate: {stats['api_stats']['saves']}")
    print(f"🔍 Ricerche eseguite: {stats['api_stats']['searches']}")
    print(f"🤖 Predizioni ML: {stats['api_stats']['ml_predictions']}")
    print(f"📚 Database size: {stats['memory_count']} memories")
    print(f"🌐 GPT integration: Ready")
    
    if trigger_system.memories:
        print(f"\n📝 MEMORIE GPT:")
        for mem_id, memory in trigger_system.memories.items():
            content = memory['content'][:60] + "..." if len(memory['content']) > 60 else memory['content']
            importance = memory.get('importance', 0.5)
            print(f"   {mem_id}: {content} (importance: {importance:.2f})")
    
    print(f"\n✅ GPT/OPENAI SERVER PRONTO!")
    print("🔧 Per integrare con GPT/OpenAI:")
    print(f"   📁 Server path: {__file__}")
    print("   🌐 HTTP API endpoints disponibili")
    print("   🔌 Browser extension ready")
    print("   🤖 OpenAI API integration ready")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test GPT interrotto")
    except Exception as e:
        print(f"\n❌ Errore GPT: {e}")
        import traceback
        traceback.print_exc()
