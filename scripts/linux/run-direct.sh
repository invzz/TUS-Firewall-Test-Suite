#!/bin/bash

# Alternative run script if Docker has issues
# This can be run on any Linux system with nftables installed

echo "=== NFTables Test (Direct Run) Started at $(date) ==="

# Check if running as root (required for nftables)
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root to manage nftables"
    echo "Please run: sudo $0"
    exit 1
fi

# Check if nftables is available
if ! command -v nft &> /dev/null; then
    echo "nftables (nft command) is not installed"
    echo "Please install nftables first"
    exit 1
fi

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "python3 is not installed"
    echo "Please install python3 first"
    exit 1
fi

# Load nftables configuration
echo "Loading nftables configuration..."
if nft -f ../config/nftables.conf; then
    echo "✓ NFTables rules loaded successfully"
else
    echo "✗ Failed to load NFTables rules"
    exit 1
fi

# Run the Python test server
echo "Starting Python test server..."
python3 ../src/server/nftables-test-server.py

echo "=== Test completed at $(date) ==="