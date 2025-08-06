"""
Main configuration settings for MCP Memory Server
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus

from .environment import get_environment, get_env_config, Environment


@dataclass
class DatabaseConfig:
    """Database configuration"""
    # MongoDB connection
    uri: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_URI"))
    host: str = field(default_factory=lambda: os.getenv("MONGODB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("MONGODB_PORT", "27017")))
    username: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_PASSWORD"))
    database_name: str = field(default_factory=lambda: os.getenv("MONGODB_DATABASE", "mcp_memory"))
    collection_name: str = field(default_factory=lambda: os.getenv("MONGODB_COLLECTION", "memories"))
    
    # Connection pooling
    max_pool_size: int = field(default_factory=lambda: int(os.getenv("MONGODB_MAX_POOL_SIZE", "10")))
    min_pool_size: int = field(default_factory=lambda: int(os.getenv("MONGODB_MIN_POOL_SIZE", "1")))
    max_idle_time_ms: int = field(default_factory=lambda: int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "30000")))
    server_selection_timeout_ms: int = field(default_factory=lambda: int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000")))
    
    # SSL/TLS
    use_ssl: bool = field(default_factory=lambda: os.getenv("MONGODB_USE_SSL", "false").lower() == "true")
    ssl_cert_path: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_SSL_CERT_PATH"))
    
    @property
    def url(self) -> str:
        """Get MongoDB connection URL"""
        # If URI is provided (for MongoDB Atlas), use it directly
        if self.uri:
            return self.uri

        # Otherwise, build URL from components
        if self.username and self.password:
            # URL encode username and password
            username = quote_plus(self.username)
            password = quote_plus(self.password)
            auth = f"{username}:{password}@"
        else:
            auth = ""

        ssl_params = ""
        if self.use_ssl:
            ssl_params = "?ssl=true"
            if self.ssl_cert_path:
                ssl_params += f"&ssl_cert_reqs=CERT_REQUIRED&ssl_ca_certs={self.ssl_cert_path}"

        return f"mongodb://{auth}{self.host}:{self.port}/{self.database_name}{ssl_params}"


@dataclass
class EmbeddingConfig:
    """Embedding service configuration"""
    provider: str = field(default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "sentence_transformers"))
    model_name: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    model_cache_dir: str = field(default_factory=lambda: os.getenv("MODEL_CACHE_DIR", "./models"))
    batch_size: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_BATCH_SIZE", "32")))
    max_text_length: int = field(default_factory=lambda: int(os.getenv("MAX_TEXT_LENGTH", "512")))
    
    # OpenAI settings (if using OpenAI embeddings)
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"))
    
    # Hugging Face settings
    hf_token: Optional[str] = field(default_factory=lambda: os.getenv("HUGGINGFACE_TOKEN"))
    
    # Performance settings
    device: str = field(default_factory=lambda: os.getenv("EMBEDDING_DEVICE", "cpu"))
    normalize_embeddings: bool = field(default_factory=lambda: os.getenv("NORMALIZE_EMBEDDINGS", "true").lower() == "true")


@dataclass
class ServerConfig:
    """Server configuration"""
    name: str = field(default_factory=lambda: os.getenv("SERVER_NAME", "mcp-memory-server"))
    version: str = field(default_factory=lambda: os.getenv("SERVER_VERSION", "1.0.0"))
    host: str = field(default_factory=lambda: os.getenv("SERVER_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("SERVER_PORT", "8000")))
    
    # Performance
    workers: int = field(default_factory=lambda: int(os.getenv("SERVER_WORKERS", "1")))
    max_connections: int = field(default_factory=lambda: int(os.getenv("MAX_CONNECTIONS", "1000")))
    keepalive_timeout: int = field(default_factory=lambda: int(os.getenv("KEEPALIVE_TIMEOUT", "5")))
    
    # Security
    cors_origins: List[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(","))
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("API_KEY"))
    
    # Health checks
    health_check_interval: int = field(default_factory=lambda: int(os.getenv("HEALTH_CHECK_INTERVAL", "30")))


@dataclass
class MemoryConfig:
    """Memory management configuration"""
    default_project: str = field(default_factory=lambda: os.getenv("DEFAULT_PROJECT", "default"))
    max_search_results: int = field(default_factory=lambda: int(os.getenv("MAX_SEARCH_RESULTS", "20")))
    default_importance: float = field(default_factory=lambda: float(os.getenv("DEFAULT_IMPORTANCE", "0.5")))
    max_text_length: int = field(default_factory=lambda: int(os.getenv("MAX_TEXT_LENGTH", "10000")))
    similarity_threshold: float = field(default_factory=lambda: float(os.getenv("SIMILARITY_THRESHOLD", "0.3")))
    
    # Memory types
    memory_types: List[str] = field(default_factory=lambda: [
        "conversation", "function", "context", "knowledge", "decision", "error", "warning"
    ])
    
    # Auto-trigger settings
    auto_save_enabled: bool = field(default_factory=lambda: os.getenv("AUTO_SAVE_ENABLED", "true").lower() == "true")
    trigger_threshold: float = field(default_factory=lambda: float(os.getenv("TRIGGER_THRESHOLD", "0.7")))
    min_text_length: int = field(default_factory=lambda: int(os.getenv("MIN_TEXT_LENGTH", "50")))


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_expiration_hours: int = field(default_factory=lambda: int(os.getenv("JWT_EXPIRATION_HOURS", "24")))
    
    # Rate limiting
    rate_limit_enabled: bool = field(default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true")
    rate_limit_requests: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", "100")))
    rate_limit_window: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW", "3600")))  # 1 hour
    
    # Encryption
    encryption_enabled: bool = field(default_factory=lambda: os.getenv("ENCRYPTION_ENABLED", "false").lower() == "true")
    encryption_key: Optional[str] = field(default_factory=lambda: os.getenv("ENCRYPTION_KEY"))


@dataclass
class Config:
    """Main configuration class"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Environment
    environment: Environment = field(default_factory=get_environment)
    env_config: Dict[str, Any] = field(default_factory=get_env_config)
    
    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    models_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "models")
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Create necessary directories
        self.logs_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Apply environment-specific overrides
        self._apply_env_overrides()
        
        # Validate configuration
        self._validate()
    
    def _apply_env_overrides(self):
        """Apply environment-specific configuration overrides"""
        env_config = self.env_config
        
        # Override database pool size
        if "database_pool_size" in env_config:
            self.database.max_pool_size = env_config["database_pool_size"]
    
    def _validate(self):
        """Validate configuration"""
        # Validate required fields for production
        if self.environment == Environment.PRODUCTION:
            if not self.database.username or not self.database.password:
                raise ValueError("Database credentials required for production")
            
            if self.security.secret_key == "your-secret-key-change-in-production":
                raise ValueError("Secret key must be changed for production")
        
        # Validate embedding configuration
        if self.embedding.provider == "openai" and not self.embedding.openai_api_key:
            raise ValueError("OpenAI API key required when using OpenAI embeddings")
        
        # Validate paths
        if not self.base_dir.exists():
            raise ValueError(f"Base directory does not exist: {self.base_dir}")


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment"""
    global _config
    _config = Config()
    return _config
