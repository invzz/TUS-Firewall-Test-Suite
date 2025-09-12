#!/usr/bin/env python3
"""
Analyze ping collection patterns and calculate expected vs actual ping counts.
"""

import json
import os
from datetime import datetime, timedelta

def analyze_ping_collection():
    """Analyze ping collection in latest report."""
    
    # Read latest client report
    results_dir = "results"
    client_files = [f for f in os.listdir(results_dir) if f.startswith("client-report-")]
    if not client_files:
        print("No client report files found")
        return
    
    latest_file = sorted(client_files)[-1]
    filepath = os.path.join(results_dir, latest_file)
    
    print(f"Analyzing: {latest_file}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    config = data.get('simulation_config', {})
    session_duration = config.get('session_duration', 0)
    num_players = config.get('num_players', 0)
    connections_per_player = config.get('connections_per_player', 1)
    total_connections = num_players * connections_per_player
    
    print(f"\n=== SIMULATION CONFIG ===")
    print(f"Session duration: {session_duration:.1f} seconds")
    print(f"Logical players: {num_players}")
    print(f"Connections per player: {connections_per_player}")
    print(f"Total connections: {total_connections}")
    
    # Calculate expected pings
    ping_interval = 5  # seconds
    expected_pings_per_connection = session_duration // ping_interval
    total_expected_pings = expected_pings_per_connection * total_connections
    
    print(f"\n=== EXPECTED PING COLLECTION ===")
    print(f"Ping interval: {ping_interval} seconds")
    print(f"Expected pings per connection: {expected_pings_per_connection:.0f}")
    print(f"Expected total pings: {total_expected_pings:.0f}")
    
    # Analyze actual pings
    summary = data.get('summary_stats', {})
    actual_total_pings = summary.get('ping_count', 0)
    
    players = data.get('player_details', [])
    ping_counts_per_connection = [p.get('ping_count', 0) for p in players]
    
    print(f"\n=== ACTUAL PING COLLECTION ===")
    print(f"Total pings collected: {actual_total_pings}")
    print(f"Collection efficiency: {(actual_total_pings / total_expected_pings * 100):.1f}%")
    
    if ping_counts_per_connection:
        min_pings = min(ping_counts_per_connection)
        max_pings = max(ping_counts_per_connection)
        avg_pings = sum(ping_counts_per_connection) / len(ping_counts_per_connection)
        
        print(f"Pings per connection - Min: {min_pings}, Max: {max_pings}, Avg: {avg_pings:.1f}")
        
        # Check if any connections terminated early
        connections_with_low_pings = [count for count in ping_counts_per_connection if count < expected_pings_per_connection * 0.8]
        
        print(f"Connections with <80% expected pings: {len(connections_with_low_pings)}/{len(ping_counts_per_connection)}")
        
        if connections_with_low_pings:
            print("This suggests some connections terminated early!")
            print("Likely causes:")
            print("- Server availability check too strict")
            print("- Server not responding under high load") 
            print("- Network timeout issues")
    
    # Timeline analysis
    print(f"\n=== IMPROVEMENTS MADE ===")
    print("- Increased server availability timeout: 2s → 5s")
    print("- Reduced check frequency: every 10s → every 15s")  
    print("- Increased failure tolerance: 3 → 5 consecutive failures")
    print("- Added better logging for debugging")

if __name__ == "__main__":
    analyze_ping_collection()