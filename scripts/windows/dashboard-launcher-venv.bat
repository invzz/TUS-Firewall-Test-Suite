@echo off
REM Dashboard Launcher with Virtual Environment Support

echo.
echo ================================
echo TUS Firewall Dashboard Launcher
echo ================================
echo.

REM Check if virtual environment exists
if not exist "..\..\venv-dashboard" (
    echo Virtual environment not found. Setting up now...
    echo.
    call setup-dashboard-venv.bat
    if %errorlevel% neq 0 (
        echo Failed to setup virtual environment
        pause
        exit /b 1
    )
) else (
    echo ✓ Virtual environment found: venv-dashboard
)

echo.
echo Activating virtual environment...
call ..\..\venv-dashboard\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Try running setup-dashboard-venv.bat first
    pause
    exit /b 1
)

echo ✓ Virtual environment activated
echo.

REM Check if streamlit is available in venv
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing missing dependencies...
    pip install -r ..\..\requirements-dashboard.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting TUS Firewall Test Dashboard...
echo Dashboard will open in your default browser at http://localhost:8501
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run ..\..\dashboard.py --server.port 8501 --server.address localhost

pause