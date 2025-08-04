#!/usr/bin/env python3
"""
Replit Smart Auto-Memory Integration
Advanced automation with cloud development pattern learning and collaboration features
"""

import asyncio
import json
import re
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.mcp_server import MCPServer
from examples.smart_triggers import SmartTriggerSystem
from examples.auto_memory_system import AutoMemorySystem

class ReplitSmartAutoMemory:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_base = self.config.get('api_base', 'http://localhost:8000')
        self.project = self.config.get('project', 'replit')
        self.enabled = self.config.get('enabled', True)
        self.use_replit_db = self.config.get('use_replit_db', False)
        
        # Smart tracking for cloud development
        self.cloud_session = {
            "start_time": datetime.now().isoformat(),
            "files_edited": {},
            "collaborators": set(),
            "deployments": [],
            "packages_installed": [],
            "ai_interactions": 0,
            "auto_saves": 0,
            "context_retrievals": 0,
            "code_runs": 0,
            "errors_fixed": 0
        }
        
        # Cloud-specific patterns
        self.cloud_patterns = {
            "deployment_patterns": {},
            "collaboration_patterns": {},
            "performance_patterns": {},
            "debugging_patterns": {},
            "package_patterns": {}
        }
        
        # Learning system
        self.learning_data = {
            "user_preferences": {},
            "common_workflows": {},
            "error_solutions": {},
            "optimization_tips": {}
        }
        
        # Environment detection
        self.is_replit = self._detect_replit_environment()
        self.repl_info = self._get_repl_info() if self.is_replit else {}

    def _detect_replit_environment(self) -> bool:
        """Rileva se siamo in ambiente Replit"""
        return (
            os.getenv('REPL_ID') is not None or
            os.getenv('REPLIT_DB_URL') is not None or
            os.path.exists('/home/runner')
        )

    def _get_repl_info(self) -> Dict[str, Any]:
        """Ottieni informazioni sul Repl corrente"""
        info = {
            "repl_id": os.getenv('REPL_ID', 'unknown'),
            "repl_slug": os.getenv('REPL_SLUG', 'unknown'),
            "user": os.getenv('REPL_OWNER', 'unknown'),
            "language": os.getenv('REPL_LANGUAGE', 'unknown'),
            "db_url": os.getenv('REPLIT_DB_URL'),
            "is_multiplayer": os.getenv('REPL_MULTIPLAYER') == 'true'
        }
        return info

    async def initialize(self):
        """Inizializza il sistema di memoria intelligente"""
        print("🧠 Initializing Replit Smart Auto-Memory...")
        
        if not self.enabled:
            print("❌ Auto-memory disabled")
            return False
        
        # Inizializza MCP server o Replit DB
        if self.use_replit_db and self.is_replit:
            await self._init_replit_db_mode()
        else:
            await self._init_mcp_mode()
        
        # Setup cloud-specific triggers
        await self._setup_cloud_triggers()
        
        # Load historical patterns
        await self._load_cloud_patterns()
        
        # Setup collaboration monitoring
        await self._setup_collaboration_monitoring()
        
        # Setup deployment tracking
        await self._setup_deployment_tracking()
        
        print("✅ Replit Smart Auto-Memory ready!")
        print("🎯 Cloud-aware features enabled:")
        print("   - Automatic deployment pattern detection")
        print("   - Collaboration workflow learning")
        print("   - Cloud resource optimization")
        print("   - Real-time error solution suggestions")
        print("   - Package dependency intelligence")
        
        if self.is_replit:
            print(f"🌐 Replit environment detected:")
            print(f"   - Repl: {self.repl_info.get('repl_slug', 'unknown')}")
            print(f"   - Language: {self.repl_info.get('language', 'unknown')}")
            print(f"   - Multiplayer: {self.repl_info.get('is_multiplayer', False)}")
        
        return True

    async def _init_mcp_mode(self):
        """Inizializza modalità MCP standard"""
        self.mcp_server = MCPServer()
        await self.mcp_server.initialize()
        
        self.smart_triggers = SmartTriggerSystem(self.mcp_server)
        self.auto_memory = AutoMemorySystem(self.mcp_server)

    async def _init_replit_db_mode(self):
        """Inizializza modalità Replit Database"""
        try:
            from replit import db
            self.replit_db = db
            print("🗄️ Using Replit Database for storage")
            
            # Setup simple memory system with Replit DB
            await self._setup_simple_memory_system()
            
        except ImportError:
            print("❌ Replit module not available, falling back to MCP mode")
            await self._init_mcp_mode()

    async def _setup_simple_memory_system(self):
        """Setup sistema di memoria semplificato con Replit DB"""
        
        class SimpleMemorySystem:
            def __init__(self, db):
                self.db = db
                self.embeddings = {}  # Cache embeddings
            
            async def save_memory(self, text: str, memory_type: str, project: str, 
                                importance: float = 0.5, tags: List[str] = None):
                memory_id = hashlib.md5(text.encode()).hexdigest()[:10]
                
                memory_data = {
                    "text": text,
                    "memory_type": memory_type,
                    "project": project,
                    "importance": importance,
                    "tags": tags or [],
                    "timestamp": datetime.now().isoformat(),
                    "id": memory_id
                }
                
                self.db[f"memory_{memory_id}"] = json.dumps(memory_data)
                return {"success": True, "memory_id": memory_id}
            
            async def search_memory(self, query: str, project: str, 
                                  limit: int = 5, threshold: float = 0.3):
                memories = []
                query_lower = query.lower()
                
                # Simple text search (no embeddings in simplified mode)
                for key in self.db.keys():
                    if key.startswith("memory_"):
                        try:
                            memory_data = json.loads(self.db[key])
                            if (project in memory_data.get("project", "") and
                                query_lower in memory_data.get("text", "").lower()):
                                
                                # Simple similarity score
                                similarity = len(set(query_lower.split()) & 
                                               set(memory_data["text"].lower().split())) / len(query_lower.split())
                                
                                if similarity >= threshold:
                                    memory_data["similarity"] = similarity
                                    memories.append(memory_data)
                        except:
                            continue
                
                # Sort by similarity and limit
                memories.sort(key=lambda x: x.get("similarity", 0), reverse=True)
                return {"memories": memories[:limit]}
        
        self.simple_memory = SimpleMemorySystem(self.replit_db)
        
        # Create simplified trigger system
        self.smart_triggers = SimpleCloudTriggerSystem(self.simple_memory)
        self.auto_memory = SimpleAutoMemorySystem(self.simple_memory)

    async def _setup_cloud_triggers(self):
        """Setup trigger specifici per sviluppo cloud"""
        
        self.cloud_triggers = {
            # Deployment patterns
            "deployment": {
                "patterns": [
                    r"(deployed|published|released)\s+(.+)",
                    r"(hosting|deployment|production)\s*:\s*(.+)",
                    r"(build|compile|bundle)\s+(successful|failed|error)",
                    r"(environment|env)\s+(variables|config|setup)"
                ],
                "confidence": 0.9,
                "importance": 0.9,
                "action": "track_deployment"
            },
            
            # Collaboration patterns
            "collaboration": {
                "patterns": [
                    r"(shared|invited|collaborated)\s+(.+)",
                    r"(multiplayer|team|pair programming)",
                    r"(review|feedback|comment)\s*:\s*(.+)",
                    r"(merged|conflict|resolution)\s+(.+)"
                ],
                "confidence": 0.8,
                "importance": 0.7,
                "action": "track_collaboration"
            },
            
            # Package management
            "packages": {
                "patterns": [
                    r"(installed|added|updated)\s+(package|library|dependency)\s+(.+)",
                    r"(requirements|dependencies|package\.json)\s+(.+)",
                    r"(version|upgrade|downgrade)\s+(.+)",
                    r"(npm|pip|yarn|poetry)\s+(install|add|update)\s+(.+)"
                ],
                "confidence": 0.8,
                "importance": 0.6,
                "action": "track_package"
            },
            
            # Performance patterns
            "performance": {
                "patterns": [
                    r"(slow|fast|performance|optimization)\s+(.+)",
                    r"(memory|cpu|resource)\s+(usage|consumption|leak)",
                    r"(cache|caching|optimization)\s+(.+)",
                    r"(startup|boot|initialization)\s+(time|speed)"
                ],
                "confidence": 0.7,
                "importance": 0.8,
                "action": "track_performance"
            },
            
            # Error patterns
            "errors": {
                "patterns": [
                    r"(error|exception|bug|issue)\s*:\s*(.+)",
                    r"(fixed|resolved|solved)\s+(.+)",
                    r"(timeout|connection|network)\s+(error|issue)",
                    r"(syntax|runtime|compilation)\s+(error|warning)"
                ],
                "confidence": 0.9,
                "importance": 0.9,
                "action": "track_error"
            }
        }

    async def process_cloud_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa eventi di sviluppo cloud con automazione completa"""
        
        if not self.enabled:
            return {"success": False, "reason": "disabled"}
        
        results = {
            "triggers_detected": [],
            "auto_saved": [],
            "context_retrieved": [],
            "cloud_suggestions": [],
            "collaboration_insights": {},
            "performance_analysis": {},
            "proactive_actions": []
        }
        
        try:
            # 1. Update session tracking
            await self._update_cloud_session(event_type, event_data)
            
            # 2. Detect cloud-specific triggers
            triggers = await self._detect_cloud_triggers(event_data)
            results["triggers_detected"] = triggers
            
            # 3. Execute automatic saves
            if triggers:
                save_results = await self._execute_cloud_saves(triggers, event_data)
                results["auto_saved"] = save_results
                self.cloud_session["auto_saves"] += len(save_results)
            
            # 4. Retrieve intelligent context
            context = await self._get_cloud_context(event_type, event_data)
            results["context_retrieved"] = context
            if context:
                self.cloud_session["context_retrievals"] += 1
            
            # 5. Generate cloud-specific suggestions
            suggestions = await self._generate_cloud_suggestions(event_type, event_data, context)
            results["cloud_suggestions"] = suggestions
            
            # 6. Analyze collaboration patterns
            if self.repl_info.get("is_multiplayer"):
                collaboration_insights = await self._analyze_collaboration(event_data)
                results["collaboration_insights"] = collaboration_insights
            
            # 7. Performance analysis
            performance_analysis = await self._analyze_performance(event_type, event_data)
            results["performance_analysis"] = performance_analysis
            
            # 8. Execute proactive actions
            proactive_actions = await self._execute_cloud_proactive_actions(
                event_type, event_data, results
            )
            results["proactive_actions"] = proactive_actions
            
            # 9. Learn from cloud patterns
            await self._learn_from_cloud_interaction(event_type, event_data, results)
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing cloud event: {e}")
            return {"success": False, "error": str(e)}

    async def _update_cloud_session(self, event_type: str, event_data: Dict[str, Any]):
        """Aggiorna tracking della sessione cloud"""
        
        if event_type == "file_edit":
            file_path = event_data.get("file_path", "unknown")
            self.cloud_session["files_edited"][file_path] = {
                "last_edit": datetime.now().isoformat(),
                "edit_count": self.cloud_session["files_edited"].get(file_path, {}).get("edit_count", 0) + 1
            }
        
        elif event_type == "collaboration":
            collaborator = event_data.get("user", "unknown")
            self.cloud_session["collaborators"].add(collaborator)
        
        elif event_type == "deployment":
            self.cloud_session["deployments"].append({
                "timestamp": datetime.now().isoformat(),
                "type": event_data.get("deployment_type", "unknown"),
                "status": event_data.get("status", "unknown")
            })
        
        elif event_type == "package_install":
            package = event_data.get("package", "unknown")
            self.cloud_session["packages_installed"].append({
                "package": package,
                "timestamp": datetime.now().isoformat(),
                "version": event_data.get("version", "latest")
            })
        
        elif event_type == "code_run":
            self.cloud_session["code_runs"] += 1
        
        elif event_type == "error_fix":
            self.cloud_session["errors_fixed"] += 1

    async def _detect_cloud_triggers(self, event_data: Dict[str, Any]) -> List[Dict]:
        """Rileva trigger specifici per il cloud"""
        triggers = []
        text = self._extract_text_from_event(event_data)
        
        for trigger_type, config in self.cloud_triggers.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    triggers.append({
                        "type": trigger_type,
                        "pattern": pattern,
                        "match": match.group(0),
                        "confidence": config["confidence"],
                        "importance": config["importance"],
                        "action": config["action"],
                        "extracted_data": match.groups()
                    })
        
        return triggers

    async def _generate_cloud_suggestions(self, 
                                        event_type: str, 
                                        event_data: Dict[str, Any],
                                        context: List[Dict]) -> List[Dict]:
        """Genera suggerimenti specifici per il cloud"""
        suggestions = []
        
        # Deployment suggestions
        if event_type == "deployment":
            suggestions.extend(await self._generate_deployment_suggestions(event_data, context))
        
        # Performance suggestions
        if event_type == "performance_issue":
            suggestions.extend(await self._generate_performance_suggestions(event_data, context))
        
        # Collaboration suggestions
        if self.repl_info.get("is_multiplayer"):
            suggestions.extend(await self._generate_collaboration_suggestions(event_data, context))
        
        # Package suggestions
        if event_type == "package_install":
            suggestions.extend(await self._generate_package_suggestions(event_data, context))
        
        # Environment suggestions
        environment_suggestions = await self._generate_environment_suggestions(event_data)
        suggestions.extend(environment_suggestions)
        
        return [s for s in suggestions if s.get("confidence", 0) > 0.6]

    async def _generate_deployment_suggestions(self, 
                                             event_data: Dict[str, Any],
                                             context: List[Dict]) -> List[Dict]:
        """Genera suggerimenti per deployment"""
        suggestions = []
        
        # Check for common deployment issues
        if event_data.get("status") == "failed":
            suggestions.append({
                "type": "deployment_troubleshooting",
                "message": "Check build logs and environment variables for deployment issues",
                "confidence": 0.8,
                "actionable": True,
                "commands": [
                    "Check .replit configuration",
                    "Verify all dependencies are installed",
                    "Check for environment variable requirements"
                ]
            })
        
        # Suggest deployment optimizations
        if event_data.get("build_time", 0) > 60:  # More than 1 minute
            suggestions.append({
                "type": "build_optimization",
                "message": "Consider optimizing build time with caching and minimal dependencies",
                "confidence": 0.7,
                "tips": [
                    "Use .dockerignore to exclude unnecessary files",
                    "Implement build caching",
                    "Remove unused dependencies"
                ]
            })
        
        return suggestions

    async def _generate_collaboration_suggestions(self,
                                                event_data: Dict[str, Any],
                                                context: List[Dict]) -> List[Dict]:
        """Genera suggerimenti per collaborazione"""
        suggestions = []
        
        collaborator_count = len(self.cloud_session["collaborators"])
        
        if collaborator_count > 1:
            suggestions.append({
                "type": "collaboration_best_practices",
                "message": "Consider implementing code review practices for team development",
                "confidence": 0.7,
                "practices": [
                    "Use comments for code review",
                    "Implement branching strategy",
                    "Set up automated testing",
                    "Document coding standards"
                ]
            })
        
        # Suggest communication improvements
        if event_data.get("conflicts", 0) > 0:
            suggestions.append({
                "type": "conflict_resolution",
                "message": "Implement conflict resolution strategies",
                "confidence": 0.8,
                "strategies": [
                    "Communicate changes before editing",
                    "Use file-level locking",
                    "Implement proper version control"
                ]
            })
        
        return suggestions

    async def _analyze_performance(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza performance del cloud development"""
        
        analysis = {
            "session_duration": self._get_session_duration(),
            "files_per_hour": self._calculate_files_per_hour(),
            "deployment_frequency": len(self.cloud_session["deployments"]),
            "error_rate": self._calculate_error_rate(),
            "collaboration_efficiency": self._calculate_collaboration_efficiency(),
            "recommendations": []
        }
        
        # Generate performance recommendations
        if analysis["error_rate"] > 0.2:  # More than 20% error rate
            analysis["recommendations"].append({
                "type": "error_reduction",
                "message": "High error rate detected. Consider implementing better testing practices."
            })
        
        if analysis["files_per_hour"] < 2:  # Less than 2 files per hour
            analysis["recommendations"].append({
                "type": "productivity_boost",
                "message": "Consider using code templates and snippets to increase productivity."
            })
        
        return analysis

    def _get_session_duration(self) -> float:
        """Ottieni durata sessione in ore"""
        start_time = datetime.fromisoformat(self.cloud_session["start_time"])
        duration = datetime.now() - start_time
        return duration.total_seconds() / 3600

    def _calculate_files_per_hour(self) -> float:
        """Calcola file modificati per ora"""
        duration_hours = self._get_session_duration()
        if duration_hours == 0:
            return 0
        return len(self.cloud_session["files_edited"]) / duration_hours

    def _calculate_error_rate(self) -> float:
        """Calcola tasso di errore"""
        total_runs = self.cloud_session["code_runs"]
        if total_runs == 0:
            return 0
        return self.cloud_session["errors_fixed"] / total_runs

    def _calculate_collaboration_efficiency(self) -> float:
        """Calcola efficienza collaborazione"""
        collaborators = len(self.cloud_session["collaborators"])
        if collaborators <= 1:
            return 1.0
        
        # Simple metric: files edited per collaborator
        files_edited = len(self.cloud_session["files_edited"])
        return files_edited / collaborators if collaborators > 0 else 0

    def get_cloud_analytics(self) -> Dict[str, Any]:
        """Ottieni analytics completi del cloud development"""
        
        analytics = {
            "session_info": {
                "duration_hours": round(self._get_session_duration(), 2),
                "start_time": self.cloud_session["start_time"],
                "is_multiplayer": self.repl_info.get("is_multiplayer", False),
                "repl_language": self.repl_info.get("language", "unknown")
            },
            
            "development_metrics": {
                "files_edited": len(self.cloud_session["files_edited"]),
                "code_runs": self.cloud_session["code_runs"],
                "errors_fixed": self.cloud_session["errors_fixed"],
                "packages_installed": len(self.cloud_session["packages_installed"]),
                "deployments": len(self.cloud_session["deployments"])
            },
            
            "collaboration_metrics": {
                "collaborators": list(self.cloud_session["collaborators"]),
                "collaboration_efficiency": self._calculate_collaboration_efficiency()
            },
            
            "automation_metrics": {
                "auto_saves": self.cloud_session["auto_saves"],
                "context_retrievals": self.cloud_session["context_retrievals"],
                "ai_interactions": self.cloud_session["ai_interactions"]
            },
            
            "performance_scores": {
                "productivity_score": self._calculate_productivity_score(),
                "collaboration_score": self._calculate_collaboration_score(),
                "automation_efficiency": self._calculate_automation_efficiency()
            }
        }
        
        return analytics

    def _calculate_productivity_score(self) -> float:
        """Calcola punteggio produttività"""
        files_factor = min(1.0, len(self.cloud_session["files_edited"]) / 10)
        runs_factor = min(1.0, self.cloud_session["code_runs"] / 20)
        deployment_factor = min(1.0, len(self.cloud_session["deployments"]) / 5)
        
        return round((files_factor * 0.4 + runs_factor * 0.3 + deployment_factor * 0.3), 2)

    def _calculate_collaboration_score(self) -> float:
        """Calcola punteggio collaborazione"""
        if not self.repl_info.get("is_multiplayer"):
            return 1.0
        
        collaborators = len(self.cloud_session["collaborators"])
        if collaborators <= 1:
            return 0.5
        
        efficiency = self._calculate_collaboration_efficiency()
        return min(1.0, efficiency * collaborators / 3)

    def _calculate_automation_efficiency(self) -> float:
        """Calcola efficienza automazione"""
        total_actions = (len(self.cloud_session["files_edited"]) + 
                        self.cloud_session["code_runs"] + 
                        len(self.cloud_session["deployments"]))
        
        if total_actions == 0:
            return 0
        
        automated_actions = (self.cloud_session["auto_saves"] + 
                           self.cloud_session["context_retrievals"])
        
        return min(1.0, automated_actions / total_actions)

    def _extract_text_from_event(self, event_data: Dict[str, Any]) -> str:
        """Estrae testo da eventi vari"""
        text_sources = [
            event_data.get("message", ""),
            event_data.get("description", ""),
            event_data.get("error", ""),
            event_data.get("solution", ""),
            str(event_data.get("file_path", "")),
            str(event_data.get("package", "")),
            json.dumps(event_data)
        ]
        
        return " ".join(filter(None, text_sources)).lower()

    # Placeholder methods for simplified implementation
    async def _load_cloud_patterns(self):
        """Load historical cloud patterns"""
        pass

    async def _setup_collaboration_monitoring(self):
        """Setup collaboration monitoring"""
        pass

    async def _setup_deployment_tracking(self):
        """Setup deployment tracking"""
        pass

    async def _execute_cloud_saves(self, triggers, event_data):
        """Execute cloud-specific saves"""
        return []

    async def _get_cloud_context(self, event_type, event_data):
        """Get cloud-specific context"""
        return []

    async def _analyze_collaboration(self, event_data):
        """Analyze collaboration patterns"""
        return {}

    async def _execute_cloud_proactive_actions(self, event_type, event_data, results):
        """Execute proactive cloud actions"""
        return []

    async def _learn_from_cloud_interaction(self, event_type, event_data, results):
        """Learn from cloud interactions"""
        pass

    async def _generate_performance_suggestions(self, event_data, context):
        """Generate performance suggestions"""
        return []

    async def _generate_package_suggestions(self, event_data, context):
        """Generate package suggestions"""
        return []

    async def _generate_environment_suggestions(self, event_data):
        """Generate environment suggestions"""
        return []

