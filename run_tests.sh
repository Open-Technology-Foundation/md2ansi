#!/usr/bin/env bash
# run_tests.sh - Test runner for md2ansi
#
# This script runs the md2ansi test suite using pytest if available,
# or falls back to Python's built-in unittest module.
#
# Usage: ./run_tests.sh [--coverage] [--verbose]
#
# Options:
#   --coverage  Generate coverage report (requires pytest-cov)
#   --verbose   Show detailed test output
#   --help      Show this help message

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
COVERAGE=false
VERBOSE=false

for arg in "$@"; do
  case $arg in
    --coverage)
      COVERAGE=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--coverage] [--verbose]"
      echo ""
      echo "Options:"
      echo "  --coverage  Generate coverage report (requires pytest-cov)"
      echo "  --verbose   Show detailed test output"
      echo "  --help      Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo -e "${GREEN}=== MD2ANSI Test Suite ===${NC}"
echo ""

# Check if we're in the right directory
if [[ ! -f "md2ansi.py" ]]; then
  echo -e "${RED}Error: md2ansi.py not found. Please run this script from the md2ansi directory.${NC}"
  exit 1
fi

# Check if test file exists
if [[ ! -f "test_md2ansi.py" ]]; then
  echo -e "${RED}Error: test_md2ansi.py not found.${NC}"
  exit 1
fi

# Function to run tests with unittest
run_unittest() {
  echo -e "${YELLOW}Running tests with unittest...${NC}"
  echo ""
  
  if [[ "$VERBOSE" == true ]]; then
    python3 test_md2ansi.py -v
  else
    python3 test_md2ansi.py
  fi
}

# Function to run tests with pytest
run_pytest() {
  echo -e "${YELLOW}Running tests with pytest...${NC}"
  echo ""
  
  local pytest_args=""
  
  if [[ "$VERBOSE" == true ]]; then
    pytest_args="$pytest_args -v"
  fi
  
  if [[ "$COVERAGE" == true ]]; then
    # Check if pytest-cov is installed
    if python3 -c "import pytest_cov" 2>/dev/null; then
      pytest_args="$pytest_args --cov=md2ansi --cov-report=term-missing --cov-report=html"
      echo -e "${GREEN}Coverage reporting enabled${NC}"
    else
      echo -e "${YELLOW}Warning: pytest-cov not installed. Skipping coverage report.${NC}"
      echo "Install with: pip install pytest-cov"
    fi
  fi
  
  pytest test_md2ansi.py $pytest_args
}

# Check if pytest is available
if command -v pytest &> /dev/null; then
  run_pytest
elif python3 -c "import pytest" 2>/dev/null; then
  # pytest is installed as a module but not in PATH
  echo -e "${YELLOW}Running tests with pytest module...${NC}"
  echo ""
  
  if [[ "$VERBOSE" == true ]]; then
    python3 -m pytest test_md2ansi.py -v
  else
    python3 -m pytest test_md2ansi.py
  fi
else
  # Fall back to unittest
  echo -e "${YELLOW}pytest not found. Using built-in unittest module.${NC}"
  
  if [[ "$COVERAGE" == true ]]; then
    echo -e "${YELLOW}Note: Coverage reporting requires pytest-cov${NC}"
  fi
  
  run_unittest
fi

# Check test results
if [[ $? -eq 0 ]]; then
  echo ""
  echo -e "${GREEN}✓ All tests passed!${NC}"
  
  # Test with actual markdown files
  echo ""
  echo -e "${GREEN}=== Testing with fixture files ===${NC}"
  
  for fixture in test_fixtures/*.md; do
    if [[ -f "$fixture" ]]; then
      filename=$(basename "$fixture")
      echo -n "Testing $filename... "
      
      # Test normal mode
      if ./md2ansi "$fixture" > /dev/null 2>&1; then
        echo -n "✓ "
      else
        echo -e "${RED}✗ Failed${NC}"
        continue
      fi
      
      # Test debug mode
      if ./md2ansi --debug "$fixture" 2>/dev/null 1>/dev/null; then
        echo -n "✓ "
      else
        echo -e "${RED}✗ Debug failed${NC}"
        continue
      fi
      
      # Test plain mode
      if ./md2ansi --plain "$fixture" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
      else
        echo -e "${RED}✗ Plain failed${NC}"
      fi
    fi
  done
  
  # Show coverage report location if generated
  if [[ "$COVERAGE" == true ]] && [[ -d "htmlcov" ]]; then
    echo ""
    echo -e "${GREEN}Coverage report generated in ./htmlcov/index.html${NC}"
  fi
  
  exit 0
else
  echo ""
  echo -e "${RED}✗ Tests failed!${NC}"
  exit 1
fi

#fin