#!/usr/bin/env python3

"""
Configuration constants for the NFTables test server.
"""

# TCP ports from nftables configuration
TCP_PORTS = [
    20, 21, 990, 1194, 3467, 6560, 6567, 6671, 8095, 9075, 9825, 
    19998, 19999, 44578, 53691, 53990, 58581, 62500, 48481
]

# UDP ports from nftables configuration  
UDP_PORTS = [
    6962, 6963, 7787, 7797, 9696, 9697, 5555, 5556, 7766, 7767, 
    9090, 9091, 6669, 6670, 6979, 6996, 6997, 8888, 8889, 9669, 
    9670, 5858, 5859, 4848, 4849
]

# Default selected ports for testing (to avoid too many listeners)
DEFAULT_TCP_PORTS = [21, 1194, 6567, 19999]
DEFAULT_UDP_PORTS = [6962, 6963, 9090, 9091, 7787, 19999, 6979]

# Test connectivity ports (mix of allowed and blocked)
TEST_TCP_PORTS = [21, 1194, 6567, 22, 80, 443]
TEST_UDP_PORTS = [6962, 9090, 19999, 53]