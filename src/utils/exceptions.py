"""
Custom exceptions for MCP Memory Server
"""


class MCPMemoryError(Exception):
    """Base exception for MCP Memory Server"""
    pass


class MemoryServiceError(MCPMemoryError):
    """Exception raised by memory service operations"""
    pass


class DatabaseServiceError(MCPMemoryError):
    """Exception raised by database service operations"""
    pass


class EmbeddingServiceError(MCPMemoryError):
    """Exception raised by embedding service operations"""
    pass


class ValidationError(MCPMemoryError):
    """Exception raised for validation errors"""
    pass


class ConfigurationError(MCPMemoryError):
    """Exception raised for configuration errors"""
    pass


class NotFoundError(MCPMemoryError):
    """Exception raised when a resource is not found"""
    pass


class AuthenticationError(MCPMemoryError):
    """Exception raised for authentication errors"""
    pass


class AuthorizationError(MCPMemoryError):
    """Exception raised for authorization errors"""
    pass


class RateLimitError(MCPMemoryError):
    """Exception raised when rate limit is exceeded"""
    pass


class ServiceUnavailableError(MCPMemoryError):
    """Exception raised when a service is unavailable"""
    pass


# New exceptions for advanced services
class PluginServiceError(MCPMemoryError):
    """Exception raised by plugin service operations"""
    pass


class CacheServiceError(MCPMemoryError):
    """Exception raised by cache service operations"""
    pass


class BackupServiceError(MCPMemoryError):
    """Exception raised by backup service operations"""
    pass


class NotificationServiceError(MCPMemoryError):
    """Exception raised by notification service operations"""
    pass


class ExportServiceError(MCPMemoryError):
    """Exception raised by export service operations"""
    pass


class MonitoringServiceError(MCPMemoryError):
    """Exception raised by monitoring service operations"""
    pass


class AdapterError(MCPMemoryError):
    """Exception raised by platform adapter operations"""
    pass


class HookError(MCPMemoryError):
    """Exception raised by plugin hook operations"""
    pass