# Simplified classes for Replit DB mode
class SimpleCloudTriggerSystem:
    def __init__(self, memory_system):
        self.memory_system = memory_system

class SimpleAutoMemorySystem:
    def __init__(self, memory_system):
        self.memory_system = memory_system

# Demo and configuration
async def demo_replit_smart():
    """Demo del sistema Replit Smart Auto-Memory"""
    
    replit_smart = ReplitSmartAutoMemory({
        "project": "demo_repl",
        "enabled": True,
        "use_replit_db": False  # Use MCP mode for demo
    })
    
    success = await replit_smart.initialize()
    if not success:
        print("❌ Failed to initialize")
        return
    
    print("🎯 Testing Replit Smart Auto-Memory\n")
    
    # Simula eventi cloud
    events = [
        {
            "type": "file_edit",
            "data": {
                "file_path": "main.py",
                "message": "Implemented Flask API with authentication"
            }
        },
        {
            "type": "package_install",
            "data": {
                "package": "flask",
                "version": "2.0.1",
                "message": "Installed Flask for web development"
            }
        },
        {
            "type": "deployment",
            "data": {
                "deployment_type": "web",
                "status": "success",
                "build_time": 45,
                "message": "Successfully deployed Flask application"
            }
        },
        {
            "type": "collaboration",
            "data": {
                "user": "collaborator_1",
                "action": "joined",
                "message": "New collaborator joined the project"
            }
        },
        {
            "type": "error_fix",
            "data": {
                "error": "ImportError: No module named 'requests'",
                "solution": "Added requests to requirements.txt",
                "message": "Fixed import error by adding missing dependency"
            }
        }
    ]
    
    for i, event in enumerate(events, 1):
        print(f"🔄 Processing event {i}: {event['type']}")
        
        results = await replit_smart.process_cloud_event(event["type"], event["data"])
        
        print(f"   Triggers: {len(results.get('triggers_detected', []))}")
        print(f"   Auto-saved: {len(results.get('auto_saved', []))}")
        print(f"   Context: {len(results.get('context_retrieved', []))}")
        print(f"   Suggestions: {len(results.get('cloud_suggestions', []))}")
        print()
    
    # Analytics finali
    analytics = replit_smart.get_cloud_analytics()
    print("📊 Cloud Development Analytics:")
    print(f"   Session Duration: {analytics['session_info']['duration_hours']} hours")
    print(f"   Files Edited: {analytics['development_metrics']['files_edited']}")
    print(f"   Productivity Score: {analytics['performance_scores']['productivity_score']}")
    print(f"   Automation Efficiency: {analytics['performance_scores']['automation_efficiency']}")

if __name__ == "__main__":
    asyncio.run(demo_replit_smart()) 