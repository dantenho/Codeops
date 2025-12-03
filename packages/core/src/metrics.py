# 📊 AGENT METRICS & EVALUATION SYSTEM (AMES)

> **Version:** 1.0 | **Last Updated:** 2025-12-03
> **Purpose:** Comprehensive evaluation framework for AI coding agents
> **Scope:** Multi-language, multi-function, multi-complexity assessment

---

## 📌 SYSTEM OVERVIEW

The Agent Metrics & Evaluation System (AMES) provides a standardized framework for measuring, comparing, and improving AI agent performance across diverse coding tasks. This system enables objective assessment of agent capabilities and identifies areas for optimization.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT METRICS & EVALUATION SYSTEM                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   COLLECT   │───▶│   ANALYZE   │───▶│    SCORE    │───▶│   REPORT    │  │
│  │   Metrics   │    │    Data     │    │    Agent    │    │   Results   │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │                  │          │
│         ▼                  ▼                  ▼                  ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  Telemetry  │    │  Benchmarks │    │  Rankings   │    │  Dashboard  │  │
│  │    Logs     │    │  Comparison │    │  & Badges   │    │  & Alerts   │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 EVALUATION DIMENSIONS

### The Five Pillars of Agent Evaluation

```
                              ┌─────────────────┐
                              │   AGENT SCORE   │
                              │    (0-100)      │
                              └────────┬────────┘
                                       │
           ┌───────────┬───────────┬───┴───┬───────────┬───────────┐
           ▼           ▼           ▼       ▼           ▼           │
    ┌─────────────┐ ┌─────────┐ ┌─────┐ ┌─────────┐ ┌─────────────┐│
    │  ACCURACY   │ │  SPEED  │ │QUAL-│ │ ADAPT-  │ │   RELIA-    ││
    │   (25%)     │ │  (20%)  │ │ITY  │ │ ABILITY │ │   BILITY    ││
    │             │ │         │ │(25%)│ │  (15%)  │ │    (15%)    ││
    └─────────────┘ └─────────┘ └─────┘ └─────────┘ └─────────────┘│
           │           │           │           │           │       │
           └───────────┴───────────┴─────┬─────┴───────────┴───────┘
                                         │
                              ┌──────────┴──────────┐
                              │   COMPOSITE SCORE   │
                              │   Language × Task   │
                              │     × Complexity    │
                              └─────────────────────┘
```

---

## 📋 METRIC CATEGORIES

### 1. ACCURACY METRICS (25% of total score)

| Metric ID | Metric Name | Description | Formula | Weight |
|-----------|-------------|-------------|---------|--------|
| `ACC-001` | Functional Correctness | Code produces expected output | `(passed_tests / total_tests) × 100` | 40% |
| `ACC-002` | Syntax Validity | Code compiles/parses without errors | `(valid_files / total_files) × 100` | 20% |
| `ACC-003` | Logic Accuracy | Algorithms implement correct logic | `(correct_algorithms / total_algorithms) × 100` | 25% |
| `ACC-004` | Edge Case Handling | Handles boundary conditions | `(edge_cases_handled / edge_cases_total) × 100` | 15% |

#### Accuracy Scoring Formula

```
ACCURACY_SCORE = (
    (ACC-001 × 0.40) +
    (ACC-002 × 0.20) +
    (ACC-003 × 0.25) +
    (ACC-004 × 0.15)
) × COMPLEXITY_MULTIPLIER
```

---

### 2. SPEED METRICS (20% of total score)

| Metric ID | Metric Name | Description | Formula | Weight |
|-----------|-------------|-------------|---------|--------|
| `SPD-001` | Time to First Token | Latency before output begins | `first_token_ms` | 15% |
| `SPD-002` | Completion Time | Total time to complete task | `completion_ms` | 35% |
| `SPD-003` | Tokens per Second | Output generation rate | `total_tokens / duration_seconds` | 25% |
| `SPD-004` | Iteration Efficiency | Tasks completed per iteration | `tasks_done / iterations_needed` | 25% |

#### Speed Benchmarks by Complexity

| Complexity | Target Time | Good | Acceptable | Poor |
|------------|-------------|------|------------|------|
| Easy | < 5s | < 10s | < 30s | > 30s |
| Medium | < 30s | < 60s | < 120s | > 120s |
| Hard | < 120s | < 300s | < 600s | > 600s |
| Complex | < 300s | < 600s | < 1200s | > 1200s |

#### Speed Scoring Formula

```
SPEED_SCORE = (
    (normalize(SPD-001, target_ttft) × 0.15) +
    (normalize(SPD-002, target_completion) × 0.35) +
    (normalize(SPD-003, target_tps) × 0.25) +
    (SPD-004 × 0.25)
) × 100
```

---

### 3. QUALITY METRICS (25% of total score)

| Metric ID | Metric Name | Description | Formula | Weight |
|-----------|-------------|-------------|---------|--------|
| `QUA-001` | Documentation Coverage | Functions with complete docstrings | `(documented_functions / total_functions) × 100` | 20% |
| `QUA-002` | Code Readability | Lint score + naming conventions | `(lint_score + naming_score) / 2` | 20% |
| `QUA-003` | Type Safety | Type hints coverage | `(typed_params / total_params) × 100` | 15% |
| `QUA-004` | Maintainability Index | Cyclomatic complexity + LOC balance | `MI_score (0-100)` | 15% |
| `QUA-005` | Test Coverage | Lines covered by tests | `(covered_lines / total_lines) × 100` | 15% |
| `QUA-006` | Security Score | No vulnerabilities + secure patterns | `(100 - vulnerability_penalty)` | 15% |

