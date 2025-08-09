"""
Logging configuration for MCP Memory Server
"""

import os
import logging
import logging.config
from pathlib import Path
from typing import Dict, Any

from .environment import get_environment, Environment


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration based on environment"""
    env = get_environment()
    
    # Base paths
    base_dir = Path(__file__).parent.parent.parent
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Log levels by environment
    log_levels = {
        Environment.DEVELOPMENT: "DEBUG",
        Environment.TESTING: "DEBUG", 
        Environment.STAGING: "INFO",
        Environment.PRODUCTION: "WARNING"
    }
    
    level = log_levels.get(env, "INFO")
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s - %(message)s"
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "line": %(lineno)d}',
                "datefmt": "%Y-%m-%dT%H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "detailed" if env == Environment.DEVELOPMENT else "simple",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": str(logs_dir / "mcp_memory_server.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": str(logs_dir / "errors.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "mcp_memory_server": {
                "level": level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "motor": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            }
        }
    }
    
    # Add JSON logging for production
    if env == Environment.PRODUCTION:
        config["handlers"]["json_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": str(logs_dir / "app.json.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10
        }
        config["loggers"][""]["handlers"].append("json_file")
    
    return config


def setup_logging() -> None:
    """Setup logging configuration"""
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Set up root logger
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for environment: {get_environment().value}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
