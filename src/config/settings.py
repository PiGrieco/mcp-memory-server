"""

Configuration settings for MCP Memory Server
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path
import logging

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = field(default_factory=lambda: os.getenv(
        "MONGODB_URL", 
        "mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin"
    ))
    database_name: str = field(default_factory=lambda: os.getenv("DATABASE_NAME", "memory_db"))
    collection_name: str = field(default_factory=lambda: os.getenv("COLLECTION_NAME", "memories"))
    max_pool_size: int = field(default_factory=lambda: int(os.getenv("MONGODB_MAX_POOL_SIZE", "10")))
    min_pool_size: int = field(default_factory=lambda: int(os.getenv("MONGODB_MIN_POOL_SIZE", "1")))
    max_idle_time_ms: int = field(default_factory=lambda: int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "30000")))
    server_selection_timeout_ms: int = field(default_factory=lambda: int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000")))

@dataclass
class EmbeddingConfig:
    """Embedding model configuration"""
    model_name: str = field(default_factory=lambda: os.getenv(
        "EMBEDDING_MODEL", 
        "sentence-transformers/all-MiniLM-L6-v2"
    ))
    cache_dir: Optional[str] = field(default_factory=lambda: os.getenv("EMBEDDING_CACHE_DIR"))
    device: str = field(default_factory=lambda: os.getenv("EMBEDDING_DEVICE", "cpu"))
    normalize_embeddings: bool = field(default_factory=lambda: os.getenv("EMBEDDING_NORMALIZE", "true").lower() == "true")

@dataclass
class ServerConfig:
    """MCP Server configuration"""
    name: str = field(default_factory=lambda: os.getenv("MCP_SERVER_NAME", "memory-server"))
    version: str = field(default_factory=lambda: os.getenv("MCP_SERVER_VERSION", "1.0.0"))
    description: str = field(default_factory=lambda: os.getenv("MCP_SERVER_DESCRIPTION", "AI Memory Management Server"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

@dataclass
class MemoryConfig:
    """Memory management configuration"""
    default_project: str = field(default_factory=lambda: os.getenv("DEFAULT_PROJECT", "default"))
    max_search_results: int = field(default_factory=lambda: int(os.getenv("MAX_SEARCH_RESULTS", "20")))
    default_importance: float = field(default_factory=lambda: float(os.getenv("DEFAULT_IMPORTANCE", "0.5")))
    max_text_length: int = field(default_factory=lambda: int(os.getenv("MAX_TEXT_LENGTH", "10000")))
    similarity_threshold: float = field(default_factory=lambda: float(os.getenv("SIMILARITY_THRESHOLD", "0.3")))
    memory_types: list = field(default_factory=lambda: [
        "conversation", "function", "context", "knowledge", "decision", "error", "warning"
    ])

@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_auth: bool = field(default_factory=lambda: os.getenv("ENABLE_AUTH", "false").lower() == "true")
    api_key_header: str = field(default_factory=lambda: os.getenv("API_KEY_HEADER", "X-API-Key"))
    allowed_origins: list = field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "*").split(","))

@dataclass
class Config:
    """Main configuration class"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Environment
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")
    backups_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "backups")
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Create necessary directories
        self.logs_dir.mkdir(exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate configuration values"""
        if self.memory.max_search_results <= 0:
            raise ValueError("MAX_SEARCH_RESULTS must be positive")
        
        if not (0.0 <= self.memory.default_importance <= 1.0):
            raise ValueError("DEFAULT_IMPORTANCE must be between 0.0 and 1.0")
        
        if not (0.0 <= self.memory.similarity_threshold <= 1.0):
            raise ValueError("SIMILARITY_THRESHOLD must be between 0.0 and 1.0")
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.server.log_level,
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.server.log_level,
                    "formatter": "detailed",
                    "filename": str(self.logs_dir / "memory-server.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": self.server.log_level,
                    "propagate": False
                }
            }
        }

# Global configuration instance
config = Config() 