@echo off
REM Validate Docker files after script reorganization

echo =======================================
echo Docker Configuration Validation
echo =======================================
echo.

echo Validating Docker Compose files...
echo.

echo 1. Testing docker-compose.yml...
docker-compose -f docker\docker-compose.yml config --quiet
if %errorlevel% neq 0 (
    echo ✗ docker-compose.yml has validation errors
    exit /b 1
)
echo ✓ docker-compose.yml is valid

echo.
echo 2. Testing docker-compose-game.yml...
docker-compose -f docker\docker-compose-game.yml config --quiet
if %errorlevel% neq 0 (
    echo ✗ docker-compose-game.yml has validation errors
    exit /b 1
)
echo ✓ docker-compose-game.yml is valid

echo.
echo 3. Testing docker-compose-dashboard.yml...
docker-compose -f docker\docker-compose-dashboard.yml config --quiet
if %errorlevel% neq 0 (
    echo ✗ docker-compose-dashboard.yml has validation errors
    exit /b 1
)
echo ✓ docker-compose-dashboard.yml is valid

echo.
echo Testing Dockerfile contexts...
echo.

echo 4. Checking script file paths...
if exist "scripts\linux\run-auto-tests.sh" (
    echo ✓ scripts/linux/run-auto-tests.sh exists
) else (
    echo ✗ scripts/linux/run-auto-tests.sh missing
    exit /b 1
)

if exist "src\utils\test-nftables.sh" (
    echo ✓ src/utils/test-nftables.sh exists
) else (
    echo ✗ src/utils/test-nftables.sh missing
    exit /b 1
)

if exist "src\utils\enhanced-test.sh" (
    echo ✓ src/utils/enhanced-test.sh exists
) else (
    echo ✗ src/utils/enhanced-test.sh missing
    exit /b 1
)

echo.
echo =======================================
echo All Docker configurations validated! ✓
echo =======================================
echo.
echo Updated paths in:
echo   - Dockerfile.server: scripts/linux/run-auto-tests.sh
echo   - docker-compose.yml: scripts/linux/run-auto-tests.sh  
echo   - launcher.sh: scripts/linux/run-direct.sh
echo   - Documentation files: Updated script paths
echo.
pause