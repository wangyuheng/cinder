#!/bin/bash

set -e

echo "=========================================="
echo "Cinder LLM Agent Observability - Local Testing"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=1
FAILED_TESTS=1

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo ""
    echo "Test $TOTAL_TESTS: $test_name"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

# Check prerequisites
echo ""
echo "Checking prerequisites..."
echo "----------------------------------------"

# Check Python version
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3 is available${NC}"
else
    echo -e "${RED}✗ Python 3 is not available${NC}"
    exit 1
fi

# Check virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}✓ Virtual environment is active: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}⚠ No virtual environment detected${NC}"
fi

# Check Phoenix
echo ""
echo "Checking Phoenix..."
echo "----------------------------------------"

if docker ps | grep -q cinder-phoenix; then
    echo -e "${GREEN}✓ Phoenix container is running${NC}"
else
    echo -e "${YELLOW}⚠ Phoenix container is not running${NC}"
    echo "  Start with: make start"
fi

# Run unit tests
echo ""
echo "=========================================="
echo "Running Unit Tests"
echo "=========================================="

run_test "Tracing Module Tests" "python -m pytest tests/test_tracing.py -v"
run_test "Performance Tests" "python -m pytest tests/test_tracing_performance.py -v"

# Run integration tests
echo ""
echo "=========================================="
echo "Running Integration Tests"
echo "=========================================="

run_test "End-to-End Tests" "python -m pytest tests/ -v --cov=cinder_cli --cov-report=html"

# Test CLI commands
echo ""
echo "=========================================="
echo "Testing CLI Commands"
echo "=========================================="

echo ""
echo "Test: cinder --help"
cinder --help

echo ""
echo "Test: cinder service status"
cinder service status

echo ""
echo "Test: cinder trace config --show"
cinder trace config --show

# Test Phoenix UI
echo ""
echo "=========================================="
echo "Testing Phoenix UI"
echo "=========================================="

if curl -s http://localhost:6006/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Phoenix UI is accessible${NC}"
    echo "  URL: http://localhost:6006"
else
    echo -e "${RED}✗ Phoenix UI is not accessible${NC}"
fi

# Test trace creation
echo ""
echo "=========================================="
echo "Testing Trace Creation"
echo "=========================================="

echo ""
echo "Creating test trace..."
python test_trace_schema.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test trace created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create test trace${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="

echo ""
echo "Total Tests: $((TOTAL_TESTS - 1))"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}All tests passed!${NC}"
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="

echo ""
echo "1. Open Phoenix UI: http://localhost:6006"
echo "2. View traces in the 'Projects' section"
echo "3. Run a real execution: cinder execute 'your task'"
echo ""
