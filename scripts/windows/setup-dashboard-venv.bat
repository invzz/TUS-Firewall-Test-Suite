@echo off
REM Virtual Environment Setup for TUS Firewall Dashboard

echo.
echo ========================================
echo TUS Firewall Dashboard - Virtual Environment Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Creating virtual environment for dashboard...
echo.

REM Create virtual environment if it doesn't exist
if not exist "..\..\venv-dashboard" (
    echo Creating new virtual environment: venv-dashboard
    python -m venv ..\..\venv-dashboard
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure you have venv module installed
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created successfully
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo Activating virtual environment...
call ..\..\venv-dashboard\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment activated

echo.
echo Installing dashboard dependencies...
python -m pip install --upgrade pip
pip install -r ..\..\requirements-dashboard.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ✓ Dependencies installed successfully
echo.
echo ========================================
echo Dashboard Setup Complete!
echo ========================================
echo.
echo The virtual environment is ready and activated.
echo You can now run the dashboard with:
echo   python dashboard.py
echo.
echo Or use the integrated launcher:
echo   .\scripts\windows\dashboard-launcher-venv.bat
echo.
pause