# Environment Variable Configuration

The TUS Firewall Test Suite now supports environment variable configuration for easy Docker deployment.

## Environment Variables

### Client Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NUM_CLIENTS` | `18` | Number of simulated game clients |
| `SERVER_IP` | `nftables-test-container` | Target server hostname/IP |
| `DURATION` | `120` | Simulation duration in seconds |

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_DURATION` | `120` | Server run duration in seconds (for game mode) |

## Usage Examples

### Using Docker Compose with Environment Variables

1. **Create a `.env` file:**
```bash
# Copy the example and modify
cp .env.example .env
```

2. **Edit `.env` file:**
```bash
NUM_CLIENTS=50
DURATION=300
```

3. **Run with docker-compose:**
```bash
docker-compose -f docker/docker-compose-game.yml up
```

### Using Environment Variables Directly

```bash
# Light testing (5 clients, 30 seconds)
NUM_CLIENTS=5 DURATION=30 docker-compose -f docker/docker-compose-game.yml up

# Stress testing (100 clients, 5 minutes)  
NUM_CLIENTS=100 DURATION=300 docker-compose -f docker/docker-compose-game.yml up

# Performance testing (500 clients, 10 minutes)
NUM_CLIENTS=500 DURATION=600 docker-compose -f docker/docker-compose-game.yml up
```

### Command Line Override (still supported)

You can still override via command line arguments:
```bash
# Inside the container
python3 /app/client/game-client-simulator.py 25 server-hostname 180
```

## Priority Order

Configuration is applied in this order (highest to lowest priority):
1. Command line arguments
2. Environment variables  
3. Default values

## Test Scenarios

### Quick Validation
```bash
NUM_CLIENTS=5
DURATION=30
```

### Realistic Game Load
```bash
NUM_CLIENTS=25
DURATION=180  
```

### Stress Testing
```bash
NUM_CLIENTS=100
DURATION=300
```

### Performance Testing
```bash
NUM_CLIENTS=500
DURATION=600
```

## Monitoring Performance

When using high client counts (>100), monitor:
- CPU usage on host system
- Memory consumption 
- Network interface statistics
- Docker container resource usage

Use `docker stats` to monitor container resource consumption during tests.