#### Quality Grading Scale

| Grade | Score Range | Description |
|-------|-------------|-------------|
| A+ | 95-100 | Exceptional - Production ready |
| A | 90-94 | Excellent - Minor improvements only |
| B+ | 85-89 | Very Good - Ready for review |
| B | 80-84 | Good - Some improvements needed |
| C+ | 75-79 | Acceptable - Needs work |
| C | 70-74 | Fair - Significant improvements needed |
| D | 60-69 | Poor - Major rework required |
| F | < 60 | Failing - Does not meet standards |

---

### 4. ADAPTABILITY METRICS (15% of total score)

| Metric ID | Metric Name | Description | Formula | Weight |
|-----------|-------------|-------------|---------|--------|
| `ADP-001` | Language Versatility | Performance across languages | `avg(language_scores)` | 30% |
| `ADP-002` | Task Flexibility | Performance across task types | `avg(task_type_scores)` | 30% |
| `ADP-003` | Context Retention | Maintains context in long sessions | `(relevant_responses / total_responses) × 100` | 20% |
| `ADP-004` | Learning Curve | Improvement over iterations | `(final_score - initial_score) / iterations` | 20% |

#### Language Proficiency Matrix

| Agent | Python | JavaScript | TypeScript | Go | Rust | Java | C++ |
|-------|--------|------------|------------|-----|------|------|-----|
| GrokIA | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| GeminiFlash25 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| GeminiPro25 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| GeminiPro30 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Jules | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| ClaudeCode | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Composer | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

*Legend: ⬜ = Not evaluated, 🟥 = Poor (<60), 🟨 = Fair (60-79), 🟩 = Good (80-100)*

---

### 5. RELIABILITY METRICS (15% of total score)

| Metric ID | Metric Name | Description | Formula | Weight |
|-----------|-------------|-------------|---------|--------|
| `REL-001` | Success Rate | Tasks completed without failure | `(successful_tasks / total_tasks) × 100` | 35% |
| `REL-002` | Error Recovery | Recovers from errors gracefully | `(recovered_errors / total_errors) × 100` | 25% |
| `REL-003` | Consistency | Same input produces same quality | `1 - std_dev(quality_scores)` | 25% |
| `REL-004` | Uptime | Available when needed | `(available_time / total_time) × 100` | 15% |

---

## 🏋️ TASK COMPLEXITY CLASSIFICATION

### Complexity Levels

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TASK COMPLEXITY TAXONOMY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LEVEL 1: EASY (Multiplier: 1.0x)                                          │
│  ├── Single function implementation                                         │
│  ├── Simple CRUD operations                                                 │
│  ├── Basic data transformations                                             │
│  ├── Simple API calls                                                       │
│  └── Configuration file creation                                            │
│                                                                             │
│  LEVEL 2: MEDIUM (Multiplier: 1.5x)                                        │
│  ├── Multi-function modules                                                 │
│  ├── Class implementations with methods                                     │
│  ├── Basic algorithms (sorting, searching)                                  │
│  ├── Database queries with joins                                            │
│  └── Unit test creation                                                     │
│                                                                             │
│  LEVEL 3: HARD (Multiplier: 2.0x)                                          │
│  ├── Multi-class systems                                                    │
│  ├── Design pattern implementation                                          │
│  ├── Complex algorithms (graphs, DP)                                        │
│  ├── API design and implementation                                          │
│  └── Integration with external services                                     │
│                                                                             │
│  LEVEL 4: COMPLEX (Multiplier: 3.0x)                                       │
│  ├── Full module/package architecture                                       │
│  ├── Distributed system components                                          │
│  ├── Performance optimization                                               │
│  ├── Security-critical implementations                                      │
│  └── Multi-language interoperability                                        │
│                                                                             │
│  LEVEL 5: EXPERT (Multiplier: 4.0x)                                        │
│  ├── System architecture design                                             │
│  ├── Novel algorithm development                                            │
│  ├── Compiler/interpreter components                                        │
│  ├── Real-time system implementations                                       │
│  └── Machine learning model integration                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Complexity Scoring Matrix

| Factor | Weight | L1 (Easy) | L2 (Medium) | L3 (Hard) | L4 (Complex) | L5 (Expert) |
|--------|--------|-----------|-------------|-----------|--------------|-------------|
| Lines of Code | 10% | 1-50 | 51-200 | 201-500 | 501-1000 | 1000+ |
| Functions | 15% | 1-3 | 4-10 | 11-25 | 26-50 | 50+ |
| Classes | 15% | 0-1 | 2-5 | 6-15 | 16-30 | 30+ |
| Dependencies | 10% | 0-2 | 3-5 | 6-10 | 11-20 | 20+ |
| Cyclomatic Complexity | 20% | 1-5 | 6-10 | 11-20 | 21-40 | 40+ |
| Integration Points | 15% | 0 | 1-2 | 3-5 | 6-10 | 10+ |
| Domain Knowledge | 15% | Basic | Intermediate | Advanced | Expert | Research |

---

## 🌐 LANGUAGE-SPECIFIC METRICS

### Python Metrics

