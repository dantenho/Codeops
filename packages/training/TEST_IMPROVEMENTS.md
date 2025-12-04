# Test Improvement Suggestions

**Generated After Training Session Analysis**
**Agent:** Composer
**Date:** 2025-12-03
**Training Session:** Completed Successfully

---

## 📊 Executive Summary

After analyzing the codebase and running the training session, I've identified **critical test gaps** and **improvement opportunities**. The current test suite has **import issues**, **API mismatches**, and **incomplete coverage** of core functionality.

### Current Test Status
- ✅ **2 test files** exist (`test_spaced_repetition.py`, `test_models.py`)
- ❌ **0 tests passing** due to import/API issues
- ⚠️ **Missing coverage** for services, managers, and access control
- ⚠️ **No integration tests** for training workflows

---

## 🔴 Critical Issues Found

### 1. Import/Export Mismatches

**Problem:** Tests import `FlashcardFront` and `FlashcardBack` but these are not exported from `training.models`.

**Current Code:**
```python
# tests/test_models.py and test_spaced_repetition.py
from training.models import (
    FlashcardFront,  # ❌ Not exported
    FlashcardBack,   # ❌ Not exported
    ...
)
```

**Solution:**
```python
# src/training/models/__init__.py
from .flashcard import (
    Flashcard,
    FlashcardDeck,
    FlashcardCategory,
    FlashcardFront,    # ✅ Add this
    FlashcardBack,     # ✅ Add this
    ReviewRating,
    SpacedRepetitionData,
)
```

### 2. API Mismatches in Test Data

**Problem:** Tests use old API (`id`, `language`, `level` fields) but current model uses `card_id`, `deck_id`.

**Current Test Code:**
```python
flashcard = Flashcard(
    id="FC-PY-0001",        # ❌ Should be card_id
    language="python",      # ❌ Not in model
    level=1,                # ❌ Not in model
    ...
)
```

**Solution:** Update all test fixtures to match current API:
```python
flashcard = Flashcard(
    card_id="FC-PY-0001",
    deck_id="deck-python-syntax",
    category=FlashcardCategory.SYNTAX,
    front=FlashcardFront(question="..."),
    back=FlashcardBack(answer="...", explanation="..."),
    ...
)
```

### 3. Missing Test Infrastructure

**Problem:** No `conftest.py` for shared fixtures, no test utilities.

**Solution:** Create `tests/conftest.py`:
```python
"""
[CREATE] Shared pytest fixtures and test utilities.

Agent: Composer
Timestamp: 2025-12-03T03:50:44Z
Operation: [CREATE]
"""

import pytest
from datetime import date, datetime, timezone
from training.models import (
    Flashcard,
    FlashcardFront,
    FlashcardBack,
    FlashcardCategory,
    SpacedRepetitionData,
    ReviewRating,
)

@pytest.fixture
def sample_flashcard():
    """Create a standard test flashcard."""
    return Flashcard(
        card_id="FC-TEST-001",
        deck_id="deck-test",
        category=FlashcardCategory.SYNTAX,
        front=FlashcardFront(question="Test question?"),
        back=FlashcardBack(answer="Test answer", explanation="Test explanation"),
        sr_data=SpacedRepetitionData(next_review=date.today()),
    )

@pytest.fixture
def sm2_service():
    """Create SM2SpacedRepetition service instance."""
    from training.services.spaced_repetition import SM2SpacedRepetition
    return SM2SpacedRepetition()
```

---

## 📈 Test Coverage Improvements

### 1. Add Tests for Access Control System

**File:** `tests/test_access_control.py`

**Priority:** HIGH
**Coverage Needed:**
- Permission level hierarchy
- Resource type access checks
- Command whitelist/blacklist logic
- Critical agent auto-configuration
- Audit logging
- Config persistence

