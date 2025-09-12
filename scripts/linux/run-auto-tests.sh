#!/bin/bash

# Auto-run script that executes all tests and outputs to shared volume
LOG_FILE="/shared/nftables-test-results.log"
PYTHON_TEST_SERVER="/usr/local/bin/nftables-test-server.py"
KEEP_RUNNING=${KEEP_RUNNING:-false}
mkdir -p /shared

echo "=== NFTables Auto-Test Started at $(date) ===" | tee $LOG_FILE

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "Running Python-based nftables test server..."

# Run the Python test server which handles everything
if [ -f "$PYTHON_TEST_SERVER" ]; then
    if [ "$KEEP_RUNNING" = "true" ]; then
        log "Running in server mode (will keep running)..."
        python3 $PYTHON_TEST_SERVER server 2>&1 | tee -a $LOG_FILE
    elif [ "${GAME_MODE:-false}" = "true" ]; then
        log "Running in game server mode for 2 minutes..."
        python3 $PYTHON_TEST_SERVER game 120 2>&1 | tee -a $LOG_FILE
    else
        log "Running comprehensive tests..."
        python3 $PYTHON_TEST_SERVER 2>&1 | tee -a $LOG_FILE
    fi
else
    log "Python test server not found at $PYTHON_TEST_SERVER"
    exit 1
fi

log "Results saved to $LOG_FILE"

# Keep container running for manual inspection if needed
if [ "$KEEP_RUNNING" = "true" ]; then
    log "Container staying alive for manual testing..."
    tail -f /dev/null
else
    log "Container will exit after 30 seconds. Set KEEP_RUNNING=true to keep it alive."
    sleep 30
fi