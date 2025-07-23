#!/bin/bash

# Code quality script for todo microservices
# Runs import sorting, formatting, and linting for both todo-app and todo-backend
# Usage: 
#   ./quality.sh          - Fix mode (default) - fixes formatting and import issues automatically
#   ./quality.sh --check  - Check only (exits with error if issues found)

# Parse arguments
FIX_MODE=true
if [[ "$1" == "--check" ]]; then
    FIX_MODE=false
fi

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
BACKEND_ISSUES=()
FRONTEND_ISSUES=()
ALL_PASSED=true

if [ "$FIX_MODE" = true ]; then
    echo "🔧 Running code quality fixes for Todo Microservices..."
else
    echo "🔧 Running code quality checks for Todo Microservices..."
fi
echo ""

# Function to run quality checks for a project
run_quality_checks() {
    local project_name=$1
    local project_dir=$2
    local issues_array_name=$3
    
    echo -e "${BLUE}📦 Checking ${project_name}...${NC}"
    echo "----------------------------------------"
    
    cd "$project_dir"
    
    # isort (using shared config)
    echo "📦 Sorting imports with isort..."
    if [ "$FIX_MODE" = true ]; then
        uv run isort . --settings-path=../pyproject.toml
        echo -e "${GREEN}✅ Imports sorted${NC}"
    else
        if ! uv run isort . --settings-path=../pyproject.toml --check-only --diff; then
            eval "${issues_array_name}+=(\"${project_name}: Import sorting needed\")"
            ALL_PASSED=false
            echo -e "${RED}❌ Import sorting issues found${NC}"
        else
            echo -e "${GREEN}✅ Imports are correctly sorted${NC}"
        fi
    fi
    
    # black (using shared config)
    echo "🎨 Formatting code with black..."
    if [ "$FIX_MODE" = true ]; then
        uv run black . --config=../pyproject.toml
        echo -e "${GREEN}✅ Code formatted${NC}"
    else
        if ! uv run black . --config=../pyproject.toml --check --diff; then
            eval "${issues_array_name}+=(\"${project_name}: Code formatting needed\")"
            ALL_PASSED=false
            echo -e "${RED}❌ Formatting issues found${NC}"
        else
            echo -e "${GREEN}✅ Code is correctly formatted${NC}"
        fi
    fi
    
    # flake8 (using shared config) - always check only, never fix
    echo "🔍 Linting with flake8..."
    if ! uv run flake8 . --config=../.flake8; then
        eval "${issues_array_name}+=(\"${project_name}: Linting issues found\")"
        ALL_PASSED=false
        echo -e "${RED}❌ Linting issues found${NC}"
    else
        echo -e "${GREEN}✅ No linting issues${NC}"
    fi
    
    cd ..
    echo ""
}

# Run checks for backend
run_quality_checks "todo-backend" "todo-backend" "BACKEND_ISSUES"

# Run checks for frontend  
run_quality_checks "todo-app" "todo-app" "FRONTEND_ISSUES"

# Summary
echo "========================================="
if [ "$FIX_MODE" = true ]; then
    echo -e "${BLUE}📊 QUALITY FIX SUMMARY${NC}"
else
    echo -e "${BLUE}📊 QUALITY CHECK SUMMARY${NC}"
fi
echo "========================================="

if [ "$FIX_MODE" = true ]; then
    if [ "$ALL_PASSED" = true ]; then
        echo -e "${GREEN}🎉 All formatting and imports fixed!${NC}"
        echo ""
        echo "✅ todo-backend: Formatting and imports processed"
        echo "✅ todo-app: Formatting and imports processed"
        echo ""
        echo -e "${YELLOW}💡 Run in check mode to see what needs fixing:${NC}"
        echo "   ./quality.sh --check"
    else
        echo -e "${RED}❌ Some linting issues remain (cannot be auto-fixed):${NC}"
        echo ""
        
        if [ ${#BACKEND_ISSUES[@]} -gt 0 ]; then
            echo -e "${YELLOW}🔧 todo-backend issues:${NC}"
            for issue in "${BACKEND_ISSUES[@]}"; do
                echo "  - $issue"
            done
            echo ""
        fi
        
        if [ ${#FRONTEND_ISSUES[@]} -gt 0 ]; then
            echo -e "${YELLOW}🔧 todo-app issues:${NC}"
            for issue in "${FRONTEND_ISSUES[@]}"; do
                echo "  - $issue"
            done
            echo ""
        fi
        echo -e "${YELLOW}💡 These linting issues need manual fixes${NC}"
        exit 1
    fi
elif [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}🎉 All quality checks passed!${NC}"
    echo ""
    echo "✅ todo-backend: All checks passed"
    echo "✅ todo-app: All checks passed"
else
    echo -e "${RED}❌ Quality issues found:${NC}"
    echo ""
    
    if [ ${#BACKEND_ISSUES[@]} -gt 0 ]; then
        echo -e "${YELLOW}🔧 todo-backend issues:${NC}"
        for issue in "${BACKEND_ISSUES[@]}"; do
            echo "  - $issue"
        done
        echo ""
    fi
    
    if [ ${#FRONTEND_ISSUES[@]} -gt 0 ]; then
        echo -e "${YELLOW}🔧 todo-app issues:${NC}"
        for issue in "${FRONTEND_ISSUES[@]}"; do
            echo "  - $issue"
        done
        echo ""
    fi
    
    echo -e "${YELLOW}💡 To fix formatting and import issues automatically:${NC}"
    echo "   ./quality.sh"
    echo ""
    echo -e "${YELLOW}💡 Or fix manually:${NC}"
    echo "   cd todo-backend && uv run isort . --settings-path=../pyproject.toml && uv run black . --config=../pyproject.toml"
    echo "   cd todo-app && uv run isort . --settings-path=../pyproject.toml && uv run black . --config=../pyproject.toml"
    echo ""
    
    exit 1
fi
