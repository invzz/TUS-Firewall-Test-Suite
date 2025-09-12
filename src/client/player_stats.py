#!/usr/bin/env python3

import time
from dataclasses import dataclass
from typing import List, Optional, Dict


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
    # Time-series data for graphs
    ping_history: Optional[List[Dict]] = None  # [{timestamp, ping_ms}, ...]
    throughput_history: Optional[List[Dict]] = None  # [{timestamp, packets_per_sec}, ...]
    start_time: Optional[float] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.ping_times is None:
            self.ping_times = []
        if self.ping_history is None:
            self.ping_history = []
        if self.throughput_history is None:
            self.throughput_history = []
        if self.start_time is None:
            self.start_time = time.time()
            
    def record_ping(self, ping_ms: float):
        """Record a ping measurement with timestamp"""
        self.ping_times.append(ping_ms)
        self.ping_history.append({
            'timestamp': time.time() - self.start_time,  # Relative time in seconds
            'ping_ms': ping_ms
        })
    
    def record_throughput_snapshot(self):
        """Record current throughput snapshot"""
        current_time = time.time() - self.start_time
        # Calculate packets per second since last snapshot
        if self.throughput_history:
            last_snapshot = self.throughput_history[-1]
            time_diff = current_time - last_snapshot['timestamp']
            packet_diff = self.udp_packets_sent - last_snapshot.get('total_packets', 0)
            packets_per_sec = packet_diff / time_diff if time_diff > 0 else 0
        else:
            packets_per_sec = self.udp_packets_sent / current_time if current_time > 0 else 0
            
        self.throughput_history.append({
            'timestamp': current_time,
            'packets_per_sec': packets_per_sec,
            'total_packets': self.udp_packets_sent,
            'total_bytes': self.total_bytes_sent
        })

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
            'ping_count': len(valid_pings),
            # Time-series data for dashboard graphs
            'ping_history': self.ping_history,
            'throughput_history': self.throughput_history
        }