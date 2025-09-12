#!/bin/bash

echo "=== NFTables Game Server + Client Simulation ==="
echo "This will:"
echo "  1. Start NFTables server with your firewall rules"
echo "  2. Simulate 18 game players sending traffic for 2 minutes"
echo "  3. Generate detailed reports from both server and client"
echo ""

# Clean up any existing containers
echo "Cleaning up previous containers..."
docker-compose -f ../configs/docker/docker-compose-game.yml down --remove-orphans 2>/dev/null

# Create results directory
mkdir -p ../results

# Start the simulation
echo "Starting game simulation..."
echo "Server will run for 2 minutes while 18 clients send realistic game traffic"
echo ""

docker-compose -f ../configs/docker/docker-compose-game.yml up --build

echo ""
echo "=== Simulation Complete ==="
echo "Check the 'results' folder for:"
echo "  - server-report-*.json (NFTables server statistics)"
echo "  - client-report-*.json (Client traffic statistics)"
echo "  - nftables-test-results.log (Detailed server logs)"

# Clean up
docker-compose -f ../configs/docker/docker-compose-game.yml down --remove-orphans