@echo off
REM Quick test for docker-compose validation

echo Testing Docker Compose files...
echo.

echo Validating docker-compose-game.yml...
docker-compose -f docker\docker-compose-game.yml config --quiet
if %errorlevel% neq 0 (
    echo ERROR: docker-compose-game.yml has validation errors
    exit /b 1
)
echo ✓ docker-compose-game.yml is valid

echo.
echo Validating docker-compose.yml...
docker-compose -f docker\docker-compose.yml config --quiet
if %errorlevel% neq 0 (
    echo ERROR: docker-compose.yml has validation errors
    exit /b 1
)
echo ✓ docker-compose.yml is valid

echo.
echo Validating docker-compose-dashboard.yml...
docker-compose -f docker\docker-compose-dashboard.yml config --quiet
if %errorlevel% neq 0 (
    echo ERROR: docker-compose-dashboard.yml has validation errors
    exit /b 1
)
echo ✓ docker-compose-dashboard.yml is valid

echo.
echo ================================
echo All Docker Compose files are valid!
echo ================================
echo.
echo You can now run the launcher safely:
echo   .\launcher.bat
echo.
pause