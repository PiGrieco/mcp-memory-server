"""
Custom exceptions for MCP Memory Server
"""

from typing import Optional, Dict, Any


class MCPMemoryError(Exception):
    """Base exception for MCP Memory Server"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class DatabaseError(MCPMemoryError):
    """Database operation error"""
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation


class EmbeddingError(MCPMemoryError):
    """Embedding service error"""
    
    def __init__(self, message: str, model: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EMBEDDING_ERROR", details)
        self.model = model


class ValidationError(MCPMemoryError):
    """Data validation error"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value


class NotFoundError(MCPMemoryError):
    """Resource not found error"""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} not found: {identifier}"
        details = {"resource": resource, "identifier": identifier}
        super().__init__(message, "NOT_FOUND", details)
        self.resource = resource
        self.identifier = identifier


class ConfigurationError(MCPMemoryError):
    """Configuration error"""
    
    def __init__(self, message: str, setting: Optional[str] = None):
        details = {}
        if setting:
            details["setting"] = setting
        
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.setting = setting


class AuthenticationError(MCPMemoryError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(MCPMemoryError):
    """Authorization error"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class RateLimitError(MCPMemoryError):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.retry_after = retry_after


class ServiceUnavailableError(MCPMemoryError):
    """Service unavailable error"""

    def __init__(self, service: str, message: Optional[str] = None):
        if not message:
            message = f"{service} service is unavailable"

        details = {"service": service}
        super().__init__(message, "SERVICE_UNAVAILABLE", details)
        self.service = service


class MemoryServiceError(MCPMemoryError):
    """Memory service specific error"""

    def __init__(self, message: str, operation: Optional[str] = None):
        details = {}
        if operation:
            details["operation"] = operation
        super().__init__(message, "MEMORY_SERVICE_ERROR", details)
        self.operation = operation
