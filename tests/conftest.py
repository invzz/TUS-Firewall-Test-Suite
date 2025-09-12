#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for TUS Firewall Test Suite.
"""

import pytest
import os
import sys
import tempfile
import shutil
import json
from unittest.mock import Mock, patch
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'NUM_CLIENTS': '5',
        'SERVER_IP': 'test-server',
        'DURATION': '60',
        'CONNECTIONS_PER_PLAYER': '2',
        'UT_UDP_OVERHEAD': '28',
        'UT_TICKRATE': '85',
        'UT_DEFAULT_NETSPEED': '40000',
        'UT_MAX_NETSPEED': '100000'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def sample_client_report():
    """Sample client report data for testing."""
    return {
        "simulation_config": {
            "num_players": 5,
            "server_ip": "test-server",
            "duration_seconds": 60,
            "connections_per_player": 2,
            "original_duration_setting": 60
        },
        "summary_stats": {
            "total_tcp_connections": 10,
            "total_tcp_failed": 1,
            "total_udp_packets": 500,
            "total_udp_responses": 450,
            "total_udp_timeouts": 50,
            "total_bytes_sent": 25000,
            "total_bytes_received": 22500,
            "ping_min_ms": 1.2,
            "ping_max_ms": 15.8,
            "ping_avg_ms": 5.4,
            "ping_count": 100
        },
        "player_details": [
            {
                "player_id": 1,
                "tcp_connections": 2,
                "tcp_failed": 0,
                "udp_packets_sent": 100,
                "udp_responses": 90,
                "udp_timeouts": 10,
                "total_bytes_sent": 5000,
                "total_bytes_received": 4500,
                "error_count": 0
            }
        ]
    }

@pytest.fixture
def sample_server_report():
    """Sample server report data for testing."""
    return {
        "total_tcp_connections": 10,
        "total_udp_packets": 500,
        "test_duration_seconds": 60,
        "port_details": [
            {
                "port": 21,
                "protocol": "tcp",
                "connections": 5,
                "packets": 0
            },
            {
                "port": 6567,
                "protocol": "udp",
                "connections": 0,
                "packets": 250
            }
        ],
        "nft_counters": {
            "ftp_counter": 5,
            "game_counter": 250
        }
    }

@pytest.fixture
def mock_socket():
    """Mock socket for network testing."""
    mock_sock = Mock()
    mock_sock.connect.return_value = None
    mock_sock.send.return_value = 100
    mock_sock.recv.return_value = b"test response"
    mock_sock.sendto.return_value = 100
    mock_sock.recvfrom.return_value = (b"test response", ("127.0.0.1", 1234))
    mock_sock.settimeout.return_value = None
    mock_sock.close.return_value = None
    return mock_sock

@pytest.fixture
def results_dir(temp_dir):
    """Create a temporary results directory with sample files."""
    results_path = os.path.join(temp_dir, 'results')
    os.makedirs(results_path, exist_ok=True)
    
    # Create sample report files
    client_report = {
        "simulation_config": {"num_players": 5, "duration_seconds": 60},
        "summary_stats": {"total_tcp_connections": 10}
    }
    
    server_report = {
        "total_tcp_connections": 10,
        "test_duration_seconds": 60
    }
    
    with open(os.path.join(results_path, 'client-report-20250912-120000.json'), 'w') as f:
        json.dump(client_report, f)
        
    with open(os.path.join(results_path, 'server-report-20250912-120000.json'), 'w') as f:
        json.dump(server_report, f)
    
    return results_path