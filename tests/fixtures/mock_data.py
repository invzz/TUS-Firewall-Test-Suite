#!/usr/bin/env python3
"""
Test fixtures and mock data for TUS Firewall Test Suite tests.
Provides common test data, mock objects, and utilities for testing.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta


class MockReportGenerator:
    """Generates realistic mock report data for testing."""
    
    @staticmethod
    def generate_client_report(num_players=5, duration=60, success_rate=0.9):
        """Generate a realistic client report."""
        total_connections = num_players * 3  # 3 connections per player avg
        failed_connections = int(total_connections * (1 - success_rate))
        
        udp_packets_per_player = duration * 10  # 10 packets/sec avg
        total_udp_packets = num_players * udp_packets_per_player
        udp_responses = int(total_udp_packets * success_rate)
        udp_timeouts = total_udp_packets - udp_responses
        
        bytes_per_packet = 470  # Authentic UT packet size
        total_bytes_sent = total_udp_packets * bytes_per_packet
        total_bytes_received = udp_responses * bytes_per_packet
        
        # Generate player details
        player_details = []
        for i in range(1, num_players + 1):
            player_connections = total_connections // num_players
            player_failed = failed_connections // num_players if i <= failed_connections % num_players else failed_connections // num_players
            
            player_udp_packets = udp_packets_per_player
            player_udp_responses = int(player_udp_packets * success_rate)
            player_udp_timeouts = player_udp_packets - player_udp_responses
            
            player_bytes_sent = player_udp_packets * bytes_per_packet
            player_bytes_received = player_udp_responses * bytes_per_packet
            
            player_details.append({
                "player_id": i,
                "tcp_connections": player_connections,
                "tcp_failed": player_failed,
                "udp_packets_sent": player_udp_packets,
                "udp_responses": player_udp_responses,
                "udp_timeouts": player_udp_timeouts,
                "total_bytes_sent": player_bytes_sent,
                "total_bytes_received": player_bytes_received,
                "error_count": player_failed,
                "ping_times": [5.2, 6.1, 4.8, 7.3, 5.9]  # Sample ping times
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "simulation_config": {
                "num_players": num_players,
                "server_ip": "test-server",
                "duration_seconds": duration,
                "connections_per_player": 3,
                "original_duration_setting": duration,
                "ut_specs": {
                    "udp_overhead": 28,
                    "tickrate": 85,
                    "default_netspeed": 40000,
                    "max_netspeed": 100000
                }
            },
            "summary_stats": {
                "total_tcp_connections": total_connections,
                "total_tcp_failed": failed_connections,
                "total_udp_packets": total_udp_packets,
                "total_udp_responses": udp_responses,
                "total_udp_timeouts": udp_timeouts,
                "total_bytes_sent": total_bytes_sent,
                "total_bytes_received": total_bytes_received,
                "ping_min_ms": 2.1,
                "ping_max_ms": 12.5,
                "ping_avg_ms": 5.8,
                "ping_count": num_players * 5,
                "test_duration_actual": duration
            },
            "player_details": player_details
        }
    
    @staticmethod
    def generate_server_report(num_players=5, duration=60, port_activity_level=0.8):
        """Generate a realistic server report."""
        # TCP connections (FTP, game control)
        tcp_connections = num_players * 3
        
        # UDP packets (game data)
        udp_packets_per_player = duration * 10
        total_udp_packets = num_players * udp_packets_per_player
        
        # Port activity details
        port_details = [
            # FTP port
            {
                "port": 21,
                "protocol": "tcp",
                "connections": int(tcp_connections * 0.3),
                "packets": 0
            },
            # Game control ports
            {
                "port": 6962,
                "protocol": "tcp", 
                "connections": int(tcp_connections * 0.4),
                "packets": 0
            },
            {
                "port": 6963,
                "protocol": "tcp",
                "connections": int(tcp_connections * 0.3),
                "packets": 0
            },
            # Main game port
            {
                "port": 6567,
                "protocol": "udp",
                "connections": 0,
                "packets": int(total_udp_packets * 0.8)
            },
            # Secondary game ports
            {
                "port": 9090,
                "protocol": "udp",
                "connections": 0,
                "packets": int(total_udp_packets * 0.1)
            },
            {
                "port": 9091,
                "protocol": "udp",
                "connections": 0,
                "packets": int(total_udp_packets * 0.1)
            }
        ]
        
        # NFTables counters
        nft_counters = {
            "ftp_counter": port_details[0]["connections"],
            "game_counter": sum(p["packets"] for p in port_details if p["protocol"] == "udp"),
            "tcp_counter": sum(p["connections"] for p in port_details if p["protocol"] == "tcp"),
            "udp_counter": sum(p["packets"] for p in port_details if p["protocol"] == "udp")
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tcp_connections": tcp_connections,
            "total_udp_packets": total_udp_packets,
            "test_duration_seconds": duration,
            "server_mode": "game",
            "port_details": port_details,
            "nft_counters": nft_counters,
            "performance_metrics": {
                "connections_per_second": tcp_connections / duration,
                "packets_per_second": total_udp_packets / duration,
                "bytes_processed": total_udp_packets * 470,
                "cpu_usage_percent": 25.5,
                "memory_usage_mb": 128
            }
        }


class TestEnvironments:
    """Provides different environment configurations for testing."""
    
    LIGHT_TESTING = {
        'NUM_CLIENTS': '5',
        'DURATION': '30',
        'CONNECTIONS_PER_PLAYER': '2',
        'UT_UDP_OVERHEAD': '28',
        'UT_TICKRATE': '85',
        'UT_DEFAULT_NETSPEED': '40000',
        'UT_MAX_NETSPEED': '100000',
        'SERVER_IP': 'test-server'
    }
    
    NORMAL_TESTING = {
        'NUM_CLIENTS': '25',
        'DURATION': '180',
        'CONNECTIONS_PER_PLAYER': '3',
        'UT_UDP_OVERHEAD': '28',
        'UT_TICKRATE': '85', 
        'UT_DEFAULT_NETSPEED': '40000',
        'UT_MAX_NETSPEED': '100000',
        'SERVER_IP': 'test-server'
    }
    
    STRESS_TESTING = {
        'NUM_CLIENTS': '100',
        'DURATION': '300',
        'CONNECTIONS_PER_PLAYER': '3',
        'UT_UDP_OVERHEAD': '28',
        'UT_TICKRATE': '85',
        'UT_DEFAULT_NETSPEED': '40000',
        'UT_MAX_NETSPEED': '100000',
        'SERVER_IP': 'test-server'
    }
    
    AUTHENTIC_UT = {
        'NUM_CLIENTS': '25',
        'DURATION': '180',
        'CONNECTIONS_PER_PLAYER': '3',
        'UT_UDP_OVERHEAD': '28',
        'UT_TICKRATE': '85',
        'UT_DEFAULT_NETSPEED': '40000', 
        'UT_MAX_NETSPEED': '100000',
        'SERVER_IP': 'nftables-server-container'
    }


class MockSocketFactory:
    """Factory for creating mock socket objects with realistic behavior."""
    
    @staticmethod
    def create_successful_tcp_socket():
        """Create a mock socket that simulates successful TCP operations."""
        from unittest.mock import Mock
        
        mock_socket = Mock()
        mock_socket.connect.return_value = None
        mock_socket.send.return_value = 100
        mock_socket.recv.return_value = b"ACK_TCP"
        mock_socket.close.return_value = None
        mock_socket.settimeout.return_value = None
        
        return mock_socket
    
    @staticmethod
    def create_successful_udp_socket():
        """Create a mock socket that simulates successful UDP operations."""
        from unittest.mock import Mock
        
        mock_socket = Mock()
        mock_socket.sendto.return_value = 470  # Authentic UT packet size
        mock_socket.recvfrom.return_value = (b"ACK_UDP", ("127.0.0.1", 6567))
        mock_socket.close.return_value = None
        mock_socket.settimeout.return_value = None
        
        return mock_socket
    
    @staticmethod
    def create_failing_socket():
        """Create a mock socket that simulates connection failures."""
        from unittest.mock import Mock
        import socket as socket_module
        
        mock_socket = Mock()
        mock_socket.connect.side_effect = socket_module.error("Connection refused")
        mock_socket.send.side_effect = socket_module.error("Broken pipe")
        mock_socket.sendto.side_effect = socket_module.error("Network unreachable")
        
        return mock_socket
    
    @staticmethod
    def create_timeout_socket():
        """Create a mock socket that simulates timeout scenarios."""
        from unittest.mock import Mock
        import socket as socket_module
        
        mock_socket = Mock()
        mock_socket.connect.side_effect = socket_module.timeout("Connection timeout")
        mock_socket.recv.side_effect = socket_module.timeout("Receive timeout")
        mock_socket.recvfrom.side_effect = socket_module.timeout("Receive timeout")
        
        return mock_socket


class TestFileManager:
    """Manages test files and temporary directories."""
    
    def __init__(self):
        """Initialize test file manager."""
        self.temp_dirs = []
        self.temp_files = []
    
    def create_temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def create_temp_results_dir_with_reports(self, num_client_reports=2, num_server_reports=2):
        """Create a temporary results directory with sample report files."""
        results_dir = self.create_temp_dir()
        
        # Create client reports
        for i in range(num_client_reports):
            timestamp = (datetime.now() - timedelta(hours=i)).strftime('%Y%m%d-%H%M%S')
            filename = f'client-report-{timestamp}.json'
            filepath = os.path.join(results_dir, filename)
            
            report_data = MockReportGenerator.generate_client_report()
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.temp_files.append(filepath)
        
        # Create server reports
        for i in range(num_server_reports):
            timestamp = (datetime.now() - timedelta(hours=i)).strftime('%Y%m%d-%H%M%S')
            filename = f'server-report-{timestamp}.json'
            filepath = os.path.join(results_dir, filename)
            
            report_data = MockReportGenerator.generate_server_report()
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.temp_files.append(filepath)
        
        return results_dir
    
    def cleanup(self):
        """Clean up all created temporary files and directories."""
        import shutil
        
        for temp_dir in self.temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        for temp_file in self.temp_files:
            try:
                os.remove(temp_file)
            except FileNotFoundError:
                pass
        
        self.temp_dirs.clear()
        self.temp_files.clear()


# Common test data constants
SAMPLE_PORTS = {
    'TCP_PORTS': [21, 6962, 6963, 7787],
    'UDP_PORTS': [1194, 6567, 19999, 9090, 9091, 6979]
}

AUTHENTIC_UT_SPECS = {
    'UDP_OVERHEAD': 28,
    'TICKRATE': 85, 
    'DEFAULT_NETSPEED': 40000,
    'MAX_NETSPEED': 100000,
    'PACKET_SIZE_DEFAULT': 442,  # (40000/85) - 28
    'PACKET_SIZE_MAX': 1147      # (100000/85) - 28
}

EXPECTED_PERFORMANCE_RANGES = {
    'LIGHT_LOAD': {
        'tcp_connections': (5, 15),
        'udp_packets': (150, 500),
        'duration': (10, 60)
    },
    'NORMAL_LOAD': {
        'tcp_connections': (50, 100),
        'udp_packets': (1000, 5000),
        'duration': (60, 300)
    },
    'HEAVY_LOAD': {
        'tcp_connections': (200, 500),
        'udp_packets': (10000, 50000),
        'duration': (300, 600)
    }
}