**Example Test:**
```python
"""
[CREATE] Tests for access control system.

Agent: Composer
Timestamp: 2025-12-03T03:50:44Z
Operation: [CREATE]
"""

import pytest
from pathlib import Path
import tempfile
import json

from packages.core.src.access_control import (
    AccessControlManager,
    PermissionLevel,
    ResourceType,
    AgentPermissions,
    check_terminal_access,
    require_terminal_access,
)

class TestAccessControlManager:
    """Test AccessControlManager functionality."""

    def test_critical_agents_auto_configured(self):
        """Test that critical agents get full access automatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AccessControlManager(config_path=f"{tmpdir}/access_control.json")

            grokia_perms = manager.get_agent_permissions("GrokIA")
            assert grokia_perms is not None
            assert grokia_perms.permission_level == PermissionLevel.FULL
            assert ResourceType.TERMINAL in grokia_perms.allowed_resources
            assert "*" in grokia_perms.allowed_commands

    def test_permission_level_hierarchy(self):
        """Test permission level hierarchy enforcement."""
        manager = AccessControlManager()

        # READ level cannot execute
        assert not manager.check_agent_access(
            "test_agent",
            ResourceType.TERMINAL,
            operation="execute",
            command="ls"
        )

        # FULL level can execute
        assert manager.check_agent_access(
            "GrokIA",
            ResourceType.TERMINAL,
            operation="execute",
            command="ls"
        )

    def test_blocked_commands(self):
        """Test that dangerous commands are blocked."""
        manager = AccessControlManager()

        # Even FULL access should respect global blocks
        assert not manager.check_agent_access(
            "GrokIA",
            ResourceType.TERMINAL,
            operation="execute",
            command="rm -rf /"
        )

        assert not manager.check_agent_access(
            "GrokIA",
            ResourceType.TERMINAL,
            operation="execute",
            command="sudo rm -rf /"
        )

    def test_audit_logging(self):
        """Test audit log captures access decisions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AccessControlManager(config_path=f"{tmpdir}/access_control.json")

            manager.check_agent_access("GrokIA", ResourceType.FILESYSTEM, "read")
            manager.check_agent_access("test_agent", ResourceType.TERMINAL, "execute", "ls")

            audit_log = manager.get_audit_log(limit=10)
            assert len(audit_log) >= 2
            assert any(entry["agent"] == "GrokIA" for entry in audit_log)
            assert any(entry["decision"] == "DENIED" for entry in audit_log)

    def test_config_persistence(self):
        """Test config saves and loads correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "access_control.json"
            manager = AccessControlManager(config_path=str(config_path))

            # Create custom permissions
            custom_perms = AgentPermissions(
                agent_name="TestAgent",
                permission_level=PermissionLevel.WRITE,
                allowed_resources={ResourceType.FILESYSTEM},
            )
            manager.update_agent_permissions(custom_perms)

            # Reload and verify
            manager2 = AccessControlManager(config_path=str(config_path))
            loaded_perms = manager2.get_agent_permissions("TestAgent")
            assert loaded_perms is not None
            assert loaded_perms.permission_level == PermissionLevel.WRITE
```

### 2. Add Tests for Training Manager Service

**File:** `tests/test_training_manager.py`

**Priority:** HIGH
**Coverage Needed:**
- Session lifecycle (start, complete, cancel)
- Activity generation
- Progress tracking
- XP calculation
- Level progression

**Example Test:**
```python
"""
[CREATE] Tests for TrainingManager service.

Agent: Composer
Timestamp: 2025-12-03T03:50:44Z
Operation: [CREATE]
"""

import pytest
from pathlib import Path
import tempfile

from training.services.training_manager import TrainingManager
from training.models import SessionType, SessionStatus, ActivityType

class TestTrainingManager:
    """Test TrainingManager functionality."""

    @pytest.fixture
    def manager(self):
        """Create TrainingManager with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield TrainingManager(Path(tmpdir))

    def test_initialize_agent(self, manager):
        """Test agent initialization."""
        # This will fail until agent profiles are configured
        # but shows the test structure needed
        pass

    def test_start_session(self, manager):
        """Test session creation."""
        session = manager.start_session("TestAgent", SessionType.DAILY)

        assert session is not None
        assert session.agent_id == "TestAgent"
        assert session.session_type == SessionType.DAILY
        assert session.status == SessionStatus.IN_PROGRESS

    def test_session_lifecycle(self, manager):
        """Test complete session lifecycle."""
        session = manager.start_session("TestAgent", SessionType.DAILY)
        assert session.status == SessionStatus.IN_PROGRESS

        # Complete session
        session.complete()
        assert session.status == SessionStatus.COMPLETED
        assert session.completed_at is not None
```

