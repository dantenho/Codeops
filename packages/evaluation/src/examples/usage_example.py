"""
Code Evaluation System - Usage Examples

Demonstrates how to use the code evaluation system for:
- Quality analysis
- Quality gate enforcement
- Batch evaluation
- Trend analysis
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from evaluation.core.evaluator import CodeEvaluator
from evaluation.metrics.code_quality import analyze_code_quality
from evaluation.gates.quality_gate import (
    get_quality_gate,
    check_quality_gate,
    create_gate_report,
)


# === EXAMPLE 1: Simple Quality Analysis ===

def example_simple_analysis():
    """Analyze code quality without quality gates."""
    code = '''
def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.

    Args:
        n: Position in Fibonacci sequence

    Returns:
        Fibonacci number at position n
    """
    if n <= 0:
        raise ValueError("n must be positive")
    elif n <= 2:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
'''

    # Analyze code quality
    metrics = analyze_code_quality(code, language="python")

    print("=== Simple Quality Analysis ===")
    print(f"Overall Score: {metrics.overall_score:.1f}/100")
    print(f"Grade: {metrics.grade}")
    print(f"Complexity: {metrics.cyclomatic_complexity}")
    print(f"Type Coverage: {metrics.type_coverage:.1f}%")
    print(f"Docstring Coverage: {metrics.docstring_coverage:.1f}%")
    print(f"Security Issues: {len(metrics.security_issues)}")
    print()


# === EXAMPLE 2: Full Evaluation with Quality Gate ===

def example_full_evaluation():
    """Comprehensive evaluation with quality gate check."""
    code = '''
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class UserRequest(BaseModel):
    """User creation request."""
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    """User creation response."""
    id: int
    username: str
    email: str

