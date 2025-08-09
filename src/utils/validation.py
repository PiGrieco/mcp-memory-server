"""
Validation utilities for MCP Memory Server
"""

from typing import Any, Dict


def validate_memory_data(data: Dict[str, Any]) -> bool:
    """Validate memory data"""
    required_fields = ["content", "project"]
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    
    return True


def validate_search_query(query: Dict[str, Any]) -> bool:
    """Validate search query"""
    if "query" not in query or not query["query"]:
        return False
    
    return True
