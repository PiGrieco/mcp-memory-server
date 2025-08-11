"""
Base models and mixins for MCP Memory Server
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod

T = TypeVar('T', bound='BaseModel')


class ValidationError(Exception):
    """Validation error for models"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


@dataclass
class BaseModel(ABC):
    """Base model class with validation and serialization"""
    
    def __post_init__(self):
        """Post-initialization validation"""
        self.validate()
    
    @abstractmethod
    def validate(self) -> None:
        """Validate model data"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create model from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update(self, **kwargs) -> None:
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid field: {key}")
        self.validate()


@dataclass
class TimestampMixin:
    """Mixin for models with timestamps"""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def touch(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()


def validate_required_field(value: Any, field_name: str) -> None:
    """Validate that a required field is not None or empty"""
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)
    
    if isinstance(value, str) and not value.strip():
        raise ValidationError(f"{field_name} cannot be empty", field_name)


def validate_string_length(value: str, field_name: str, min_length: int = 0, max_length: Optional[int] = None) -> None:
    """Validate string length"""
    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters", field_name)
    
    if max_length and len(value) > max_length:
        raise ValidationError(f"{field_name} must be at most {max_length} characters", field_name)


def validate_numeric_range(value: float, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> None:
    """Validate numeric range"""
    if min_value is not None and value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}", field_name)
    
    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}", field_name)


def validate_list_not_empty(value: list, field_name: str) -> None:
    """Validate that a list is not empty"""
    if not value:
        raise ValidationError(f"{field_name} cannot be empty", field_name)
