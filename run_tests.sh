#!/bin/bash
# OpsZen Test Runner Script
#
# This script provides convenient shortcuts for running various test configurations

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Help message
show_help() {
    cat << EOF
OpsZen Test Runner

Usage: ./run_tests.sh [OPTIONS]

OPTIONS:
    all                 Run all tests (default)
    unit                Run only unit tests
    integration         Run only integration tests
    coverage            Run tests with coverage report
    fast                Run tests in parallel (faster)
    verbose             Run tests with verbose output
    failed              Re-run only failed tests from last run
    markers             List all available test markers
    specific TEST       Run specific test file or function
    watch               Run tests in watch mode (re-run on file changes)

    docker              Run only Docker-related tests
    ssh                 Run only SSH-related tests
    aws                 Run only AWS-related tests
    logs                Run only log analyzer tests
    monitoring          Run only monitoring tests

    clean               Clean test artifacts and cache
    install             Install test dependencies
    report              Generate HTML coverage report
    help                Show this help message

EXAMPLES:
    ./run_tests.sh                          # Run all tests
    ./run_tests.sh unit                     # Run unit tests only
    ./run_tests.sh coverage                 # Run with coverage
    ./run_tests.sh fast coverage            # Fast tests with coverage
    ./run_tests.sh specific test_docker     # Run specific test file
    ./run_tests.sh docker                   # Run Docker tests only
    ./run_tests.sh clean install all        # Clean, install, and run all

ENVIRONMENT VARIABLES:
    PYTEST_ARGS         Additional pytest arguments
    TEST_TIMEOUT        Test timeout in seconds (default: 300)

EOF
}

# Check if pytest is installed
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        print_error "pytest is not installed"
        print_warning "Install test dependencies with: ./run_tests.sh install"
        exit 1
    fi
}

# Check if virtual environment is activated, create/activate if needed
ensure_venv() {
    print_header "Checking Virtual Environment"

    # Check if already in a virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        print_success "Virtual environment already activated: $VIRTUAL_ENV"
        return 0
    fi

    # Check if .venv exists
    if [ ! -d ".venv" ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv .venv
        if [ $? -ne 0 ]; then
            print_error "Failed to create virtual environment"
            exit 1
        fi
        print_success "Virtual environment created"
    fi

    # Activate the virtual environment
    print_warning "Activating virtual environment..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        print_success "Virtual environment activated: $VIRTUAL_ENV"
    elif [ -f ".venv/Scripts/activate" ]; then
        # Windows Git Bash
        source .venv/Scripts/activate
        print_success "Virtual environment activated: $VIRTUAL_ENV"
    else
        print_error "Could not find activation script"
        exit 1
    fi
}

# Install test dependencies
install_deps() {
    print_header "Installing Test Dependencies"

    # Ensure venv is active
    ensure_venv

    if [ -f "tests/requirements-test.txt" ]; then
        pip install -r tests/requirements-test.txt
        print_success "Test dependencies installed"
    else
        print_error "tests/requirements-test.txt not found"
        exit 1
    fi
}

# Clean test artifacts
clean_artifacts() {
    print_header "Cleaning Test Artifacts"

    # Remove cache directories
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

    # Remove coverage files
    rm -rf htmlcov/ 2>/dev/null || true
    rm -f .coverage 2>/dev/null || true
    rm -f coverage.xml 2>/dev/null || true

    # Remove test reports
    rm -rf test-results/ 2>/dev/null || true
    rm -f pytest_report.html 2>/dev/null || true

    print_success "Test artifacts cleaned"
}

# List test markers
list_markers() {
    print_header "Available Test Markers"
    check_pytest
    pytest --markers
}

# Generate HTML coverage report
generate_report() {
    print_header "Generating Coverage Report"

    if [ -f ".coverage" ]; then
        coverage html
        print_success "Coverage report generated in htmlcov/index.html"

        # Try to open in browser (optional)
        if command -v xdg-open &> /dev/null; then
            xdg-open htmlcov/index.html 2>/dev/null || true
        elif command -v open &> /dev/null; then
            open htmlcov/index.html 2>/dev/null || true
        fi
    else
        print_error "No coverage data found. Run tests with coverage first."
        exit 1
    fi
}

# Default values
PYTEST_ARGS=${PYTEST_ARGS:-""}
TEST_TIMEOUT=${TEST_TIMEOUT:-300}
MODE="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        help|--help|-h)
            show_help
            exit 0
            ;;
        install)
            install_deps
            exit 0
            ;;
        clean)
            clean_artifacts
            exit 0
            ;;
        markers)
            list_markers
            exit 0
            ;;
        report)
            generate_report
            exit 0
            ;;
        all)
            MODE="all"
            shift
            ;;
        unit)
            MODE="unit"
            shift
            ;;
        integration)
            MODE="integration"
            shift
            ;;
        docker)
            MODE="docker"
            shift
            ;;
        ssh)
            MODE="ssh"
            shift
            ;;
        aws)
            MODE="aws"
            shift
            ;;
        logs)
            MODE="logs"
            shift
            ;;
        monitoring)
            MODE="monitoring"
            shift
            ;;
        coverage)
            PYTEST_ARGS="$PYTEST_ARGS --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml --cov-branch"
            shift
            ;;
        fast)
            PYTEST_ARGS="$PYTEST_ARGS -n auto"
            shift
            ;;
        verbose)
            PYTEST_ARGS="$PYTEST_ARGS -vv"
            shift
            ;;
        failed)
            PYTEST_ARGS="$PYTEST_ARGS --lf"
            shift
            ;;
        specific)
            if [ -z "$2" ]; then
                print_error "Please specify a test file or function"
                exit 1
            fi
            MODE="specific"
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        watch)
            print_header "Watch Mode - Tests will re-run on file changes"
            print_warning "Press Ctrl+C to stop"
            check_pytest
            pytest-watch -- tests/
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# Ensure virtual environment is set up and activated
ensure_venv

