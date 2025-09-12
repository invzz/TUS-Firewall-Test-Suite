#!/usr/bin/env python3

"""
Game Client Simulator for NFTables Firewall Testing

This module coordinates the simulation of multiple game clients
to test firewall rules and network connectivity.
"""

import sys
import os
from client_manager import GameClientManager


def main():
    """Main entry point for the game client simulator."""
    # Parse configuration from environment variables and command line arguments
    # Priority: Command line args > Environment variables > Defaults
    
    # Number of clients: ENV var NUM_CLIENTS, command line arg, or default
    default_num_players = int(os.getenv('NUM_CLIENTS', '18'))
    num_players = int(sys.argv[1]) if len(sys.argv) > 1 else default_num_players
    
    # Server IP: ENV var SERVER_IP, command line arg, or default
    default_server_ip = os.getenv('SERVER_IP', 'nftables-test-container')
    server_ip = sys.argv[2] if len(sys.argv) > 2 else default_server_ip
    
    # Duration: ENV var DURATION, command line arg, or default
    default_duration = int(os.getenv('DURATION', '120'))
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else default_duration
    
    print("Game Client Simulator")
    print("Configuration:")
    print(f"  Players: {num_players} (ENV: {os.getenv('NUM_CLIENTS', 'not set')})")
    print(f"  Server: {server_ip} (ENV: {os.getenv('SERVER_IP', 'not set')})")
    print(f"  Duration: {duration}s (ENV: {os.getenv('DURATION', 'not set')})")
    
    manager = GameClientManager(num_players, server_ip, duration)
    manager.run_complete_simulation()


if __name__ == "__main__":
    main()