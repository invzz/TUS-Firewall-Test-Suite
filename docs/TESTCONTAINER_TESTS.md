# Testcontainer Integration Tests

## Overview

The TUS Firewall Test Suite includes comprehensive integration tests using [testcontainers-python](https://testcontainers-python.readthedocs.io/) to test the complete system with real Docker containers.

## Prerequisites

### 1. Docker Installation
- **Docker Desktop** (Windows/macOS) or **Docker Engine** (Linux)
- Docker must be running and accessible
- User must have permissions to run Docker containers

### 2. Python Dependencies
```bash
# Install test dependencies including testcontainers
pip install -r tests/requirements-test.txt
```

### 3. System Requirements
- **Memory**: At least 4GB available for Docker containers
- **Disk Space**: 2GB free space for images and containers
- **Network**: Internet access to pull base images

## Running Container Tests

### Run All Container Tests
```bash
# Run all testcontainer-based integration tests
pytest tests/integration/test_containers.py -v

# Run with specific markers
pytest -m container -v
pytest -m "container and not slow" -v
```

### Run Specific Test Categories

#### 1. Basic Container Functionality
```bash
pytest tests/integration/test_containers.py::TestContainerIntegration::test_single_server_container_startup -v
```

#### 2. Full System Integration
```bash
pytest tests/integration/test_containers.py::TestContainerIntegration::test_client_server_communication_with_compose -v
```

#### 3. Graceful Shutdown Testing
```bash
pytest tests/integration/test_containers.py::TestContainerIntegration::test_graceful_shutdown_system -v
```

#### 4. NFTables Integration
```bash
pytest tests/integration/test_containers.py::TestContainerIntegration::test_nftables_rules_loading_in_container -v
```

#### 5. Performance Testing
```bash
pytest tests/integration/test_containers.py::TestContainerIntegration::test_performance_under_load -v
```

## Test Categories

### 🚀 **TestContainerIntegration**
Tests the complete TUS system using real containers:

- **Server Startup**: Verifies server container starts and loads nftables
- **Client-Server Communication**: Tests full docker-compose orchestration
- **Graceful Shutdown**: Validates shutdown notification system
- **Performance**: Tests system under load with multiple clients
- **Results Generation**: Verifies JSON report creation

### 🌐 **TestContainerNetworking** 
Tests Docker networking fundamentals:

- **Container-to-Container Communication**: Tests network connectivity
- **DNS Resolution**: Tests container name resolution
- **Port Mapping**: Tests exposed port functionality

## What These Tests Validate

### ✅ **Real Environment Testing**
- Actual Docker containers (not mocks)
- Real network communication
- Actual file system operations
- True privilege escalation (nftables)

### ✅ **System Integration** 
- Docker Compose orchestration
- Container interdependencies
- Volume mounting
- Environment variable handling

### ✅ **Network Functionality**
- UDP/TCP port communication
- Container-to-container networking
- Shutdown notification system
- Docker bridge networking

### ✅ **Performance Validation**
- Multiple client connections
- High traffic simulation
- Resource utilization
- Error handling under load

## Test Configuration

### Environment Variables
```bash
# Override default test settings
export DOCKER_HOST=unix:///var/run/docker.sock
export TESTCONTAINERS_RYUK_DISABLED=true  # If cleanup issues
export TESTCONTAINERS_HOST_OVERRIDE=localhost  # For special setups
```

### Pytest Markers
- `@pytest.mark.container` - Requires Docker
- `@pytest.mark.slow` - Takes >30 seconds
- `@pytest.mark.network` - Requires network access

## Troubleshooting

### Common Issues

#### 1. Docker Not Running
```
Error: Cannot connect to the Docker daemon
```
**Solution**: Start Docker Desktop or Docker service

#### 2. Permission Denied
```
Error: Permission denied while trying to connect to Docker
```
**Solution**: Add user to docker group or run with sudo

#### 3. Port Conflicts
```
Error: Port already in use
```
**Solution**: Stop other services or wait for cleanup

#### 4. Timeout Issues
```
Error: Container did not start in time
```
**Solution**: Increase timeout or check system resources

### Debug Mode
```bash
# Run with debug output
pytest tests/integration/test_containers.py -v -s --tb=long

# Keep containers running after test failure for inspection
pytest --lf --tb=short -s tests/integration/test_containers.py
```

### Manual Container Inspection
```bash
# List running test containers
docker ps | grep testcontainers

# Inspect logs from a test container
docker logs <container_id>

# Connect to a running test container
docker exec -it <container_id> /bin/bash
```

## Performance Considerations

### Resource Usage
- Each test may use 200-500MB RAM
- Tests create temporary Docker images
- Network bandwidth for image pulls

### Optimization
```bash
# Run tests in parallel (if safe)
pytest -n auto tests/integration/test_containers.py

# Skip slow tests for quick validation
pytest -m "container and not slow"

# Run specific test only
pytest tests/integration/test_containers.py::TestContainerIntegration::test_graceful_shutdown_system
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Container Integration Tests
  run: |
    docker --version
    pytest -m container --tb=short
  env:
    DOCKER_HOST: unix:///var/run/docker.sock
```

### Local Development
```bash
# Quick smoke test before commits
pytest -m "container and smoke" -v

# Full integration test suite
pytest -m container --tb=short
```

## Expected Test Results

### Success Indicators
- All containers start successfully
- Network communication works
- Graceful shutdown notifications received  
- nftables rules load properly
- Performance meets thresholds

### What Tests Validate About Your Fixes
1. **Graceful Shutdown**: Verifies clients receive shutdown notifications
2. **Real-time Logging**: Confirms unbuffered output works
3. **Docker Networking**: Tests container-to-container communication
4. **nftables Integration**: Validates firewall rule loading

These tests provide confidence that the system works correctly in production Docker environments, not just with mocks!