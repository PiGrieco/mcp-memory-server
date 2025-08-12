"""
Memory models for MCP Memory Server
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memories"""
    CONVERSATION = "conversation"
    FUNCTION = "function"
    CONTEXT = "context"
    KNOWLEDGE = "knowledge"
    DECISION = "decision"
    ERROR = "error"
    WARNING = "warning"


class MemoryImportance(str, Enum):
    """Importance levels for memories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Memory:
    """Memory data model"""
    id: str
    project: str
    content: str
    memory_type: MemoryType
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    similarity_score: Optional[float] = None
    
    def increment_access(self) -> None:
        """Increment access count and update last accessed time"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class MemoryCreate(BaseModel):
    """Model for creating a new memory"""
    project: str = Field(..., description="Project name")
    content: str = Field(..., description="Memory content")
    memory_type: MemoryType = Field(default=MemoryType.CONVERSATION, description="Type of memory")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance level (0-1)")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context information")
    embedding: Optional[List[float]] = Field(default=None, description="Text embedding vector")


class MemoryUpdate(BaseModel):
    """Model for updating a memory"""
    content: Optional[str] = Field(default=None, description="Memory content")
    memory_type: Optional[MemoryType] = Field(default=None, description="Type of memory")
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Importance level (0-1)")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context information")
    embedding: Optional[List[float]] = Field(default=None, description="Text embedding vector")


class MemorySearchQuery(BaseModel):
    """Model for memory search queries"""
    query: str = Field(..., description="Search query")
    project: Optional[str] = Field(default=None, description="Project to search in")
    memory_types: Optional[List[MemoryType]] = Field(default=None, description="Filter by memory types")
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum importance")
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum number of results")
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum similarity score")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    user_id: Optional[str] = Field(default=None, description="Filter by user ID")
    session_id: Optional[str] = Field(default=None, description="Filter by session ID")
    date_from: Optional[datetime] = Field(default=None, description="Start date filter")
    date_to: Optional[datetime] = Field(default=None, description="End date filter")


class MemorySearchResult(BaseModel):
    """Model for memory search results"""
    memories: List[Memory] = Field(default_factory=list, description="Found memories")
    total_count: int = Field(default=0, description="Total number of memories found")
    query: str = Field(..., description="Original search query")
    search_time_ms: float = Field(default=0.0, description="Search execution time in milliseconds")
    similarity_scores: List[float] = Field(default_factory=list, description="Similarity scores for results")


class MemoryContext(BaseModel):
    """Model for memory context queries"""
    project: str = Field(..., description="Project name")
    types: List[MemoryType] = Field(default_factory=list, description="Memory types to include")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum number of memories per type")
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum importance")


class MemoryContextResult(BaseModel):
    """Model for memory context results"""
    project: str = Field(..., description="Project name")
    context: Dict[str, List[Memory]] = Field(default_factory=dict, description="Memories grouped by type")
    total_memories: int = Field(default=0, description="Total number of memories")
    retrieval_time_ms: float = Field(default=0.0, description="Retrieval time in milliseconds")


class MemoryStats(BaseModel):
    """Model for memory statistics"""
    total_memories: int = Field(default=0, description="Total number of memories")
    total_projects: int = Field(default=0, description="Total number of projects")
    memories_by_type: Dict[str, int] = Field(default_factory=dict, description="Count by memory type")
    memories_by_project: Dict[str, int] = Field(default_factory=dict, description="Count by project")
    avg_importance: float = Field(default=0.0, description="Average importance")
    last_activity: Optional[datetime] = Field(default=None, description="Last memory activity")


class MemoryHealth(BaseModel):
    """Model for memory system health"""
    status: str = Field(..., description="Health status")
    total_memories: int = Field(default=0, description="Total memories")
    storage_type: str = Field(default="unknown", description="Storage type")
    auto_save_enabled: bool = Field(default=False, description="Auto-save status")
    ml_triggers_enabled: bool = Field(default=False, description="ML triggers status")
    last_activity: str = Field(default="never", description="Last activity timestamp")
    error: Optional[str] = Field(default=None, description="Error message if unhealthy")
