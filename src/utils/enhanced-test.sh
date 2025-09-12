#!/bin/bash

# Enhanced test script that starts some services to test actual connectivity

LOG_FILE="/shared/nftables-enhanced-test.log"
mkdir -p /shared

echo "=== Enhanced NFTables Test with Services Started at $(date) ===" | tee $LOG_FILE

# Start some services to test actual connectivity
echo "Starting test services..." | tee -a $LOG_FILE

# Start a simple HTTP server on port 21 (FTP port) for testing
python3 -m http.server 21 &
FTP_PID=$!

# Start netcat listeners on some UDP ports
nc -u -l -p 6962 &
NC1_PID=$!
nc -u -l -p 9090 &
NC2_PID=$!

sleep 2

# Load nftables rules
echo "Loading nftables configuration..." | tee -a $LOG_FILE
if nft -f /etc/nftables/nftables.conf 2>&1 | tee -a $LOG_FILE; then
    echo "✓ NFTables rules loaded successfully" | tee -a $LOG_FILE
else
    echo "✗ Failed to load NFTables rules" | tee -a $LOG_FILE
    exit 1
fi

# Test connectivity to running services
echo "Testing connectivity to running services..." | tee -a $LOG_FILE

# Test FTP port (now has HTTP server running)
if nc -z -w3 127.0.0.1 21 2>/dev/null; then
    echo "✓ TCP port 21 (with service) is accessible" | tee -a $LOG_FILE
else
    echo "✗ TCP port 21 (with service) is blocked" | tee -a $LOG_FILE
fi

# Test UDP ports with running listeners
echo "test packet" | nc -u -w1 127.0.0.1 6962 && echo "✓ UDP 6962 received packet" | tee -a $LOG_FILE
echo "test packet" | nc -u -w1 127.0.0.1 9090 && echo "✓ UDP 9090 received packet" | tee -a $LOG_FILE

# Test blocked services
if nc -z -w3 127.0.0.1 80 2>/dev/null; then
    echo "✗ TCP port 80 should be blocked but is accessible" | tee -a $LOG_FILE
else
    echo "✓ TCP port 80 correctly blocked" | tee -a $LOG_FILE
fi

# Test rate limiting with actual flood
echo "Testing UDP rate limiting with packet flood..." | tee -a $LOG_FILE
for i in {1..50}; do
    echo "flood packet $i" | nc -u -w1 127.0.0.1 6962 2>/dev/null &
done
wait
echo "Rate limiting flood test completed" | tee -a $LOG_FILE

# Clean up background processes
kill $FTP_PID $NC1_PID $NC2_PID 2>/dev/null

# Show final rule counters
echo "Final rule counters:" | tee -a $LOG_FILE
nft list ruleset 2>&1 | tee -a $LOG_FILE

echo "=== Enhanced test completed at $(date) ===" | tee -a $LOG_FILE

# Keep container running if requested
if [ "$KEEP_RUNNING" = "true" ]; then
    echo "Container staying alive for manual testing..." | tee -a $LOG_FILE
    tail -f /dev/null
else
    echo "Container will exit after 30 seconds." | tee -a $LOG_FILE
    sleep 30
fi