### 3. Add Tests for Config Service

**File:** `tests/test_config_service.py`

**Priority:** MEDIUM
**Coverage Needed:**
- YAML config loading
- Agent profile retrieval
- Schedule configuration
- Difficulty curve calculations

### 4. Add Integration Tests

**File:** `tests/integration/test_training_workflow.py`

**Priority:** HIGH
**Coverage Needed:**
- Complete training session workflow
- Multi-modal training selection
- Project-based learning integration
- Telemetry logging integration

**Example Test:**
```python
"""
[CREATE] Integration tests for complete training workflows.

Agent: Composer
Timestamp: 2025-12-03T03:50:44Z
Operation: [CREATE]
"""

import pytest
from training.services.training_manager import TrainingManager
from training.services.spaced_repetition import SM2SpacedRepetition
from training.models import SessionType, ReviewRating

class TestTrainingWorkflow:
    """Test complete training workflows."""

    def test_complete_daily_session_workflow(self):
        """Test complete daily training session."""
        # 1. Start session
        # 2. Generate activities
        # 3. Complete activities
        # 4. Record results
        # 5. Update progress
        # 6. Log telemetry
        pass

    def test_flashcard_review_workflow(self):
        """Test complete flashcard review cycle."""
        sm2 = SM2SpacedRepetition()
        # Create flashcard
        # Review with GOOD rating
        # Verify interval updated
        # Review again after interval
        # Verify ease factor changes
        pass
```

---

## 🎯 Test Quality Improvements

### 1. Add Parametrized Tests

**Current:** Single test per scenario
**Improved:** Parametrize to test multiple scenarios

**Example:**
```python
@pytest.mark.parametrize("rating,expected_interval", [
    (ReviewRating.AGAIN, 0),
    (ReviewRating.HARD, 1),
    (ReviewRating.GOOD, 1),
    (ReviewRating.EASY, 4),
])
def test_new_card_intervals(sm2_service, sample_flashcard, rating, expected_interval):
    """Test new card intervals for all ratings."""
    next_review, _ = sm2_service.calculate_next_review(
        sample_flashcard, rating, 2000
    )
    actual_interval = (next_review - date.today()).days
    assert actual_interval == expected_interval
```

### 2. Add Edge Case Tests

**Missing Coverage:**
- Boundary conditions (ease factor min/max)
- Empty collections
- Invalid inputs
- Concurrent access (if applicable)
- Time zone edge cases

**Example:**
```python
def test_ease_factor_boundaries(sm2_service):
    """Test ease factor stays within bounds."""
    card = create_flashcard_with_ease(1.3)  # Minimum
    _, new_ease = sm2_service.calculate_next_review(
        card, ReviewRating.AGAIN, 2000
    )
    assert new_ease >= 1.3

    card = create_flashcard_with_ease(3.0)  # High ease
    _, new_ease = sm2_service.calculate_next_review(
        card, ReviewRating.EASY, 2000
    )
    assert new_ease <= 3.5  # Reasonable maximum
```

### 3. Add Property-Based Tests

**Use Hypothesis library for fuzzing:**

```python
from hypothesis import given, strategies as st

@given(
    ease=st.floats(min_value=1.3, max_value=3.0),
    rating=st.sampled_from(list(ReviewRating)),
)
def test_ease_factor_always_valid(sm2_service, ease, rating):
    """Property: Ease factor always stays valid after any rating."""
    card = create_flashcard_with_ease(ease)
    _, new_ease = sm2_service.calculate_next_review(card, rating, 2000)
    assert 1.3 <= new_ease <= 3.5
```

