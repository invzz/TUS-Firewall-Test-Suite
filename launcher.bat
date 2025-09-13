@echo off

REM NFTables Testing Framework - Main Windows Launcher

REM This is a convenience wrapper that calls the actual launcher in cmd/

echo.
echo ================================
echo NFTables Testing Framework
echo ================================
echo Starting Complete Game Simulation (with Dashboard)...
echo.

cd /d "%~dp0"

call :select_env_and_run_game
goto :end

:select_env_and_run_game
echo.
echo Select test configuration:
echo 1. Light Testing (5 clients, 30s) - Quick validation
echo 2. Normal Testing (25 clients, 3min) - Realistic load  
echo 3. Stress Testing (100 clients, 5min) - High load
echo 4. Performance Testing (500 clients, 10min) - Very high load
echo 5. Authentic UT Server Specs (25 clients, 3min) - Real server simulation
echo 6. Default (.env or defaults)
echo.
set /p env_choice="Enter configuration (1-6): "

if "%env_choice%"=="1" (
    echo Starting light testing configuration...
    docker compose --env-file .env.light -f compose.yml up --build --force-recreate
) else if "%env_choice%"=="2" (
    echo Starting normal testing configuration...
    docker compose --env-file .env.normal -f compose.yml up --build --force-recreate
) else if "%env_choice%"=="3" (
    echo Starting stress testing configuration...
    docker compose --env-file .env.stress -f compose.yml up --build --force-recreate
) else if "%env_choice%"=="4" (
    echo Starting performance testing configuration...
    docker compose --env-file .env.performance -f compose.yml up --build --force-recreate
) else if "%env_choice%"=="5" (
    echo Starting authentic UT server specification testing...
    echo Using real server specs for authentic network simulation
    docker compose --env-file .env.ut-specs -f compose.yml up --build --force-recreate
) else if "%env_choice%"=="6" (
    echo Starting with default configuration...
    docker compose -f compose.yml up --build --force-recreate
) else (
    echo Invalid choice, using default configuration...
    docker compose -f compose.yml up --build --force-recreate
)
goto :eof

:end

pause