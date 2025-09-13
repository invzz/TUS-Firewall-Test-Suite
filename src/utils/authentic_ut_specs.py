#!/usr/bin/env python3
"""
Authentic UT Server Specifications

This module contains specifications and constants for authentic Unreal Tournament server behavior,
used for realistic network simulation and testing.
"""

# Authentic UT Server Network Specifications
UT_UDP_OVERHEAD = 28            # UT protocol UDP overhead (bytes)
UT_TICKRATE = 85               # Server tickrate (Hz)
UT_DEFAULT_NETSPEED = 40000    # Default netspeed (bytes/sec)
UT_MAX_NETSPEED = 100000       # Maximum netspeed (bytes/sec)

# Calculated packet sizes
PACKET_SIZE_DEFAULT = (UT_DEFAULT_NETSPEED // UT_TICKRATE) - UT_UDP_OVERHEAD  # 442 bytes
PACKET_SIZE_MAX = (UT_MAX_NETSPEED // UT_TICKRATE) - UT_UDP_OVERHEAD          # 1147 bytes

def display_ut_specs():
    """Display authentic UT server specifications."""
    print("=== Authentic UT Server Specifications ===")
    print(f"UDP Overhead: {UT_UDP_OVERHEAD} bytes")
    print(f"Server Tickrate: {UT_TICKRATE} Hz")
    print(f"Default Netspeed: {UT_DEFAULT_NETSPEED} bytes/sec")
    print(f"Maximum Netspeed: {UT_MAX_NETSPEED} bytes/sec")
    print(f"Default Packet Size: {PACKET_SIZE_DEFAULT} bytes")
    print(f"Maximum Packet Size: {PACKET_SIZE_MAX} bytes")
    print("==========================================")

if __name__ == "__main__":
    display_ut_specs()