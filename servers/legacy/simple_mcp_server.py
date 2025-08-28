#!/usr/bin/env python3
"""
Simple MCP Server for immediate testing with Cursor
"""

from typing import Dict, List
import time
from datetime import datetime

# Simple MCP server implementation
class SimpleMCPServer:
    def __init__(self):
        self.memories = []
        self.auto_trigger_enabled = True
        self.trigger_keywords = ['ricorda', 'nota', 'importante', 'salva', 'memorizza']
        self.solution_patterns = ['risolto', 'solved', 'fixed', 'bug fix', 'solution']
        
    def analyze_for_auto_trigger(self, content: str) -> List[Dict]:
        """Analizza content per auto-trigger"""
        triggers = []
        content_lower = content.lower()
        
        # Keyword trigger
        found_keywords = [kw for kw in self.trigger_keywords if kw in content_lower]
        if found_keywords:
            triggers.append({
                'type': 'save_memory',
                'reason': f'Keywords found: {found_keywords}',
                'params': {
                    'content': content,
                    'importance': 0.8,
                    'memory_type': 'explicit_request',
                    'auto_triggered': True
                }
            })
        
        # Pattern trigger
        found_patterns = [pattern for pattern in self.solution_patterns if pattern in content_lower]
        if found_patterns:
            triggers.append({
                'type': 'save_memory', 
                'reason': f'Solution patterns found: {found_patterns}',
                'params': {
                    'content': content,
                    'importance': 0.9,
                    'memory_type': 'solution',
                    'auto_triggered': True
                }
            })
            
        return triggers
    
    def save_memory(self, content: str, importance: float = 0.5, memory_type: str = "conversation", auto_triggered: bool = False) -> Dict:
        """Salva una memoria"""
        memory_id = f"mem_{len(self.memories) + 1:03d}"
        memory = {
            'id': memory_id,
            'content': content,
            'importance': importance,
            'memory_type': memory_type,
            'auto_triggered': auto_triggered,
            'timestamp': datetime.now().isoformat(),
            'created_at': time.time()
        }
        
        self.memories.append(memory)
        
        print(f"💾 Memory saved: {memory_id}")
        print(f"   Content: {content[:100]}...")
        print(f"   Auto-triggered: {auto_triggered}")
        
        return {
            'success': True,
            'memory_id': memory_id,
            'message': 'Memory saved successfully'
        }
    
    def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Cerca nelle memories"""
        # Simple search by content similarity
        query_lower = query.lower()
        results = []
        
        for memory in self.memories:
            content_lower = memory['content'].lower()
            # Simple similarity check
            if any(word in content_lower for word in query_lower.split()):
                similarity = len([w for w in query_lower.split() if w in content_lower]) / len(query_lower.split())
                results.append({
                    **memory,
                    'similarity': similarity
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"🔍 Search for '{query}': found {len(results)} results")
        for result in results[:limit]:
            print(f"   {result['id']}: {result['content'][:60]}... (similarity: {result['similarity']:.2f})")
        
        return results[:limit]
    
    def handle_message(self, content: str, auto_analyze: bool = True) -> Dict:
        """Gestisce un messaggio con auto-trigger"""
        result = {
            'message_processed': True,
            'auto_triggers': [],
            'actions_executed': []
        }
        
        if auto_analyze and self.auto_trigger_enabled:
            triggers = self.analyze_for_auto_trigger(content)
            result['auto_triggers'] = triggers
            
            # Esegui i trigger
            for trigger in triggers:
                if trigger['type'] == 'save_memory':
                    save_result = self.save_memory(**trigger['params'])
                    result['actions_executed'].append({
                        'action': 'save_memory',
                        'result': save_result,
                        'reason': trigger['reason']
                    })
                    
        return result

# Server globale
server = SimpleMCPServer()

def main():
    """Entry point per il server semplice"""
    print("🚀 Simple MCP Server with Auto-Trigger")
    print("=" * 50)
    print("✅ Server ready for testing")
    print("✅ Auto-trigger enabled")
    print("✅ Keywords:", server.trigger_keywords)
    print("✅ Patterns:", server.solution_patterns)
    print()
    print("🎯 Test con questi comandi:")
    print("1. server.handle_message('Ricorda che il bug era nel timeout')")
    print("2. server.handle_message('Ho risolto il problema CORS')")
    print("3. server.search_memories('timeout bug')")
    print()
    
    # Test automatico
    print("📺 RUNNING AUTO-TEST...")
    print("-" * 30)
    
    # Test 1: Keyword trigger
    print("\n🔤 Test Keyword Trigger:")
    result1 = server.handle_message("Ricorda che per il CORS devi aggiungere Access-Control-Allow-Origin")
    print(f"Result: {len(result1['actions_executed'])} action(s) executed")
    
    # Test 2: Pattern trigger  
    print("\n🔍 Test Pattern Trigger:")
    result2 = server.handle_message("Ho risolto il bug di timeout aumentando la connection_timeout")
    print(f"Result: {len(result2['actions_executed'])} action(s) executed")
    
    # Test 3: Search
    print("\n🎯 Test Search:")
    search_results = server.search_memories("timeout CORS")
    print(f"Found: {len(search_results)} relevant memories")
    
    print(f"\n📊 Total memories: {len(server.memories)}")
    print("\n✅ Simple server test completed!")
    print("\n🔗 Now configure Cursor to use this server...")
    
    return server

if __name__ == "__main__":
    main()
