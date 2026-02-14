#!/bin/bash
# Test runner script for OpenFOAM GUI

set -e

echo "==================================="
echo "OpenFOAM GUI Test Suite"
echo "==================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Run unit tests
echo -e "${YELLOW}Running Unit Tests...${NC}"
echo "-----------------------------------"
python tests/unit/test_core.py
UNIT_RESULT=$?

echo ""

# Run functional tests
echo -e "${YELLOW}Running Functional Tests...${NC}"
echo "-----------------------------------"
python tests/functional/test_integration.py
FUNCTIONAL_RESULT=$?

echo ""
echo "==================================="
echo "Test Results Summary"
echo "==================================="

if [ $UNIT_RESULT -eq 0 ]; then
    echo -e "Unit Tests:       ${GREEN}PASSED${NC}"
else
    echo -e "Unit Tests:       ${RED}FAILED${NC}"
fi

if [ $FUNCTIONAL_RESULT -eq 0 ]; then
    echo -e "Functional Tests: ${GREEN}PASSED${NC}"
else
    echo -e "Functional Tests: ${RED}FAILED${NC}"
fi

echo "==================================="

# Exit with error if any tests failed
if [ $UNIT_RESULT -ne 0 ] || [ $FUNCTIONAL_RESULT -ne 0 ]; then
    exit 1
fi

exit 0
