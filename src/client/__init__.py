#!/usr/bin/env python3

"""
Client package initialization for the TUS Firewall Test Suite.

This package contains modular components for simulating game client behavior
to test firewall rules and network connectivity.
"""

from .player_stats import PlayerStats
from .game_client import GameClient  
from .client_manager import GameClientManager

__all__ = ['PlayerStats', 'GameClient', 'GameClientManager']