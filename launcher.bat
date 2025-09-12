@echo off
REM NFTables Testing Framework - Windows Launcher

echo.
echo ================================
echo NFTables Testing Framework
echo ================================
echo.
echo Select testing mode:
echo 1. Complete Game Simulation (with Dashboard)
echo 2. Basic Rule Testing (with Dashboard)  
echo 3. Interactive Server Mode
echo 4. Dashboard Only (view existing results)
echo 5. Local Dashboard (Python venv)
echo 6. Show Project Structure
echo 0. Exit
echo.
set /p choice="Enter your choice (0-6): "

if "%choice%"=="1" (
    call :select_env_and_run_game
) else if "%choice%"=="2" (
    echo Starting basic rule testing...
    docker-compose -f docker\docker-compose.yml up --build --force-recreate
) else if "%choice%"=="3" (
    echo Starting interactive server mode...
    set KEEP_RUNNING=true
    docker-compose -f docker\docker-compose.yml up --build --force-recreate
) else if "%choice%"=="4" (
    echo Starting Dashboard Only...
    echo This will show existing results from previous tests
    docker-compose -f docker\docker-compose-dashboard.yml up --build
) else if "%choice%"=="5" (
    echo Starting Local Dashboard with Virtual Environment...
    call scripts\windows\dashboard-launcher-venv.bat
) else if "%choice%"=="6" (
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
goto :end

:select_env_and_run_game
echo.
echo Select test configuration:
echo 1. Light Testing (5 clients, 30s) - Quick validation
echo 2. Normal Testing (25 clients, 3min) - Realistic load  
echo 3. Stress Testing (100 clients, 5min) - High load
echo 4. Performance Testing (500 clients, 10min) - Very high load
echo 5. Default (.env or defaults)
echo.
set /p env_choice="Enter configuration (1-5): "

if "%env_choice%"=="1" (
    echo Starting light testing configuration...
    docker-compose --env-file .env.light -f docker\docker-compose-game.yml up --build --force-recreate
) else if "%env_choice%"=="2" (
    echo Starting normal testing configuration...
    docker-compose --env-file .env.normal -f docker\docker-compose-game.yml up --build --force-recreate
) else if "%env_choice%"=="3" (
    echo Starting stress testing configuration...
    docker-compose --env-file .env.stress -f docker\docker-compose-game.yml up --build --force-recreate
) else if "%env_choice%"=="4" (
    echo Starting performance testing configuration...
    echo WARNING: This will use significant system resources!
    set /p confirm="Continue? (y/N): "
    if /i "%confirm%"=="y" (
        docker-compose --env-file .env.performance -f docker\docker-compose-game.yml up --build --force-recreate
    ) else (
        echo Performance test cancelled.
    )
) else if "%env_choice%"=="5" (
    echo Starting with default configuration...
    docker-compose -f docker\docker-compose-game.yml up --build --force-recreate
) else (
    echo Invalid choice, using default configuration...
    docker-compose -f docker\docker-compose-game.yml up --build --force-recreate
)
goto :eof

:end

pause