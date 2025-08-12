"""
Utilities for MCP Memory Server
"""

from .exceptions import (
    MCPMemoryError, MemoryServiceError, DatabaseServiceError,
    EmbeddingServiceError, ValidationError, ConfigurationError,
    NotFoundError, AuthenticationError, AuthorizationError,
    RateLimitError, ServiceUnavailableError, PluginServiceError,
    CacheServiceError, BackupServiceError, NotificationServiceError,
    ExportServiceError, MonitoringServiceError, AdapterError, HookError
)

__all__ = [
    "MCPMemoryError",
    "MemoryServiceError",
    "DatabaseServiceError",
    "EmbeddingServiceError", 
    "ValidationError",
    "ConfigurationError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ServiceUnavailableError",
    "PluginServiceError",
    "CacheServiceError",
    "BackupServiceError",
    "NotificationServiceError",
    "ExportServiceError",
    "MonitoringServiceError",
    "AdapterError",
    "HookError"
]
