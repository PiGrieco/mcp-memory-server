"""
Memory models for MCP Memory Server
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from .base import (
    BaseModel, 
    TimestampMixin, 
    ValidationError,
    validate_required_field,
    validate_string_length,
    validate_numeric_range,
    validate_list_not_empty
)


class MemoryType(Enum):
    """Types of memories"""
    CONVERSATION = "conversation"
    FUNCTION = "function"
    CONTEXT = "context"
    KNOWLEDGE = "knowledge"
    DECISION = "decision"
    ERROR = "error"
    WARNING = "warning"
    SYSTEM = "system"
    USER = "user"


class MemoryImportance(Enum):
    """Memory importance levels"""
    LOW = 0.2
    MEDIUM = 0.5
    HIGH = 0.8
    CRITICAL = 1.0


@dataclass
class Memory(BaseModel, TimestampMixin):
    """Memory model"""
    id: Optional[str] = None
    project: str = ""
    content: str = ""
    memory_type: MemoryType = MemoryType.CONVERSATION
    importance: float = MemoryImportance.MEDIUM.value
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    
    # Context information
    context: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Search and retrieval
    similarity_score: Optional[float] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def validate(self) -> None:
        """Validate memory data"""
        validate_required_field(self.project, "project")
        validate_required_field(self.content, "content")
        
        validate_string_length(self.project, "project", min_length=1, max_length=100)
        validate_string_length(self.content, "content", min_length=1, max_length=50000)
        
        validate_numeric_range(self.importance, "importance", min_value=0.0, max_value=1.0)
        
        if self.similarity_score is not None:
            validate_numeric_range(self.similarity_score, "similarity_score", min_value=0.0, max_value=1.0)
        
        if self.source:
            validate_string_length(self.source, "source", max_length=200)
    
    def increment_access(self) -> None:
        """Increment access count and update last accessed time"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        self.touch()


@dataclass
class MemoryCreate(BaseModel):
    """Model for creating a new memory"""
    project: str = ""
    content: str = ""
    memory_type: MemoryType = MemoryType.CONVERSATION
    importance: float = MemoryImportance.MEDIUM.value
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    context: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def validate(self) -> None:
        """Validate memory creation data"""
        validate_required_field(self.project, "project")
        validate_required_field(self.content, "content")
        
        validate_string_length(self.project, "project", min_length=1, max_length=100)
        validate_string_length(self.content, "content", min_length=1, max_length=50000)
        
        validate_numeric_range(self.importance, "importance", min_value=0.0, max_value=1.0)
        
        if self.source:
            validate_string_length(self.source, "source", max_length=200)


@dataclass
class MemoryUpdate(BaseModel):
    """Model for updating a memory"""
    content: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    importance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    
    def validate(self) -> None:
        """Validate memory update data"""
        if self.content is not None:
            validate_string_length(self.content, "content", min_length=1, max_length=50000)
        
        if self.importance is not None:
            validate_numeric_range(self.importance, "importance", min_value=0.0, max_value=1.0)


@dataclass
class MemorySearchQuery(BaseModel):
    """Model for memory search queries"""
    query: str = ""
    project: Optional[str] = None
    memory_types: List[MemoryType] = field(default_factory=list)
    min_importance: float = 0.0
    max_results: int = 20
    similarity_threshold: float = 0.3
    tags: List[str] = field(default_factory=list)
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    def validate(self) -> None:
        """Validate search query"""
        validate_required_field(self.query, "query")
        validate_string_length(self.query, "query", min_length=1, max_length=1000)
        
        validate_numeric_range(self.min_importance, "min_importance", min_value=0.0, max_value=1.0)
        validate_numeric_range(self.similarity_threshold, "similarity_threshold", min_value=0.0, max_value=1.0)
        validate_numeric_range(self.max_results, "max_results", min_value=1, max_value=100)
        
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError("date_from must be before date_to")


@dataclass
class MemorySearchResult(BaseModel):
    """Model for memory search results"""
    memories: List[Memory] = field(default_factory=list)
    total_count: int = 0
    query: str = ""
    search_time_ms: float = 0.0
    similarity_scores: List[float] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate search result"""
        validate_numeric_range(self.total_count, "total_count", min_value=0)
        validate_numeric_range(self.search_time_ms, "search_time_ms", min_value=0)
        
        if len(self.memories) != len(self.similarity_scores):
            raise ValidationError("memories and similarity_scores must have the same length")


@dataclass
class MemoryContext(BaseModel):
    """Model for memory context queries"""
    project: str = ""
    types: List[MemoryType] = field(default_factory=list)
    limit: int = 50
    min_importance: float = 0.0
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def validate(self) -> None:
        """Validate context query"""
        validate_required_field(self.project, "project")
        validate_string_length(self.project, "project", min_length=1, max_length=100)
        validate_list_not_empty(self.types, "types")
        validate_numeric_range(self.limit, "limit", min_value=1, max_value=200)
        validate_numeric_range(self.min_importance, "min_importance", min_value=0.0, max_value=1.0)


@dataclass
class MemoryContextResult(BaseModel):
    """Model for memory context results"""
    project: str = ""
    context: Dict[str, List[Memory]] = field(default_factory=dict)
    total_memories: int = 0
    retrieval_time_ms: float = 0.0
    
    def validate(self) -> None:
        """Validate context result"""
        validate_required_field(self.project, "project")
        validate_numeric_range(self.total_memories, "total_memories", min_value=0)
        validate_numeric_range(self.retrieval_time_ms, "retrieval_time_ms", min_value=0)