| Metric ID | Metric Name | Tool | Target |
|-----------|-------------|------|--------|
| `PY-001` | PEP 8 Compliance | ruff/flake8 | 100% |
| `PY-002` | Type Coverage | mypy | ≥ 90% |
| `PY-003` | Docstring Coverage | interrogate | ≥ 90% |
| `PY-004` | Import Organization | isort | Pass |
| `PY-005` | Security Score | bandit | No HIGH/CRITICAL |
| `PY-006` | Complexity Score | radon | A/B grade |

### JavaScript/TypeScript Metrics

| Metric ID | Metric Name | Tool | Target |
|-----------|-------------|------|--------|
| `JS-001` | ESLint Score | eslint | 0 errors |
| `JS-002` | Type Coverage (TS) | typescript | ≥ 95% |
| `JS-003` | JSDoc Coverage | jsdoc | ≥ 80% |
| `JS-004` | Bundle Size | webpack-analyzer | < threshold |
| `JS-005` | Security Audit | npm audit | 0 vulnerabilities |
| `JS-006` | Complexity | eslint-complexity | ≤ 10 |

### Go Metrics

| Metric ID | Metric Name | Tool | Target |
|-----------|-------------|------|--------|
| `GO-001` | Go Vet | go vet | Pass |
| `GO-002` | Go Lint | golangci-lint | Pass |
| `GO-003` | Test Coverage | go test -cover | ≥ 80% |
| `GO-004` | Documentation | godoc | All exported |
| `GO-005` | Security | gosec | No issues |
| `GO-006` | Formatting | gofmt | Pass |

### Rust Metrics

| Metric ID | Metric Name | Tool | Target |
|-----------|-------------|------|--------|
| `RS-001` | Clippy Lints | cargo clippy | 0 warnings |
| `RS-002` | Formatting | cargo fmt | Pass |
| `RS-003` | Documentation | cargo doc | All public |
| `RS-004` | Test Coverage | cargo tarpaulin | ≥ 80% |
| `RS-005` | Security Audit | cargo audit | 0 vulnerabilities |
| `RS-006` | Unsafe Usage | manual review | Justified only |

---

## 📝 TASK TYPE EVALUATION

### Task Categories

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TASK TYPE TAXONOMY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │    CREATE       │  │    REFACTOR     │  │     DEBUG       │             │
│  │    (New Code)   │  │  (Restructure)  │  │   (Fix Bugs)    │             │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤             │
│  │ • Functions     │  │ • Extract method│  │ • Error tracing │             │
│  │ • Classes       │  │ • Rename        │  │ • Root cause    │             │
│  │ • Modules       │  │ • Move          │  │ • Fix implement │             │
│  │ • APIs          │  │ • Inline        │  │ • Regression    │             │
│  │ • Tests         │  │ • Simplify      │  │ • Edge cases    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │    OPTIMIZE     │  │    DOCUMENT     │  │    ANALYZE      │             │
│  │  (Performance)  │  │  (Explanation)  │  │   (Review)      │             │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤             │
│  │ • Speed         │  │ • Docstrings    │  │ • Code review   │             │
│  │ • Memory        │  │ • README        │  │ • Security audit│             │
│  │ • Algorithm     │  │ • API docs      │  │ • Architecture  │             │
│  │ • Query         │  │ • Comments      │  │ • Dependencies  │             │
│  │ • Caching       │  │ • Examples      │  │ • Tech debt     │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Task-Specific Scoring Criteria

#### CREATE Tasks

| Criterion | Weight | Excellent (90-100) | Good (70-89) | Fair (50-69) | Poor (<50) |
|-----------|--------|-------------------|--------------|--------------|------------|
| Completeness | 25% | All requirements met | Minor gaps | Major gaps | Incomplete |
| Correctness | 25% | All tests pass | >90% pass | >70% pass | <70% pass |
| Structure | 20% | Optimal design | Good design | Acceptable | Poor design |
| Documentation | 15% | Complete + examples | Complete | Partial | Missing |
| Edge Cases | 15% | All handled | Most handled | Some handled | Not handled |

#### REFACTOR Tasks

| Criterion | Weight | Excellent (90-100) | Good (70-89) | Fair (50-69) | Poor (<50) |
|-----------|--------|-------------------|--------------|--------------|------------|
| Behavior Preserved | 30% | 100% same | Minor changes | Some changes | Broken |
| Improvement | 25% | Significant | Moderate | Minor | None/Worse |
| Clarity | 20% | Much clearer | Clearer | Same | Less clear |
| Test Coverage | 15% | Increased | Maintained | Slight decrease | Major decrease |
| Breaking Changes | 10% | None | Documented | Undocumented | Untracked |

#### DEBUG Tasks

| Criterion | Weight | Excellent (90-100) | Good (70-89) | Fair (50-69) | Poor (<50) |
|-----------|--------|-------------------|--------------|--------------|------------|
| Bug Fixed | 30% | Completely | Mostly | Partially | Not fixed |
| Root Cause | 25% | Identified + explained | Identified | Guessed | Unknown |
| No Regressions | 20% | Verified | Likely | Possible | Introduced |
| Prevention | 15% | Measures added | Suggested | Noted | Not addressed |
| Documentation | 10% | Complete analysis | Good notes | Brief | None |

---

## 🧮 COMPOSITE SCORING ALGORITHM

### Final Score Calculation

