"""
Configuration management for MCP Memory Server
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Server configuration"""
    name: str = "MCP Memory Server"
    version: str = "2.0.0"
    host: str = "localhost"
    port: int = 8000
    mode: str = "universal"  # universal, mcp_only, http_only
    debug: bool = False


class EnvironmentConfig(BaseModel):
    """Environment configuration"""
    name: str = "development"  # development, staging, production
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_health_checks: bool = True


class MemoryConfig(BaseModel):
    """Memory configuration"""
    storage: str = "mongodb"  # mongodb, postgresql, sqlite
    auto_save: bool = True
    ml_triggers: bool = True
    trigger_threshold: float = 0.7
    min_text_length: int = 10
    max_text_length: int = 10000
    default_project: str = "default"
    retention_days: int = 365


class DatabaseConfig(BaseModel):
    """Database configuration"""
    mongodb: Dict[str, Any] = Field(default_factory=lambda: {
        "uri": "mongodb://localhost:27017",
        "database": "mcp_memory",
        "collection": "memories",
        "max_pool_size": 10,
        "min_pool_size": 1,
        "max_idle_time_ms": 30000,
        "server_selection_timeout_ms": 5000
    })


class EmbeddingConfig(BaseModel):
    """Embedding configuration"""
    provider: str = "sentence_transformers"  # sentence_transformers, huggingface
    model_name: str = "all-MiniLM-L6-v2"
    model_cache_dir: str = "./models"
    device: str = "cpu"  # cpu, cuda, mps
    max_text_length: int = 512
    normalize_embeddings: bool = True


class MLTriggersConfig(BaseModel):
    """ML Triggers configuration"""
    enabled: bool = True
    model_path: str = "./models/trigger_model.pkl"
    confidence_threshold: float = 0.8
    retrain_interval_hours: int = 24


class SecurityConfig(BaseModel):
    """Security configuration"""
    enable_auth: bool = False
    jwt_secret: str = "your-secret-key"
    api_key_required: bool = False
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])


class PlatformConfig(BaseModel):
    """Platform-specific configuration"""
    name: str = "Platform"
    auto_trigger: bool = True
    ide_integration: bool = False
    code_analysis: bool = False
    file_watching: bool = False
    conversation_mode: bool = False
    context_integration: bool = False
    api_enabled: bool = False
    webhook_support: bool = False
    supported_languages: List[str] = Field(default_factory=list)
    max_context_length: int = 4000


class PlatformsConfig(BaseModel):
    """Platforms configuration"""
    cursor: PlatformConfig = Field(default_factory=lambda: PlatformConfig(
        name="Cursor IDE",
        auto_trigger=True,
        ide_integration=True,
        code_analysis=True,
        file_watching=True,
        supported_languages=["python", "javascript", "typescript", "java", "cpp"]
    ))
    claude: PlatformConfig = Field(default_factory=lambda: PlatformConfig(
        name="Claude Desktop",
        auto_trigger=True,
        conversation_mode=True,
        context_integration=True,
        max_context_length=4000
    ))
    universal: PlatformConfig = Field(default_factory=lambda: PlatformConfig(
        name="Universal Platform",
        auto_trigger=True,
        api_enabled=True,
        webhook_support=True
    ))


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "./logs/mcp_memory.log"
    max_size_mb: int = 100
    backup_count: int = 5


class PathsConfig(BaseModel):
    """Paths configuration"""
    data_dir: str = "./data"
    logs_dir: str = "./logs"
    models_dir: str = "./models"
    plugins_dir: str = "./plugins"
    exports_dir: str = "./exports"


class PluginsConfig(BaseModel):
    """Plugins configuration"""
    directory: str = "./plugins"
    auto_load: bool = True
    enable_hot_reload: bool = False
    builtin_plugins: List[str] = Field(default_factory=lambda: [
        "memory_analytics",
        "backup_manager", 
        "notification_service",
        "export_service"
    ])


class CacheConfig(BaseModel):
    """Cache configuration"""
    redis_enabled: bool = False
    redis: Dict[str, Any] = Field(default_factory=lambda: {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None
    })
    memory_ttl: int = 3600  # 1 hour
    search_ttl: int = 1800  # 30 minutes
    embedding_ttl: int = 7200  # 2 hours
    cleanup_interval: int = 300  # 5 minutes


