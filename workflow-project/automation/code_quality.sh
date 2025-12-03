#!/bin/bash
# [CREATE] Code Quality Automation Script
# Agent: GrokIA
# Timestamp: 2025-12-03T10:28:00Z

set -e

echo "🔧 Starting code quality checks..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "Using virtual environment: $VIRTUAL_ENV"
else
    print_warning "Not in a virtual environment. Consider using: source .venv/bin/activate"
fi

# Check for required tools
echo "📋 Checking required tools..."
tools=("black" "isort" "ruff" "mypy" "interrogate" "pydocstyle")
missing_tools=()

for tool in "${tools[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        missing_tools+=("$tool")
    else
        print_status "$tool found"
    fi
done

if [ ${#missing_tools[@]} -ne 0 ]; then
    print_error "Missing tools: ${missing_tools[*]}"
    echo "Install with: uv pip install ${missing_tools[*]}"
    exit 1
fi

# Run code formatting
echo "🎨 Running code formatting..."
echo "  └─ Black formatting..."
black . --check
print_status "Black formatting passed"

echo "  └─ Import sorting..."
isort . --check-only
print_status "Import sorting passed"

# Run linting
echo "🔍 Running code linting..."
echo "  └─ Ruff linting..."
ruff check . --output-format=github
print_status "Ruff linting passed"

# Run type checking (warnings only by default)
echo "🔬 Running type checking..."
mypy . --config-file workflow-project/config/mypy.ini || print_warning "MyPy found issues (warnings only in current config)"

# Run documentation checks
echo "📚 Running documentation checks..."
echo "  └─ Docstring coverage..."
interrogate -v -i --fail-under=70 workflow-project/ || print_warning "Documentation coverage below 70%"

echo "  └─ Docstring style..."
pydocstyle --convention=google workflow-project/ || print_warning "Some docstring style issues found"

echo "🎉 Code quality checks completed!"

# Generate summary report
echo ""
echo "📊 Quality Summary:"
echo "  • Black formatting: ✅ PASSED"
echo "  • Import sorting: ✅ PASSED"
echo "  • Ruff linting: ✅ PASSED"
echo "  • MyPy type checking: ⚠️  WARNINGS (configure as needed)"
echo "  • Docstring coverage: ⚠️  CHECKED (configure threshold)"
echo "  • Docstring style: ⚠️  CHECKED (configure conventions)"

echo ""
echo "💡 For CI integration, use:"
echo "   ./automation/code_quality.sh"
