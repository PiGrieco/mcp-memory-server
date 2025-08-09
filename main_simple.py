#!/usr/bin/env python3
"""
Simple MCP Memory Server - No External Database Required
Perfect for immediate testing with Cursor
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Simple in-memory storage
MEMORY_STORE = []
EMBEDDING_CACHE = {}

class InMemoryDatabase:
    """Simple in-memory database for testing"""
    
    def __init__(self):
        self.memories = []
        self.next_id = 1
    
    async def save_memory(self, content: str, importance: float = 0.5, 
                         memory_type: str = "conversation", metadata: Dict = None) -> Dict:
        """Save memory to in-memory store"""
        memory_id = f"mem_{self.next_id:03d}"
        self.next_id += 1
        
        memory = {
            'id': memory_id,
            'content': content,
            'importance': importance,
            'memory_type': memory_type,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'created_at': time.time()
        }
        
        self.memories.append(memory)
        return memory
    
    async def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Simple text-based search"""
        query_words = query.lower().split()
        results = []
        
        for memory in self.memories:
            content_lower = memory['content'].lower()
            # Calculate simple similarity
            matches = sum(1 for word in query_words if word in content_lower)
            if matches > 0:
                similarity = matches / len(query_words)
                results.append({**memory, 'similarity': similarity})
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]

class AutoTriggerProcessor:
    """Auto-trigger processing without complex dependencies"""
    
    def __init__(self, database):
        self.db = database
        self.keywords = ['ricorda', 'nota', 'importante', 'salva', 'memorizza', 'remember']
        self.patterns = ['risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial']
    
    async def process_message(self, content: str) -> Dict:
        """Process message for auto-triggers"""
        content_lower = content.lower()
        actions = []
        
        # Keyword trigger
        found_keywords = [kw for kw in self.keywords if kw in content_lower]
        if found_keywords:
            memory = await self.db.save_memory(
                content=content,
                importance=0.8,
                memory_type='explicit_request',
                metadata={
                    'auto_triggered': True,
                    'trigger_type': 'keyword',
                    'keywords': found_keywords
                }
            )
            actions.append({
                'type': 'save_memory',
                'memory_id': memory['id'],
                'trigger': 'keyword',
                'keywords': found_keywords
            })
        
        # Pattern trigger
        found_patterns = [p for p in self.patterns if p in content_lower]
        if found_patterns:
            memory = await self.db.save_memory(
                content=content,
                importance=0.9,
                memory_type='solution',
                metadata={
                    'auto_triggered': True,
                    'trigger_type': 'pattern',
                    'patterns': found_patterns
                }
            )
            actions.append({
                'type': 'save_memory',
                'memory_id': memory['id'],
                'trigger': 'pattern',
                'patterns': found_patterns
            })
        
        # Search trigger for questions
        if any(word in content_lower for word in ['come', 'how', 'cosa', 'what', 'problema', 'problem']):
            search_results = await self.db.search_memories(content[:100])
            if search_results:
                actions.append({
                    'type': 'search_memories',
                    'results_count': len(search_results),
                    'trigger': 'semantic_search'
                })
        
        return {
            'content': content,
            'actions_triggered': actions,
            'timestamp': datetime.now().isoformat()
        }

class SimpleMCPServer:
    """Simple MCP-compatible server for immediate testing"""
    
    def __init__(self):
        self.db = InMemoryDatabase()
        self.auto_trigger = AutoTriggerProcessor(self.db)
        self.running = False
    
    async def handle_save_memory(self, content: str, **kwargs) -> Dict:
        """Handle save memory request"""
        memory = await self.db.save_memory(content, **kwargs)
        print(f"💾 Memory saved: {memory['id']}")
        print(f"   Content: {content[:80]}...")
        return {'success': True, 'memory_id': memory['id']}
    
    async def handle_search_memories(self, query: str, limit: int = 5) -> Dict:
        """Handle search memories request"""
        results = await self.db.search_memories(query, limit)
        print(f"🔍 Search '{query}': {len(results)} results")
        for result in results:
            print(f"   {result['id']}: {result['content'][:60]}... (similarity: {result['similarity']:.2f})")
        return {'success': True, 'results': results, 'count': len(results)}
    
    async def handle_auto_trigger(self, content: str) -> Dict:
        """Handle auto-trigger processing"""
        result = await self.auto_trigger.process_message(content)
        print(f"⚡ Auto-trigger processed: {len(result['actions_triggered'])} actions")
        for action in result['actions_triggered']:
            print(f"   {action['type']} ({action['trigger']})")
        return {'success': True, 'auto_trigger_result': result}
    
    async def start(self):
        """Start the simple server"""
        self.running = True
        print("🚀 Simple MCP Memory Server Started")
        print("=" * 50)
        print("✅ In-memory database ready")
        print("✅ Auto-trigger system enabled")
        print("✅ No external dependencies required")
        print(f"✅ Keywords: {self.auto_trigger.keywords}")
        print(f"✅ Patterns: {self.auto_trigger.patterns}")
        print("\n📡 Server ready for MCP connections")
        print("🎯 Test: python test_simple_server.py")
        
        # Keep running
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        finally:
            print("👋 Simple MCP Server shutdown")

# Test function
async def test_server():
    """Test the simple server"""
    server = SimpleMCPServer()
    
    print("📺 TESTING AUTO-TRIGGER SYSTEM")
    print("-" * 40)
    
    # Test messages
    test_messages = [
        "Ricorda che React usa JSX per il rendering",
        "Ho risolto il bug di CORS aggiungendo proxy nel package.json",
        "Come posso ottimizzare le performance in React?",
        "Importante: sempre validare input utente"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔸 Test {i}: {message}")
        result = await server.handle_auto_trigger(message)
    
    # Test search
    print(f"\n🔍 Testing search:")
    search_result = await server.handle_search_memories("React performance")
    
    print(f"\n📊 Summary:")
    print(f"   Total memories: {len(server.db.memories)}")
    print(f"   Auto-triggered actions: {sum(len(result['auto_trigger_result']['actions_triggered']) for result in [await server.handle_auto_trigger(msg) for msg in test_messages])}")

def main():
    """Main entry point"""
    try:
        # Run test
        asyncio.run(test_server())
        
        print(f"\n🚀 Starting server...")
        server = SimpleMCPServer()
        asyncio.run(server.start())
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
