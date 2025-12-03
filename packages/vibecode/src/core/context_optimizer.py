"""
Context Optimizer - Smart context assembly with token optimization.

Assembles the most relevant context within token budget using
semantic search, relevance ranking, and compression strategies.
"""

import hashlib
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from ..models.vibe_session import VibeIntent, VibeContext


class ContextOptimizer:
    """
    Optimizes context assembly for code generation.

    Uses multiple strategies to fit the most relevant information
    within token budgets while maximizing context quality.
    """

    def __init__(self, memory_service=None, token_counter=None):
        """
        Initialize context optimizer.

        Args:
            memory_service: Memory service for retrieving training materials
            token_counter: Function to count tokens (default: estimate)
        """
        self.memory_service = memory_service
        self.token_counter = token_counter or self._estimate_tokens

        # Cache for embeddings and summaries
        self._context_cache: Dict[str, any] = {}
        self._summary_cache: Dict[str, str] = {}

    def assemble_context(
        self,
        intent: VibeIntent,
        max_tokens: int,
        agent_id: str,
        codebase_path: Optional[Path] = None,
    ) -> VibeContext:
        """
        Assemble optimized context for code generation.

        Args:
            intent: Parsed user intent
            max_tokens: Maximum tokens for context
            agent_id: Agent identifier
            codebase_path: Path to codebase for file search

        Returns:
            VibeContext with selected materials
        """
        context = VibeContext()
        remaining_tokens = max_tokens

        # 1. Retrieve relevant code snippets (40% of budget)
        code_budget = int(max_tokens * 0.4)
        relevant_code, code_tokens = self._retrieve_relevant_code(
            intent,
            code_budget,
            codebase_path
        )
        context.relevant_code = relevant_code
        context.token_breakdown["code"] = code_tokens
        remaining_tokens -= code_tokens

        # 2. Retrieve matched patterns (30% of budget)
        pattern_budget = int(max_tokens * 0.3)
        patterns, pattern_tokens = self._retrieve_patterns(
            intent,
            min(pattern_budget, remaining_tokens)
        )
        context.patterns = patterns
        context.token_breakdown["patterns"] = pattern_tokens
        remaining_tokens -= pattern_tokens

        # 3. Retrieve agent memory (30% of budget)
        if self.memory_service and remaining_tokens > 0:
            memory_budget = min(int(max_tokens * 0.3), remaining_tokens)
            memory, memory_tokens = self._retrieve_agent_memory(
                intent,
                agent_id,
                memory_budget
            )
            context.agent_memory = memory
            context.token_breakdown["memory"] = memory_tokens
            remaining_tokens -= memory_tokens

        # Calculate total tokens
        context.total_tokens = max_tokens - remaining_tokens

        return context

    def _retrieve_relevant_code(
        self,
        intent: VibeIntent,
        max_tokens: int,
        codebase_path: Optional[Path] = None
    ) -> Tuple[List[Dict], int]:
        """
        Retrieve relevant code snippets from codebase.

        Args:
            intent: Parsed intent
            max_tokens: Token budget
            codebase_path: Path to search

        Returns:
            Tuple of (code snippets, total tokens)
        """
        snippets = []
        total_tokens = 0

        if not codebase_path or not codebase_path.exists():
            return snippets, total_tokens

        # Search for relevant files based on context needs
        relevant_files = self._find_relevant_files(intent, codebase_path)

        for file_path in relevant_files:
            if total_tokens >= max_tokens:
                break

            try:
                content = file_path.read_text(encoding="utf-8")

                # Check if we have a cached summary
                cache_key = self._get_cache_key(str(file_path))
                if cache_key in self._summary_cache:
                    content = self._summary_cache[cache_key]
                    context.cache_hits += 1
                else:
                    # Optionally summarize if too large
                    content_tokens = self.token_counter(content)
                    if content_tokens > max_tokens * 0.3:
                        content = self._summarize_code(content, intent)
                        self._summary_cache[cache_key] = content
                        context.compression_applied = True

                snippet_tokens = self.token_counter(content)

                if total_tokens + snippet_tokens > max_tokens:
                    # Truncate to fit
                    available = max_tokens - total_tokens
                    content = self._truncate_to_tokens(content, available)
                    snippet_tokens = available
                    context.truncated_items.append(str(file_path))

                snippets.append({
                    "file_path": str(file_path),
                    "content": content,
                    "tokens": snippet_tokens,
                    "relevance": self._calculate_relevance(content, intent),
                })

                total_tokens += snippet_tokens

            except Exception as e:
                # Skip files that can't be read
                continue

        # Sort by relevance (highest first)
        snippets.sort(key=lambda s: s["relevance"], reverse=True)

        return snippets, total_tokens

    def _retrieve_patterns(
        self,
        intent: VibeIntent,
        max_tokens: int
    ) -> Tuple[List[Dict], int]:
        """
        Retrieve matched code generation patterns.

        Args:
            intent: Parsed intent
            max_tokens: Token budget

        Returns:
            Tuple of (patterns, total tokens)
        """
        patterns = []
        total_tokens = 0

        # In a full implementation, this would query a pattern database
        # For now, return matched pattern IDs from intent
        for pattern_id in intent.matched_patterns:
            if total_tokens >= max_tokens:
                break

            # Placeholder pattern retrieval
            pattern_content = f"Pattern: {pattern_id}\n# Template code here..."
            pattern_tokens = self.token_counter(pattern_content)

            if total_tokens + pattern_tokens <= max_tokens:
                patterns.append({
                    "pattern_id": pattern_id,
                    "content": pattern_content,
                    "tokens": pattern_tokens,
                })
                total_tokens += pattern_tokens

        return patterns, total_tokens

    def _retrieve_agent_memory(
        self,
        intent: VibeIntent,
        agent_id: str,
        max_tokens: int
    ) -> Tuple[List[Dict], int]:
        """
        Retrieve relevant memories from agent's past learnings.

        Args:
            intent: Parsed intent
            agent_id: Agent identifier
            max_tokens: Token budget

        Returns:
            Tuple of (memories, total tokens)
        """
        memories = []
        total_tokens = 0

        if not self.memory_service:
            return memories, total_tokens

        # Build search query from intent
        query = self._build_memory_query(intent)

        try:
            # Use memory service with token budget
            result = self.memory_service.recall_with_token_budget(
                topic=query,
                max_tokens=max_tokens,
                agent_id=agent_id,
                relevance_threshold=0.6,
            )

            memories = result.get("materials", [])
            total_tokens = result.get("total_tokens", 0)

        except Exception as e:
            # Fall back to empty memories on error
            pass

        return memories, total_tokens

    def _find_relevant_files(
        self,
        intent: VibeIntent,
        codebase_path: Path
    ) -> List[Path]:
        """Find files relevant to the intent."""
        relevant_files = []

        if not intent.language:
            return relevant_files

        # Map language to file extensions
        ext_map = {
            "python": [".py"],
            "javascript": [".js", ".jsx"],
            "typescript": [".ts", ".tsx"],
            "rust": [".rs"],
            "go": [".go"],
            "java": [".java"],
            "c++": [".cpp", ".hpp", ".h"],
            "c": [".c", ".h"],
        }

        extensions = ext_map.get(intent.language, [])

        # Search for files with matching extensions
        for ext in extensions:
            relevant_files.extend(codebase_path.rglob(f"*{ext}"))

        # Limit to top 10 files to avoid excessive scanning
        return relevant_files[:10]

    def _calculate_relevance(self, content: str, intent: VibeIntent) -> float:
        """
        Calculate relevance score for content.

        Args:
            content: Code content
            intent: User intent

        Returns:
            Relevance score 0-1
        """
        content_lower = content.lower()
        score = 0.0

        # Keyword matching
        matched_keywords = sum(
            1 for kw in intent.keywords
            if kw in content_lower
        )
        if intent.keywords:
            score += (matched_keywords / len(intent.keywords)) * 0.6

        # Target entity matching
        if intent.target in content_lower:
            score += 0.2

        # Framework matching
        if intent.framework and intent.framework in content_lower:
            score += 0.2

        return min(1.0, score)

    def _summarize_code(self, code: str, intent: VibeIntent) -> str:
        """
        Summarize code to reduce token count.

        Simple implementation: extract relevant functions/classes.

        Args:
            code: Full code content
            intent: User intent

        Returns:
            Summarized code
        """
        lines = code.split('\n')
        summary_lines = []

        # Keep imports
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                summary_lines.append(line)

        # Keep function/class signatures that match keywords
        in_relevant_block = False
        for line in lines:
            stripped = line.strip()

            # Check if this is a definition line
            if any(stripped.startswith(kw) for kw in ['def ', 'class ', 'async def ']):
                # Check if it matches intent keywords
                if any(kw in stripped.lower() for kw in intent.keywords):
                    in_relevant_block = True
                    summary_lines.append(line)
                else:
                    in_relevant_block = False
            elif in_relevant_block:
                summary_lines.append(line)
                # Stop after docstring or first few lines
                if len(summary_lines) % 20 == 0:
                    in_relevant_block = False

        return '\n'.join(summary_lines[:100])  # Limit to 100 lines

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token budget."""
        current_tokens = self.token_counter(text)

        if current_tokens <= max_tokens:
            return text

        # Estimate characters per token (rough: 4 chars = 1 token)
        chars_per_token = len(text) / current_tokens if current_tokens > 0 else 4
        target_chars = int(max_tokens * chars_per_token * 0.9)  # 90% to be safe

        return text[:target_chars] + "\n... (truncated)"

    def _build_memory_query(self, intent: VibeIntent) -> str:
        """Build search query for memory retrieval."""
        query_parts = []

        if intent.action:
            query_parts.append(intent.action)

        if intent.target:
            query_parts.append(intent.target)

        if intent.language:
            query_parts.append(intent.language)

        query_parts.extend(intent.keywords[:5])  # Top 5 keywords

        return " ".join(query_parts)

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens in text.

        Fallback method when no tokenizer available.

        Args:
            text: Text to count

        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for content."""
        return hashlib.md5(text.encode()).hexdigest()

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            "context_cache_size": len(self._context_cache),
            "summary_cache_size": len(self._summary_cache),
        }

    def clear_cache(self):
        """Clear all caches."""
        self._context_cache.clear()
        self._summary_cache.clear()
