#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PlayerStats:
    """Statistics tracking for a game client player."""
    player_id: int
    tcp_connections: int = 0
    tcp_failed: int = 0
    udp_packets_sent: int = 0
    udp_responses: int = 0
    udp_timeouts: int = 0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    errors: Optional[List[str]] = None
    ping_times: Optional[List[float]] = None  # Store ping round-trip times in ms

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.ping_times is None:
            self.ping_times = []

    def get_stats_dict(self):
        """Return stats as dictionary for JSON serialization"""
        # Calculate ping stats
        valid_pings = [p for p in self.ping_times if p is not None]
        ping_min = min(valid_pings) if valid_pings else None
        ping_max = max(valid_pings) if valid_pings else None
        ping_avg = sum(valid_pings) / len(valid_pings) if valid_pings else None
        
        return {
            'player_id': self.player_id,
            'tcp_connections': self.tcp_connections,
            'tcp_failed': self.tcp_failed,
            'udp_packets_sent': self.udp_packets_sent,
            'udp_responses': self.udp_responses,
            'udp_timeouts': self.udp_timeouts,
            'total_bytes_sent': self.total_bytes_sent,
            'total_bytes_received': self.total_bytes_received,
            'error_count': len(self.errors),
            'errors': self.errors[:10],  # Limit errors in output
            'ping_min_ms': ping_min,
            'ping_max_ms': ping_max,
            'ping_avg_ms': ping_avg,
            'ping_count': len(valid_pings)
        }