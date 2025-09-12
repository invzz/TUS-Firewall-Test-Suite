#!/usr/bin/env python3
"""
Debug script to check if ping data is being read correctly from JSON reports.
"""

import json
import os

def check_ping_data():
    """Check ping data in the latest client report."""
    results_dir = "results"
    
    # Find the latest client report
    client_files = [f for f in os.listdir(results_dir) if f.startswith("client-report-")]
    if not client_files:
        print("No client report files found")
        return
    
    latest_file = sorted(client_files)[-1]
    filepath = os.path.join(results_dir, latest_file)
    
    print(f"Reading: {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        summary = data.get('summary_stats', {})
        
        print("\n=== PING DATA DEBUG ===")
        print(f"ping_min_ms: {summary.get('ping_min_ms')}")
        print(f"ping_max_ms: {summary.get('ping_max_ms')}")
        print(f"ping_avg_ms: {summary.get('ping_avg_ms')}")
        print(f"ping_count: {summary.get('ping_count', 0)}")
        
        # Check if condition for display would pass
        ping_count = summary.get('ping_count', 0)
        ping_min = summary.get('ping_min_ms')
        
        print(f"\nDisplay condition check:")
        print(f"ping_count > 0: {ping_count > 0}")
        print(f"ping_min is not None: {ping_min is not None}")
        print(f"Should display ping section: {ping_count > 0 and ping_min is not None}")
        
        # Check individual player ping data
        players = data.get('player_details', [])
        players_with_ping = 0
        total_ping_history = 0
        
        for player in players[:5]:  # Check first 5 players
            player_ping_count = player.get('ping_count', 0)
            player_ping_history = player.get('ping_history', [])
            if player_ping_count > 0:
                players_with_ping += 1
                total_ping_history += len(player_ping_history)
                print(f"Player {player.get('player_id')}: {player_ping_count} pings, {len(player_ping_history)} history entries")
        
        print(f"\nPlayer ping summary:")
        print(f"Players with ping data: {players_with_ping}")
        print(f"Total ping history entries (first 5 players): {total_ping_history}")
        
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    check_ping_data()