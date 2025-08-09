#!/usr/bin/env python3
"""
Test Server per Cursor Auto-Trigger
Server semplificato per testare l'auto-trigger direttamente in Cursor
"""

import json
import sys
import asyncio
import re
from datetime import datetime
from typing import Dict, List, Any

class SimpleMCPAutoTrigger:
    def __init__(self):
        self.memories = {}
        self.memory_counter = 0
        
        # Configurazione trigger
        self.keyword_triggers = ['ricorda', 'nota', 'importante', 'salva', 'memorizza', 'riferimento']
        self.pattern_triggers = [
            r'(?:risolto|solved|fixed)',
            r'(?:bug.*fix|bug.*risolto)',
            r'(?:tutorial|come fare|how to)',
            r'(?:soluzione|solution)'
        ]
        
        print("🎯 Simple MCP Auto-Trigger Server initialized")
        print(f"✅ Keywords: {self.keyword_triggers}")
        print(f"✅ Patterns: {len(self.pattern_triggers)} configured")

    def analyze_message(self, content: str) -> Dict:
        """Analizza il messaggio per trigger automatici"""
        content_lower = content.lower()
        triggers = []
        
        # Check keyword triggers
        for keyword in self.keyword_triggers:
            if keyword in content_lower:
                triggers.append({
                    'type': 'keyword_based',
                    'action': 'save_memory',
                    'trigger': keyword,
                    'content': content
                })
                break
        
        # Check pattern triggers
        for pattern in self.pattern_triggers:
            if re.search(pattern, content_lower):
                triggers.append({
                    'type': 'pattern_recognition', 
                    'action': 'save_memory',
                    'trigger': pattern,
                    'content': content
                })
                break
                
        return {
            'triggers': triggers,
            'should_save': len(triggers) > 0,
            'importance': self._calculate_importance(content)
        }

    def _calculate_importance(self, content: str) -> float:
        """Calcola l'importanza del contenuto"""
        importance_keywords = ['importante', 'critico', 'urgent', 'bug', 'error', 'fix', 'solution']
        score = 0.5  # Base score
        
        for keyword in importance_keywords:
            if keyword in content.lower():
                score += 0.1
                
        return min(score, 1.0)

    def save_memory(self, content: str, trigger_type: str = 'manual') -> str:
        """Salva una memoria"""
        self.memory_counter += 1
        memory_id = f"mem_{self.memory_counter:03d}"
        
        self.memories[memory_id] = {
            'id': memory_id,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'trigger_type': trigger_type,
            'importance': self._calculate_importance(content),
            'auto_triggered': trigger_type != 'manual'
        }
        
        print(f"💾 Memory saved: {memory_id}")
        print(f"   Content: {content[:50]}...")
        print(f"   Trigger: {trigger_type}")
        print(f"   Auto-triggered: {trigger_type != 'manual'}")
        
        return memory_id

    def search_memories(self, query: str) -> List[Dict]:
        """Cerca memories per query"""
        results = []
        query_lower = query.lower()
        
        for memory_id, memory in self.memories.items():
            content_lower = memory['content'].lower()
            
            # Simple similarity based on common words
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            common_words = query_words.intersection(content_words)
            
            if common_words:
                similarity = len(common_words) / max(len(query_words), len(content_words))
                if similarity > 0.2:  # Threshold
                    results.append({
                        'id': memory_id,
                        'content': memory['content'],
                        'similarity': similarity,
                        'timestamp': memory['timestamp']
                    })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:5]  # Top 5 results

    def handle_message(self, message: str) -> Dict:
        """Gestisce un messaggio in arrivo e applica trigger automatici"""
        print(f"\n📝 Processing message: {message[:50]}...")
        
        # Analizza per trigger
        analysis = self.analyze_message(message)
        actions_taken = []
        
        # Esegui azioni basate sui trigger
        for trigger in analysis['triggers']:
            if trigger['action'] == 'save_memory':
                memory_id = self.save_memory(trigger['content'], trigger['type'])
                actions_taken.append({
                    'action': 'save_memory',
                    'memory_id': memory_id,
                    'trigger_type': trigger['type']
                })
        
        return {
            'message': message,
            'analysis': analysis,
            'actions_taken': actions_taken,
            'total_memories': len(self.memories)
        }

    def get_all_memories(self) -> List[Dict]:
        """Ottieni tutte le memories"""
        return list(self.memories.values())

    def get_memory_context(self, query: str = "") -> str:
        """Ottieni contesto dalle memories per la conversazione"""
        if not self.memories:
            return "Nessuna memoria disponibile."
        
        if query:
            relevant_memories = self.search_memories(query)
            if relevant_memories:
                context = "💭 **Memorie rilevanti:**\n"
                for mem in relevant_memories[:3]:
                    context += f"- {mem['content'][:100]}...\n"
                return context
        
        # Ultime 3 memories
        recent_memories = sorted(
            self.memories.values(), 
            key=lambda x: x['timestamp'], 
            reverse=True
        )[:3]
        
        context = "💭 **Memorie recenti:**\n"
        for mem in recent_memories:
            context += f"- {mem['content'][:100]}...\n"
        
        return context

