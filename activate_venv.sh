#!/bin/bash
# OpsZen Virtual Environment Activation Helper
#
# This script ensures a virtual environment is created and activated.
# Usage: source activate_venv.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check if already in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    print_success "Virtual environment already activated: $VIRTUAL_ENV"

    # Check if it's the project's venv
    if [ "$VIRTUAL_ENV" = "$VENV_DIR" ]; then
        print_info "Using project virtual environment"
    else
        print_warning "Using a different virtual environment"
        print_warning "Project venv: $VENV_DIR"
        print_warning "Current venv: $VIRTUAL_ENV"
    fi
    return 0 2>/dev/null || exit 0
fi

# Check if .venv directory exists
if [ ! -d "$VENV_DIR" ]; then
    print_warning "Virtual environment not found at $VENV_DIR"
    print_info "Creating virtual environment..."

    # Create virtual environment
    python3 -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        print_error "Please ensure Python 3 is installed: python3 --version"
        return 1 2>/dev/null || exit 1
    fi

    print_success "Virtual environment created at $VENV_DIR"
fi

# Detect OS and activate accordingly
if [ -f "$VENV_DIR/bin/activate" ]; then
    # Linux/macOS
    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated!"
    print_info "Python: $(which python)"
    print_info "Location: $VIRTUAL_ENV"

elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    # Windows (Git Bash/MSYS)
    print_info "Activating virtual environment (Windows)..."
    source "$VENV_DIR/Scripts/activate"
    print_success "Virtual environment activated!"
    print_info "Python: $(which python)"
    print_info "Location: $VIRTUAL_ENV"

else
    print_error "Could not find activation script"
    print_error "Expected: $VENV_DIR/bin/activate or $VENV_DIR/Scripts/activate"
    return 1 2>/dev/null || exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    print_warning "pip not found in virtual environment"
    print_info "You may need to reinstall the virtual environment"
    return 1 2>/dev/null || exit 1
fi

# Upgrade pip if needed (suppress output)
print_info "Ensuring pip is up to date..."
pip install --upgrade pip --quiet 2>/dev/null

# Check if test dependencies are installed
if [ -f "$SCRIPT_DIR/tests/requirements-test.txt" ]; then
    if ! python -c "import pytest" 2>/dev/null; then
        print_warning "Test dependencies not installed"
        echo ""
        echo "To install test dependencies, run:"
        echo "  pip install -r tests/requirements-test.txt"
        echo "Or:"
        echo "  make install-dev"
        echo "  ./run_tests.sh install"
    else
        print_success "Test dependencies are installed"
    fi
fi

echo ""
print_success "Virtual environment is ready!"
echo ""
echo "To deactivate, run: deactivate"
echo "To run tests, use: make test or ./run_tests.sh"
echo ""
