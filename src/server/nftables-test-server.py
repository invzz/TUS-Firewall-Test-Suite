#!/usr/bin/env python3

"""
NFTables Test Server - Main Entry Point

This module provides the main entry point for the NFTables firewall test server.
It coordinates various testing modes including basic tests, game server simulation,
and continuous server mode.
"""

import sys
from .test_server import NFTablesTestServer


def main():
    """Main entry point for the NFTables test server."""
    server = NFTablesTestServer()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'server':
            server.run_server_mode()
        elif sys.argv[1] == 'game':
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 120
            server.run_game_server_mode(duration)
        else:
            print("Usage: python3 nftables-test-server.py [server|game] [duration_seconds]")
            sys.exit(1)
    else:
        server.run_tests()


if __name__ == "__main__":
    main()