```python
"""
[CREATE] Agent Composite Score Calculator

Calculates the final evaluation score for an AI coding agent
based on multiple dimensions, task types, and complexity levels.

Agent: AMES (Agent Metrics & Evaluation System)
Timestamp: 2025-12-03T10:00:00Z
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class ComplexityLevel(Enum):
    """Task complexity levels with score multipliers."""
    EASY = 1.0
    MEDIUM = 1.5
    HARD = 2.0
    COMPLEX = 3.0
    EXPERT = 4.0


class TaskType(Enum):
    """Types of coding tasks."""
    CREATE = "create"
    REFACTOR = "refactor"
    DEBUG = "debug"
    OPTIMIZE = "optimize"
    DOCUMENT = "document"
    ANALYZE = "analyze"


@dataclass
class MetricScores:
    """
    [CREATE] Container for all metric dimension scores.

    Attributes:
        accuracy (float): Accuracy score (0-100)
        speed (float): Speed score (0-100)
        quality (float): Quality score (0-100)
        adaptability (float): Adaptability score (0-100)
        reliability (float): Reliability score (0-100)

    Agent: AMES
    Timestamp: 2025-12-03T10:00:00Z
    """
    accuracy: float
    speed: float
    quality: float
    adaptability: float
    reliability: float

    def validate(self) -> bool:
        """Validates all scores are within 0-100 range."""
        scores = [self.accuracy, self.speed, self.quality,
                  self.adaptability, self.reliability]
        return all(0 <= s <= 100 for s in scores)


@dataclass
class TaskContext:
    """
    [CREATE] Context information for a coding task.

    Attributes:
        task_type (TaskType): Type of task performed
        complexity (ComplexityLevel): Difficulty level
        language (str): Programming language used
        lines_of_code (int): Total lines produced/modified
        duration_seconds (float): Time taken to complete

    Agent: AMES
    Timestamp: 2025-12-03T10:00:00Z
    """
    task_type: TaskType
    complexity: ComplexityLevel
    language: str
    lines_of_code: int
    duration_seconds: float


class AgentEvaluator:
    """
    [CREATE] Evaluates AI coding agent performance.

    Implements the AMES scoring algorithm to calculate
    composite scores across multiple dimensions.

    Attributes:
        dimension_weights (Dict[str, float]): Weights for each dimension
        language_benchmarks (Dict[str, Dict]): Per-language benchmarks
        agent_history (List[Dict]): Historical evaluation data

    Example:
        >>> evaluator = AgentEvaluator()
        >>> scores = MetricScores(
        ...     accuracy=92.5,
        ...     speed=85.0,
        ...     quality=88.5,
        ...     adaptability=78.0,
        ...     reliability=95.0
        ... )
        >>> context = TaskContext(
        ...     task_type=TaskType.CREATE,
        ...     complexity=ComplexityLevel.HARD,
        ...     language="python",
        ...     lines_of_code=350,
        ...     duration_seconds=180.5
        ... )
        >>> result = evaluator.calculate_composite_score(scores, context)
        >>> print(f"Final Score: {result['composite_score']:.2f}")
        Final Score: 87.45

    Complexity:
        Time: O(1) for score calculation
        Space: O(n) where n is history size

    Agent: AMES
    Timestamp: 2025-12-03T10:00:00Z
    """

    # Dimension weights (must sum to 1.0)
    DIMENSION_WEIGHTS = {
        "accuracy": 0.25,
        "speed": 0.20,
        "quality": 0.25,
        "adaptability": 0.15,
        "reliability": 0.15
    }

    # Task type modifiers
    TASK_TYPE_WEIGHTS = {
        TaskType.CREATE: {"accuracy": 1.1, "quality": 1.1, "speed": 0.9},
        TaskType.REFACTOR: {"quality": 1.2, "reliability": 1.1, "speed": 0.8},
        TaskType.DEBUG: {"accuracy": 1.2, "reliability": 1.1, "speed": 1.0},
        TaskType.OPTIMIZE: {"speed": 1.2, "quality": 1.0, "accuracy": 1.0},
        TaskType.DOCUMENT: {"quality": 1.3, "accuracy": 0.9, "speed": 0.9},
        TaskType.ANALYZE: {"accuracy": 1.1, "quality": 1.1, "adaptability": 1.1}
    }

    # Language difficulty modifiers
    LANGUAGE_MODIFIERS = {
        "python": 1.0,
        "javascript": 1.0,
        "typescript": 1.05,
        "go": 1.1,
        "rust": 1.2,
        "java": 1.05,
        "cpp": 1.15,
        "c": 1.2,
        "haskell": 1.25,
        "assembly": 1.5
    }

    def __init__(self) -> None:
        """
        [CREATE] Initializes the agent evaluator.

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        self.agent_history: List[Dict] = []

    def calculate_composite_score(
        self,
        scores: MetricScores,
        context: TaskContext
    ) -> Dict:
        """
        [CREATE] Calculates the composite evaluation score.

        Combines all metric dimensions with task context to produce
        a final weighted score that accounts for complexity and
        language difficulty.

        Args:
            scores (MetricScores): Raw scores for each dimension
            context (TaskContext): Task context information

        Returns:
            Dict: Comprehensive evaluation result containing:
                - composite_score: Final weighted score (0-100)
                - adjusted_scores: Per-dimension adjusted scores
                - grade: Letter grade (A+ to F)
                - percentile: Performance percentile
                - breakdown: Detailed score breakdown

        Raises:
            ValueError: If scores are invalid (outside 0-100 range)

        Algorithm:
            1. Validate input scores
            2. Apply task type modifiers
            3. Calculate weighted base score
            4. Apply complexity multiplier
            5. Apply language modifier
            6. Normalize to 0-100 range
            7. Calculate grade and percentile

        Complexity:
            Time: O(1)
            Space: O(1)

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        if not scores.validate():
            raise ValueError("All scores must be between 0 and 100")

        # Step 1: Get task type modifiers
        task_mods = self.TASK_TYPE_WEIGHTS.get(
            context.task_type,
            {"accuracy": 1.0, "speed": 1.0, "quality": 1.0}
        )

        # Step 2: Apply task type modifiers to scores
        adjusted_scores = {
            "accuracy": scores.accuracy * task_mods.get("accuracy", 1.0),
            "speed": scores.speed * task_mods.get("speed", 1.0),
            "quality": scores.quality * task_mods.get("quality", 1.0),
            "adaptability": scores.adaptability * task_mods.get("adaptability", 1.0),
            "reliability": scores.reliability * task_mods.get("reliability", 1.0)
        }

        # Step 3: Calculate weighted base score
        base_score = sum(
            adjusted_scores[dim] * weight
            for dim, weight in self.DIMENSION_WEIGHTS.items()
        )

        # Step 4: Apply complexity bonus
        complexity_bonus = self._calculate_complexity_bonus(
            base_score,
            context.complexity
        )

        # Step 5: Apply language modifier
        lang_modifier = self.LANGUAGE_MODIFIERS.get(
            context.language.lower(),
            1.0
        )

        # Step 6: Calculate final score
        final_score = min(100, (base_score + complexity_bonus) * lang_modifier)

        # Step 7: Determine grade
        grade = self._score_to_grade(final_score)

        # Step 8: Calculate percentile (based on history)
        percentile = self._calculate_percentile(final_score)

        result = {
            "composite_score": round(final_score, 2),
            "base_score": round(base_score, 2),
            "complexity_bonus": round(complexity_bonus, 2),
            "language_modifier": lang_modifier,
            "grade": grade,
            "percentile": percentile,
            "adjusted_scores": {k: round(v, 2) for k, v in adjusted_scores.items()},
            "context": {
                "task_type": context.task_type.value,
                "complexity": context.complexity.name,
                "language": context.language,
                "lines_of_code": context.lines_of_code,
                "duration_seconds": context.duration_seconds
            },
            "breakdown": self._generate_breakdown(scores, adjusted_scores, context)
        }

        # Store in history
        self.agent_history.append(result)

        return result

    def _calculate_complexity_bonus(
        self,
        base_score: float,
        complexity: ComplexityLevel
    ) -> float:
        """
        [CREATE] Calculates bonus points for task complexity.

        Higher complexity tasks receive bonus points when completed
        successfully. The bonus scales with both the base score and
        the complexity level.

        Args:
            base_score (float): The weighted base score
            complexity (ComplexityLevel): Task complexity level

        Returns:
            float: Bonus points to add (0-20 range)

        Formula:
            bonus = (base_score / 100) * (complexity_multiplier - 1) * 20

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        if base_score < 60:  # No bonus for poor performance
            return 0.0

        multiplier = complexity.value
        bonus = (base_score / 100) * (multiplier - 1) * 20

        return min(bonus, 20.0)  # Cap at 20 bonus points

    def _score_to_grade(self, score: float) -> str:
        """
        [CREATE] Converts numeric score to letter grade.

        Args:
            score (float): Numeric score (0-100)

        Returns:
            str: Letter grade (A+ to F)

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        elif score >= 60:
            return "D-"
        else:
            return "F"

    def _calculate_percentile(self, score: float) -> int:
        """
        [CREATE] Calculates percentile rank based on history.

        Args:
            score (float): Score to rank

        Returns:
            int: Percentile (0-100)

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        if not self.agent_history:
            return 50  # Default to median if no history

        historical_scores = [h["composite_score"] for h in self.agent_history]
        below_count = sum(1 for s in historical_scores if s < score)

        return int((below_count / len(historical_scores)) * 100)

    def _generate_breakdown(
        self,
        raw_scores: MetricScores,
        adjusted_scores: Dict[str, float],
        context: TaskContext
    ) -> Dict:
        """
        [CREATE] Generates detailed score breakdown.

        Args:
            raw_scores (MetricScores): Original scores
            adjusted_scores (Dict): Task-adjusted scores
            context (TaskContext): Task context

        Returns:
            Dict: Detailed breakdown with analysis

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        return {
            "raw_scores": {
                "accuracy": raw_scores.accuracy,
                "speed": raw_scores.speed,
                "quality": raw_scores.quality,
                "adaptability": raw_scores.adaptability,
                "reliability": raw_scores.reliability
            },
            "weights_applied": self.DIMENSION_WEIGHTS,
            "task_modifiers": self.TASK_TYPE_WEIGHTS.get(context.task_type, {}),
            "contribution": {
                dim: round(adjusted_scores[dim] * weight, 2)
                for dim, weight in self.DIMENSION_WEIGHTS.items()
            }
        }

    def get_agent_summary(self, agent_name: str) -> Dict:
        """
        [CREATE] Generates performance summary for an agent.

        Args:
            agent_name (str): Name of the agent

        Returns:
            Dict: Summary statistics and trends

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        if not self.agent_history:
            return {"error": "No evaluation history available"}

        scores = [h["composite_score"] for h in self.agent_history]

        return {
            "agent": agent_name,
            "total_evaluations": len(scores),
            "average_score": round(sum(scores) / len(scores), 2),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "latest_score": scores[-1] if scores else None,
            "trend": self._calculate_trend(scores),
            "grade_distribution": self._grade_distribution()
        }

    def _calculate_trend(self, scores: List[float]) -> str:
        """
        [CREATE] Calculates performance trend.

        Args:
            scores (List[float]): Historical scores

        Returns:
            str: Trend indicator (improving/stable/declining)

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        if len(scores) < 3:
            return "insufficient_data"

        recent = scores[-3:]
        avg_recent = sum(recent) / len(recent)
        avg_total = sum(scores) / len(scores)

        diff = avg_recent - avg_total

        if diff > 2:
            return "📈 improving"
        elif diff < -2:
            return "📉 declining"
        else:
            return "➡️ stable"

    def _grade_distribution(self) -> Dict[str, int]:
        """
        [CREATE] Calculates grade distribution from history.

        Returns:
            Dict[str, int]: Count of each grade

        Agent: AMES
        Timestamp: 2025-12-03T10:00:00Z
        """
        distribution = {}
        for entry in self.agent_history:
            grade = entry.get("grade", "Unknown")
            distribution[grade] = distribution.get(grade, 0) + 1
        return distribution


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Initialize evaluator
    evaluator = AgentEvaluator()

    # Example evaluation
    scores = MetricScores(
        accuracy=92.5,
        speed=85.0,
        quality=88.5,
        adaptability=78.0,
        reliability=95.0
    )

    context = TaskContext(
        task_type=TaskType.CREATE,
        complexity=ComplexityLevel.HARD,
        language="python",
        lines_of_code=350,
        duration_seconds=180.5
    )

    result = evaluator.calculate_composite_score(scores, context)

    print("=" * 60)
    print("AGENT EVALUATION RESULT")
    print("=" * 60)
    print(f"Composite Score: {result['composite_score']}")
    print(f"Grade: {result['grade']}")
    print(f"Percentile: {result['percentile']}th")
    print(f"Complexity Bonus: +{result['complexity_bonus']}")
    print("=" * 60)
```

