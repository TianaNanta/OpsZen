#!/usr/bin/env bash
# precommit.sh - Run prek (pre-commit) hooks manually

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

# Check if prek is installed
if ! command -v prek &> /dev/null; then
    echo -e "${RED}✗ Prek not found. Installing...${NC}"
    uv pip install prek
fi

echo "========================================"
echo "🔍 Prek (Pre-commit) Hooks"
echo "========================================"

# Parse command line arguments
MODE="${1:-run}"

case "$MODE" in
    run)
        echo -e "${GREEN}Running prek on staged files...${NC}"
        prek run
        echo ""
        echo -e "${GREEN}✓ Prek hooks complete!${NC}"
        ;;

    all)
        echo -e "${GREEN}Running prek on all files...${NC}"
        prek run --all-files
        echo ""
        echo -e "${GREEN}✓ Prek hooks complete!${NC}"
        ;;

    install)
        echo -e "${BLUE}Installing prek hooks...${NC}"
        prek install
        prek install --hook-type commit-msg
        echo ""
        echo -e "${GREEN}✓ Prek hooks installed!${NC}"
        echo ""
        echo "Hooks are now active. They will run automatically on:"
        echo "  • git commit (runs pre-commit hook)"
        echo "  • git commit -m (runs commit-msg hook)"
        ;;

    uninstall)
        echo -e "${YELLOW}Uninstalling prek hooks...${NC}"
        prek uninstall
        prek uninstall --hook-type commit-msg
        echo ""
        echo -e "${GREEN}✓ Prek hooks uninstalled!${NC}"
        ;;

    update)
        echo -e "${BLUE}Updating prek hooks...${NC}"
        prek autoupdate
        echo ""
        echo -e "${GREEN}✓ Prek hooks updated!${NC}"
        ;;

    clean)
        echo -e "${YELLOW}Cleaning prek cache...${NC}"
        prek clean
        echo ""
        echo -e "${GREEN}✓ Prek cache cleaned!${NC}"
        ;;

    validate)
        echo -e "${BLUE}Validating prek configuration...${NC}"
        prek validate-config
        echo ""
        echo -e "${GREEN}✓ Configuration is valid!${NC}"
        ;;

    sample)
        echo -e "${BLUE}Running prek on sample files...${NC}"
        prek run --files src/cli.py tests/conftest.py
        echo ""
        echo -e "${GREEN}✓ Sample run complete!${NC}"
        ;;

    hook)
        if [ -z "$2" ]; then
            echo -e "${RED}✗ Hook name required${NC}"
            echo "Usage: ./precommit.sh hook <hook-name>"
            echo "Example: ./precommit.sh hook ruff"
            exit 1
        fi
        echo -e "${GREEN}Running specific hook: $2${NC}"
        prek run "$2" --all-files
        echo ""
        echo -e "${GREEN}✓ Hook '$2' complete!${NC}"
        ;;

    help|--help|-h)
        cat << EOF
Usage: ./precommit.sh [MODE] [OPTIONS]

Modes:
  run          Run prek on staged files (default)
  all          Run prek on all files in the repository
  install      Install prek hooks to git
  uninstall    Uninstall prek hooks from git
  update       Update prek hook versions
  clean        Clean prek cache
  validate     Validate prek configuration
  sample       Run prek on sample files
  hook <name>  Run specific hook on all files
  help         Show this help message

Examples:
  ./precommit.sh                 # Run on staged files
  ./precommit.sh all             # Run on all files
  ./precommit.sh install         # Install hooks
  ./precommit.sh update          # Update hook versions
  ./precommit.sh hook ruff       # Run only ruff hook
  ./precommit.sh validate        # Validate config

Available hooks in this project:
  - ruff                         # Python linter
  - ruff-format                  # Python formatter
  - check-added-large-files      # Prevent large files
  - check-case-conflict          # Check case conflicts
  - end-of-file-fixer            # Fix EOF newlines
  - trailing-whitespace          # Trim trailing spaces
  - debug-statements             # Check for debugger
  - check-merge-conflict         # Check merge conflicts
  - check-yaml                   # Validate YAML
  - check-toml                   # Validate TOML
  - check-json                   # Validate JSON
  - shellcheck                   # Shell script linting

EOF
        ;;

    *)
        echo -e "${RED}✗ Unknown mode: $MODE${NC}"
        echo "Run './precommit.sh help' for usage information"
        exit 1
        ;;
esac

echo "========================================"
