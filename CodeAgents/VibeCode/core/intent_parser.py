"""
Intent Parser - Natural language to structured intent.

Parses user input to extract action, target, language, and context requirements.
"""

import re
from typing import Dict, List, Optional, Set
from ..models.vibe_session import VibeIntent, VibeConfidence


class IntentParser:
    """
    Parser that converts natural language to structured VibeIntent.

    Uses pattern matching and keyword extraction to understand
    what the user wants to create or modify.
    """

    # Action keywords
    ACTIONS = {
        "create": ["create", "add", "new", "generate", "make", "build", "implement", "write"],
        "modify": ["modify", "change", "update", "edit", "alter", "adjust", "refactor"],
        "delete": ["delete", "remove", "drop"],
        "test": ["test", "check", "verify", "validate"],
        "fix": ["fix", "repair", "debug", "correct"],
        "optimize": ["optimize", "improve", "enhance", "speed up"],
        "document": ["document", "comment", "explain"],
        "refactor": ["refactor", "restructure", "reorganize", "clean up"],
    }

    # Target entities
    TARGETS = {
        "function": ["function", "func", "method", "def", "fn"],
        "class": ["class", "object", "type"],
        "api": ["api", "endpoint", "route", "handler"],
        "database": ["database", "db", "table", "model", "schema"],
        "test": ["test", "spec", "unit test", "integration test"],
        "component": ["component", "widget", "ui", "interface"],
        "service": ["service", "module", "package"],
        "config": ["config", "configuration", "settings"],
    }

    # Programming languages
    LANGUAGES = [
        "python", "javascript", "typescript", "rust", "go", "java",
        "c++", "c", "cpp", "csharp", "c#", "ruby", "php", "swift",
        "kotlin", "dart", "sql", "bash", "shell"
    ]

    # Frameworks
    FRAMEWORKS = {
        "python": ["fastapi", "flask", "django", "pytest", "sqlalchemy"],
        "javascript": ["react", "vue", "angular", "express", "next.js", "nest.js"],
        "typescript": ["react", "vue", "angular", "express", "next.js", "nest.js"],
        "rust": ["actix", "rocket", "axum", "tokio"],
        "go": ["gin", "echo", "fiber"],
    }

    # Complexity indicators
    COMPLEXITY_KEYWORDS = {
        "simple": ["simple", "basic", "quick", "easy", "straightforward"],
        "moderate": ["moderate", "standard", "typical", "normal"],
        "complex": ["complex", "advanced", "sophisticated", "comprehensive", "full"],
    }

    # Context requirements
    CONTEXT_NEEDS = {
        "db_schema": ["database", "table", "model", "schema", "orm"],
        "auth": ["auth", "authentication", "login", "user", "permission"],
        "models": ["model", "class", "type", "interface"],
        "config": ["config", "settings", "environment"],
        "existing_code": ["modify", "update", "extend", "refactor"],
    }

    def __init__(self):
        """Initialize the intent parser."""
        self._action_patterns = self._compile_action_patterns()
        self._target_patterns = self._compile_target_patterns()

    def parse(self, user_input: str) -> VibeIntent:
        """
        Parse natural language input into structured intent.

        Args:
            user_input: Natural language description of what to create

        Returns:
            VibeIntent with parsed components
        """
        user_input_lower = user_input.lower()

        # Extract action
        action = self._extract_action(user_input_lower)

        # Extract target
        target = self._extract_target(user_input_lower)

        # Extract language
        language = self._extract_language(user_input_lower)

        # Extract framework
        framework = self._extract_framework(user_input_lower, language)

        # Extract keywords
        keywords = self._extract_keywords(user_input_lower)

        # Extract entities (specific names, paths, etc.)
        entities = self._extract_entities(user_input)

        # Determine context requirements
        requires_context = self._determine_context_needs(user_input_lower, action)

        # Assess complexity
        complexity = self._assess_complexity(user_input_lower, keywords)

        # Calculate confidence
        confidence = self._calculate_confidence(
            action, target, language, len(keywords)
        )

        # Recommend token budget based on complexity
        token_budget = self._recommend_token_budget(complexity, target)

        return VibeIntent(
            raw_input=user_input,
            action=action,
            target=target,
            language=language,
            framework=framework,
            keywords=keywords,
            entities=entities,
            requires_context=requires_context,
            estimated_complexity=complexity,
            recommended_token_budget=token_budget,
            confidence=confidence,
        )

    def _extract_action(self, text: str) -> str:
        """Extract the primary action from text."""
        for action, keywords in self.ACTIONS.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    return action

        # Default action if none detected
        return "create"

    def _extract_target(self, text: str) -> str:
        """Extract the target entity from text."""
        for target, keywords in self.TARGETS.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    return target

        # Default to generic code
        return "code"

    def _extract_language(self, text: str) -> Optional[str]:
        """Extract programming language from text."""
        for lang in self.LANGUAGES:
            # Check for language mentions
            pattern = r'\b' + re.escape(lang) + r'\b'
            if re.search(pattern, text):
                return lang

        # Check for file extensions
        ext_match = re.search(r'\.([a-z]+)\b', text)
        if ext_match:
            ext = ext_match.group(1)
            ext_to_lang = {
                "py": "python",
                "js": "javascript",
                "ts": "typescript",
                "rs": "rust",
                "go": "go",
                "java": "java",
                "cpp": "c++",
                "c": "c",
                "cs": "csharp",
                "rb": "ruby",
                "php": "php",
            }
            if ext in ext_to_lang:
                return ext_to_lang[ext]

        return None

    def _extract_framework(self, text: str, language: Optional[str]) -> Optional[str]:
        """Extract framework from text given the language."""
        if not language:
            return None

        frameworks = self.FRAMEWORKS.get(language, [])
        for framework in frameworks:
            if framework in text:
                return framework

        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Remove common stop words
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "can", "to", "for",
            "of", "in", "on", "at", "by", "with", "from", "about", "that",
            "this", "these", "those", "i", "you", "we", "they", "it"
        }

        words = re.findall(r'\b[a-z_]+\b', text)
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        # Get unique keywords, preserving order
        seen: Set[str] = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:20]  # Limit to top 20

    def _extract_entities(self, text: str) -> Dict[str, str]:
        """Extract specific entities like names, paths, etc."""
        entities = {}

        # Extract quoted strings (names, descriptions)
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            entities["name"] = quoted[0]

        # Extract file paths
        paths = re.findall(r'[\w/\\]+\.[\w]+', text)
        if paths:
            entities["file_path"] = paths[0]

        # Extract URLs
        urls = re.findall(r'https?://[^\s]+', text)
        if urls:
            entities["url"] = urls[0]

        # Extract identifiers (CamelCase or snake_case)
        identifiers = re.findall(r'\b[A-Z][a-zA-Z]*(?:[A-Z][a-zA-Z]*)*\b', text)
        if identifiers:
            entities["class_name"] = identifiers[0]

        snake_identifiers = re.findall(r'\b[a-z]+_[a-z_]+\b', text)
        if snake_identifiers:
            entities["function_name"] = snake_identifiers[0]

        return entities

    def _determine_context_needs(self, text: str, action: str) -> List[str]:
        """Determine what context is needed based on intent."""
        needs = []

        for context_type, keywords in self.CONTEXT_NEEDS.items():
            for keyword in keywords:
                if keyword in text:
                    needs.append(context_type)
                    break

        # Actions that always need existing code
        if action in ["modify", "refactor", "fix"]:
            if "existing_code" not in needs:
                needs.append("existing_code")

        return list(set(needs))  # Remove duplicates

    def _assess_complexity(self, text: str, keywords: List[str]) -> str:
        """Assess complexity based on text and keywords."""
        # Check for explicit complexity indicators
        for complexity, indicators in self.COMPLEXITY_KEYWORDS.items():
            for indicator in indicators:
                if indicator in text:
                    return complexity

        # Infer from length and keywords
        word_count = len(text.split())
        keyword_count = len(keywords)

        if word_count < 10 or keyword_count < 5:
            return "simple"
        elif word_count < 30 or keyword_count < 10:
            return "moderate"
        else:
            return "complex"

    def _calculate_confidence(
        self,
        action: str,
        target: str,
        language: Optional[str],
        keyword_count: int
    ) -> VibeConfidence:
        """Calculate confidence in the parsed intent."""
        score = 0.0

        # Action detected (+25 points)
        if action != "create":  # Non-default action
            score += 25
        else:
            score += 15  # Default action

        # Target detected (+25 points)
        if target != "code":  # Non-default target
            score += 25
        else:
            score += 10  # Default target

        # Language detected (+30 points)
        if language:
            score += 30
        else:
            score += 5  # Can still work without explicit language

        # Keyword richness (+20 points)
        if keyword_count >= 10:
            score += 20
        elif keyword_count >= 5:
            score += 15
        elif keyword_count >= 3:
            score += 10
        else:
            score += 5

        # Map score to confidence level
        if score >= 85:
            return VibeConfidence.VERY_HIGH
        elif score >= 70:
            return VibeConfidence.HIGH
        elif score >= 55:
            return VibeConfidence.MEDIUM
        elif score >= 40:
            return VibeConfidence.LOW
        else:
            return VibeConfidence.VERY_LOW

    def _recommend_token_budget(self, complexity: str, target: str) -> int:
        """Recommend token budget based on complexity and target."""
        base_budgets = {
            "simple": 500,
            "moderate": 1000,
            "complex": 2000,
        }

        target_multipliers = {
            "function": 1.0,
            "class": 1.5,
            "api": 1.8,
            "database": 1.6,
            "test": 1.2,
            "component": 1.7,
            "service": 2.0,
            "config": 0.8,
        }

        base = base_budgets.get(complexity, 1000)
        multiplier = target_multipliers.get(target, 1.0)

        return int(base * multiplier)

    def _compile_action_patterns(self) -> Dict:
        """Compile regex patterns for action detection."""
        patterns = {}
        for action, keywords in self.ACTIONS.items():
            pattern = r'\b(' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
            patterns[action] = re.compile(pattern)
        return patterns

    def _compile_target_patterns(self) -> Dict:
        """Compile regex patterns for target detection."""
        patterns = {}
        for target, keywords in self.TARGETS.items():
            pattern = r'\b(' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
            patterns[target] = re.compile(pattern)
        return patterns
