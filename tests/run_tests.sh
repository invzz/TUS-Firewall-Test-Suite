#!/bin/bash

# Linux shell script for running TUS Firewall Test Suite tests

echo ""
echo "================================"
echo "TUS Firewall Test Suite - Tests"
echo "================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Get the directory of this script and change to project root
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR/.."

# Check if virtual environment exists and activate it
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "No virtual environment found, using system Python"
fi

# Install test dependencies if needed
echo "Checking test dependencies..."
python3 -c "import pytest" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing test dependencies..."
    pip3 install -r tests/requirements-test.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install test dependencies"
        exit 1
    fi
fi

# Run the test runner
echo ""
echo "Running tests..."
python3 tests/run_tests.py "$@"

# Check exit code and provide feedback
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo ""
    echo "❌ Tests failed! Check the output above for details."
    exit $exit_code
else
    echo ""
    echo "✅ All tests passed successfully!"
    echo "📊 Coverage report available at: tests/coverage_html/index.html"
fi