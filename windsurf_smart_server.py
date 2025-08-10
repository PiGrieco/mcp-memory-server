#!/usr/bin/env python3
"""
Smart Windsurf IDE MCP Server with Live Progress and On-Demand ML
Optimized for Windsurf Cascade AI IDE with advanced code understanding
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

# Set environment for Windsurf
os.environ.setdefault("ML_MODEL_TYPE", "huggingface")
os.environ.setdefault("HUGGINGFACE_MODEL_NAME", "PiGrieco/mcp-memory-auto-trigger-model")
os.environ.setdefault("AUTO_TRIGGER_ENABLED", "true")
os.environ.setdefault("WINDSURF_MODE", "true")
os.environ.setdefault("IDE_INTEGRATION", "true")


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


class WindsurfTriggerSystem:
    """Trigger system optimized for Windsurf Cascade IDE"""
    
    def __init__(self):
        self.keyword_triggers = [
            'ricorda', 'importante', 'nota', 'salva', 'memorizza',
            'remember', 'save', 'note', 'important', 'store',
            'bookmark', 'keep', 'archive', 'document'
        ]
        self.pattern_triggers = [
            'risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial',
            'how to', 'guide', 'step by step', 'instructions', 'tip',
            'best practice', 'workaround', 'hack', 'refactor', 'optimize'
        ]
        self.code_triggers = [
            'function', 'class', 'method', 'variable', 'algorithm',
            'pattern', 'architecture', 'design', 'implementation',
            'library', 'framework', 'api', 'endpoint', 'database'
        ]
        self.memories = {}  # Simple in-memory storage for demo
        self.memory_counter = 0
        self.ml_model = None
        self._model_loading = False
        self.windsurf_stats = {
            'code_snippets_saved': 0,
            'explanations_saved': 0,
            'searches_performed': 0,
            'ml_predictions': 0,
            'sessions': 0
        }
        
        print("✅ Windsurf trigger system inizializzato")
    
    async def _load_ml_model_lazy(self):
        """Load ML model only when needed with progress"""
        if self.ml_model is not None or self._model_loading:
            return True
        
        self._model_loading = True
        
        try:
            print(f"\n🌪️ [WINDSURF] Caricamento modello ML da Hugging Face...")
            progress = ProgressBar(5, "Windsurf ML Loading")
            
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
                print(f"\n✅ [WINDSURF] Modello trovato: {model_name}")
                print(f"   📊 Dimensione: ~{info.safetensors.total // (1024*1024) if hasattr(info, 'safetensors') and info.safetensors else 'N/A'}MB")
            except Exception as e:
                print(f"\n⚠️ [WINDSURF] Problema accesso modello: {e}")
                print("🔄 Uso modello generico di backup...")
                model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            
            # Step 3: Initialize pipeline (lightweight)
            progress.update()
            print(f"\n🧠 [WINDSURF] Inizializzazione pipeline ML...")
            
            self.ml_model = pipeline(
                "text-classification",
                model=model_name,
                return_all_scores=True,
                device=-1,  # CPU for IDE compatibility
                model_kwargs={"torch_dtype": "auto"}
            )
            
            # Step 4: Test prediction
            progress.update()
            print(f"\n🧪 [WINDSURF] Test predizione...")
            test_result = self.ml_model("Test message for Windsurf initialization")
            
            progress.update()
            print(f"\n✅ [WINDSURF] Modello ML caricato e testato!")
            print(f"   🎯 Ottimizzato per: Windsurf Cascade IDE")
            print(f"   ⚡ Device: CPU (IDE integration)")
            print(f"   🌪️ Features: Code-aware triggers")
            
            self._model_loading = False
            return True
            
        except Exception as e:
            print(f"\n❌ [WINDSURF] Errore caricamento ML: {e}")
            print("🔄 Continuando con trigger deterministici...")
            self._model_loading = False
            return False
    
    def _check_deterministic_triggers(self, message: str, code_context: Dict = None) -> Dict:
        """Fast deterministic triggers optimized for Windsurf"""
        message_lower = message.lower()
        triggers = []
        
        # Enhanced keyword triggers for Windsurf IDE
        for keyword in self.keyword_triggers:
            if keyword in message_lower:
                triggers.append(f"keyword_{keyword}")
        
        # Enhanced pattern triggers  
        for pattern in self.pattern_triggers:
            if pattern in message_lower:
                triggers.append(f"pattern_{pattern}")
        
        # Code-specific triggers for Windsurf
        for code_word in self.code_triggers:
            if code_word in message_lower:
                triggers.append(f"code_{code_word}")
        
        # Enhanced question detection for Windsurf
        question_words = [
            'come', 'cosa', 'perché', 'dove', 'quando', 'chi',
            'how', 'what', 'why', 'where', 'when', 'who', 'which',
            'can you', 'could you', 'would you', 'please explain',
            'how do i', 'how to', '?'
        ]
        if any(q in message_lower for q in question_words):
            triggers.append("question_detected")
        
        # Windsurf-specific triggers
        windsurf_words = [
            'cascade', 'ai assistant', 'code review', 'refactor',
            'explain this code', 'debug', 'error', 'exception',
            'optimize', 'improve', 'suggestion'
        ]
        if any(word in message_lower for word in windsurf_words):
            triggers.append("windsurf_specific")
        
        # Code snippet detection
        if code_context and (code_context.get('has_code') or 
                           any(lang in message_lower for lang in ['python', 'javascript', 'react', 'css', 'html', 'sql'])):
            triggers.append("code_snippet")
        
        return {
            "triggers": triggers,
            "should_save": len([t for t in triggers if any(x in t for x in ['keyword', 'pattern', 'code', 'windsurf_specific'])]) > 0,
            "should_search": any(t in triggers for t in ["question_detected"]),
            "confidence": 0.9 if triggers else 0.1,
            "code_related": any(t.startswith('code_') for t in triggers)
        }
    
    async def _check_ml_triggers(self, message: str, code_context: Dict = None) -> Dict:
        """ML-based triggers for Windsurf"""
        if self.ml_model is None:
            if not await self._load_ml_model_lazy():
                return {"ml_available": False}
        
        try:
            print(f"\n🌪️ [WINDSURF] Analisi ML del messaggio...")
            start_time = time.time()
            
            # Get ML prediction
            predictions = self.ml_model(message)
            self.windsurf_stats['ml_predictions'] += 1
            
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
            
            # Windsurf-optimized decision logic
            should_save = (best_pred['label'] == 'SAVE_MEMORY' and best_pred['score'] > 0.6) or \
                         (best_pred['score'] > 0.7 and 'NEGATIVE' not in best_pred['label'])
            
            # Enhanced search logic for code context
            should_search = (best_pred['label'] == 'SEARCH_MEMORY' and best_pred['score'] > 0.5) or \
                           ('question' in message.lower() or '?' in message or 'how' in message.lower())
            
            # Boost for code-related content
            if code_context and code_context.get('has_code'):
                if best_pred['label'] == 'SAVE_MEMORY':
                    should_save = True
                    self.windsurf_stats['code_snippets_saved'] += 1
            
            return {
                "ml_available": True,
                "ml_prediction": best_pred,
                "should_save": should_save,
                "should_search": should_search,
                "confidence": best_pred['score'],
                "ml_time": ml_time,
                "windsurf_optimized": True,
                "code_aware": code_context is not None
            }
            
        except Exception as e:
            print(f"   ❌ [WINDSURF] Errore ML: {e}")
            return {"ml_available": False, "error": str(e)}
    
    async def process_message(self, message: str, code_context: Dict = None, session_info: Dict = None) -> Dict:
        """Process message with Windsurf-optimized triggers"""
        print(f"\n📝 [WINDSURF] Processando: '{message[:50]}...'")
        
        # Track session
        if session_info:
            self.windsurf_stats['sessions'] += 1
        
        # Always do fast deterministic check first
        det_result = self._check_deterministic_triggers(message, code_context)
        print(f"⚡ [WINDSURF] Trigger deterministici: {len(det_result['triggers'])} trovati")
        
        # Do ML check for meaningful messages
        ml_result = {}
        if det_result['triggers'] or len(message) > 15:  # Windsurf threshold
            ml_result = await self._check_ml_triggers(message, code_context)
        
        # Combine results with Windsurf-specific logic
        should_save = det_result.get('should_save', False) or ml_result.get('should_save', False)
        should_search = det_result.get('should_search', False) or ml_result.get('should_search', False)
        
        actions_taken = []
        
        # Save memory if triggered
        if should_save:
            memory_type = 'code_snippet' if det_result.get('code_related') else 'explanation'
            memory_id = self._save_memory(message, code_context, session_info, memory_type)
            actions_taken.append(f"save_{memory_id}")
            
            if memory_type == 'explanation':
                self.windsurf_stats['explanations_saved'] += 1
            
            print(f"💾 [WINDSURF] Memoria salvata: {memory_id} (tipo: {memory_type})")
        
        # Search memories if triggered
        if should_search:
            results = self._search_memories(message, code_context)
            actions_taken.append(f"search_{len(results)}_results")
            self.windsurf_stats['searches_performed'] += 1
            print(f"🔍 [WINDSURF] Ricerca eseguita: {len(results)} risultati")
        
        # No action
        if not actions_taken:
            print(f"😴 [WINDSURF] Nessuna azione necessaria")
        
        return {
            "message": message,
            "deterministic": det_result,
            "ml": ml_result,
            "actions": actions_taken,
            "code_context": code_context,
            "session_info": session_info,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "saved": should_save,
                "searched": should_search,
                "triggers_count": len(det_result['triggers']),
                "ml_used": ml_result.get('ml_available', False),
                "windsurf_optimized": True,
                "code_aware": code_context is not None
            }
        }
    
    def _save_memory(self, content: str, code_context: Dict = None, session_info: Dict = None, memory_type: str = 'general') -> str:
        """Save memory (Windsurf optimized)"""
        self.memory_counter += 1
        memory_id = f"windsurf_mem_{self.memory_counter:03d}"
        
        self.memories[memory_id] = {
            "content": content,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "id": memory_id,
            "source": "windsurf_ide",
            "memory_type": memory_type,
            "code_context": code_context or {},
            "session_info": session_info or {},
            "importance": self._calculate_importance(content, code_context),
            "tags": self._extract_tags(content, code_context)
        }
        
        return memory_id
    
    def _calculate_importance(self, content: str, code_context: Dict = None) -> float:
        """Calculate importance score for Windsurf content"""
        importance_words = [
            'important', 'critical', 'urgent', 'remember', 'note',
            'key', 'essential', 'vital', 'crucial', 'significant',
            'bug', 'error', 'solution', 'fix', 'optimize'
        ]
        
        content_lower = content.lower()
        score = 0.5  # Base score
        
        # Check for importance keywords
        for word in importance_words:
            if word in content_lower:
                score += 0.1
        
        # Check for code-related content (higher importance)
        if code_context and code_context.get('has_code'):
            score += 0.2
        
        # Check for technical content
        tech_words = ['function', 'variable', 'algorithm', 'pattern', 'architecture', 'library', 'framework']
        for word in tech_words:
            if word in content_lower:
                score += 0.05
        
        # Length bonus
        if len(content) > 100:
            score += 0.1
        
        return min(1.0, score)
    
    def _extract_tags(self, content: str, code_context: Dict = None) -> List[str]:
        """Extract tags for categorization"""
        tags = []
        content_lower = content.lower()
        
        # Programming language tags
        languages = ['python', 'javascript', 'react', 'css', 'html', 'sql', 'java', 'cpp', 'go', 'rust']
        for lang in languages:
            if lang in content_lower:
                tags.append(f"lang_{lang}")
        
        # Concept tags
        concepts = ['bug', 'error', 'solution', 'tutorial', 'guide', 'tip', 'best practice']
        for concept in concepts:
            if concept in content_lower:
                tags.append(concept.replace(' ', '_'))
        
        # Code context tags
        if code_context:
            if code_context.get('has_code'):
                tags.append('code_snippet')
            if code_context.get('file_type'):
                tags.append(f"file_{code_context['file_type']}")
        
        return tags
    
    def _search_memories(self, query: str, code_context: Dict = None) -> List[Dict]:
        """Search memories (Windsurf optimized)"""
        query_lower = query.lower()
        results = []
        
        for mem_id, memory in self.memories.items():
            content_lower = memory['content'].lower()
            
            # Enhanced similarity for Windsurf
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            common_words = query_words.intersection(content_words)
            
            if common_words:
                similarity = len(common_words) / len(query_words.union(content_words))
                
                # Boost based on importance
                importance_boost = memory.get('importance', 0.5) * 0.2
                
                # Boost for code context match
                code_boost = 0.0
                if code_context and memory.get('code_context'):
                    if code_context.get('file_type') == memory['code_context'].get('file_type'):
                        code_boost = 0.1
                
                # Tag-based boost
                tag_boost = 0.0
                memory_tags = memory.get('tags', [])
                for tag in memory_tags:
                    if tag in query_lower:
                        tag_boost += 0.05
                
                final_score = similarity + importance_boost + code_boost + tag_boost
                
                if final_score > 0.1:  # Threshold
                    results.append({
                        "id": mem_id,
                        "content": memory['content'],
                        "similarity": similarity,
                        "importance": memory.get('importance', 0.5),
                        "final_score": final_score,
                        "source": "windsurf_ide",
                        "memory_type": memory.get('memory_type', 'general'),
                        "tags": memory_tags,
                        "datetime": memory.get('datetime', ''),
                        "code_context": memory.get('code_context', {})
                    })
        
        # Sort by final score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return results[:5]  # Top 5 results
    
    def get_windsurf_stats(self) -> Dict:
        """Get Windsurf-specific statistics"""
        return {
            "windsurf_stats": self.windsurf_stats,
            "memory_count": len(self.memories),
            "ml_loaded": self.ml_model is not None,
            "server_type": "windsurf_ide"
        }


async def main():
    """Main demo for Windsurf IDE integration"""
    print("🌪️ WINDSURF CASCADE IDE SMART MCP SERVER")
    print("=" * 50)
    print("💡 Funzionalità Windsurf-specifiche:")
    print("   • ⚡ Trigger deterministici ottimizzati per IDE")
    print("   • 🤖 ML on-demand per Windsurf Cascade")
    print("   • 📊 Progress bar per caricamento")
    print("   • 🔄 Uso diretto da Hugging Face")
    print("   • 💾 Auto-salvataggio memorie code-aware")
    print("   • 🔍 Ricerca intelligente con context")
    print("   • 🌪️ Integrazione nativa Windsurf")
    print("   • 🏷️ Tag-based categorization")
    
    # Initialize system
    trigger_system = WindsurfTriggerSystem()
    
    # Windsurf-specific test messages with code context
    test_scenarios = [
        {
            "message": "How do I implement a React hook for state management?",
            "code_context": {"has_code": False, "file_type": "jsx"},
            "session_info": {"file": "App.jsx", "line": 42}
        },
        {
            "message": "I solved the memory leak by properly cleaning up event listeners in useEffect",
            "code_context": {"has_code": True, "file_type": "jsx"},
            "session_info": {"file": "Component.jsx", "line": 15}
        },
        {
            "message": "Remember this CSS trick for centering elements with flexbox",
            "code_context": {"has_code": True, "file_type": "css"},
            "session_info": {"file": "styles.css", "line": 28}
        },
        {
            "message": "Can you explain async/await vs Promises in JavaScript?",
            "code_context": {"has_code": False, "file_type": "js"},
            "session_info": {"file": "utils.js", "line": 5}
        },
        {
            "message": "Good morning! Starting work on the new feature.",
            "code_context": None,
            "session_info": {"project": "webapp"}
        },
        {
            "message": "This algorithm optimizes the search function using binary search",
            "code_context": {"has_code": True, "file_type": "python"},
            "session_info": {"file": "search.py", "line": 100}
        }
    ]
    
    print(f"\n🧪 TESTING WINDSURF con {len(test_scenarios)} scenari:")
    print("=" * 50)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 WINDSURF TEST {i}/{len(test_scenarios)}:")
        print("─" * 40)
        
        start_time = time.time()
        result = await trigger_system.process_message(
            scenario['message'], 
            scenario['code_context'], 
            scenario['session_info']
        )
        total_time = time.time() - start_time
        
        summary = result['summary']
        print(f"\n📊 [WINDSURF] RISULTATO:")
        print(f"   ⏱️ Tempo totale: {total_time:.2f}s")
        print(f"   💾 Salvato: {'✅' if summary['saved'] else '❌'}")
        print(f"   🔍 Cercato: {'✅' if summary['searched'] else '❌'}")
        print(f"   🎯 Trigger: {summary['triggers_count']}")
        print(f"   🤖 ML usato: {'✅' if summary['ml_used'] else '❌'}")
        print(f"   🌪️ Windsurf ottimizzato: {'✅' if summary['windsurf_optimized'] else '❌'}")
        print(f"   💻 Code-aware: {'✅' if summary['code_aware'] else '❌'}")
        print(f"   🎬 Azioni: {len(result['actions'])}")
        
        if result['actions']:
            print(f"   📝 Azioni eseguite: {', '.join(result['actions'])}")
    
    # Show Windsurf-specific stats
    stats = trigger_system.get_windsurf_stats()
    print(f"\n📈 STATISTICHE WINDSURF:")
    print("=" * 30)
    print(f"💾 Code snippets salvati: {stats['windsurf_stats']['code_snippets_saved']}")
    print(f"📝 Spiegazioni salvate: {stats['windsurf_stats']['explanations_saved']}")
    print(f"🔍 Ricerche eseguite: {stats['windsurf_stats']['searches_performed']}")
    print(f"🤖 Predizioni ML: {stats['windsurf_stats']['ml_predictions']}")
    print(f"📚 Database size: {stats['memory_count']} memories")
    print(f"🌪️ Windsurf integration: Ready")
    
    if trigger_system.memories:
        print(f"\n📝 MEMORIE WINDSURF:")
        for mem_id, memory in trigger_system.memories.items():
            content = memory['content'][:60] + "..." if len(memory['content']) > 60 else memory['content']
            memory_type = memory.get('memory_type', 'general')
            importance = memory.get('importance', 0.5)
            tags = ', '.join(memory.get('tags', [])[:3])
            print(f"   {mem_id}: {content}")
            print(f"      Type: {memory_type}, Importance: {importance:.2f}, Tags: {tags}")
    
    print(f"\n✅ WINDSURF CASCADE IDE SERVER PRONTO!")
    print("🔧 Per integrare con Windsurf IDE:")
    print(f"   📁 Server path: {__file__}")
    print("   ⚙️ Configura nelle impostazioni Windsurf")
    print("   🚀 Riavvia Windsurf e testa con AI Cascade")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test Windsurf interrotto")
    except Exception as e:
        print(f"\n❌ Errore Windsurf: {e}")
        import traceback
        traceback.print_exc()
