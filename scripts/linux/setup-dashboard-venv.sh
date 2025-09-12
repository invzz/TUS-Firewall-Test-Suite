#!/bin/bash

# Virtual Environment Setup for TUS Firewall Dashboard

echo "========================================"
echo "TUS Firewall Dashboard - Virtual Environment Setup"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Creating virtual environment for dashboard..."
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "../../venv-dashboard" ]; then
    echo "Creating new virtual environment: venv-dashboard"
    python3 -m venv ../../venv-dashboard
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to create virtual environment"
        echo "Please ensure you have python3-venv installed"
        echo "On Ubuntu/Debian: sudo apt install python3-venv"
        echo "On CentOS/RHEL: sudo yum install python3-venv"
        exit 1
    fi
    echo "✅ Virtual environment created successfully"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source ../../venv-dashboard/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"

echo ""
echo "Installing dashboard dependencies..."
python -m pip install --upgrade pip
pip install -r ../../requirements-dashboard.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully"
echo ""
echo "========================================"
echo "Dashboard Setup Complete!"
echo "========================================"
echo ""
echo "The virtual environment is ready and activated."
echo "You can now run the dashboard with:"
echo "  python dashboard.py"
echo ""
echo "Or use the integrated launcher:"
echo "  ./scripts/linux/dashboard-launcher-venv.sh"
echo ""