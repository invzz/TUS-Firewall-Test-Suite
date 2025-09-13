@echo off
REM Container Integration Test Runner for TUS Firewall Test Suite (Windows)

setlocal enabledelayedexpansion

set TEST_TYPE=all
set VERBOSE=false
set KEEP_CONTAINERS=false
set INSTALL_DEPS=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto main
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help
if "%~1"=="-v" (
    set VERBOSE=true
    shift
    goto parse_args
)
if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto parse_args
)
if "%~1"=="-k" (
    set KEEP_CONTAINERS=true
    shift
    goto parse_args
)
if "%~1"=="--keep" (
    set KEEP_CONTAINERS=true
    shift
    goto parse_args
)
if "%~1"=="--install" (
    set INSTALL_DEPS=true
    shift
    goto parse_args
)
if "%~1"=="-" (
    echo [ERROR] Unknown option %~1
    goto show_help
)
set TEST_TYPE=%~1
shift
goto parse_args

:show_help
echo Container Integration Test Runner (Windows)
echo.
echo Usage: %~nx0 [OPTIONS] [TEST_TYPE]
echo.
echo TEST_TYPE:
echo     all         Run all container tests (default)
echo     smoke       Run quick smoke tests only
echo     shutdown    Test graceful shutdown system
echo     nftables    Test nftables integration
echo     networking  Test container networking
echo     performance Test performance under load
echo.
echo OPTIONS:
echo     -h, --help       Show this help
echo     -v, --verbose    Verbose output
echo     -k, --keep       Keep containers after test failure (for debugging)
echo     --install        Install test dependencies first
echo.
echo EXAMPLES:
echo     %~nx0                          # Run all tests
echo     %~nx0 smoke                    # Quick validation
echo     %~nx0 shutdown -v              # Test shutdown with verbose output
echo     %~nx0 performance --keep       # Performance test, keep containers on failure
echo     %~nx0 --install all            # Install deps then run all tests
goto end

:main
echo [INFO] TUS Firewall Test Suite - Container Integration Tests
echo [INFO] ==================================================

REM Check if Docker is running
echo [INFO] Checking Docker availability...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running or not accessible
    echo [ERROR] Please start Docker Desktop
    exit /b 1
)
echo [SUCCESS] Docker is available

REM Install dependencies if requested
if "%INSTALL_DEPS%"=="true" (
    echo [INFO] Installing test dependencies...
    pip install -r tests\requirements-test.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed
)

REM Prepare pytest arguments
set PYTEST_ARGS=
if "%VERBOSE%"=="true" (
    set PYTEST_ARGS=!PYTEST_ARGS! -v -s
) else (
    set PYTEST_ARGS=!PYTEST_ARGS! --tb=short
)

if "%KEEP_CONTAINERS%"=="true" (
    set PYTEST_ARGS=!PYTEST_ARGS! --lf
)

REM Run tests based on type
if "%TEST_TYPE%"=="all" (
    echo [INFO] Running all container integration tests...
    pytest tests\integration\test_containers.py -m container !PYTEST_ARGS!
) else if "%TEST_TYPE%"=="smoke" (
    echo [INFO] Running smoke tests...
    pytest tests\integration\test_containers.py::TestContainerIntegration::test_single_server_container_startup !PYTEST_ARGS!
) else if "%TEST_TYPE%"=="shutdown" (
    echo [INFO] Testing graceful shutdown system...
    pytest tests\integration\test_containers.py::TestContainerIntegration::test_graceful_shutdown_system !PYTEST_ARGS!
) else if "%TEST_TYPE%"=="nftables" (
    echo [INFO] Testing nftables integration...
    pytest tests\integration\test_containers.py::TestContainerIntegration::test_nftables_rules_loading_in_container !PYTEST_ARGS!
) else if "%TEST_TYPE%"=="networking" (
    echo [INFO] Testing container networking...
    pytest tests\integration\test_containers.py::TestContainerNetworking !PYTEST_ARGS!
) else if "%TEST_TYPE%"=="performance" (
    echo [INFO] Testing performance under load...
    pytest tests\integration\test_containers.py::TestContainerIntegration::test_performance_under_load !PYTEST_ARGS!
) else (
    echo [ERROR] Unknown test type: %TEST_TYPE%
    goto show_help
)

if errorlevel 1 (
    echo [ERROR] Some tests failed
    if "%KEEP_CONTAINERS%"=="true" (
        echo [WARNING] Containers preserved for debugging
        echo [INFO] Use 'docker ps' to see running containers
        echo [INFO] Use 'docker logs <container_id>' to inspect logs
    )
    goto cleanup_and_exit_error
) else (
    echo [SUCCESS] All tests completed successfully!
    goto cleanup_and_exit_success
)

:cleanup_and_exit_success
if "%KEEP_CONTAINERS%"=="false" (
    echo [INFO] Cleaning up test containers...
    docker container prune -f >nul 2>&1
    docker network prune -f >nul 2>&1
)
exit /b 0

:cleanup_and_exit_error
if "%KEEP_CONTAINERS%"=="false" (
    echo [INFO] Cleaning up test containers...
    docker container prune -f >nul 2>&1
    docker network prune -f >nul 2>&1
)
exit /b 1

:end
exit /b 0