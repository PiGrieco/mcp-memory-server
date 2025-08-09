#!/usr/bin/env python3
"""
Test Script per Auto-Trigger System
Dimostra come funzionano i trigger automatici
"""

import asyncio
import json
import time
from datetime import datetime

# Simula il sistema di auto-trigger
class AutoTriggerDemo:
    def __init__(self):
        self.trigger_keywords = ['ricorda', 'nota', 'importante', 'salva', 'memorizza']
        self.solution_patterns = ['risolto', 'solved', 'fixed', 'bug fix', 'solution']
        self.memories_saved = []
        self.searches_performed = []
    
    def analyze_message(self, message):
        """Analizza un messaggio per trigger automatici"""
        triggers_fired = []
        content_lower = message.lower()
        
        # 1. Keyword-based trigger
        found_keywords = [kw for kw in self.trigger_keywords if kw in content_lower]
        if found_keywords:
            triggers_fired.append({
                'type': 'keyword_based',
                'action': 'save_memory',
                'keywords': found_keywords,
                'content': message,
                'importance': min(0.9, 0.5 + len(found_keywords) * 0.1)
            })
        
        # 2. Pattern recognition trigger
        found_patterns = [pattern for pattern in self.solution_patterns if pattern in content_lower]
        if found_patterns:
            triggers_fired.append({
                'type': 'pattern_recognition', 
                'action': 'save_memory',
                'patterns': found_patterns,
                'content': message,
                'memory_type': 'solution',
                'importance': 0.8
            })
        
        # 3. Semantic similarity trigger (simulato)
        if len(message) > 100 and any(word in content_lower for word in ['database', 'timeout', 'error', 'bug']):
            triggers_fired.append({
                'type': 'semantic_similarity',
                'action': 'search_memories',
                'query': message[:100] + '...',
                'threshold': 0.8
            })
        
        return triggers_fired
    
    async def execute_triggers(self, triggers):
        """Esegue i trigger automatici"""
        for trigger in triggers:
            if trigger['action'] == 'save_memory':
                memory_id = f"mem_{len(self.memories_saved) + 1:03d}"
                self.memories_saved.append({
                    'id': memory_id,
                    'content': trigger['content'],
                    'importance': trigger.get('importance', 0.5),
                    'memory_type': trigger.get('memory_type', 'conversation'),
                    'trigger_type': trigger['type'],
                    'auto_triggered': True,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"💾 AUTO-SAVE: {memory_id} ({trigger['type']})")
                
            elif trigger['action'] == 'search_memories':
                # Simula ricerca di memories rilevanti
                found_memories = [
                    {"id": "mem_001", "content": "Database timeout risolto aumentando connection_timeout", "similarity": 0.85},
                    {"id": "mem_007", "content": "Bug authentication timeout fixed con retry logic", "similarity": 0.78}
                ]
                self.searches_performed.append({
                    'query': trigger['query'],
                    'results': found_memories,
                    'trigger_type': trigger['type'],
                    'timestamp': datetime.now().isoformat()
                })
                print(f"🔍 AUTO-SEARCH: Found {len(found_memories)} relevant memories")
                for mem in found_memories:
                    print(f"   📝 {mem['id']}: {mem['content'][:50]}... (similarity: {mem['similarity']})")

# Test conversazioni realistiche
test_conversations = [
    {
        "scenario": "🔤 Keyword-Based Trigger",
        "messages": [
            "Ho un problema con il database",
            "Ricorda che per fixare il timeout devi aumentare connection_timeout a 30 secondi"
        ]
    },
    {
        "scenario": "🔍 Pattern Recognition Trigger", 
        "messages": [
            "Ho un errore di autenticazione",
            "Ho risolto il bug aggiungendo retry logic nel codice di login"
        ]
    },
    {
        "scenario": "🎯 Semantic Similarity Trigger",
        "messages": [
            "Il mio database va sempre in timeout quando faccio query complesse. Ho provato a ottimizzare ma niente da fare, continua a crashare dopo 5 secondi"
        ]
    },
    {
        "scenario": "⭐ Multiple Triggers",
        "messages": [
            "Importante: ho risolto il problema critico del timeout del database",
            "Ricorda questa soluzione per il futuro: aumentare connection_timeout e aggiungere connection pooling"
        ]
    }
]

async def run_demo():
    """Esegue la demo dei trigger automatici"""
    print("🚀 DEMO AUTO-TRIGGER SYSTEM PER MCP MEMORY SERVER")
    print("=" * 60)
    
    demo = AutoTriggerDemo()
    
    for i, conversation in enumerate(test_conversations, 1):
        print(f"\n📺 TEST SCENARIO {i}: {conversation['scenario']}")
        print("-" * 50)
        
        for j, message in enumerate(conversation['messages'], 1):
            print(f"\n💬 Message {j}: {message}")
            
            # Analizza il messaggio
            triggers = demo.analyze_message(message)
            
            if triggers:
                print(f"⚡ {len(triggers)} TRIGGER(S) ATTIVATI:")
                for trigger in triggers:
                    print(f"   🎯 {trigger['type']} → {trigger['action']}")
                
                # Esegui i trigger
                await demo.execute_triggers(triggers)
            else:
                print("   😴 Nessun trigger attivato")
            
            # Piccola pausa per simulare conversazione reale
            await asyncio.sleep(0.5)
    
    # Statistiche finali
    print(f"\n📊 STATISTICHE DEMO:")
    print("=" * 30)
    print(f"💾 Memories salvate automaticamente: {len(demo.memories_saved)}")
    print(f"🔍 Ricerche automatiche eseguite: {len(demo.searches_performed)}")
    
    print(f"\n📝 MEMORIES SALVATE:")
    for memory in demo.memories_saved:
        print(f"   {memory['id']}: {memory['content'][:60]}...")
        print(f"   └─ Trigger: {memory['trigger_type']}, Importanza: {memory['importance']}")
    
    print(f"\n🔍 RICERCHE ESEGUITE:")
    for search in demo.searches_performed:
        print(f"   Query: {search['query'][:50]}...")
        print(f"   └─ Trovate {len(search['results'])} memories rilevanti")

if __name__ == "__main__":
    print("🎯 AVVIO DEMO...")
    asyncio.run(run_demo())
    print("\n✅ DEMO COMPLETATA!")
    
    print(f"\n🚀 COME USARE IL SISTEMA REALE:")
    print("1. Avvia: python main_auto.py")
    print("2. Configura Cursor: .cursor/mcp_auto.json")
    print("3. Configura Claude: claude_desktop_auto_config.json") 
    print("4. Installa Browser Extension con auto-trigger")
    print("5. Le tue conversazioni verranno automaticamente analizzate!")
    print("\n💡 Prova a dire 'Ricorda questa soluzione' in qualsiasi AI!")
