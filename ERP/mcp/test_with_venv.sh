#!/bin/bash

# ERP MCP Server Test Script with Virtual Environment

echo "Testing ERP MCP Server with Virtual Environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run tests
echo "Running tests..."
python test_client.py

echo "Test completed!"
