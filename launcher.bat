@echo off
REM NFTables Testing Framework - Windows Launcher

echo.
echo ================================
echo NFTables Testing Framework
echo ================================
echo.
echo Select testing mode:
echo 1. Complete Game Simulation (Recommended)
echo 2. Basic Rule Testing  
echo 3. Interactive Server Mode
echo 4. Show Project Structure
echo 0. Exit
echo.
set /p choice="Enter your choice (0-4): "

if "%choice%"=="1" (
    echo Starting complete game simulation...
    docker-compose -f docker\docker-compose-game.yml up --build
) else if "%choice%"=="2" (
    echo Starting basic rule testing...
    docker-compose -f docker\docker-compose.yml up --build  
) else if "%choice%"=="3" (
    echo Starting interactive server mode...
    set KEEP_RUNNING=true
    docker-compose -f docker\docker-compose.yml up --build
) else if "%choice%"=="4" (
    echo.
    echo Project Structure:
    dir /AD
    echo.
    echo Results Location: .\results\
    dir results\ 2>nul || echo   (No results yet - run a test first)
) else if "%choice%"=="0" (
    echo Goodbye!
) else (
    echo Invalid choice. Please run again.
)

pause