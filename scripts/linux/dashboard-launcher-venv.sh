#!/bin/bash

# Dashboard Launcher with Virtual Environment Support

echo "================================"
echo "TUS Firewall Dashboard Launcher"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "../../venv-dashboard" ]; then
    echo "Virtual environment not found. Setting up now..."
    echo ""
    chmod +x setup-dashboard-venv.sh
    ./setup-dashboard-venv.sh
    if [ $? -ne 0 ]; then
        echo "Failed to setup virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment found: venv-dashboard"
fi

echo ""
echo "Activating virtual environment..."
source ../../venv-dashboard/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to activate virtual environment"
    echo "Try running ./setup-dashboard-venv.sh first"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Check if streamlit is available in venv
python -c "import streamlit" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "📦 Installing missing dependencies..."
    pip install -r ../../requirements-dashboard.txt
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo "🚀 Starting TUS Firewall Test Dashboard..."
echo "📱 Dashboard will open in your default browser at http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the dashboard"
echo ""

python -m streamlit run ../../dashboard.py --server.port 8501 --server.address localhost