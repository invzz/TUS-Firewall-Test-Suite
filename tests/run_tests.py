#!/usr/bin/env python3
"""
Test runner script for TUS Firewall Test Suite.
Runs all tests with proper configuration and reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_test_environment():
    """Setup the test environment."""
    # Add src to Python path
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Set environment variables for testing
    test_env = {
        'PYTHONPATH': str(src_path),
        'TUS_TEST_MODE': '1',
        'NUM_CLIENTS': '3',
        'SERVER_IP': 'test-server',
        'DURATION': '5',
        'CONNECTIONS_PER_PLAYER': '1',
        'UT_UDP_OVERHEAD': '28',
        'UT_TICKRATE': '85',
        'UT_DEFAULT_NETSPEED': '40000',
        'UT_MAX_NETSPEED': '100000'
    }
    
    os.environ.update(test_env)
    print("✅ Test environment configured")


def run_tests(test_type=None, verbose=False, coverage=True):
    """Run tests with specified configuration."""
    project_root = Path(__file__).parent.parent
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test type filter
    if test_type == "unit":
        cmd.extend(["tests/unit/"])
    elif test_type == "integration": 
        cmd.extend(["tests/integration/"])
    elif test_type == "all":
        cmd.extend(["tests/"])
    else:
        cmd.extend(["tests/"])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=html:tests/coverage_html",
            "--cov-report=term-missing"
        ])
    
    # Run from project root
    print(f"🧪 Running tests: {' '.join(cmd)}")
    print(f"📁 Working directory: {project_root}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def check_dependencies():
    """Check if test dependencies are installed."""
    required_packages = ['pytest', 'coverage']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing test dependencies: {', '.join(missing_packages)}")
        print("📦 Install with: pip install -r tests/requirements-test.txt")
        return False
    
    print("✅ All test dependencies available")
    return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run TUS Firewall Test Suite tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true", 
        help="Skip coverage reporting"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check dependencies, don't run tests"
    )
    
    args = parser.parse_args()
    
    print("🔥 TUS Firewall Test Suite - Test Runner")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    if args.check_only:
        print("✅ Dependency check complete")
        return 0
    
    # Setup test environment
    setup_test_environment()
    
    # Run tests
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=not args.no_coverage
    )
    
    if success:
        print("\n✅ All tests passed!")
        print("📊 Coverage report: tests/coverage_html/index.html")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())