class BackupConfig(BaseModel):
    """Backup configuration"""
    enabled: bool = True
    schedule: str = "0 2 * * *"  # Daily at 2 AM
    retention_days: int = 30
    compression: bool = True
    storage: Dict[str, Any] = Field(default_factory=lambda: {
        "type": "local",  # local, s3, gcs
        "path": "./backups"
    })


class NotificationsConfig(BaseModel):
    """Notifications configuration"""
    enabled: bool = False
    providers: Dict[str, Any] = Field(default_factory=lambda: {
        "email": {
            "enabled": False,
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": ""
        },
        "webhook": {
            "enabled": False,
            "url": "",
            "headers": {}
        }
    })


class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    enabled: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    alert_thresholds: Dict[str, Any] = Field(default_factory=lambda: {
        "memory_usage_percent": 80,
        "response_time_ms": 1000,
        "error_rate_percent": 5
    })


class ExportConfig(BaseModel):
    """Export configuration"""
    formats: List[str] = Field(default_factory=lambda: ["json", "csv", "markdown"])
    include_embeddings: bool = False
    batch_size: int = 1000
    compression: bool = True


@dataclass
class Settings:
    """Main settings class"""
    server: ServerConfig = field(default_factory=ServerConfig)
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    ml_triggers: MLTriggersConfig = field(default_factory=MLTriggersConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    platforms: PlatformsConfig = field(default_factory=PlatformsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    plugins: PluginsConfig = field(default_factory=PluginsConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    notifications: NotificationsConfig = field(default_factory=NotificationsConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    
    def __post_init__(self):
        """Post-initialization setup"""
        self._load_from_yaml()
        self._load_from_env()
        self._create_directories()
    
    def _load_from_yaml(self):
        """Load configuration from YAML file"""
        config_file = Path("config/settings.yaml")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                    self._update_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Could not load YAML config: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Server settings
        if os.getenv("SERVER_HOST"):
            self.server.host = os.getenv("SERVER_HOST")
        if os.getenv("SERVER_PORT"):
            self.server.port = int(os.getenv("SERVER_PORT"))
        if os.getenv("SERVER_MODE"):
            self.server.mode = os.getenv("SERVER_MODE")
        
        # Database settings
        if os.getenv("MONGODB_URI"):
            self.database.mongodb["uri"] = os.getenv("MONGODB_URI")
        if os.getenv("MONGODB_DATABASE"):
            self.database.mongodb["database"] = os.getenv("MONGODB_DATABASE")
        
        # Environment settings
        if os.getenv("ENVIRONMENT"):
            self.environment.name = os.getenv("ENVIRONMENT")
        if os.getenv("LOG_LEVEL"):
            self.environment.log_level = os.getenv("LOG_LEVEL")
        
        # Embedding settings
        if os.getenv("EMBEDDING_PROVIDER"):
            self.embedding.provider = os.getenv("EMBEDDING_PROVIDER")
        if os.getenv("EMBEDDING_MODEL"):
            self.embedding.model_name = os.getenv("EMBEDDING_MODEL")
        
        # Cache settings
        if os.getenv("REDIS_ENABLED"):
            self.cache.redis_enabled = os.getenv("REDIS_ENABLED").lower() == "true"
        if os.getenv("REDIS_HOST"):
            self.cache.redis["host"] = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            self.cache.redis["port"] = int(os.getenv("REDIS_PORT"))
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update settings from dictionary"""
        for key, value in config_data.items():
            if hasattr(self, key):
                attr = getattr(self, key)
                if hasattr(attr, 'model_validate'):
                    # Pydantic model
                    setattr(self, key, attr.__class__.model_validate(value))
                else:
                    # Regular attribute
                    setattr(self, key, value)
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.paths.data_dir,
            self.paths.logs_dir,
            self.paths.models_dir,
            self.paths.plugins_dir,
            self.paths.exports_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from configuration files"""
    global _settings
    _settings = Settings()
    return _settings