### 4. Add Performance Tests

**File:** `tests/performance/test_spaced_repetition_perf.py`

```python
import pytest
import time

@pytest.mark.performance
def test_calculate_next_review_performance(sm2_service, sample_flashcard):
    """Test that review calculation is fast."""
    start = time.perf_counter()
    for _ in range(1000):
        sm2_service.calculate_next_review(
            sample_flashcard, ReviewRating.GOOD, 2000
        )
    elapsed = time.perf_counter() - start

    # Should complete 1000 calculations in < 1 second
    assert elapsed < 1.0
    assert elapsed / 1000 < 0.001  # < 1ms per calculation
```

---

## 🛠️ Test Infrastructure Improvements

### 1. Fix pytest Configuration

**File:** `pytest.ini` (Update)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=src/training
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    performance: Performance tests
```

### 2. Add Test Coverage Requirements

**File:** `pyproject.toml` (Add)

```toml
[tool.coverage.run]
source = ["src/training"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### 3. Add GitHub Actions Test Workflow

**File:** `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          pytest tests/ -v --cov=src/training --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📋 Priority Action Items

### Immediate (Fix Blocking Issues)
1. ✅ **Fix model exports** - Add `FlashcardFront` and `FlashcardBack` to `__init__.py`
2. ✅ **Update test fixtures** - Fix API mismatches (`id` → `card_id`, etc.)
3. ✅ **Create `conftest.py`** - Add shared fixtures
4. ✅ **Fix import paths** - Ensure PYTHONPATH or package installation works

### High Priority (This Sprint)
5. ✅ **Add access control tests** - Critical security functionality
6. ✅ **Add training manager tests** - Core business logic
7. ✅ **Add integration tests** - End-to-end workflows
8. ✅ **Add parametrized tests** - Improve coverage efficiency

### Medium Priority (Next Sprint)
9. ⚠️ **Add config service tests**
10. ⚠️ **Add edge case tests**
11. ⚠️ **Add performance tests**
12. ⚠️ **Add property-based tests**

### Low Priority (Future)
13. ⚪ **Add mutation testing**
14. ⚪ **Add visual regression tests** (if UI components added)
15. ⚪ **Add load/stress tests**

---

## 📊 Test Metrics Goals

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| **Test Coverage** | ~30% | 80%+ | HIGH |
| **Tests Passing** | 0/18 | 100% | CRITICAL |
| **Integration Tests** | 0 | 5+ | HIGH |
| **Performance Tests** | 0 | 3+ | MEDIUM |
| **Test Execution Time** | N/A | < 30s | MEDIUM |

---

## 🎓 Best Practices Recommendations

### 1. Test Organization
- ✅ Use `tests/unit/` for unit tests
- ✅ Use `tests/integration/` for integration tests
- ✅ Use `tests/fixtures/` for test data files
- ✅ Use descriptive test names: `test_<function>_<scenario>_<expected>`

### 2. Test Data Management
- ✅ Use factories for complex objects
- ✅ Use fixtures for shared setup
- ✅ Clean up test data (temp directories, etc.)
- ✅ Use faker library for realistic test data

### 3. Assertions
- ✅ Use specific assertions (`assert x == y` not `assert x`)
- ✅ Include helpful error messages
- ✅ Test one thing per test
- ✅ Use pytest's `approx()` for float comparisons

### 4. Documentation
- ✅ Document test purpose in docstrings
- ✅ Include examples in docstrings
- ✅ Mark slow tests with `@pytest.mark.slow`
- ✅ Document test data requirements

---

## 🔗 Related Documentation

- [Agents.MD Protocol](../Agents.MD) - Code standards and telemetry
- [Training System README](README.md) - System overview
- [Pytest Documentation](https://docs.pytest.org/) - Testing framework
- [Coverage.py Documentation](https://coverage.readthedocs.io/) - Coverage tool

---

**Agent:** Composer
**Timestamp:** 2025-12-03T03:50:44Z
**Operation:** [ANALYZE]
**Status:** COMPLETED
