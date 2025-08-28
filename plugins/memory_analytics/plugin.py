"""
Memory Analytics Plugin for MCP Memory Server
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from collections import defaultdict, Counter
import json
from pathlib import Path

PLUGIN_INFO = {
    "name": "Memory Analytics",
    "version": "1.0.0",
    "description": "Advanced analytics and insights for memories",
    "author": "MCP Memory Server Team",
    "hooks": [
        "memory_created",
        "memory_updated", 
        "memory_deleted",
        "search_performed",
        "system_startup",
        "system_shutdown"
    ],
    "enabled": True,
    "config": {
        "analytics_enabled": True,
        "metrics_retention_days": 30,
        "insights_enabled": True,
        "export_analytics": True,
        "analytics_file": "memory_analytics.json"
    }
}

class MemoryAnalytics:
    """Memory analytics and insights engine."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.analytics_file = Path(config.get("analytics_file", "memory_analytics.json"))
        
        # Analytics data
        self.metrics = {
            "total_memories": 0,
            "total_searches": 0,
            "memory_creation_rate": [],
            "search_patterns": defaultdict(int),
            "popular_tags": Counter(),
            "project_distribution": Counter(),
            "importance_distribution": defaultdict(int),
            "memory_types": Counter(),
            "access_patterns": defaultdict(int),
            "creation_timeline": [],
            "search_timeline": []
        }
        
        # Insights cache
        self.insights = {}
        self.last_analysis = None
        
    async def initialize(self):
        """Initialize analytics plugin."""
        try:
            # Load existing analytics if available
            await self._load_analytics()
            
            # Schedule periodic analysis
            asyncio.create_task(self._periodic_analysis())
            
            self.logger.info("Memory Analytics plugin initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Memory Analytics plugin: {e}")
            raise
    
    async def _load_analytics(self):
        """Load analytics data from file."""
        try:
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics.update(data.get("metrics", {}))
                    self.insights = data.get("insights", {})
                    self.last_analysis = data.get("last_analysis")
                    
                self.logger.info("Analytics data loaded successfully")
                
        except Exception as e:
            self.logger.warning(f"Failed to load analytics data: {e}")
    
    async def _save_analytics(self):
        """Save analytics data to file."""
        try:
            data = {
                "metrics": self.metrics,
                "insights": self.insights,
                "last_analysis": datetime.utcnow().isoformat(),
                "version": PLUGIN_INFO["version"]
            }
            
            with open(self.analytics_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            self.logger.debug("Analytics data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save analytics data: {e}")
    
    async def _periodic_analysis(self):
        """Run periodic analysis every hour."""
        while True:
            try:
                await asyncio.sleep(3600)  # 1 hour
                await self._generate_insights()
                await self._save_analytics()
                
            except Exception as e:
                self.logger.error(f"Periodic analysis failed: {e}")
    
    async def _generate_insights(self):
        """Generate insights from collected metrics."""
        try:
            insights = {}
            
            # Memory creation insights
            if self.metrics["creation_timeline"]:
                recent_creations = [
                    t for t in self.metrics["creation_timeline"]
                    if datetime.fromisoformat(t) > datetime.utcnow() - timedelta(days=7)
                ]
                insights["creation_rate_7d"] = len(recent_creations)
                insights["avg_creations_per_day"] = len(recent_creations) / 7
            
            # Popular content insights
            if self.metrics["popular_tags"]:
                insights["top_tags"] = dict(self.metrics["popular_tags"].most_common(10))
            
            if self.metrics["project_distribution"]:
                insights["top_projects"] = dict(self.metrics["project_distribution"].most_common(5))
            
            # Search insights
            if self.metrics["search_patterns"]:
                insights["popular_searches"] = dict(
                    sorted(self.metrics["search_patterns"].items(), 
                           key=lambda x: x[1], reverse=True)[:10]
                )
            
            # Memory type insights
            if self.metrics["memory_types"]:
                insights["memory_type_distribution"] = dict(self.metrics["memory_types"])
            
            # Importance insights
            if self.metrics["importance_distribution"]:
                insights["importance_distribution"] = dict(self.metrics["importance_distribution"])
            
            self.insights = insights
            self.last_analysis = datetime.utcnow().isoformat()
            
            self.logger.info("Insights generated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to generate insights: {e}")
    
    def _update_metrics(self, event_type: str, data: Dict[str, Any]):
        """Update metrics with new event data."""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            if event_type == "memory_created":
                self.metrics["total_memories"] += 1
                self.metrics["creation_timeline"].append(timestamp)
                
                # Update tag metrics
                if data.get("tags"):
                    self.metrics["popular_tags"].update(data["tags"])
                
                # Update project metrics
                if data.get("project"):
                    self.metrics["project_distribution"][data["project"]] += 1
                
                # Update memory type metrics
                if data.get("memory_type"):
                    self.metrics["memory_types"][data["memory_type"]] += 1
                
                # Update importance metrics
                if data.get("importance"):
                    importance_bucket = round(data["importance"] * 10) / 10
                    self.metrics["importance_distribution"][importance_bucket] += 1
            
            elif event_type == "search_performed":
                self.metrics["total_searches"] += 1
                self.metrics["search_timeline"].append(timestamp)
                
                # Update search patterns
                if data.get("query"):
                    self.metrics["search_patterns"][data["query"]] += 1
                
                # Update access patterns
                if data.get("project"):
                    self.metrics["access_patterns"][data["project"]] += 1
            
            # Cleanup old data
            await self._cleanup_old_data()
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old analytics data."""
        try:
            retention_days = self.config.get("metrics_retention_days", 30)
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Cleanup creation timeline
            self.metrics["creation_timeline"] = [
                t for t in self.metrics["creation_timeline"]
                if datetime.fromisoformat(t) > cutoff_date
            ]
            
            # Cleanup search timeline
            self.metrics["search_timeline"] = [
                t for t in self.metrics["search_timeline"]
                if datetime.fromisoformat(t) > cutoff_date
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        try:
            await self._generate_insights()
            
            return {
                "metrics": {
                    "total_memories": self.metrics["total_memories"],
                    "total_searches": self.metrics["total_searches"],
                    "top_tags": dict(self.metrics["popular_tags"].most_common(5)),
                    "top_projects": dict(self.metrics["project_distribution"].most_common(5)),
                    "memory_types": dict(self.metrics["memory_types"]),
                    "popular_searches": dict(
                        sorted(self.metrics["search_patterns"].items(), 
                               key=lambda x: x[1], reverse=True)[:5]
                    )
                },
                "insights": self.insights,
                "last_analysis": self.last_analysis,
                "plugin_info": PLUGIN_INFO
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics summary: {e}")
            return {"error": str(e)}

# Global analytics instance
analytics = None

async def initialize(settings, config):
    """Initialize the Memory Analytics plugin."""
    global analytics
    
    try:
        plugin_config = {**PLUGIN_INFO["config"], **config}
        analytics = MemoryAnalytics(plugin_config)
        await analytics.initialize()
        
        print(f"✅ {PLUGIN_INFO['name']} v{PLUGIN_INFO['version']} initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize {PLUGIN_INFO['name']}: {e}")
        raise

async def memory_created(memory, context):
    """Hook called when memory is created."""
    if analytics and analytics.config.get("analytics_enabled", True):
        try:
            data = {
                "id": memory.id,
                "project": memory.project,
                "tags": memory.tags,
                "memory_type": memory.memory_type.value,
                "importance": memory.importance,
                "content_length": len(memory.content)
            }
            
            analytics._update_metrics("memory_created", data)
            
        except Exception as e:
            analytics.logger.error(f"Failed to process memory_created hook: {e}")

async def memory_updated(memory, context):
    """Hook called when memory is updated."""
    if analytics and analytics.config.get("analytics_enabled", True):
        try:
            # Track memory updates
            analytics.metrics["memory_updates"] = analytics.metrics.get("memory_updates", 0) + 1
            
        except Exception as e:
            analytics.logger.error(f"Failed to process memory_updated hook: {e}")

async def memory_deleted(memory_id, context):
    """Hook called when memory is deleted."""
    if analytics and analytics.config.get("analytics_enabled", True):
        try:
            # Track memory deletions
            analytics.metrics["memory_deletions"] = analytics.metrics.get("memory_deletions", 0) + 1
            
        except Exception as e:
            analytics.logger.error(f"Failed to process memory_deleted hook: {e}")

async def search_performed(query, results, context):
    """Hook called when search is performed."""
    if analytics and analytics.config.get("analytics_enabled", True):
        try:
            data = {
                "query": query,
                "results_count": len(results),
                "project": context.get("project"),
                "query_length": len(query)
            }
            
            analytics._update_metrics("search_performed", data)
            
        except Exception as e:
            analytics.logger.error(f"Failed to process search_performed hook: {e}")

async def system_startup(settings):
    """Hook called on system startup."""
    if analytics:
        try:
            analytics.logger.info("Memory Analytics plugin started")
            
        except Exception as e:
            analytics.logger.error(f"Failed to process system_startup hook: {e}")

async def system_shutdown():
    """Hook called on system shutdown."""
    if analytics:
        try:
            await analytics._save_analytics()
            analytics.logger.info("Memory Analytics plugin shutdown")
            
        except Exception as e:
            analytics.logger.error(f"Failed to process system_shutdown hook: {e}")

# Additional plugin functions
async def get_analytics():
    """Get current analytics data."""
    if analytics:
        return await analytics.get_analytics_summary()
    return {"error": "Analytics not initialized"}

async def export_analytics(format: str = "json") -> Dict[str, Any]:
    """Export analytics data."""
    if not analytics:
        return {"error": "Analytics not initialized"}
    
    try:
        summary = await analytics.get_analytics_summary()
        
        if format == "json":
            return {
                "success": True,
                "format": "json",
                "data": summary,
                "exported_at": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"Unsupported format: {format}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Export failed: {e}"
        } 