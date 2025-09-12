#!/bin/bash

# Dashboard Launcher for TUS Firewall Test Suite

echo "================================"
echo "TUS Firewall Dashboard Launcher"
echo "================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ ERROR: pip is not available"
    echo "Please ensure pip is installed with Python"
    exit 1
fi

echo "📦 Installing dashboard dependencies..."
pip3 install -r requirements-dashboard.txt 2>/dev/null || pip install -r requirements-dashboard.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo ""
echo "🚀 Starting TUS Firewall Test Dashboard..."
echo "📱 Dashboard will open in your default browser"
echo "⏹️  Press Ctrl+C to stop the dashboard"
echo ""

# Use python3 if available, otherwise fall back to python
if command -v python3 &> /dev/null; then
    python3 -m streamlit run dashboard.py --server.port 8501 --server.address localhost
else
    python -m streamlit run dashboard.py --server.port 8501 --server.address localhost
fi