"""
Metrics collection service for MCP Memory Server
"""

import asyncio
import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque

from ..config import get_config
from ..models import MetricsResponse

logger = logging.getLogger(__name__)


class MetricsService:
    """Service for collecting and aggregating metrics"""
    
    def __init__(self):
        self.config = get_config()
        self.start_time = time.time()
        
        # Metrics storage
        self._metrics_history: deque = deque(maxlen=1000)
        self._operation_counts = defaultdict(int)
        self._operation_times = defaultdict(list)
        self._error_counts = defaultdict(int)
        
        # Performance tracking
        self._request_times: deque = deque(maxlen=100)
        self._memory_usage_history: deque = deque(maxlen=100)
        self._cpu_usage_history: deque = deque(maxlen=100)
    
    def record_operation(self, operation: str, duration: float, success: bool = True) -> None:
        """Record an operation metric"""
        self._operation_counts[operation] += 1
        self._operation_times[operation].append(duration)
        
        # Keep only recent times (last 100)
        if len(self._operation_times[operation]) > 100:
            self._operation_times[operation] = self._operation_times[operation][-100:]
        
        if not success:
            self._error_counts[operation] += 1
        
        # Record request time
        self._request_times.append({
            "timestamp": datetime.utcnow(),
            "operation": operation,
            "duration": duration,
            "success": success
        })
    
    def record_system_metrics(self, memory_mb: float, cpu_percent: float) -> None:
        """Record system resource metrics"""
        timestamp = datetime.utcnow()
        
        self._memory_usage_history.append({
            "timestamp": timestamp,
            "memory_mb": memory_mb
        })
        
        self._cpu_usage_history.append({
            "timestamp": timestamp,
            "cpu_percent": cpu_percent
        })
    
    async def get_metrics(self) -> MetricsResponse:
        """Get comprehensive metrics"""
        try:
            # Get service metrics
            from .memory_service import memory_service
            from .database_service import database_service
            from .embedding_service import embedding_service
            
            memory_metrics = await memory_service.get_metrics()
            db_metrics = memory_metrics.get("database_metrics", {})
            embedding_metrics = memory_metrics.get("embedding_metrics", {})
            
            # Calculate averages
            avg_search_time = self._calculate_average_time("search")
            avg_embedding_time = embedding_metrics.get("avg_embedding_time_ms", 0.0)
            
            # Get current system metrics
            try:
                import psutil
                current_memory = psutil.virtual_memory().used / (1024 * 1024)
                current_cpu = psutil.cpu_percent()
                disk_usage = psutil.disk_usage('/').used / (1024 * 1024)
            except ImportError:
                current_memory = 0.0
                current_cpu = 0.0
                disk_usage = 0.0
            
            # Calculate error rate
            total_operations = sum(self._operation_counts.values())
            total_errors = sum(self._error_counts.values())
            error_rate = (total_errors / total_operations * 100) if total_operations > 0 else 0.0
            
            metrics = MetricsResponse(
                total_memories=db_metrics.get("total_memories", 0),
                memories_by_type=db_metrics.get("memories_by_type", {}),
                memories_by_project=db_metrics.get("memories_by_project", {}),
                avg_search_time_ms=avg_search_time,
                avg_embedding_time_ms=avg_embedding_time,
                total_searches=self._operation_counts.get("search", 0),
                total_embeddings=embedding_metrics.get("embedding_count", 0),
                memory_usage_mb=current_memory,
                cpu_usage_percent=current_cpu,
                disk_usage_mb=disk_usage,
                database_size_mb=db_metrics.get("database_size_mb", 0.0),
                database_connections=0,  # Would need to get from MongoDB
                database_operations=db_metrics.get("operation_count", 0),
                error_count=total_errors,
                error_rate_percent=error_rate
            )
            
            # Store metrics in history
            self._store_metrics_snapshot(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return MetricsResponse()
    
    def _calculate_average_time(self, operation: str) -> float:
        """Calculate average time for an operation"""
        times = self._operation_times.get(operation, [])
        if not times:
            return 0.0
        return sum(times) / len(times) * 1000  # Convert to milliseconds
    
    def _store_metrics_snapshot(self, metrics: MetricsResponse) -> None:
        """Store metrics snapshot in history"""
        snapshot = {
            "timestamp": metrics.timestamp,
            "total_memories": metrics.total_memories,
            "avg_search_time_ms": metrics.avg_search_time_ms,
            "memory_usage_mb": metrics.memory_usage_mb,
            "cpu_usage_percent": metrics.cpu_usage_percent,
            "error_rate_percent": metrics.error_rate_percent
        }
        
        self._metrics_history.append(snapshot)
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified number of hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            snapshot for snapshot in self._metrics_history
            if snapshot["timestamp"] >= cutoff_time
        ]
    
    def get_operation_stats(self) -> Dict[str, Any]:
        """Get detailed operation statistics"""
        stats = {}
        
        for operation, count in self._operation_counts.items():
            times = self._operation_times.get(operation, [])
            errors = self._error_counts.get(operation, 0)
            
            if times:
                avg_time = sum(times) / len(times) * 1000
                min_time = min(times) * 1000
                max_time = max(times) * 1000
            else:
                avg_time = min_time = max_time = 0.0
            
            success_rate = ((count - errors) / count * 100) if count > 0 else 0.0
            
            stats[operation] = {
                "count": count,
                "errors": errors,
                "success_rate_percent": success_rate,
                "avg_time_ms": avg_time,
                "min_time_ms": min_time,
                "max_time_ms": max_time
            }
        
        return stats
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trend analysis"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Recent request times
        recent_requests = [
            req for req in self._request_times
            if req["timestamp"] >= hour_ago
        ]
        
        # Recent memory usage
        recent_memory = [
            mem for mem in self._memory_usage_history
            if mem["timestamp"] >= hour_ago
        ]
        
        # Recent CPU usage
        recent_cpu = [
            cpu for cpu in self._cpu_usage_history
            if cpu["timestamp"] >= hour_ago
        ]
        
        return {
            "requests_last_hour": len(recent_requests),
            "avg_response_time_last_hour": (
                sum(req["duration"] for req in recent_requests) / len(recent_requests) * 1000
                if recent_requests else 0.0
            ),
            "avg_memory_usage_last_hour": (
                sum(mem["memory_mb"] for mem in recent_memory) / len(recent_memory)
                if recent_memory else 0.0
            ),
            "avg_cpu_usage_last_hour": (
                sum(cpu["cpu_percent"] for cpu in recent_cpu) / len(recent_cpu)
                if recent_cpu else 0.0
            )
        }
    
    async def run_periodic_collection(self, interval: int = 60) -> None:
        """Run periodic metrics collection"""
        logger.info(f"Starting periodic metrics collection every {interval} seconds")
        
        while True:
            try:
                # Collect system metrics
                try:
                    import psutil
                    memory_mb = psutil.virtual_memory().used / (1024 * 1024)
                    cpu_percent = psutil.cpu_percent()
                    self.record_system_metrics(memory_mb, cpu_percent)
                except ImportError:
                    pass
                
                # Get and store comprehensive metrics
                await self.get_metrics()
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info("Periodic metrics collection cancelled")
                break
            except Exception as e:
                logger.error(f"Periodic metrics collection error: {e}")
                await asyncio.sleep(interval)


# Global metrics service instance
metrics_service = MetricsService()
