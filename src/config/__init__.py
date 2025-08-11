"""
Configuration management for MCP Memory Server
"""

from .settings import Config, get_config
from .logging_config import setup_logging, get_logging_config
from .environment import Environment, get_environment

# Global configuration instance
config = get_config()

__all__ = [
    "Config",
    "config", 
    "get_config",
    "setup_logging",
    "get_logging_config",
    "Environment",
    "get_environment"
]
