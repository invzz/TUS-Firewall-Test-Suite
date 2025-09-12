@echo off
REM Dashboard Launcher for TUS Firewall Test Suite

echo.
echo ================================
echo TUS Firewall Dashboard Launcher
echo ================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo Installing dashboard dependencies...
pip install -r requirements-dashboard.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Starting TUS Firewall Test Dashboard...
echo Dashboard will open in your default browser
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run dashboard.py --server.port 8501 --server.address localhost

pause