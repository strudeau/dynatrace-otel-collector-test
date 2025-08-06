#!/bin/bash
# Linux/macOS script for running OTel Collector diagnostics

set -e

echo "======================================================================"
echo "DYNATRACE OPENTELEMETRY COLLECTOR DIAGNOSTICS (LINUX/MACOS)"
echo "======================================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.7+ using your system package manager"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Change to script directory
cd "$(dirname "$0")"

# Check if diagnostics script exists
if [[ ! -f "diagnostics.py" ]]; then
    echo "ERROR: diagnostics.py not found in current directory"
    echo "Please ensure you're running this from the scripts/ directory"
    exit 1
fi

echo "Running diagnostics..."
echo

# Run diagnostics with error handling
if ! $PYTHON_CMD diagnostics.py "$@"; then
    echo
    echo "ERROR: Diagnostics failed to run"
    echo "Common solutions:"
    echo "- Ensure collector container is running: docker-compose up -d"
    echo "- Check if ports 13133 and 8888 are accessible"
    echo "- Verify network connectivity to localhost"
    exit 1
fi

echo
echo "======================================================================"
echo "Diagnostics complete."