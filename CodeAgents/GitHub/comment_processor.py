"""
GitHub Comment Processor - Parse and process PR comments.

Extracts optimization suggestions, code improvements, and
learning opportunities from GitHub bot and reviewer comments.
"""

import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class CommentType(str, Enum):
    """Type of comment."""
    OPTIMIZATION = "optimization"
    BUG = "bug"
    STYLE = "style"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    APPROVAL = "approval"


class CommentSeverity(str, Enum):
    """Severity of comment."""
    BLOCKER = "blocker"
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class CodeSnippet(BaseModel):
    """Code snippet from comment."""
    language: str = "unknown"
    code: str
    context: str = ""  # Before/after labels


class OptimizationComment(BaseModel):
    """Parsed optimization comment."""
    comment_id: str
    author: str
    timestamp: datetime
    comment_type: CommentType
    severity: CommentSeverity
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_before: Optional[CodeSnippet] = None
    code_after: Optional[CodeSnippet] = None
    keywords: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    actionable: bool = True
    implemented: bool = False


class CommentProcessor:
    """
    Process GitHub comments to extract actionable insights.

    Detects optimization suggestions, code improvements,
    and creates learning opportunities for agents.
    """

    # Patterns for detecting comment types
    OPTIMIZATION_PATTERNS = [
        r"could be optimized",
        r"consider optimizing",
        r"optimize",
        r"more efficient",
        r"better performance",
        r"faster approach",
        r"use .+ instead",
        r"consider using",
        r"suggest using",
        r"recommend using",
    ]

    BUG_PATTERNS = [
        r"bug",
        r"error",
        r"incorrect",
        r"wrong",
        r"doesn't work",
        r"not working",
        r"issue with",
        r"problem with",
        r"fix",
    ]

    SECURITY_PATTERNS = [
        r"security",
        r"vulnerable",
        r"exploit",
        r"xss",
        r"injection",
        r"sanitize",
        r"validate input",
        r"authentication",
        r"authorization",
    ]

    PERFORMANCE_PATTERNS = [
        r"performance",
        r"slow",
        r"bottleneck",
        r"inefficient",
        r"memory",
        r"cpu",
        r"complexity",
        r"o\(n\^?\d+\)",
    ]

    STYLE_PATTERNS = [
        r"style",
        r"formatting",
        r"naming",
        r"convention",
        r"pep\s*8",
        r"eslint",
        r"prettier",
        r"consistent",
    ]

    ARCHITECTURE_PATTERNS = [
        r"architecture",
        r"design",
        r"pattern",
        r"structure",
        r"refactor",
        r"decouple",
        r"separation of concerns",
        r"solid",
        r"dry",
    ]

    DOCUMENTATION_PATTERNS = [
        r"documentation",
        r"docstring",
        r"comment",
        r"document",
        r"explain",
        r"clarify",
        r"readme",
    ]

    # Code block patterns
    CODE_BLOCK_PATTERN = r"```(\w*)\n(.*?)\n```"

    # Before/after patterns
    BEFORE_AFTER_PATTERN = r"(?:before|current|old):\s*```(\w*)\n(.*?)\n```\s*(?:after|new|proposed):\s*```(\w*)\n(.*?)\n```"

    def __init__(self):
        """Initialize comment processor."""
        self.processed_comments: List[OptimizationComment] = []

    def process_comment(
        self,
        comment_text: str,
        comment_id: str,
        author: str,
        timestamp: Optional[datetime] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
    ) -> Optional[OptimizationComment]:
        """
        Process a single comment.

        Args:
            comment_text: Comment text
            comment_id: Unique comment identifier
            author: Comment author
            timestamp: Comment timestamp
            file_path: File being commented on
            line_number: Line number being commented on

        Returns:
            OptimizationComment if comment is actionable, None otherwise
        """
        # Detect comment type
        comment_type = self._detect_comment_type(comment_text)

        # Skip non-actionable comments
        if comment_type == CommentType.APPROVAL or comment_type == CommentType.QUESTION:
            return None

        # Determine severity
        severity = self._determine_severity(comment_text, comment_type)

        # Extract title (first line or sentence)
        title = self._extract_title(comment_text)

        # Extract code snippets
        code_before, code_after = self._extract_code_snippets(comment_text)

        # Extract keywords
        keywords = self._extract_keywords(comment_text)

        # Extract tags
        tags = self._extract_tags(comment_text)

        # Create comment object
        parsed_comment = OptimizationComment(
            comment_id=comment_id,
            author=author,
            timestamp=timestamp or datetime.now(timezone.utc),
            comment_type=comment_type,
            severity=severity,
            title=title,
            description=comment_text,
            file_path=file_path,
            line_number=line_number,
            code_before=code_before,
            code_after=code_after,
            keywords=keywords,
            tags=tags,
            actionable=self._is_actionable(comment_text),
        )

        # Store processed comment
        self.processed_comments.append(parsed_comment)

        return parsed_comment

    def process_pr_comments(
        self,
        pr_data: Dict,
    ) -> List[OptimizationComment]:
        """
        Process all comments from a PR.

        Args:
            pr_data: Pull request data from GitHub API

        Returns:
            List of actionable optimization comments
        """
        comments = []

        # Process review comments
        if "comments" in pr_data:
            for comment in pr_data["comments"]:
                parsed = self.process_comment(
                    comment_text=comment.get("body", ""),
                    comment_id=str(comment.get("id")),
                    author=comment.get("user", {}).get("login", "unknown"),
                    timestamp=self._parse_timestamp(comment.get("created_at")),
                    file_path=comment.get("path"),
                    line_number=comment.get("line"),
                )

                if parsed:
                    comments.append(parsed)

        return comments

    def _detect_comment_type(self, text: str) -> CommentType:
        """Detect the type of comment."""
        text_lower = text.lower()

        # Check patterns in priority order
        if self._matches_any_pattern(text_lower, self.SECURITY_PATTERNS):
            return CommentType.SECURITY

        if self._matches_any_pattern(text_lower, self.BUG_PATTERNS):
            return CommentType.BUG

        if self._matches_any_pattern(text_lower, self.PERFORMANCE_PATTERNS):
            return CommentType.PERFORMANCE

        if self._matches_any_pattern(text_lower, self.OPTIMIZATION_PATTERNS):
            return CommentType.OPTIMIZATION

        if self._matches_any_pattern(text_lower, self.ARCHITECTURE_PATTERNS):
            return CommentType.ARCHITECTURE

        if self._matches_any_pattern(text_lower, self.STYLE_PATTERNS):
            return CommentType.STYLE

        if self._matches_any_pattern(text_lower, self.DOCUMENTATION_PATTERNS):
            return CommentType.DOCUMENTATION

        # Check for approval/question
        if any(word in text_lower for word in ["lgtm", "looks good", "approved", "approve"]):
            return CommentType.APPROVAL

        if "?" in text:
            return CommentType.QUESTION

        return CommentType.SUGGESTION

    def _determine_severity(self, text: str, comment_type: CommentType) -> CommentSeverity:
        """Determine severity of comment."""
        text_lower = text.lower()

        # Blocker keywords
        if any(word in text_lower for word in ["blocker", "must fix", "critical bug", "security vulnerability"]):
            return CommentSeverity.BLOCKER

        # Critical keywords
        if any(word in text_lower for word in ["critical", "urgent", "important", "necessary"]):
            return CommentSeverity.CRITICAL

        # Security and bugs are at least major
        if comment_type in [CommentType.SECURITY, CommentType.BUG]:
            return CommentSeverity.MAJOR

        # Major keywords
        if any(word in text_lower for word in ["should", "need to", "recommend"]):
            return CommentSeverity.MAJOR

        # Minor keywords
        if any(word in text_lower for word in ["could", "might", "consider", "optional"]):
            return CommentSeverity.MINOR

        # Default to info
        return CommentSeverity.INFO

    def _extract_title(self, text: str) -> str:
        """Extract title from comment."""
        # Take first line or first sentence
        lines = text.strip().split('\n')
        first_line = lines[0].strip()

        # If first line is short enough, use it
        if len(first_line) <= 100:
            return first_line

        # Otherwise, take first sentence
        sentences = re.split(r'[.!?]', text)
        if sentences:
            return sentences[0].strip()[:100]

        return first_line[:100]

    def _extract_code_snippets(
        self,
        text: str
    ) -> Tuple[Optional[CodeSnippet], Optional[CodeSnippet]]:
        """Extract before/after code snippets."""
        # Try to find before/after pattern
        match = re.search(self.BEFORE_AFTER_PATTERN, text, re.DOTALL | re.IGNORECASE)

        if match:
            before_lang, before_code, after_lang, after_code = match.groups()

            code_before = CodeSnippet(
                language=before_lang or "unknown",
                code=before_code.strip(),
                context="before"
            )

            code_after = CodeSnippet(
                language=after_lang or "unknown",
                code=after_code.strip(),
                context="after"
            )

            return code_before, code_after

        # Look for any code blocks
        code_blocks = re.findall(self.CODE_BLOCK_PATTERN, text, re.DOTALL)

        if len(code_blocks) == 2:
            # Assume first is before, second is after
            before_lang, before_code = code_blocks[0]
            after_lang, after_code = code_blocks[1]

            return (
                CodeSnippet(language=before_lang or "unknown", code=before_code.strip()),
                CodeSnippet(language=after_lang or "unknown", code=after_code.strip())
            )

        elif len(code_blocks) == 1:
            # Single code block - context unclear
            lang, code = code_blocks[0]
            return (
                None,
                CodeSnippet(language=lang or "unknown", code=code.strip())
            )

        return None, None

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from comment."""
        # Common technical keywords
        keyword_patterns = [
            r'\b(?:function|method|class|variable|constant)\s+\w+',
            r'\b(?:use|using|implement|implements)\s+(\w+)',
            r'\b(?:pattern|algorithm|approach)\s*:?\s*(\w+)',
            r'\b(?:library|package|module)\s+(\w+)',
        ]

        keywords = []

        for pattern in keyword_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract the captured keyword
                if match.groups():
                    keywords.append(match.group(1).lower())
                else:
                    keywords.append(match.group(0).lower())

        # Deduplicate
        return list(set(keywords))

    def _extract_tags(self, text: str) -> List[str]:
        """Extract hashtags and labels from comment."""
        # Find hashtags
        tags = re.findall(r'#(\w+)', text)

        # Find @-mentions that might be tags
        tags.extend(re.findall(r'@(\w+)', text))

        return list(set(tag.lower() for tag in tags))

    def _is_actionable(self, text: str) -> bool:
        """Determine if comment is actionable."""
        text_lower = text.lower()

        # Not actionable if just a question
        if text.count('?') > text.count('.'):
            return False

        # Not actionable if approval only
        if any(word in text_lower for word in ["lgtm", "looks good", "approved"]) and len(text) < 50:
            return False

        # Actionable if contains code suggestions
        if "```" in text:
            return True

        # Actionable if contains action verbs
        action_verbs = [
            "change", "update", "modify", "fix", "add", "remove",
            "refactor", "use", "implement", "consider", "should",
        ]

        return any(verb in text_lower for verb in action_verbs)

    def _matches_any_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> datetime:
        """Parse GitHub timestamp string."""
        if not timestamp_str:
            return datetime.now(timezone.utc)

        try:
            # GitHub format: 2025-12-03T12:00:00Z
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception:
            return datetime.now(timezone.utc)

    def get_comments_by_type(
        self,
        comment_type: CommentType
    ) -> List[OptimizationComment]:
        """Get all comments of a specific type."""
        return [
            comment for comment in self.processed_comments
            if comment.comment_type == comment_type
        ]

    def get_comments_by_severity(
        self,
        severity: CommentSeverity
    ) -> List[OptimizationComment]:
        """Get all comments of a specific severity."""
        return [
            comment for comment in self.processed_comments
            if comment.severity == severity
        ]

    def get_actionable_comments(self) -> List[OptimizationComment]:
        """Get all actionable comments."""
        return [
            comment for comment in self.processed_comments
            if comment.actionable and not comment.implemented
        ]

    def get_stats(self) -> Dict:
        """Get statistics about processed comments."""
        total = len(self.processed_comments)

        if total == 0:
            return {
                "total": 0,
                "by_type": {},
                "by_severity": {},
                "actionable": 0,
                "implemented": 0,
            }

        return {
            "total": total,
            "by_type": {
                ctype.value: len(self.get_comments_by_type(ctype))
                for ctype in CommentType
            },
            "by_severity": {
                severity.value: len(self.get_comments_by_severity(severity))
                for severity in CommentSeverity
            },
            "actionable": len([c for c in self.processed_comments if c.actionable]),
            "implemented": len([c for c in self.processed_comments if c.implemented]),
        }
