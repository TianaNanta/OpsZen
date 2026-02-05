#!/usr/bin/env bash
# format.sh - Run ruff formatter and linter on the codebase

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not activated${NC}"
    echo "Activating .venv..."
    export VIRTUAL_ENV="$SCRIPT_DIR/.venv"
    export PATH="$VIRTUAL_ENV/bin:$PATH"
fi

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    echo -e "${RED}✗ Ruff not found. Installing...${NC}"
    uv pip install ruff
fi

echo "========================================"
echo "🎨 Code Formatting & Linting with Ruff"
echo "========================================"

# Parse command line arguments
MODE="${1:-format}"
TARGET="${2:-.}"

case "$MODE" in
    format)
        echo -e "${GREEN}Running ruff formatter...${NC}"
        ruff format "$TARGET"
        echo ""
        echo -e "${GREEN}Running ruff linter with auto-fix...${NC}"
        ruff check --fix "$TARGET"
        echo ""
        echo -e "${GREEN}✓ Formatting and linting complete!${NC}"
        ;;

    check)
        echo -e "${YELLOW}Checking formatting (no changes)...${NC}"
        ruff format --check "$TARGET"
        echo ""
        echo -e "${YELLOW}Checking linting (no fixes)...${NC}"
        ruff check "$TARGET"
        echo ""
        echo -e "${GREEN}✓ Check complete!${NC}"
        ;;

    lint)
        echo -e "${GREEN}Running ruff linter only...${NC}"
        ruff check --fix "$TARGET"
        echo ""
        echo -e "${GREEN}✓ Linting complete!${NC}"
        ;;

    lint-check)
        echo -e "${YELLOW}Checking linting (no fixes)...${NC}"
        ruff check "$TARGET"
        echo ""
        echo -e "${GREEN}✓ Lint check complete!${NC}"
        ;;

    stats)
        echo -e "${YELLOW}Generating linting statistics...${NC}"
        ruff check "$TARGET" --statistics
        ;;

    help|--help|-h)
        cat << EOF
Usage: ./format.sh [MODE] [TARGET]

Modes:
  format       Format code and fix linting issues (default)
  check        Check formatting and linting without making changes
  lint         Run linter with auto-fix only (no formatting)
  lint-check   Check linting without making changes
  stats        Show linting statistics
  help         Show this help message

Target:
  Path to format/lint (default: .)

Examples:
  ./format.sh                    # Format and lint entire project
  ./format.sh check              # Check without changes
  ./format.sh format src/        # Format only src/ directory
  ./format.sh lint tests/        # Lint only tests/ directory
  ./format.sh stats              # Show statistics

EOF
        ;;

    *)
        echo -e "${RED}✗ Unknown mode: $MODE${NC}"
        echo "Run './format.sh help' for usage information"
        exit 1
        ;;
esac

echo "========================================"
