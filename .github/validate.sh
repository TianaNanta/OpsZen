#!/usr/bin/env bash
# validate.sh - Validate GitHub Actions setup
#
# This script validates the GitHub Actions workflows and ensures
# all required tools and commands are available.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Print functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASS++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((FAIL++))
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARN++))
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Validation functions
check_file_exists() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        print_success "$description: $file"
        return 0
    else
        print_error "$description: $file not found"
        return 1
    fi
}

check_yaml_valid() {
    local file=$1

    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        print_success "Valid YAML: $file"
        return 0
    else
        print_error "Invalid YAML: $file"
        return 1
    fi
}

check_make_target() {
    local target=$1

    if make -n "$target" >/dev/null 2>&1; then
        print_success "Make target exists: $target"
        return 0
    else
        print_error "Make target missing: $target"
        return 1
    fi
}

check_command() {
    local cmd=$1
    local description=$2

    if command -v "$cmd" >/dev/null 2>&1; then
        local version
        version=$(eval "$cmd --version 2>&1 | head -n1" || echo "unknown")
        print_success "$description: $cmd ($version)"
        return 0
    else
        print_warning "$description: $cmd not found (will be installed in CI)"
        return 1
    fi
}

# Main validation
main() {
    print_header "GitHub Actions Setup Validation"
    echo ""

    # Check workflow files
    print_info "Checking workflow files..."
    check_file_exists ".github/workflows/tests.yml" "Main test workflow"
    check_file_exists ".github/workflows/pr-check.yml" "PR check workflow"
    check_file_exists ".github/workflows/ci.yml" "CI pipeline workflow"
    check_file_exists ".github/workflows/nightly.yml" "Nightly test workflow"
    echo ""

    # Validate YAML syntax
    print_info "Validating YAML syntax..."
    if command -v python3 >/dev/null 2>&1; then
        for workflow in .github/workflows/*.yml; do
            check_yaml_valid "$workflow"
        done
    else
        print_warning "Python3 not found, skipping YAML validation"
    fi
    echo ""

    # Check Makefile targets
    print_info "Checking Makefile targets..."
    check_make_target "test"
    check_make_target "test-unit"
    check_make_target "test-integration"
    check_make_target "test-coverage"
    check_make_target "lint"
    check_make_target "format"
    check_make_target "format-check"
    check_make_target "lint-check"
    check_make_target "quick"
    check_make_target "ci"
    check_make_target "security"
    echo ""

    # Check required files
    print_info "Checking required files..."
    check_file_exists "pyproject.toml" "Project configuration"
    check_file_exists "Makefile" "Makefile"
    check_file_exists "run_tests.sh" "Test runner script"
    check_file_exists "format.sh" "Format script"
    check_file_exists "README.md" "README"
    echo ""

    # Check documentation
    print_info "Checking documentation..."
    check_file_exists "docs/CI_CD.md" "CI/CD documentation"
    check_file_exists "docs/CI_QUICK_REF.md" "CI quick reference"
    check_file_exists "GITHUB_ACTIONS_UPDATE.md" "Update summary"
    check_file_exists ".github/DEPLOYMENT_CHECKLIST.md" "Deployment checklist"
    echo ""

    # Check tools (optional in local environment)
    print_info "Checking development tools..."
    check_command "python3" "Python 3"
    check_command "uv" "uv package manager"
    check_command "ruff" "Ruff linter/formatter"
    check_command "pytest" "pytest test framework"
    check_command "git" "Git version control"
    echo ""

    # Check pyproject.toml structure
    print_info "Checking pyproject.toml structure..."
    if command -v python3 >/dev/null 2>&1; then
        if python3 -c "
import sys
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print('WARNING: No TOML library available')
        sys.exit(1)

with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)

# Check for required sections
if 'project' not in data:
    print('ERROR: Missing [project] section')
    sys.exit(1)

if 'dependencies' not in data['project']:
    print('ERROR: Missing project.dependencies')
    sys.exit(1)

if 'dependency-groups' not in data:
    print('ERROR: Missing [dependency-groups] section')
    sys.exit(1)

if 'dev' not in data['dependency-groups']:
    print('ERROR: Missing dependency-groups.dev')
    sys.exit(1)

print('OK')
" 2>&1; then
            result=$?
            if [ $result -eq 0 ]; then
                print_success "pyproject.toml structure is valid"
            elif [ $result -eq 1 ]; then
                print_warning "pyproject.toml validation skipped (missing TOML library)"
            else
                print_error "pyproject.toml structure is invalid"
            fi
        else
            print_error "pyproject.toml validation failed"
        fi
    else
        print_warning "Python3 not found, skipping pyproject.toml validation"
    fi
    echo ""

    # Check workflow syntax patterns
    print_info "Checking workflow patterns..."

    # Check for uv usage
    if grep -q "astral-sh/setup-uv" .github/workflows/*.yml; then
        print_success "Workflows use uv for dependency management"
    else
        print_error "Workflows missing uv setup"
    fi

    # Check for make commands
    if grep -q "make test" .github/workflows/*.yml; then
        print_success "Workflows use make commands"
    else
        print_error "Workflows missing make commands"
    fi

    # Check for proper activation
    if grep -q "source .venv/bin/activate" .github/workflows/*.yml; then
        print_success "Workflows activate virtual environment"
    else
        print_error "Workflows missing venv activation"
    fi

    echo ""

    # Summary
    print_header "Validation Summary"
    echo ""
    echo -e "${GREEN}Passed:  $PASS${NC}"
    echo -e "${YELLOW}Warnings: $WARN${NC}"
    echo -e "${RED}Failed:  $FAIL${NC}"
    echo ""

    if [ $FAIL -eq 0 ]; then
        print_success "All critical validations passed!"
        echo ""
        echo "Next steps:"
        echo "1. Review the workflows in .github/workflows/"
        echo "2. Run 'make quick' to test locally"
        echo "3. Run 'make ci' to run full CI pipeline"
        echo "4. Create a test PR to verify workflows"
        echo "5. Configure branch protection rules"
        echo ""
        echo "See .github/DEPLOYMENT_CHECKLIST.md for detailed deployment steps."
        return 0
    else
        print_error "Some validations failed. Please fix the issues above."
        return 1
    fi
}

# Run main function
main
exit $?