---

## 📊 EVALUATION TEMPLATES

### Easy Task Evaluation Template

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EasyTaskEvaluation",
  "type": "object",
  "required": ["task_id", "agent", "timestamp", "scores", "result"],
  "properties": {
    "task_id": { "type": "string" },
    "agent": {
      "type": "string",
      "enum": ["GrokIA", "GeminiFlash25", "GeminiPro25", "GeminiPro30", "Jules", "ClaudeCode", "Composer"]
    },
    "timestamp": { "type": "string", "format": "date-time" },
    "complexity": { "const": "EASY" },
    "task_description": { "type": "string" },
    "language": { "type": "string" },
    "scores": {
      "type": "object",
      "properties": {
        "accuracy": { "type": "number", "minimum": 0, "maximum": 100 },
        "speed": { "type": "number", "minimum": 0, "maximum": 100 },
        "quality": { "type": "number", "minimum": 0, "maximum": 100 },
        "adaptability": { "type": "number", "minimum": 0, "maximum": 100 },
        "reliability": { "type": "number", "minimum": 0, "maximum": 100 }
      }
    },
    "result": {
      "type": "object",
      "properties": {
        "composite_score": { "type": "number" },
        "grade": { "type": "string" },
        "passed": { "type": "boolean" }
      }
    },
    "criteria": {
      "type": "object",
      "properties": {
        "functional": { "type": "boolean" },
        "documented": { "type": "boolean" },
        "linted": { "type": "boolean" },
        "tested": { "type": "boolean" }
      }
    }
  }
}
```

### Complex Task Evaluation Template

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ComplexTaskEvaluation",
  "type": "object",
  "required": ["task_id", "agent", "timestamp", "scores", "result", "detailed_analysis"],
  "properties": {
    "task_id": { "type": "string" },
    "agent": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "complexity": { "enum": ["HARD", "COMPLEX", "EXPERT"] },
    "task_description": { "type": "string" },
    "languages": {
      "type": "array",
      "items": { "type": "string" }
    },
    "scores": {
      "type": "object",
      "properties": {
        "accuracy": { "type": "number" },
        "speed": { "type": "number" },
        "quality": { "type": "number" },
        "adaptability": { "type": "number" },
        "reliability": { "type": "number" }
      }
    },
    "result": {
      "type": "object",
      "properties": {
        "composite_score": { "type": "number" },
        "base_score": { "type": "number" },
        "complexity_bonus": { "type": "number" },
        "grade": { "type": "string" },
        "percentile": { "type": "integer" }
      }
    },
    "detailed_analysis": {
      "type": "object",
      "properties": {
        "architecture_score": { "type": "number" },
        "design_patterns_used": { "type": "array", "items": { "type": "string" } },
        "security_assessment": { "type": "string" },
        "performance_analysis": { "type": "string" },
        "scalability_rating": { "type": "string" },
        "maintainability_index": { "type": "number" }
      }
    },
    "recommendations": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

---

## 📈 BENCHMARK SUITE

### Standard Benchmark Tasks

#### Level 1: Easy Benchmarks

| ID | Task | Language | Expected Time | Pass Threshold |
|----|------|----------|---------------|----------------|
| E001 | FizzBuzz implementation | Any | < 30s | 90% |
| E002 | Palindrome checker | Any | < 30s | 95% |
| E003 | Array sum function | Any | < 20s | 100% |
| E004 | String reversal | Any | < 20s | 100% |
| E005 | Temperature converter | Any | < 30s | 95% |
| E006 | Simple REST endpoint | JS/Python | < 60s | 85% |
| E007 | JSON parser usage | Any | < 45s | 90% |
| E008 | File reader function | Any | < 45s | 90% |
| E009 | Basic regex matcher | Any | < 60s | 85% |
| E010 | Config file loader | Any | < 60s | 85% |

#### Level 2: Medium Benchmarks

| ID | Task | Language | Expected Time | Pass Threshold |
|----|------|----------|---------------|----------------|
| M001 | Binary search tree | Any | < 120s | 80% |
| M002 | LRU Cache implementation | Any | < 180s | 75% |
| M003 | Rate limiter | Any | < 150s | 75% |
| M004 | JWT authentication | JS/Python | < 180s | 70% |
| M005 | Database CRUD operations | Any | < 200s | 75% |
| M006 | Unit test suite creation | Any | < 180s | 80% |
| M007 | Async task queue | Any | < 200s | 70% |
| M008 | CSV parser with validation | Any | < 150s | 80% |
| M009 | State machine | Any | < 180s | 75% |
| M010 | Observer pattern | Any | < 150s | 80% |

#### Level 3: Hard Benchmarks

| ID | Task | Language | Expected Time | Pass Threshold |
|----|------|----------|---------------|----------------|
| H001 | Graph traversal algorithms | Any | < 300s | 70% |
| H002 | Thread-safe data structure | Go/Rust/Java | < 400s | 65% |
| H003 | REST API with middleware | Any | < 500s | 65% |
| H004 | SQL query optimizer | Python/Go | < 600s | 60% |
| H005 | WebSocket server | Any | < 450s | 65% |
| H006 | Dependency injection system | Any | < 400s | 65% |
| H007 | Event sourcing implementation | Any | < 500s | 60% |
| H008 | Custom serialization format | Any | < 400s | 65% |
| H009 | Connection pool manager | Any | < 450s | 60% |
| H010 | Plugin architecture | Any | < 500s | 60% |

#### Level 4: Complex Benchmarks

| ID | Task | Language | Expected Time | Pass Threshold |
|----|------|----------|---------------|----------------|
| C001 | Distributed lock service | Go/Rust | < 900s | 55% |
| C002 | Custom ORM layer | Any | < 1200s | 50% |
| C003 | Message queue system | Any | < 1000s | 50% |
| C004 | Compiler frontend | Any | < 1500s | 45% |
| C005 | Real-time collaboration | JS/TS | < 1200s | 50% |
| C006 | Microservice framework | Any | < 1500s | 45% |
| C007 | Search engine indexer | Any | < 1200s | 50% |
| C008 | Load balancer | Go/Rust | < 900s | 55% |
| C009 | Certificate manager | Any | < 1000s | 50% |
| C010 | Service mesh component | Go/Rust | < 1500s | 45% |

---

## 🏆 AGENT RANKING SYSTEM

### Ranking Tiers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENT RANKING TIERS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🏆 LEGENDARY (Top 1%)                                                      │
│  ├── Score: 95+ average across all dimensions                               │
│  ├── Badge: Diamond                                                         │
│  └── Requirements: 100+ evaluations, 0 critical failures                   │
│                                                                             │
│  ⭐ MASTER (Top 5%)                                                         │
│  ├── Score: 90-94 average                                                   │
│  ├── Badge: Platinum                                                        │
│  └── Requirements: 50+ evaluations, <1% critical failures                  │
│                                                                             │
│  🥇 EXPERT (Top 15%)                                                        │
│  ├── Score: 85-89 average                                                   │
│  ├── Badge: Gold                                                            │
│  └── Requirements: 25+ evaluations, <3% critical failures                  │
│                                                                             │
│  🥈 ADVANCED (Top 30%)                                                      │
│  ├── Score: 80-84 average                                                   │
│  ├── Badge: Silver                                                          │
│  └── Requirements: 10+ evaluations, <5% critical failures                  │
│                                                                             │
│  🥉 INTERMEDIATE (Top 50%)                                                  │
│  ├── Score: 70-79 average                                                   │
│  ├── Badge: Bronze                                                          │
│  └── Requirements: 5+ evaluations                                          │
│                                                                             │
│  📘 BEGINNER (Bottom 50%)                                                   │
│  ├── Score: <70 average                                                     │
│  ├── Badge: None                                                            │
│  └── Requirements: Active improvement plan                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Specialization Badges

| Badge | Criteria | Icon |
|-------|----------|------|
| Python Master | 95+ score on 20+ Python tasks | 🐍 |
| JavaScript Ninja | 95+ score on 20+ JS tasks | ⚡ |
| TypeScript Pro | 95+ score on 20+ TS tasks | 💙 |
| Gopher | 95+ score on 15+ Go tasks | 🐹 |
| Rustacean | 95+ score on 15+ Rust tasks | 🦀 |
| Polyglot | 85+ score in 5+ languages | 🌍 |
| Speed Demon | Top 10% in speed metrics | 🚀 |
| Quality Guardian | Top 10% in quality metrics | 🛡️ |
| Bug Hunter | 95+ score on 20+ debug tasks | 🐛 |
| Architect | 90+ score on 10+ complex tasks | 🏛️ |
| Documentation Hero | 98+ documentation coverage | 📚 |
| Test Champion | 95+ test coverage consistently | ✅ |

---

## 📋 EVALUATION REPORT TEMPLATE

```markdown
# 🤖 Agent Evaluation Report