# MCP Protocol Implementation
class MCPServer:
    def __init__(self):
        self.auto_trigger = SimpleMCPAutoTrigger()
        
    async def handle_request(self, request: Dict) -> Dict:
        """Handle MCP requests"""
        method = request.get('method', '')
        params = request.get('params', {})
        
        if method == 'tools/list':
            return {
                'tools': [
                    {
                        'name': 'save_memory',
                        'description': 'Save a memory with auto-trigger support',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'content': {'type': 'string'},
                                'importance': {'type': 'number'}
                            }
                        }
                    },
                    {
                        'name': 'search_memories', 
                        'description': 'Search through saved memories',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'query': {'type': 'string'}
                            }
                        }
                    },
                    {
                        'name': 'get_memory_context',
                        'description': 'Get relevant memory context',
                        'inputSchema': {
                            'type': 'object', 
                            'properties': {
                                'query': {'type': 'string'}
                            }
                        }
                    }
                ]
            }
            
        elif method == 'tools/call':
            tool_name = params.get('name', '')
            tool_args = params.get('arguments', {})
            
            if tool_name == 'save_memory':
                content = tool_args.get('content', '')
                # Auto-analyze first
                result = self.auto_trigger.handle_message(content)
                if not result['actions_taken']:
                    # Manual save if no auto-trigger
                    memory_id = self.auto_trigger.save_memory(content, 'manual')
                    return {'content': [{'type': 'text', 'text': f'Memory saved manually: {memory_id}'}]}
                else:
                    return {'content': [{'type': 'text', 'text': f'Auto-triggered actions: {len(result["actions_taken"])}'}]}
                    
            elif tool_name == 'search_memories':
                query = tool_args.get('query', '')
                results = self.auto_trigger.search_memories(query)
                if results:
                    text = f"Found {len(results)} memories:\n"
                    for r in results:
                        text += f"- {r['content'][:100]}... (similarity: {r['similarity']:.2f})\n"
                else:
                    text = "No memories found"
                return {'content': [{'type': 'text', 'text': text}]}
                
            elif tool_name == 'get_memory_context':
                query = tool_args.get('query', '')
                context = self.auto_trigger.get_memory_context(query)
                return {'content': [{'type': 'text', 'text': context}]}
        
        return {'error': 'Unknown method'}

async def run_stdio_server():
    """Run MCP server over stdio"""
    server = MCPServer()
    
    print("🚀 MCP Auto-Trigger Server started", file=sys.stderr)
    print("✅ Ready for Cursor integration", file=sys.stderr)
    
    # Simple demo test
    print("\n📺 DEMO TEST:", file=sys.stderr)
    demo_messages = [
        "Ricorda che per fixare il CORS devi aggiungere headers",
        "Ho risolto il bug di timeout aumentando la connection_timeout", 
        "Questo è solo un messaggio normale"
    ]
    
    for msg in demo_messages:
        result = server.auto_trigger.handle_message(msg)
        print(f"Message: {msg[:40]}... → {len(result['actions_taken'])} actions", file=sys.stderr)
    
    print(f"\n💾 Total memories: {len(server.auto_trigger.memories)}", file=sys.stderr)
    print("🎯 Server ready for MCP protocol communication", file=sys.stderr)
    
    try:
        # Read JSON-RPC messages from stdin
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            try:
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                response['id'] = request.get('id')
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    'id': request.get('id') if 'request' in locals() else None,
                    'error': {'code': -1, 'message': str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        print("🛑 Server stopped", file=sys.stderr)

if __name__ == "__main__":
    try:
        asyncio.run(run_stdio_server())
    except KeyboardInterrupt:
        print("\n🛑 Server interrupted")
        sys.exit(0)
