#!/bin/bash
# Container Integration Test Runner for TUS Firewall Test Suite

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default settings
TEST_TYPE="all"
VERBOSE=false
KEEP_CONTAINERS=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Container Integration Test Runner

Usage: $0 [OPTIONS] [TEST_TYPE]

TEST_TYPE:
    all         Run all container tests (default)
    smoke       Run quick smoke tests only
    shutdown    Test graceful shutdown system
    nftables    Test nftables integration
    networking  Test container networking
    performance Test performance under load

OPTIONS:
    -h, --help       Show this help
    -v, --verbose    Verbose output
    -k, --keep       Keep containers after test failure (for debugging)
    --install        Install test dependencies first

EXAMPLES:
    $0                          # Run all tests
    $0 smoke                    # Quick validation
    $0 shutdown -v              # Test shutdown with verbose output
    $0 performance --keep       # Performance test, keep containers on failure
    $0 --install all            # Install deps then run all tests

EOF
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker availability..."
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not accessible"
        print_error "Please start Docker Desktop or Docker service"
        exit 1
    fi
    print_success "Docker is available"
}

# Install test dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    pip install -r tests/requirements-test.txt
    print_success "Dependencies installed"
}

# Run specific test type
run_tests() {
    local test_type=$1
    local pytest_args=""
    
    if [ "$VERBOSE" = true ]; then
        pytest_args="$pytest_args -v -s"
    else
        pytest_args="$pytest_args --tb=short"
    fi
    
    if [ "$KEEP_CONTAINERS" = true ]; then
        pytest_args="$pytest_args --lf"
    fi
    
    case $test_type in
        "all")
            print_status "Running all container integration tests..."
            pytest tests/integration/test_containers.py -m container $pytest_args
            ;;
        "smoke")
            print_status "Running smoke tests..."
            pytest tests/integration/test_containers.py::TestContainerIntegration::test_single_server_container_startup $pytest_args
            ;;
        "shutdown")
            print_status "Testing graceful shutdown system..."
            pytest tests/integration/test_containers.py::TestContainerIntegration::test_graceful_shutdown_system $pytest_args
            ;;
        "nftables")
            print_status "Testing nftables integration..."
            pytest tests/integration/test_containers.py::TestContainerIntegration::test_nftables_rules_loading_in_container $pytest_args
            ;;
        "networking")
            print_status "Testing container networking..."
            pytest tests/integration/test_containers.py::TestContainerNetworking $pytest_args
            ;;
        "performance")
            print_status "Testing performance under load..."
            pytest tests/integration/test_containers.py::TestContainerIntegration::test_performance_under_load $pytest_args
            ;;
        *)
            print_error "Unknown test type: $test_type"
            show_help
            exit 1
            ;;
    esac
}

# Cleanup function
cleanup() {
    if [ "$KEEP_CONTAINERS" = false ]; then
        print_status "Cleaning up test containers..."
        docker container prune -f >/dev/null 2>&1 || true
        docker network prune -f >/dev/null 2>&1 || true
    else
        print_warning "Containers kept for debugging (use docker ps to see running containers)"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -k|--keep)
            KEEP_CONTAINERS=true
            shift
            ;;
        --install)
            install_dependencies
            shift
            ;;
        -*)
            print_error "Unknown option $1"
            show_help
            exit 1
            ;;
        *)
            TEST_TYPE=$1
            shift
            ;;
    esac
done

# Main execution
main() {
    print_status "TUS Firewall Test Suite - Container Integration Tests"
    print_status "=================================================="
    
    # Pre-flight checks
    check_docker
    
    # Set up cleanup trap
    trap cleanup EXIT
    
    # Run tests
    if run_tests "$TEST_TYPE"; then
        print_success "All tests completed successfully!"
        exit 0
    else
        print_error "Some tests failed"
        if [ "$KEEP_CONTAINERS" = true ]; then
            print_warning "Containers preserved for debugging"
            print_status "Use 'docker ps' to see running containers"
            print_status "Use 'docker logs <container_id>' to inspect logs"
        fi
        exit 1
    fi
}

# Run main function
main