## Overview

| Field | Value |
|-------|-------|
| **Agent** | {AGENT_NAME} |
| **Evaluation Period** | {START_DATE} to {END_DATE} |
| **Total Tasks** | {TASK_COUNT} |
| **Current Tier** | {TIER} |
| **Overall Grade** | {GRADE} |

---

## 📊 Score Summary

### Composite Score: {COMPOSITE_SCORE}/100

```
Accuracy      [████████████████████░░░░] 85%
Speed         [██████████████████░░░░░░] 78%
Quality       [█████████████████████░░░] 92%
Adaptability  [████████████████░░░░░░░░] 72%
Reliability   [██████████████████████░░] 95%
```

---

## 🌐 Language Performance

| Language | Tasks | Avg Score | Grade | Trend |
|----------|-------|-----------|-------|-------|
| Python | {N} | {SCORE} | {GRADE} | {TREND} |
| JavaScript | {N} | {SCORE} | {GRADE} | {TREND} |
| TypeScript | {N} | {SCORE} | {GRADE} | {TREND} |
| Go | {N} | {SCORE} | {GRADE} | {TREND} |
| Rust | {N} | {SCORE} | {GRADE} | {TREND} |

---

## 📝 Task Type Performance

| Task Type | Count | Success Rate | Avg Score |
|-----------|-------|--------------|-----------|
| CREATE | {N} | {RATE}% | {SCORE} |
| REFACTOR | {N} | {RATE}% | {SCORE} |
| DEBUG | {N} | {RATE}% | {SCORE} |
| OPTIMIZE | {N} | {RATE}% | {SCORE} |
| DOCUMENT | {N} | {RATE}% | {SCORE} |
| ANALYZE | {N} | {RATE}% | {SCORE} |

