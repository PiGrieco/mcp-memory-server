"""
MCP Memory Server - AI Memory Management System
"""

__version__ = "1.0.0"
__author__ = "MCP Memory Server Team"

from .core import MCPServer
from .services import memory_service
from .config import config

__all__ = ["MCPServer", "memory_service", "config"] 