@router.post("/users")
async def create_user(request: UserRequest) -> UserResponse:
    """
    Create a new user.

    Args:
        request: User creation request

    Returns:
        Created user information

    Raises:
        HTTPException: On validation or creation errors
    """
    try:
        # Validate username
        if len(request.username) < 3:
            raise ValueError("Username must be at least 3 characters")

        # Create user (simplified)
        user_id = 123

        return UserResponse(
            id=user_id,
            username=request.username,
            email=request.email
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
'''

    # Create evaluator
    evaluator = CodeEvaluator()

    # Evaluate with quality gate
    result = evaluator.evaluate(
        code=code,
        language="python",
        intent="Create FastAPI endpoint for user creation",
        agent_id="agent_001",
        session_id="session_123",
        quality_gate="api_endpoint",
    )

    print("=== Full Evaluation with Quality Gate ===")
    print(result.summary)
    print()

    if result.priority_fixes:
        print("Priority Fixes:")
        for fix in result.priority_fixes:
            print(f"  - {fix}")
        print()

    if result.suggested_improvements:
        print("Suggested Improvements:")
        for improvement in result.suggested_improvements:
            print(f"  - {improvement}")
        print()

    print(f"Can Commit: {result.can_commit}")
    print(f"Can Deploy: {result.can_deploy}")
    print()


# === EXAMPLE 3: Quality Gate Checking ===

def example_quality_gate():
    """Check code against specific quality gate."""
    code = '''
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
'''

    # Analyze code
    metrics = analyze_code_quality(code, language="python")

    # Get quality gate
    gate = get_quality_gate("commit")

    # Create mock evaluation result
    from evaluation.core.evaluator import EvaluationResult, EvaluationContext

    result = EvaluationResult(
        evaluation_id="test",
        context=EvaluationContext(code=code, language="python"),
        quality_metrics=metrics,
    )

    # Check gate
    gate_result = check_quality_gate(result, gate)

    print("=== Quality Gate Check ===")
    print(create_gate_report(result, gate_result))
    print()


# === EXAMPLE 4: Batch Evaluation ===

def example_batch_evaluation():
    """Evaluate multiple files at once."""
    # Create evaluator
    evaluator = CodeEvaluator()

    # Example files (would be real paths in practice)
    files = [
        Path("example1.py"),
        Path("example2.py"),
        Path("example3.py"),
    ]

    # In real usage, these files would exist
    # For demo, we'll show the API:

    print("=== Batch Evaluation ===")
    print("API Usage:")
    print("results = evaluator.batch_evaluate(files, quality_gate='commit')")
    print()
    print("for file_path, result in results.items():")
    print("    print(f'{file_path}: {result.quality_metrics.grade}')")
    print()


# === EXAMPLE 5: Quality Trends ===

def example_quality_trends():
    """Track quality trends over time."""
    evaluator = CodeEvaluator()

    # Simulate multiple evaluations
    codes = [
        # First attempt - poor quality
        "def f(x):\n    return x*2",

        # Second attempt - better
        "def double(x):\n    return x * 2",

        # Third attempt - good
        '''def double(value: int) -> int:
    """Double the input value."""
    return value * 2''',
    ]

    for i, code in enumerate(codes):
        evaluator.evaluate(
            code=code,
            language="python",
            agent_id="agent_001",
            session_id=f"session_{i}",
        )

    # Analyze trends
    trends = evaluator.get_quality_trends(agent_id="agent_001")

    print("=== Quality Trends ===")
    print(f"Evaluations: {trends['evaluations_count']}")
    print(f"Average Quality: {trends['average_quality']:.1f}")
    print(f"Trend: {trends['quality_trend']}")
    print(f"Latest Score: {trends['latest_score']:.1f}")
    print(f"Best Score: {trends['best_score']:.1f}")
    print()


# === EXAMPLE 6: Security Issue Detection ===

def example_security_detection():
    """Detect security issues in code."""
    code = '''
import subprocess
import pickle

def process_command(cmd):
    # BAD: Command injection risk
    subprocess.run(cmd, shell=True)

def load_data(data):
    # BAD: Pickle deserialization risk
    return pickle.loads(data)

# BAD: Hardcoded credentials
API_KEY = "sk-1234567890abcdef"
'''

    metrics = analyze_code_quality(code, language="python", strict=True)

    print("=== Security Issue Detection ===")
    print(f"Security Issues: {len(metrics.security_issues)}")
    print(f"Critical: {metrics.critical_security_count}")
    print(f"High: {metrics.high_security_count}")
    print()

    for issue in metrics.security_issues:
        print(f"{issue.severity.upper()}: {issue.category}")
        print(f"  Line {issue.line_number}: {issue.description}")
        print(f"  Fix: {issue.recommendation}")
        print()


# === EXAMPLE 7: Complex Code Analysis ===

def example_complex_code():
    """Analyze complex code with nested loops."""
    code = '''
def complex_algorithm(matrix):
    """Process 2D matrix with nested loops."""
    result = []

    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix[i])):
            value = matrix[i][j]

            # Nested processing
            if value > 0:
                for k in range(value):
                    row.append(k * value)
            else:
                row.append(0)

        result.append(row)

    return result
'''

    metrics = analyze_code_quality(code, language="python")

    print("=== Complex Code Analysis ===")
    print(f"Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
    print(f"Average Complexity: {metrics.average_complexity:.1f}")
    print(f"Max Complexity: {metrics.max_complexity}")
    print(f"Runtime Complexity: {metrics.estimated_runtime_complexity}")
    print(f"Memory Efficiency: {metrics.memory_efficiency_score:.1f}")
    print()

    if metrics.warnings:
        print("Warnings:")
        for warning in metrics.warnings:
            print(f"  - {warning}")
        print()


# === RUN ALL EXAMPLES ===

if __name__ == "__main__":
    print("CODE EVALUATION SYSTEM - USAGE EXAMPLES\n")
    print("=" * 60)
    print()

    example_simple_analysis()
    example_full_evaluation()
    example_quality_gate()
    example_batch_evaluation()
    example_quality_trends()
    example_security_detection()
    example_complex_code()

    print("=" * 60)
    print("\nAll examples completed!")
