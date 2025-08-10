#!/usr/bin/env python3
"""
Smart Replit MCP Server with Live Progress and On-Demand ML
Optimized for Replit cloud development environment
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

# Set environment for Replit
os.environ.setdefault("ML_MODEL_TYPE", "huggingface")
os.environ.setdefault("HUGGINGFACE_MODEL_NAME", "PiGrieco/mcp-memory-auto-trigger-model")
os.environ.setdefault("AUTO_TRIGGER_ENABLED", "true")
os.environ.setdefault("REPLIT_MODE", "true")
os.environ.setdefault("CLOUD_PLATFORM", "true")


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
            print()


class ReplitTriggerSystem:
    """Trigger system optimized for Replit cloud IDE"""
    
    def __init__(self):
        self.keyword_triggers = [
            'ricorda', 'importante', 'nota', 'salva', 'memorizza',
            'remember', 'save', 'note', 'important', 'store',
            'keep', 'bookmark', 'archive', 'deploy', 'share'
        ]
        self.pattern_triggers = [
            'risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial',
            'how to', 'guide', 'instructions', 'tip', 'best practice',
            'repl', 'project', 'collaboration', 'pair programming'
        ]
        self.replit_triggers = [
            'python', 'javascript', 'html', 'css', 'node.js', 'flask',
            'express', 'database', 'api', 'web app', 'bot', 'game',
            'deployment', 'hosting', 'environment', 'package', 'import'
        ]
        self.memories = {}
        self.memory_counter = 0
        self.ml_model = None
        self._model_loading = False
        self.replit_stats = {
            'repls_tracked': 0,
            'collaborations_saved': 0,
            'deployments_documented': 0,
            'ml_predictions': 0,
            'cloud_interactions': 0
        }
        
        print("✅ Replit trigger system inizializzato")
    
    async def _load_ml_model_lazy(self):
        """Load ML model for Replit cloud environment"""
        if self.ml_model is not None or self._model_loading:
            return True
        
        self._model_loading = True
        
        try:
            print(f"\n⚡ [REPLIT] Caricamento modello ML per cloud IDE...")
            progress = ProgressBar(5, "Replit ML Loading")
            
            progress.update()
            from transformers import pipeline
            
            progress.update()
            model_name = "PiGrieco/mcp-memory-auto-trigger-model"
            
            progress.update()
            print(f"\n✅ [REPLIT] Modello per cloud development")
            
            progress.update()
            self.ml_model = pipeline(
                "text-classification",
                model=model_name,
                return_all_scores=True,
                device=-1  # CPU for cloud compatibility
            )
            
            progress.update()
            print(f"\n✅ [REPLIT] Modello ML pronto per cloud coding!")
            print(f"   ☁️ Ottimizzato per: Replit cloud environment")
            print(f"   🤝 Features: Collaboration-aware triggers")
            
            self._model_loading = False
            return True
            
        except Exception as e:
            print(f"\n❌ [REPLIT] Errore ML: {e}")
            self._model_loading = False
            return False
    
    def _check_replit_triggers(self, message: str, repl_context: Dict = None) -> Dict:
        """Check Replit-specific triggers"""
        message_lower = message.lower()
        triggers = []
        
        # Replit-specific triggers
        for trigger in self.replit_triggers:
            if trigger in message_lower:
                triggers.append(f"replit_{trigger}")
        
        # Standard triggers
        for keyword in self.keyword_triggers:
            if keyword in message_lower:
                triggers.append(f"keyword_{keyword}")
        
        for pattern in self.pattern_triggers:
            if pattern in message_lower:
                triggers.append(f"pattern_{pattern}")
        
        # Collaboration triggers
        if any(word in message_lower for word in ['share', 'collaborate', 'team', 'together']):
            triggers.append("collaboration")
        
        # Deployment triggers
        if any(word in message_lower for word in ['deploy', 'host', 'publish', 'live']):
            triggers.append("deployment")
        
        return {
            "triggers": triggers,
            "should_save": len(triggers) > 0 and any('keyword' in t or 'pattern' in t or 'deployment' in t for t in triggers),
            "should_search": '?' in message or any(q in message_lower for q in ['how', 'what', 'why', 'help']),
            "replit_specific": any(t.startswith('replit_') for t in triggers)
        }
    
    async def process_message(self, message: str, repl_context: Dict = None, user_context: Dict = None) -> Dict:
        """Process message with Replit-optimized triggers"""
        self.replit_stats['cloud_interactions'] += 1
        
        print(f"\n📝 [REPLIT] Processando: '{message[:50]}...'")
        
        # Check triggers
        trigger_result = self._check_replit_triggers(message, repl_context)
        print(f"⚡ [REPLIT] Trigger trovati: {len(trigger_result['triggers'])}")
        
        # Load ML if needed
        ml_result = {}
        if trigger_result['triggers'] or len(message) > 10:
            if self.ml_model is None:
                await self._load_ml_model_lazy()
            
            if self.ml_model:
                try:
                    predictions = self.ml_model(message)
                    self.replit_stats['ml_predictions'] += 1
                    
                    if isinstance(predictions, list) and len(predictions) > 0:
                        if isinstance(predictions[0], list):
                            predictions = predictions[0]
                        best_pred = max(predictions, key=lambda x: x['score'])
                    else:
                        best_pred = {"label": "NO_ACTION", "score": 0.5}
                    
                    ml_result = {
                        "ml_available": True,
                        "prediction": best_pred,
                        "should_save": best_pred['label'] == 'SAVE_MEMORY' and best_pred['score'] > 0.6,
                        "should_search": best_pred['label'] == 'SEARCH_MEMORY' and best_pred['score'] > 0.5
                    }
                except Exception as e:
                    ml_result = {"ml_available": False, "error": str(e)}
        
        # Combine decisions
        should_save = trigger_result.get('should_save', False) or ml_result.get('should_save', False)
        should_search = trigger_result.get('should_search', False) or ml_result.get('should_search', False)
        
        actions_taken = []
        
        # Save memory if triggered
        if should_save:
            memory_type = self._determine_memory_type(message, trigger_result['triggers'])
            memory_id = self._save_memory(message, repl_context, user_context, memory_type)
            actions_taken.append(f"save_{memory_id}")
            
            # Update specific stats
            if 'collaboration' in trigger_result['triggers']:
                self.replit_stats['collaborations_saved'] += 1
            elif 'deployment' in trigger_result['triggers']:
                self.replit_stats['deployments_documented'] += 1
            
            print(f"💾 [REPLIT] Memoria salvata: {memory_id} (tipo: {memory_type})")
        
        # Search memories if triggered
        if should_search:
            results = self._search_memories(message, repl_context)
            actions_taken.append(f"search_{len(results)}_results")
            print(f"🔍 [REPLIT] Ricerca eseguita: {len(results)} risultati")
        
        if not actions_taken:
            print(f"😴 [REPLIT] Nessuna azione necessaria")
        
        return {
            "message": message,
            "trigger_result": trigger_result,
            "ml_result": ml_result,
            "actions": actions_taken,
            "repl_context": repl_context,
            "user_context": user_context,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "saved": should_save,
                "searched": should_search,
                "triggers_count": len(trigger_result['triggers']),
                "ml_used": ml_result.get('ml_available', False),
                "replit_optimized": True,
                "cloud_ready": True
            }
        }
    
    def _determine_memory_type(self, message: str, triggers: List[str]) -> str:
        """Determine the type of memory based on content and triggers"""
        message_lower = message.lower()
        
        if any('deployment' in t for t in triggers):
            return 'deployment'
        elif any('collaboration' in t for t in triggers):
            return 'collaboration'
        elif any(lang in message_lower for lang in ['python', 'javascript', 'html', 'css']):
            return 'code_snippet'
        elif any(word in message_lower for word in ['tutorial', 'guide', 'how to']):
            return 'tutorial'
        else:
            return 'general'
    
    def _save_memory(self, content: str, repl_context: Dict = None, user_context: Dict = None, memory_type: str = 'general') -> str:
        """Save memory for Replit environment"""
        self.memory_counter += 1
        memory_id = f"replit_mem_{self.memory_counter:03d}"
        
        self.memories[memory_id] = {
            "content": content,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "id": memory_id,
            "source": "replit_cloud",
            "memory_type": memory_type,
            "repl_context": repl_context or {},
            "user_context": user_context or {},
            "importance": self._calculate_importance(content, memory_type),
            "tags": self._extract_replit_tags(content, repl_context)
        }
        
        return memory_id
    
    def _calculate_importance(self, content: str, memory_type: str) -> float:
        """Calculate importance for Replit content"""
        base_scores = {
            'deployment': 0.9,
            'collaboration': 0.8,
            'code_snippet': 0.7,
            'tutorial': 0.6,
            'general': 0.5
        }
        
        score = base_scores.get(memory_type, 0.5)
        
        # Boost for important keywords
        content_lower = content.lower()
        if any(word in content_lower for word in ['important', 'critical', 'remember']):
            score += 0.1
        
        return min(1.0, score)
    
    def _extract_replit_tags(self, content: str, repl_context: Dict = None) -> List[str]:
        """Extract Replit-specific tags"""
        tags = []
        content_lower = content.lower()
        
        # Language tags
        languages = ['python', 'javascript', 'html', 'css', 'java', 'cpp', 'go', 'rust']
        for lang in languages:
            if lang in content_lower:
                tags.append(f"lang_{lang}")
        
        # Framework tags
        frameworks = ['flask', 'express', 'react', 'vue', 'django']
        for fw in frameworks:
            if fw in content_lower:
                tags.append(f"framework_{fw}")
        
        # Replit-specific tags
        if repl_context:
            if repl_context.get('repl_name'):
                tags.append(f"repl_{repl_context['repl_name']}")
            if repl_context.get('language'):
                tags.append(f"main_lang_{repl_context['language']}")
        
        # Feature tags
        features = ['deployment', 'collaboration', 'database', 'api', 'web', 'bot', 'game']
        for feature in features:
            if feature in content_lower:
                tags.append(feature)
        
        return tags
    
    def _search_memories(self, query: str, repl_context: Dict = None) -> List[Dict]:
        """Search memories with Replit context awareness"""
        query_lower = query.lower()
        results = []
        
        for mem_id, memory in self.memories.items():
            content_lower = memory['content'].lower()
            
            # Basic text similarity
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            common_words = query_words.intersection(content_words)
            
            if common_words:
                similarity = len(common_words) / len(query_words.union(content_words))
                
                # Boost for same repl
                repl_boost = 0.0
                if repl_context and memory.get('repl_context'):
                    if repl_context.get('repl_name') == memory['repl_context'].get('repl_name'):
                        repl_boost = 0.2
                
                # Importance boost
                importance_boost = memory.get('importance', 0.5) * 0.1
                
                final_score = similarity + repl_boost + importance_boost
                
                if final_score > 0.1:
                    results.append({
                        "id": mem_id,
                        "content": memory['content'],
                        "similarity": similarity,
                        "final_score": final_score,
                        "memory_type": memory.get('memory_type', 'general'),
                        "tags": memory.get('tags', []),
                        "repl_context": memory.get('repl_context', {}),
                        "datetime": memory.get('datetime', '')
                    })
        
        # Sort by final score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return results[:5]
    
    def get_replit_stats(self) -> Dict:
        """Get Replit-specific statistics"""
        return {
            "replit_stats": self.replit_stats,
            "memory_count": len(self.memories),
            "ml_loaded": self.ml_model is not None,
            "server_type": "replit_cloud"
        }


async def main():
    """Main demo for Replit integration"""
    print("⚡ REPLIT CLOUD IDE - SMART MCP SERVER")
    print("=" * 50)
    print("💡 Funzionalità Replit-specifiche:")
    print("   • ☁️ Cloud-optimized triggers")
    print("   • 🤖 ML on-demand per Replit")
    print("   • 🤝 Collaboration-aware memory")
    print("   • 🚀 Deployment documentation")
    print("   • 📱 Multi-language support")
    print("   • 🔗 Cross-repl memory sharing")
    
    # Initialize system
    trigger_system = ReplitTriggerSystem()
    
    # Replit-specific test scenarios
    test_scenarios = [
        {
            "message": "Remember to add environment variables before deploying to production",
            "repl_context": {"repl_name": "my-web-app", "language": "python"},
            "user_context": {"username": "developer", "team": "frontend"}
        },
        {
            "message": "I solved the CORS issue by configuring the Flask app properly",
            "repl_context": {"repl_name": "api-server", "language": "python"},
            "user_context": {"username": "developer", "team": "backend"}
        },
        {
            "message": "How do I share this repl with my team for collaboration?",
            "repl_context": {"repl_name": "group-project", "language": "javascript"},
            "user_context": {"username": "student", "team": "class-project"}
        },
        {
            "message": "The React component for user authentication is working great",
            "repl_context": {"repl_name": "frontend-app", "language": "javascript"},
            "user_context": {"username": "developer", "team": "frontend"}
        },
        {
            "message": "Just testing the database connection",
            "repl_context": {"repl_name": "test-db", "language": "python"},
            "user_context": {"username": "developer", "team": "backend"}
        }
    ]
    
    print(f"\n🧪 TESTING REPLIT con {len(test_scenarios)} scenari:")
    print("=" * 50)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 REPLIT TEST {i}/{len(test_scenarios)}:")
        print("─" * 40)
        
        start_time = time.time()
        result = await trigger_system.process_message(
            scenario['message'], 
            scenario['repl_context'], 
            scenario['user_context']
        )
        total_time = time.time() - start_time
        
        summary = result['summary']
        print(f"\n📊 [REPLIT] RISULTATO:")
        print(f"   ⏱️ Tempo totale: {total_time:.2f}s")
        print(f"   💾 Salvato: {'✅' if summary['saved'] else '❌'}")
        print(f"   🔍 Cercato: {'✅' if summary['searched'] else '❌'}")
        print(f"   🎯 Trigger: {summary['triggers_count']}")
        print(f"   🤖 ML usato: {'✅' if summary['ml_used'] else '❌'}")
        print(f"   ⚡ Replit ottimizzato: {'✅' if summary['replit_optimized'] else '❌'}")
        print(f"   ☁️ Cloud ready: {'✅' if summary['cloud_ready'] else '❌'}")
        print(f"   🎬 Azioni: {len(result['actions'])}")
        
        if result['actions']:
            print(f"   📝 Azioni eseguite: {', '.join(result['actions'])}")
    
    # Show Replit-specific stats
    stats = trigger_system.get_replit_stats()
    print(f"\n📈 STATISTICHE REPLIT:")
    print("=" * 30)
    print(f"🤝 Collaborazioni salvate: {stats['replit_stats']['collaborations_saved']}")
    print(f"🚀 Deployment documentati: {stats['replit_stats']['deployments_documented']}")
    print(f"🤖 Predizioni ML: {stats['replit_stats']['ml_predictions']}")
    print(f"☁️ Interazioni cloud: {stats['replit_stats']['cloud_interactions']}")
    print(f"📚 Database size: {stats['memory_count']} memories")
    print(f"⚡ Replit integration: Ready")
    
    if trigger_system.memories:
        print(f"\n📝 MEMORIE REPLIT:")
        for mem_id, memory in trigger_system.memories.items():
            content = memory['content'][:60] + "..." if len(memory['content']) > 60 else memory['content']
            memory_type = memory.get('memory_type', 'general')
            repl_name = memory.get('repl_context', {}).get('repl_name', 'N/A')
            tags = ', '.join(memory.get('tags', [])[:3])
            print(f"   {mem_id}: {content}")
            print(f"      Repl: {repl_name}, Type: {memory_type}, Tags: {tags}")
    
    print(f"\n✅ REPLIT CLOUD IDE SERVER PRONTO!")
    print("🔧 Per integrare con Replit:")
    print(f"   📁 Server path: {__file__}")
    print("   ☁️ Deploy su Replit come servizio")
    print("   🔗 Configura webhook per auto-trigger")
    print("   🤝 Abilita collaboration memory sharing")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test Replit interrotto")
    except Exception as e:
        print(f"\n❌ Errore Replit: {e}")
        import traceback
        traceback.print_exc()
