#!/usr/bin/env python3
"""
Cursor Smart Auto-Memory Integration
Advanced automation with code-aware triggers, context enhancement, and development pattern learning
"""

import asyncio
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.mcp_server import MCPServer
from examples.smart_triggers import SmartTriggerSystem
from examples.auto_memory_system import AutoMemorySystem

class CursorSmartAutoMemory:
    def __init__(self):
        self.mcp_server = None
        self.smart_triggers = None
        self.auto_memory = None
        self.project = "cursor"
        self.workspace_path = None
        self.file_contexts = {}
        self.coding_patterns = {}
        self.active_session = {
            "start_time": datetime.now().isoformat(),
            "files_edited": [],
            "patterns_detected": [],
            "auto_saves": 0,
            "context_retrievals": 0
        }
        
    async def initialize(self, workspace_path: str = None):
        """Inizializza il sistema con consapevolezza del workspace"""
        print("🧠 Initializing Cursor Smart Auto-Memory...")
        
        self.mcp_server = MCPServer()
        await self.mcp_server.initialize()
        
        self.smart_triggers = SmartTriggerSystem(self.mcp_server)
        self.auto_memory = AutoMemorySystem(self.mcp_server)
        
        # Setup code-specific triggers
        await self._setup_code_triggers()
        
        # Detect workspace
        self.workspace_path = workspace_path or self._detect_workspace()
        if self.workspace_path:
            await self._analyze_workspace_structure()
        
        print("✅ Cursor Smart Auto-Memory ready!")
        print("🎯 Code-aware features enabled:")
        print("   - Automatic code pattern detection")
        print("   - Smart context retrieval for coding")
        print("   - Development workflow optimization")
        print("   - Project structure awareness")

    async def _setup_code_triggers(self):
        """Setup trigger specifici per il coding"""
        
        # Estendi i pattern di trigger per il coding
        code_triggers = {
            "code_patterns": {
                "patterns": [
                    r"(questo pattern|this pattern|questo approccio)\s+(.+)",
                    r"(implemento sempre|I always implement|uso sempre per)\s+(.+)",
                    r"(migliore pratica|best practice|good practice)\s*:\s*(.+)",
                    r"(antipattern|bad practice|evito sempre)\s+(.+)"
                ],
                "confidence": 0.9,
                "importance": 0.8
            },
            "library_preferences": {
                "patterns": [
                    r"(preferisco .+ a .+|prefer .+ over .+)",
                    r"(uso .+ per .+|use .+ for .+)",
                    r"(libreria migliore|best library|miglior framework)\s*:\s*(.+)",
                    r"(evito .+ perché|avoid .+ because)\s+(.+)"
                ],
                "confidence": 0.8,
                "importance": 0.7
            },
            "debugging_solutions": {
                "patterns": [
                    r"(risolto|fixed|solved)\s+(bug|error|issue|problema)\s*:\s*(.+)",
                    r"(la causa era|the cause was|il problema era)\s+(.+)",
                    r"(workaround|soluzione temporanea)\s*:\s*(.+)",
                    r"(debug tip|suggerimento debug)\s*:\s*(.+)"
                ],
                "confidence": 0.9,
                "importance": 0.9
            },
            "performance_optimizations": {
                "patterns": [
                    r"(ottimizzato|optimized|migliorato)\s+(.+)\s+(performance|velocità)",
                    r"(bottleneck|collo di bottiglia)\s*:\s*(.+)",
                    r"(caching|cache strategy)\s*:\s*(.+)",
                    r"(lazy loading|code splitting)\s+(.+)"
                ],
                "confidence": 0.8,
                "importance": 0.8
            }
        }
        
        # Aggiungi ai trigger esistenti
        self.smart_triggers.save_triggers.update(code_triggers)

    def _detect_workspace(self) -> Optional[str]:
        """Rileva automaticamente il workspace di Cursor"""
        possible_paths = [
            os.getcwd(),
            os.path.expanduser("~/"),
        ]
        
        for path in possible_paths:
            if self._is_code_project(path):
                return path
        
        return None

    def _is_code_project(self, path: str) -> bool:
        """Verifica se un path è un progetto di codice"""
        indicators = [
            "package.json", "requirements.txt", ".git", 
            "Cargo.toml", "go.mod", "pom.xml", "Gemfile"
        ]
        
        return any(os.path.exists(os.path.join(path, indicator)) for indicator in indicators)

    async def _analyze_workspace_structure(self):
        """Analizza la struttura del workspace per contesto"""
        if not self.workspace_path:
            return
        
        structure = await self._get_project_structure()
        
        # Salva informazioni sul progetto
        project_info = {
            "type": structure["project_type"],
            "main_language": structure["main_language"],
            "framework": structure.get("framework", "unknown"),
            "structure": structure["directories"]
        }
        
        await self.mcp_server.call_tool("save_memory", {
            "text": f"Project structure: {json.dumps(project_info)}",
            "memory_type": "project_structure",
            "project": self.project,
            "importance": 0.7,
            "tags": ["auto_detected", "project_info", structure["project_type"]]
        })

    async def _get_project_structure(self) -> Dict[str, Any]:
        """Analizza la struttura del progetto"""
        structure = {
            "project_type": "unknown",
            "main_language": "unknown", 
            "framework": None,
            "directories": []
        }
        
        if not self.workspace_path:
            return structure
        
        # Rileva tipo di progetto
        if os.path.exists(os.path.join(self.workspace_path, "package.json")):
            structure["project_type"] = "javascript/typescript"
            structure["main_language"] = "javascript"
            
            # Rileva framework
            package_path = os.path.join(self.workspace_path, "package.json")
            try:
                with open(package_path, 'r') as f:
                    package = json.load(f)
                    deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
                    
                    if "react" in deps:
                        structure["framework"] = "react"
                    elif "vue" in deps:
                        structure["framework"] = "vue"
                    elif "angular" in deps:
                        structure["framework"] = "angular"
                    elif "next" in deps:
                        structure["framework"] = "nextjs"
            except:
                pass
                
        elif os.path.exists(os.path.join(self.workspace_path, "requirements.txt")):
            structure["project_type"] = "python"
            structure["main_language"] = "python"
            
            # Rileva framework Python
            req_path = os.path.join(self.workspace_path, "requirements.txt")
            try:
                with open(req_path, 'r') as f:
                    requirements = f.read().lower()
                    if "django" in requirements:
                        structure["framework"] = "django"
                    elif "flask" in requirements:
                        structure["framework"] = "flask"
                    elif "fastapi" in requirements:
                        structure["framework"] = "fastapi"
            except:
                pass
        
        # Analizza directory
        try:
            dirs = [d for d in os.listdir(self.workspace_path) 
                   if os.path.isdir(os.path.join(self.workspace_path, d)) 
                   and not d.startswith('.')]
            structure["directories"] = dirs[:10]  # Limita a 10
        except:
            pass
        
        return structure

    async def process_code_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa eventi di coding con automazione completa"""
        
        results = {
            "triggers_detected": [],
            "auto_saved": [],
            "context_retrieved": [],
            "code_suggestions": [],
            "pattern_analysis": {},
            "system_actions": []
        }
        
        # Aggiorna sessione attiva
        self.active_session[f"{event_type}_count"] = self.active_session.get(f"{event_type}_count", 0) + 1
        
        if event_type == "file_edit":
            results = await self._process_file_edit(data)
        elif event_type == "code_completion":
            results = await self._process_code_completion(data)
        elif event_type == "error_fix":
            results = await self._process_error_fix(data)
        elif event_type == "search_query":
            results = await self._process_search_query(data)
        elif event_type == "chat_message":
            results = await self._process_chat_message(data)
        
        return results

    async def _process_file_edit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa modifiche ai file con analisi automatica"""
        file_path = data.get("file_path", "")
        content = data.get("content", "")
        changes = data.get("changes", "")
        
        results = {
            "triggers_detected": [],
            "auto_saved": [],
            "context_retrieved": [],
            "code_suggestions": [],
            "pattern_analysis": {}
        }
        
        # 1. Analizza pattern di codice
        code_patterns = await self._analyze_code_patterns(content, file_path)
        results["pattern_analysis"] = code_patterns
        
        # 2. Rileva trigger di coding
        if changes:
            triggers = await self.smart_triggers.analyze_message(changes, self.project)
            results["triggers_detected"] = [
                {
                    "type": t.trigger_type.value,
                    "action": t.action,
                    "confidence": t.confidence,
                    "context": t.context[:100]
                } for t in triggers
            ]
            
            # Esegui trigger
            if triggers:
                trigger_results = await self.smart_triggers.execute_triggers(triggers, self.project)
                results["auto_saved"] = trigger_results["saved"]
        
        # 3. Cerca contesto rilevante per il file
        if file_path:
            file_context = await self._get_file_context(file_path, content)
            results["context_retrieved"] = file_context
        
        # 4. Genera suggerimenti di codice
        code_suggestions = await self._generate_code_suggestions(content, file_path, code_patterns)
        results["code_suggestions"] = code_suggestions
        
        # 5. Aggiorna contesto file
        self.file_contexts[file_path] = {
            "last_edited": datetime.now().isoformat(),
            "patterns": code_patterns,
            "suggestions_generated": len(code_suggestions)
        }
        
        # 6. Auto-save informazioni importanti del file
        if code_patterns["complexity_score"] > 0.7:
            await self.mcp_server.call_tool("save_memory", {
                "text": f"Complex file pattern in {file_path}: {code_patterns['main_patterns']}",
                "memory_type": "code_pattern",
                "project": self.project,
                "importance": 0.8,
                "tags": ["auto_saved", "complex_pattern", self._get_file_type(file_path)]
            })
        
        return results

    async def _analyze_code_patterns(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analizza pattern nel codice"""
        
        patterns = {
            "file_type": self._get_file_type(file_path),
            "complexity_score": 0.0,
            "main_patterns": [],
            "imports": [],
            "functions": [],
            "classes": [],
            "design_patterns": [],
            "potential_improvements": []
        }
        
        if not content:
            return patterns
        
        lines = content.split('\n')
        
        # Analizza imports
        for line in lines:
            if re.match(r'^\s*(import|from|require)\s+', line):
                patterns["imports"].append(line.strip())
        
        # Analizza funzioni
        function_patterns = [
            r'^\s*def\s+(\w+)',  # Python
            r'^\s*function\s+(\w+)',  # JavaScript
            r'^\s*(\w+)\s*\([^)]*\)\s*{',  # JavaScript/TypeScript arrow functions
            r'^\s*async\s+(\w+)',  # Async functions
        ]
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                patterns["functions"].append(match.group(1))
        
        # Analizza classi
        class_patterns = [
            r'^\s*class\s+(\w+)',  # Python/JavaScript
            r'^\s*interface\s+(\w+)',  # TypeScript
        ]
        
        for pattern in class_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                patterns["classes"].append(match.group(1))
        
        # Rileva design patterns
        design_pattern_indicators = {
            "singleton": ["getInstance", "instance", "_instance"],
            "factory": ["create", "build", "make"],
            "observer": ["subscribe", "notify", "addEventListener"],
            "decorator": ["@", "decorator", "wrapper"],
            "strategy": ["strategy", "algorithm", "policy"]
        }
        
        content_lower = content.lower()
        for pattern_name, indicators in design_pattern_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                patterns["design_patterns"].append(pattern_name)
        
        # Calcola complessità
        complexity_indicators = [
            len(patterns["functions"]) * 0.1,
            len(patterns["classes"]) * 0.2,
            len(patterns["design_patterns"]) * 0.3,
            len(lines) / 100 * 0.1  # Lunghezza file
        ]
        patterns["complexity_score"] = min(1.0, sum(complexity_indicators))
        
        # Identifica pattern principali
        if patterns["functions"]:
            patterns["main_patterns"].append(f"Functions: {', '.join(patterns['functions'][:3])}")
        if patterns["classes"]:
            patterns["main_patterns"].append(f"Classes: {', '.join(patterns['classes'][:3])}")
        if patterns["design_patterns"]:
            patterns["main_patterns"].append(f"Patterns: {', '.join(patterns['design_patterns'])}")
        
        return patterns

    def _get_file_type(self, file_path: str) -> str:
        """Determina il tipo di file dall'estensione"""
        ext = Path(file_path).suffix.lower()
        
        type_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'typescript-react',
            '.vue': 'vue',
            '.css': 'css',
            '.scss': 'scss',
            '.html': 'html',
            '.json': 'json',
            '.md': 'markdown'
        }
        
        return type_mapping.get(ext, 'unknown')

    async def _get_file_context(self, file_path: str, content: str) -> List[Dict]:
        """Ottieni contesto rilevante per un file"""
        
        # Cerca contesto basato su:
        # 1. Nome del file
        # 2. Imports nel file
        # 3. Pattern di codice
        
        search_queries = [
            Path(file_path).stem,  # Nome file senza estensione
            self._get_file_type(file_path)  # Tipo di file
        ]
        
        # Aggiungi imports come query
        patterns = await self._analyze_code_patterns(content, file_path)
        for imp in patterns["imports"][:3]:  # Prime 3 imports
            # Estrai nome libreria
            lib_match = re.search(r'from\s+(\w+)|import\s+(\w+)', imp)
            if lib_match:
                lib_name = lib_match.group(1) or lib_match.group(2)
                search_queries.append(lib_name)
        
        # Cerca contesto per ogni query
        all_context = []
        for query in search_queries:
            try:
                result = await self.mcp_server.call_tool("search_memory", {
                    "query": query,
                    "project": self.project,
                    "limit": 2,
                    "threshold": 0.4
                })
                
                if result.get("memories"):
                    all_context.extend(result["memories"])
            except Exception as e:
                print(f"Context search failed for '{query}': {e}")
        
        # Rimuovi duplicati e ordina per rilevanza
        unique_context = []
        seen_texts = set()
        for context in all_context:
            if context["text"] not in seen_texts:
                unique_context.append(context)
                seen_texts.add(context["text"])
        
        return sorted(unique_context, key=lambda x: x.get("similarity", 0), reverse=True)[:3]

    async def _generate_code_suggestions(self, 
                                       content: str, 
                                       file_path: str, 
                                       patterns: Dict[str, Any]) -> List[Dict]:
        """Genera suggerimenti di codice intelligenti"""
        suggestions = []
        
        file_type = patterns["file_type"]
        
        # Suggerimenti basati su pattern mancanti
        if file_type in ["javascript", "typescript", "react"]:
            if "useState" in content and "useEffect" not in content:
                suggestions.append({
                    "type": "react_pattern",
                    "message": "Consider adding useEffect for side effects",
                    "confidence": 0.7
                })
            
            if "fetch(" in content and "try" not in content:
                suggestions.append({
                    "type": "error_handling",
                    "message": "Add error handling for fetch requests",
                    "confidence": 0.8
                })
        
        elif file_type == "python":
            if "def " in content and "\"\"\"" not in content:
                suggestions.append({
                    "type": "documentation",
                    "message": "Add docstrings to your functions",
                    "confidence": 0.6
                })
            
            if "open(" in content and "with " not in content:
                suggestions.append({
                    "type": "best_practice",
                    "message": "Use context manager (with statement) for file operations",
                    "confidence": 0.8
                })
        
        # Suggerimenti basati su complessità
        if patterns["complexity_score"] > 0.8:
            suggestions.append({
                "type": "refactoring",
                "message": "Consider breaking down complex functions into smaller ones",
                "confidence": 0.7
            })
        
        # Suggerimenti basati su pattern storici
        similar_patterns = await self._find_similar_code_patterns(patterns)
        if similar_patterns:
            suggestions.append({
                "type": "pattern_reuse",
                "message": "You've used similar patterns before. Consider creating a reusable component.",
                "confidence": 0.6,
                "examples": similar_patterns[:2]
            })
        
        return suggestions

    async def _find_similar_code_patterns(self, current_patterns: Dict[str, Any]) -> List[Dict]:
        """Trova pattern di codice simili dalla memoria"""
        
        # Cerca pattern simili
        search_terms = []
        if current_patterns["functions"]:
            search_terms.extend(current_patterns["functions"][:2])
        if current_patterns["design_patterns"]:
            search_terms.extend(current_patterns["design_patterns"])
        
        similar_patterns = []
        for term in search_terms:
            try:
                result = await self.mcp_server.call_tool("search_memory", {
                    "query": f"{term} {current_patterns['file_type']}",
                    "project": self.project,
                    "limit": 3,
                    "threshold": 0.5
                })
                
                if result.get("memories"):
                    similar_patterns.extend(result["memories"])
            except:
                continue
        
        return similar_patterns

    async def _process_chat_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa messaggi chat con consapevolezza del codice"""
        message = data.get("message", "")
        
        # Usa il sistema base ma aggiungi contesto di codice
        base_results = await self.auto_memory.process_conversation_turn(
            message, "", self.project
        )
        
        # Aggiungi contesto specifico del codice
        if self.workspace_path:
            code_context = await self._get_current_code_context()
            base_results["code_context"] = code_context
        
        return base_results

    async def _get_current_code_context(self) -> Dict[str, Any]:
        """Ottieni contesto del codice corrente"""
        
        # Analizza file recentemente modificati
        recent_files = list(self.file_contexts.keys())[-5:]  # Ultimi 5 file
        
        context = {
            "recent_files": recent_files,
            "workspace_type": "unknown",
            "active_patterns": [],
            "suggestions_count": 0
        }
        
        if self.workspace_path:
            structure = await self._get_project_structure()
            context["workspace_type"] = structure["project_type"]
            context["framework"] = structure.get("framework", "unknown")
        
        # Aggrega pattern dai file recenti
        all_patterns = []
        for file_path in recent_files:
            file_info = self.file_contexts.get(file_path, {})
            patterns = file_info.get("patterns", {})
            if patterns.get("main_patterns"):
                all_patterns.extend(patterns["main_patterns"])
        
        context["active_patterns"] = list(set(all_patterns))[:5]
        context["suggestions_count"] = sum(
            self.file_contexts[f].get("suggestions_generated", 0) 
            for f in recent_files
        )
        
        return context

    def get_session_analytics(self) -> Dict[str, Any]:
        """Ottieni analytics della sessione corrente"""
        
        session_duration = (
            datetime.now() - datetime.fromisoformat(self.active_session["start_time"])
        ).total_seconds() / 60  # in minuti
        
        return {
            "session_duration_minutes": round(session_duration, 2),
            "files_edited": len(self.active_session["files_edited"]),
            "patterns_detected": len(self.active_session["patterns_detected"]),
            "auto_saves": self.active_session["auto_saves"],
            "context_retrievals": self.active_session["context_retrievals"],
            "workspace_path": self.workspace_path,
            "productivity_score": self._calculate_productivity_score()
        }

    def _calculate_productivity_score(self) -> float:
        """Calcola un punteggio di produttività basato su metriche"""
        
        # Fattori di produttività
        files_factor = min(1.0, len(self.active_session["files_edited"]) / 10)
        patterns_factor = min(1.0, len(self.active_session["patterns_detected"]) / 5)
        automation_factor = min(1.0, self.active_session["auto_saves"] / 10)
        
        # Media pesata
        score = (files_factor * 0.4 + patterns_factor * 0.3 + automation_factor * 0.3)
        return round(score, 2)

# Configurazione per Cursor
CURSOR_CONFIG = {
    "mcp.servers": {
        "cursor-smart-auto": {
            "command": "python",
            "args": [str(Path(__file__))],
            "cwd": str(Path(__file__).parent.parent),
            "env": {
                "MONGODB_URL": "mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin",
                "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
                "AUTO_MEMORY": "advanced",
                "CODE_AWARE": "true"
            }
        }
    }
}

# Demo e test
async def demo_cursor_smart():
    """Demo del sistema Cursor Smart Auto-Memory"""
    
    cursor_smart = CursorSmartAutoMemory()
    await cursor_smart.initialize("/fake/workspace")
    
    print("🎯 Testing Cursor Smart Auto-Memory\n")
    
    # Simula eventi di codice
    events = [
        {
            "type": "file_edit",
            "data": {
                "file_path": "src/components/Button.tsx",
                "content": "import React, { useState } from 'react';\n\nconst Button = () => {\n  const [count, setCount] = useState(0);\n  return <button onClick={() => setCount(count + 1)}>{count}</button>;\n};",
                "changes": "Implementato counter button con React hooks"
            }
        },
        {
            "type": "chat_message", 
            "data": {
                "message": "Come posso ottimizzare questo componente React?"
            }
        },
        {
            "type": "error_fix",
            "data": {
                "error": "TypeError: Cannot read property 'map' of undefined",
                "solution": "Aggiunto controllo condizionale prima del map",
                "file_path": "src/utils/helpers.js"
            }
        }
    ]
    
    for i, event in enumerate(events, 1):
        print(f"🔄 Processing event {i}: {event['type']}")
        
        results = await cursor_smart.process_code_event(event["type"], event["data"])
        
        print(f"   Triggers: {len(results.get('triggers_detected', []))}")
        print(f"   Auto-saved: {len(results.get('auto_saved', []))}")
        print(f"   Context: {len(results.get('context_retrieved', []))}")
        print(f"   Suggestions: {len(results.get('code_suggestions', []))}")
        print()
    
    # Analytics finali
    analytics = cursor_smart.get_session_analytics()
    print("📊 Session Analytics:")
    print(f"   Duration: {analytics['session_duration_minutes']} min")
    print(f"   Productivity Score: {analytics['productivity_score']}")

if __name__ == "__main__":
    asyncio.run(demo_cursor_smart()) 