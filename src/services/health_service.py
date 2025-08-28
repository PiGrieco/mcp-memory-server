"""
Health monitoring service for MCP Memory Server
"""

import asyncio
import logging
import time
from typing import Dict, Any, List

from ..config import get_config
from ..models import HealthCheckResponse
from .database_service import database_service
from .embedding_service import embedding_service
from .memory_service import memory_service

logger = logging.getLogger(__name__)


class HealthService:
    """Service for monitoring system health"""
    
    def __init__(self):
        self.config = get_config()
        self.start_time = time.time()
        self._health_history: List[Dict[str, Any]] = []
        self._max_history = 100
    
    async def check_all(self) -> bool:
        """Check health of all services"""
        try:
            health_status = await self.get_health_status()
            return health_status.status == "healthy"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def get_health_status(self) -> HealthCheckResponse:
        """Get comprehensive health status"""
        try:
            time.time()
            
            # Check individual services
            db_health = await database_service.health_check()
            embedding_health = await embedding_service.health_check()
            memory_health = await memory_service.health_check()
            
            # Determine overall status
            all_services_healthy = all(
                health.get("status") == "healthy"
                for health in [db_health, embedding_health, memory_health]
            )
            
            overall_status = "healthy" if all_services_healthy else "unhealthy"
            uptime = time.time() - self.start_time
            
            # Get system metrics
            try:
                import psutil
                memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
                cpu_usage = psutil.cpu_percent()
            except ImportError:
                memory_usage = None
                cpu_usage = None
            
            health_response = HealthCheckResponse(
                status=overall_status,
                version=self.config.server.version,
                uptime_seconds=uptime,
                database_status=db_health.get("status", "unknown"),
                embedding_service_status=embedding_health.get("status", "unknown"),
                memory_service_status=memory_health.get("status", "unknown"),
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                database_response_time_ms=db_health.get("response_time_ms")
            )
            
            # Store in history
            self._store_health_record(health_response)
            
            return health_response
            
        except Exception as e:
            logger.error(f"Health status check failed: {e}")
            return HealthCheckResponse(
                status="unhealthy",
                version=self.config.server.version,
                uptime_seconds=time.time() - self.start_time
            )
    
    def _store_health_record(self, health: HealthCheckResponse) -> None:
        """Store health record in history"""
        record = {
            "timestamp": health.timestamp,
            "status": health.status,
            "uptime_seconds": health.uptime_seconds,
            "memory_usage_mb": health.memory_usage_mb,
            "cpu_usage_percent": health.cpu_usage_percent,
            "database_status": health.database_status,
            "embedding_service_status": health.embedding_service_status,
            "memory_service_status": health.memory_service_status
        }
        
        self._health_history.append(record)
        
        # Keep only recent records
        if len(self._health_history) > self._max_history:
            self._health_history = self._health_history[-self._max_history:]
    
    def get_health_history(self) -> List[Dict[str, Any]]:
        """Get health check history"""
        return self._health_history.copy()
    
    async def run_periodic_checks(self, interval: int = 30) -> None:
        """Run periodic health checks"""
        logger.info(f"Starting periodic health checks every {interval} seconds")
        
        while True:
            try:
                health = await self.get_health_status()
                
                if health.status != "healthy":
                    logger.warning(f"System health check failed: {health.status}")
                    # Could trigger alerts here
                else:
                    logger.debug("Health check passed")
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info("Periodic health checks cancelled")
                break
            except Exception as e:
                logger.error(f"Periodic health check error: {e}")
                await asyncio.sleep(interval)


# Global health service instance
health_service = HealthService()