# Check if pytest is available
check_pytest

# Build pytest command based on mode
case $MODE in
    all)
        print_header "Running All Tests"
        CMD="pytest tests/ $PYTEST_ARGS"
        ;;
    unit)
        print_header "Running Unit Tests"
        CMD="pytest tests/unit/ $PYTEST_ARGS"
        ;;
    integration)
        print_header "Running Integration Tests"
        CMD="pytest tests/integration/ $PYTEST_ARGS"
        ;;
    docker)
        print_header "Running Docker Tests"
        CMD="pytest tests/ -m docker $PYTEST_ARGS"
        ;;
    ssh)
        print_header "Running SSH Tests"
        CMD="pytest tests/ -m ssh $PYTEST_ARGS"
        ;;
    aws)
        print_header "Running AWS Tests"
        CMD="pytest tests/ -m aws $PYTEST_ARGS"
        ;;
    logs)
        print_header "Running Log Analyzer Tests"
        CMD="pytest tests/ -k log $PYTEST_ARGS"
        ;;
    monitoring)
        print_header "Running Monitoring Tests"
        CMD="pytest tests/ -k monitor $PYTEST_ARGS"
        ;;
    specific)
        print_header "Running Specific Test: $SPECIFIC_TEST"
        CMD="pytest $SPECIFIC_TEST $PYTEST_ARGS"
        ;;
esac

# Add timeout if not already specified
if [[ ! $PYTEST_ARGS =~ "--timeout" ]]; then
    CMD="$CMD --timeout=$TEST_TIMEOUT"
fi

# Display command being run
echo -e "${YELLOW}Command: $CMD${NC}"
echo ""

# Run tests
if eval $CMD; then
    echo ""
    print_success "All tests passed!"

    # Show coverage summary if coverage was run
    if [[ $PYTEST_ARGS =~ "--cov" ]]; then
        echo ""
        print_success "Coverage report available in htmlcov/index.html"
    fi

    exit 0
else
    echo ""
    print_error "Some tests failed!"
    print_warning "Run './run_tests.sh failed' to re-run only failed tests"
    print_warning "Run './run_tests.sh verbose' for more detailed output"
    exit 1
fi
