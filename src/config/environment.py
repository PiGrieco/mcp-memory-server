"""
Environment configuration management
"""

import os
from enum import Enum
from typing import Dict, Any


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


def get_environment() -> Environment:
    """Get current environment"""
    env_str = os.getenv("ENVIRONMENT", "development").lower()
    try:
        return Environment(env_str)
    except ValueError:
        return Environment.DEVELOPMENT


def is_production() -> bool:
    """Check if running in production"""
    return get_environment() == Environment.PRODUCTION


def is_development() -> bool:
    """Check if running in development"""
    return get_environment() == Environment.DEVELOPMENT


def is_testing() -> bool:
    """Check if running in testing"""
    return get_environment() == Environment.TESTING


def get_env_config() -> Dict[str, Any]:
    """Get environment-specific configuration"""
    env = get_environment()
    
    base_config = {
        "debug": False,
        "log_level": "INFO",
        "database_pool_size": 10,
        "enable_metrics": True,
        "enable_health_checks": True,
    }
    
    env_configs = {
        Environment.DEVELOPMENT: {
            "debug": True,
            "log_level": "DEBUG",
            "database_pool_size": 5,
            "enable_metrics": False,
        },
        Environment.TESTING: {
            "debug": True,
            "log_level": "DEBUG",
            "database_pool_size": 2,
            "enable_metrics": False,
            "enable_health_checks": False,
        },
        Environment.STAGING: {
            "debug": False,
            "log_level": "INFO",
            "database_pool_size": 8,
        },
        Environment.PRODUCTION: {
            "debug": False,
            "log_level": "WARNING",
            "database_pool_size": 20,
            "enable_metrics": True,
            "enable_health_checks": True,
        }
    }
    
    config = base_config.copy()
    config.update(env_configs.get(env, {}))
    return config
