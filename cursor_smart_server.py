#!/usr/bin/env python3
"""
Smart Cursor MCP Server with Live Progress and On-Demand ML
Uses Hugging Face models directly without full download
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment
os.environ.setdefault("ML_MODEL_TYPE", "huggingface")
os.environ.setdefault("HUGGINGFACE_MODEL_NAME", "PiGrieco/mcp-memory-auto-trigger-model")
os.environ.setdefault("AUTO_TRIGGER_ENABLED", "true")
os.environ.setdefault("CURSOR_MODE", "true")


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


class SmartTriggerSystem:
    """Lightweight trigger system with on-demand ML"""
    
    def __init__(self):
        self.keyword_triggers = ['ricorda', 'importante', 'nota', 'salva', 'memorizza', 'remember']
        self.pattern_triggers = ['risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial']
        self.memories = {}  # Simple in-memory storage for demo
        self.memory_counter = 0
        self.ml_model = None
        self._model_loading = False
        
        print("✅ Smart trigger system inizializzato")
    
    async def _load_ml_model_lazy(self):
        """Load ML model only when needed with progress"""
        if self.ml_model is not None or self._model_loading:
            return True
        
        self._model_loading = True
        
        try:
            print(f"\n🤖 Caricamento modello ML da Hugging Face...")
            progress = ProgressBar(5, "Caricamento ML Model")
            
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
                print(f"\n✅ Modello trovato: {model_name}")
                print(f"   📊 Dimensione: ~{info.safetensors.total // (1024*1024) if hasattr(info, 'safetensors') and info.safetensors else 'N/A'}MB")
            except Exception as e:
                print(f"\n⚠️ Problema accesso modello: {e}")
                print("🔄 Uso modello generico di backup...")
                model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            
            # Step 3: Initialize pipeline (lightweight)
            progress.update()
            print(f"\n🧠 Inizializzazione pipeline ML...")
            
            self.ml_model = pipeline(
                "text-classification",
                model=model_name,
                return_all_scores=True,
                device=-1,  # CPU only for speed
                model_kwargs={"torch_dtype": "auto"}
            )
            
            # Step 4: Test prediction
            progress.update()
            print(f"\n🧪 Test predizione...")
            test_result = self.ml_model("Test message for initialization")
            
            progress.update()
            print(f"\n✅ Modello ML caricato e testato!")
            print(f"   🎯 Tipo: Text Classification")
            print(f"   ⚡ Device: CPU (ottimizzato per velocità)")
            print(f"   🎪 Labels: {len(test_result)} categorie")
            
            self._model_loading = False
            return True
            
        except Exception as e:
            print(f"\n❌ Errore caricamento ML: {e}")
            print("🔄 Continuando con trigger deterministici...")
            self._model_loading = False
            return False
    
    def _check_deterministic_triggers(self, message: str) -> Dict:
        """Fast deterministic triggers"""
        message_lower = message.lower()
        triggers = []
        
        # Keyword triggers
        for keyword in self.keyword_triggers:
            if keyword in message_lower:
                triggers.append(f"keyword_{keyword}")
        
        # Pattern triggers  
        for pattern in self.pattern_triggers:
            if pattern in message_lower:
                triggers.append(f"pattern_{pattern}")
        
        # Question detection
        if any(q in message_lower for q in ['come', 'cosa', 'perché', 'dove', 'quando', 'chi', '?']):
            triggers.append("question_detected")
        
        return {
            "triggers": triggers,
            "should_save": len([t for t in triggers if 'keyword' in t or 'pattern' in t]) > 0,
            "should_search": "question_detected" in triggers,
            "confidence": 0.9 if triggers else 0.1
        }
    
    async def _check_ml_triggers(self, message: str) -> Dict:
        """ML-based triggers with lazy loading"""
        if self.ml_model is None:
            if not await self._load_ml_model_lazy():
                return {"ml_available": False}
        
        try:
            print(f"\n🤖 Analisi ML del messaggio...")
            start_time = time.time()
            
            # Get ML prediction
            predictions = self.ml_model(message)
            
            # Handle different response formats
            if isinstance(predictions, list) and len(predictions) > 0:
                if isinstance(predictions[0], list):
                    # Multiple sequences, take first
                    predictions = predictions[0]
                
                # Find best prediction
                best_pred = max(predictions, key=lambda x: x['score'])
            else:
                # Fallback
                best_pred = {"label": "UNKNOWN", "score": 0.5}
            ml_time = time.time() - start_time
            
            print(f"   ⚡ Tempo ML: {ml_time:.2f}s")
            print(f"   🎯 Predizione: {best_pred['label']} ({best_pred['score']:.3f})")
            
            # Map to actions (simplified)
            should_save = best_pred['score'] > 0.7 and 'NEGATIVE' not in best_pred['label']
            should_search = 'question' in message.lower() or '?' in message
            
            return {
                "ml_available": True,
                "ml_prediction": best_pred,
                "should_save": should_save,
                "should_search": should_search,
                "confidence": best_pred['score'],
                "ml_time": ml_time
            }
            
        except Exception as e:
            print(f"   ❌ Errore ML: {e}")
            return {"ml_available": False, "error": str(e)}
    
    async def process_message(self, message: str) -> Dict:
        """Process message with smart triggers"""
        print(f"\n📝 Processando: '{message[:50]}...'")
        
        # Always do fast deterministic check first
        det_result = self._check_deterministic_triggers(message)
        print(f"⚡ Trigger deterministici: {len(det_result['triggers'])} trovati")
        
        # Do ML check if needed
        ml_result = {}
        if det_result['triggers'] or len(message) > 20:  # Only for meaningful messages
            ml_result = await self._check_ml_triggers(message)
        
        # Combine results
        should_save = det_result.get('should_save', False) or ml_result.get('should_save', False)
        should_search = det_result.get('should_search', False) or ml_result.get('should_search', False)
        
        actions_taken = []
        
        # Save memory if triggered
        if should_save:
            memory_id = self._save_memory(message)
            actions_taken.append(f"save_{memory_id}")
            print(f"💾 Memoria salvata: {memory_id}")
        
        # Search memories if triggered
        if should_search:
            results = self._search_memories(message)
            actions_taken.append(f"search_{len(results)}_results")
            print(f"🔍 Ricerca eseguita: {len(results)} risultati")
        
        # No action
        if not actions_taken:
            print(f"😴 Nessuna azione necessaria")
        
        return {
            "message": message,
            "deterministic": det_result,
            "ml": ml_result,
            "actions": actions_taken,
            "summary": {
                "saved": should_save,
                "searched": should_search,
                "triggers_count": len(det_result['triggers']),
                "ml_used": ml_result.get('ml_available', False)
            }
        }
    
    def _save_memory(self, content: str) -> str:
        """Save memory (simplified)"""
        self.memory_counter += 1
        memory_id = f"mem_{self.memory_counter:03d}"
        
        self.memories[memory_id] = {
            "content": content,
            "timestamp": time.time(),
            "id": memory_id
        }
        
        return memory_id
    
    def _search_memories(self, query: str) -> List[Dict]:
        """Search memories (simplified)"""
        query_lower = query.lower()
        results = []
        
        for mem_id, memory in self.memories.items():
            # Simple keyword matching
            content_lower = memory['content'].lower()
            
            # Calculate simple similarity
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            common_words = query_words.intersection(content_words)
            
            if common_words:
                similarity = len(common_words) / len(query_words.union(content_words))
                if similarity > 0.1:  # Basic threshold
                    results.append({
                        "id": mem_id,
                        "content": memory['content'],
                        "similarity": similarity
                    })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:5]  # Top 5 results


async def main():
    """Main demo function"""
    print("🚀 CURSOR SMART MCP SERVER")
    print("=" * 50)
    print("💡 Funzionalità:")
    print("   • ⚡ Trigger deterministici (istantanei)")
    print("   • 🤖 ML on-demand (carica solo quando serve)")
    print("   • 📊 Progress bar per caricamento")
    print("   • 🔄 Uso diretto da Hugging Face")
    print("   • 💾 Auto-salvataggio memorie")
    print("   • 🔍 Ricerca intelligente")
    
    # Initialize system
    trigger_system = SmartTriggerSystem()
    
    # Test messages
    test_messages = [
        "Ciao, come va?",  # No action
        "Ricorda che React hooks vanno usati solo nei componenti funzionali",  # Save
        "Ho risolto il bug di rendering aggiungendo key props ai componenti della lista",  # Save + ML
        "Come si gestisce lo stato globale in React?",  # Search
        "Importante: sempre usare useEffect per side effects",  # Save
        "Cosa significa dependency array in useEffect?"  # Search + ML
    ]
    
    print(f"\n🧪 TESTING CON {len(test_messages)} MESSAGGI:")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📋 TEST {i}/{len(test_messages)}:")
        print("─" * 30)
        
        start_time = time.time()
        result = await trigger_system.process_message(message)
        total_time = time.time() - start_time
        
        summary = result['summary']
        print(f"\n📊 RISULTATO:")
        print(f"   ⏱️ Tempo totale: {total_time:.2f}s")
        print(f"   💾 Salvato: {'✅' if summary['saved'] else '❌'}")
        print(f"   🔍 Cercato: {'✅' if summary['searched'] else '❌'}")
        print(f"   🎯 Trigger: {summary['triggers_count']}")
        print(f"   🤖 ML usato: {'✅' if summary['ml_used'] else '❌'}")
        print(f"   🎬 Azioni: {len(result['actions'])}")
        
        if result['actions']:
            print(f"   📝 Azioni eseguite: {', '.join(result['actions'])}")
    
    # Show final stats
    print(f"\n📈 STATISTICHE FINALI:")
    print("=" * 30)
    print(f"💾 Memorie salvate: {trigger_system.memory_counter}")
    print(f"🤖 ML model caricato: {'✅' if trigger_system.ml_model else '❌'}")
    print(f"📚 Database size: {len(trigger_system.memories)} memories")
    
    if trigger_system.memories:
        print(f"\n📝 MEMORIE SALVATE:")
        for mem_id, memory in trigger_system.memories.items():
            content = memory['content'][:60] + "..." if len(memory['content']) > 60 else memory['content']
            print(f"   {mem_id}: {content}")
    
    print(f"\n✅ CURSOR SERVER PRONTO!")
    print("🔧 Per integrare con Cursor:")
    print(f"   📁 Server path: {__file__}")
    print("   ⚙️ Configura in ~/.cursor/mcp_settings.json")
    print("   🚀 Riavvia Cursor e testa con Cmd+L")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrotto dall'utente")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
