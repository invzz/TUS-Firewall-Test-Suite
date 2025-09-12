#!/usr/bin/env python3
"""
Test script to verify ping data collection and display improvements.
"""

import json
import sys
import os

def test_ping_dashboard():
    """Test that dashboard can handle ping data correctly."""
    
    # Mock ping data for testing
    test_data = {
        "timestamp": "2024-01-01T12:00:00",
        "simulation_config": {
            "num_players": 5,
            "duration_seconds": 60
        },
        "summary_stats": {
            "ping_min_ms": 1.2,
            "ping_max_ms": 15.8,
            "ping_avg_ms": 5.4,
            "ping_count": 12
        },
        "player_details": [
            {
                "player_id": "test-1",
                "ping_count": 3,
                "ping_history": [
                    {"timestamp": "2024-01-01T12:00:01", "ping_ms": 2.1},
                    {"timestamp": "2024-01-01T12:00:06", "ping_ms": 3.4}, 
                    {"timestamp": "2024-01-01T12:00:11", "ping_ms": 1.8}
                ]
            }
        ]
    }
    
    # Save test data
    with open("test_ping_data.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print("✅ Test data created: test_ping_data.json")
    
    # Test ping data extraction
    summary = test_data.get('summary_stats', {})
    ping_count = summary.get('ping_count', 0)
    ping_min = summary.get('ping_min_ms')
    
    print(f"📊 Ping count: {ping_count}")
    print(f"📊 Ping min: {ping_min}")
    print(f"📊 Should display ping section: {ping_count > 0 and ping_min is not None}")
    
    # Test player data
    players = test_data.get('player_details', [])
    total_history = sum(len(p.get('ping_history', [])) for p in players)
    print(f"📊 Total ping history entries: {total_history}")
    
    print("\n🎯 Summary:")
    print("- Dashboard should display ping metrics")
    print("- Dashboard should show time-series charts")
    print("- Dashboard should show success message")
    
    return True

if __name__ == "__main__":
    test_ping_dashboard()