---

## 🏋️ Complexity Distribution

| Level | Attempted | Completed | Avg Score |
|-------|-----------|-----------|-----------|
| Easy | {N} | {N} | {SCORE} |
| Medium | {N} | {N} | {SCORE} |
| Hard | {N} | {N} | {SCORE} |
| Complex | {N} | {N} | {SCORE} |
| Expert | {N} | {N} | {SCORE} |

---

## 🏆 Badges Earned

{BADGE_LIST}

---

## 📈 Trend Analysis

### Last 30 Days
- **Score Change:** {DELTA}
- **Trend Direction:** {TREND}
- **Consistency:** {CONSISTENCY}

### Areas of Improvement
1. {IMPROVEMENT_1}
2. {IMPROVEMENT_2}
3. {IMPROVEMENT_3}

### Strengths
1. {STRENGTH_1}
2. {STRENGTH_2}
3. {STRENGTH_3}

---

## 🎯 Recommendations

1. **Priority Focus:** {RECOMMENDATION_1}
2. **Skill Development:** {RECOMMENDATION_2}
3. **Challenge Tasks:** {RECOMMENDATION_3}

---

*Report generated by AMES v1.0 | {TIMESTAMP}*
```

---

## 🔧 INTEGRATION WITH AGENTS.MD

### Telemetry Integration

All evaluation data should be stored in the standard telemetry structure:

```
CodeAgents/
├── {AgentName}/
│   ├── logs/
│   ├── errors/
│   ├── analysis/
│   └── evaluations/          # NEW: Evaluation results
│       ├── eval_{timestamp}_{task_id}.json
│       ├── benchmark_{date}.json
│       └── summary_{period}.json
```

### Workflow Integration

```yaml
# Add to .github/workflows/agent-validation.yml

