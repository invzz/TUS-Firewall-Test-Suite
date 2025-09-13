FROM python:3.12-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install basic network tools
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy the entire src directory to maintain package structure
COPY src/ ./src/

# Set Python path to find client modules
ENV PYTHONPATH=/app

# Environment variables for configuration (with defaults)
ENV NUM_CLIENTS=18
ENV SERVER_IP=nftables-test-container
ENV DURATION=120

# Default command - run as module
CMD ["python3", "-m", "src.client.game-client-simulator"]