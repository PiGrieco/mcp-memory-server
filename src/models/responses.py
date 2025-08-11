"""
Response models for MCP Memory Server
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from .base import BaseModel, validate_required_field, validate_numeric_range


@dataclass
class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def validate(self) -> None:
        """Validate success response"""
        validate_required_field(self.message, "message")


@dataclass
class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str = ""
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def validate(self) -> None:
        """Validate error response"""
        validate_required_field(self.error, "error")


@dataclass
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    uptime_seconds: float = 0.0
    
    # Service status
    database_status: str = "unknown"
    embedding_service_status: str = "unknown"
    memory_service_status: str = "unknown"
    
    # Performance metrics
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    active_connections: Optional[int] = None
    
    # Database metrics
    database_connections: Optional[int] = None
    database_response_time_ms: Optional[float] = None
    
    def validate(self) -> None:
        """Validate health check response"""
        validate_required_field(self.status, "status")
        validate_required_field(self.version, "version")
        validate_numeric_range(self.uptime_seconds, "uptime_seconds", min_value=0)
        
        if self.memory_usage_mb is not None:
            validate_numeric_range(self.memory_usage_mb, "memory_usage_mb", min_value=0)
        
        if self.cpu_usage_percent is not None:
            validate_numeric_range(self.cpu_usage_percent, "cpu_usage_percent", min_value=0, max_value=100)
        
        if self.active_connections is not None:
            validate_numeric_range(self.active_connections, "active_connections", min_value=0)


@dataclass
class MetricsResponse(BaseModel):
    """Metrics response"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Memory metrics
    total_memories: int = 0
    memories_by_type: Dict[str, int] = field(default_factory=dict)
    memories_by_project: Dict[str, int] = field(default_factory=dict)
    
    # Performance metrics
    avg_search_time_ms: float = 0.0
    avg_embedding_time_ms: float = 0.0
    total_searches: int = 0
    total_embeddings: int = 0
    
    # System metrics
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_usage_mb: float = 0.0
    
    # Database metrics
    database_size_mb: float = 0.0
    database_connections: int = 0
    database_operations: int = 0
    
    # Error metrics
    error_count: int = 0
    error_rate_percent: float = 0.0
    
    def validate(self) -> None:
        """Validate metrics response"""
        validate_numeric_range(self.total_memories, "total_memories", min_value=0)
        validate_numeric_range(self.avg_search_time_ms, "avg_search_time_ms", min_value=0)
        validate_numeric_range(self.avg_embedding_time_ms, "avg_embedding_time_ms", min_value=0)
        validate_numeric_range(self.total_searches, "total_searches", min_value=0)
        validate_numeric_range(self.total_embeddings, "total_embeddings", min_value=0)
        validate_numeric_range(self.memory_usage_mb, "memory_usage_mb", min_value=0)
        validate_numeric_range(self.cpu_usage_percent, "cpu_usage_percent", min_value=0, max_value=100)
        validate_numeric_range(self.disk_usage_mb, "disk_usage_mb", min_value=0)
        validate_numeric_range(self.database_size_mb, "database_size_mb", min_value=0)
        validate_numeric_range(self.database_connections, "database_connections", min_value=0)
        validate_numeric_range(self.database_operations, "database_operations", min_value=0)
        validate_numeric_range(self.error_count, "error_count", min_value=0)
        validate_numeric_range(self.error_rate_percent, "error_rate_percent", min_value=0, max_value=100)