evaluate-performance:
  name: 📊 Performance Evaluation
  runs-on: ubuntu-latest
  needs: [validate-code-quality]

  steps:
    - name: Run AMES Evaluation
      run: |
        python -m ames.evaluate \
          --agent ${{ needs.detect-agent.outputs.agent_name }} \
          --task-type ${{ github.event.inputs.task_type }} \
          --complexity ${{ github.event.inputs.complexity }} \
          --output CodeAgents/${{ needs.detect-agent.outputs.agent_name }}/evaluations/

    - name: Update Rankings
      run: python -m ames.rankings --update

    - name: Generate Report
      run: python -m ames.report --agent ${{ needs.detect-agent.outputs.agent_name }}
```

---

## ✅ EVALUATION CHECKLIST

### Before Task Assignment
- [ ] Complexity level determined
- [ ] Task type identified
- [ ] Language(s) specified
- [ ] Success criteria defined
- [ ] Benchmark targets set

### During Evaluation
- [ ] Start time recorded
- [ ] Iterations tracked
- [ ] Errors logged
- [ ] Code quality measured
- [ ] Documentation checked

### After Completion
- [ ] All metrics collected
- [ ] Composite score calculated
- [ ] Grade assigned
- [ ] Report generated
- [ ] Telemetry stored
- [ ] Rankings updated

---

*This evaluation system integrates with Agents.MD protocol v3.0*

*All agents are evaluated fairly using consistent, objective criteria.*
