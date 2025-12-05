"""
Core models for the Suggestion Tunnel system.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4
from pydantic import BaseModel, Field


class SuggestionType(str, Enum):
    """Types of code suggestions - critical only, no optimizations."""
    BUG_FIX = "bug_fix"
    SECURITY_VULNERABILITY = "security_vulnerability"
    BREAKING_CHANGE = "breaking_change"
    RUNTIME_ERROR = "runtime_error"
    TYPE_ERROR = "type_error"
    LOGIC_ERROR = "logic_error"
    CRITICAL_REFACTOR = "critical_refactor"  # Only for critical structural issues


class SeverityLevel(str, Enum):
    """Severity levels for filtering."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


class Suggestion(BaseModel):
    """A code suggestion from Cursor IDE."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: SuggestionType
    severity: SeverityLevel
    file_path: str
    line_start: int
    line_end: Optional[int] = None
    code_snippet: str
    description: str
    suggested_fix: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "cursor_ide"  # Source of the suggestion
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_by_antigravity: bool = False
    sent_to_claude: bool = False


class Channel(BaseModel):
    """Communication channel for suggestions."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    is_active: bool = True
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SuggestionBin(BaseModel):
    """Container for grouped suggestions."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    channel_id: str
    suggestions: List[Suggestion] = Field(default_factory=list)
    status: str = "open"  # open, processing, closed
    priority: int = 0  # Higher = more urgent
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_suggestion(self, suggestion: Suggestion) -> None:
        """Add a suggestion to this bin."""
        self.suggestions.append(suggestion)
        self.updated_at = datetime.utcnow()
        # Auto-update priority based on severity
        if suggestion.severity == SeverityLevel.CRITICAL:
            self.priority = max(self.priority, 100)
        elif suggestion.severity == SeverityLevel.HIGH:
            self.priority = max(self.priority, 50)

    def get_critical_count(self) -> int:
        """Count critical suggestions."""
        return sum(1 for s in self.suggestions if s.severity == SeverityLevel.CRITICAL)
