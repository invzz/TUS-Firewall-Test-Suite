@echo off
REM Windows batch script for running TUS Firewall Test Suite tests

echo.
echo ================================
echo TUS Firewall Test Suite - Tests
echo ================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Change to project root
cd /d "%~dp0\.."

REM Check if virtual environment exists and activate it
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python
)

REM Install test dependencies if needed
echo Checking test dependencies...
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo Installing test dependencies...
    pip install -r tests\requirements-test.txt
    if errorlevel 1 (
        echo Error: Failed to install test dependencies
        exit /b 1
    )
)

REM Run the test runner
echo.
echo Running tests...
python tests\run_tests.py %*

REM Check exit code and provide feedback
if errorlevel 1 (
    echo.
    echo ❌ Tests failed! Check the output above for details.
    exit /b 1
) else (
    echo.
    echo ✅ All tests passed successfully!
    echo 📊 Coverage report available at: tests\coverage_html\index.html
)

pause