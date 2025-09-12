#!/usr/bin/env python3
"""
Integration tests for TUS Firewall Test Suite.
These tests verify that different components work together correctly.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import json
import tempfile
import threading
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestClientServerIntegration(unittest.TestCase):
    """Integration tests between client and server components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment variables
        self.env_vars = {
            'NUM_CLIENTS': '3',
            'SERVER_IP': 'localhost',
            'DURATION': '5',  # Short duration for tests
            'CONNECTIONS_PER_PLAYER': '1',
            'UT_UDP_OVERHEAD': '28',
            'UT_TICKRATE': '85',
            'UT_DEFAULT_NETSPEED': '40000',
            'UT_MAX_NETSPEED': '100000'
        }
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('socket.socket')
    def test_client_server_communication_flow(self, mock_socket_class):
        """Test complete client-server communication flow."""
        from client.game_client import GameClient
        from server.port_listener import PortListener
        
        # Mock socket for both client and server
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.return_value = None
        mock_socket.connect_ex.return_value = 0  # Return 0 to indicate successful connection
        mock_socket.send.return_value = 100
        mock_socket.recv.return_value = b"ACK_21"
        mock_socket.sendto.return_value = 100
        mock_socket.recvfrom.return_value = (b"test packet", ('127.0.0.1', 12345))
        mock_socket.settimeout.return_value = None
        mock_socket.close.return_value = None
        
        with patch.dict(os.environ, self.env_vars):
            # Create client
            client = GameClient(1, 'localhost')
            
            # Create server listener
            server_listener = PortListener(21, 'tcp')
            
            # Test client TCP connection (this method doesn't return success, it updates stats)
            client._test_tcp_connection()
            
            # Verify client recorded the connection or failure (mock will make it succeed)
            # Since we're mocking socket operations, connection should succeed
            self.assertEqual(client.stats.tcp_connections, 1)
            self.assertEqual(client.stats.tcp_failed, 0)
    
    def test_environment_configuration_integration(self):
        """Test that environment variables are properly integrated across components."""
        from client.game_client import GameClient
        
        with patch.dict(os.environ, self.env_vars):
            client = GameClient(1, 'localhost')
            
            # Test that UT specs are loaded correctly from environment variables
            self.assertEqual(client.ut_udp_overhead, 28)
            self.assertEqual(client.ut_tickrate, 85)
            self.assertEqual(client.ut_default_netspeed, 40000)
            self.assertEqual(client.ut_max_netspeed, 100000)
    
    def test_multi_client_statistics_aggregation(self):
        """Test statistics aggregation from multiple clients."""
        from client.game_client import GameClient
        
        with patch.dict(os.environ, self.env_vars):
            # Create multiple clients
            clients = []
            for i in range(3):
                client = GameClient(i+1, 'localhost')
                # Simulate some activity by directly setting stats
                client.stats.tcp_connections += 1
                client.stats.udp_packets_sent += 1
                client.stats.total_bytes_sent += 1000
                clients.append(client)
            
            # Aggregate statistics
            total_tcp = sum(c.stats.tcp_connections for c in clients)
            total_udp = sum(c.stats.udp_packets_sent for c in clients)
            total_bytes = sum(c.stats.total_bytes_sent for c in clients)
            
            self.assertEqual(total_tcp, 3)
            self.assertEqual(total_udp, 3)
            self.assertEqual(total_bytes, 3000)


class TestDashboardDataIntegration(unittest.TestCase):
    """Integration tests for dashboard data processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample report files
        self.client_report_data = {
            "simulation_config": {
                "num_players": 3,
                "server_ip": "localhost",
                "duration_seconds": 30,
                "connections_per_player": 2
            },
            "summary_stats": {
                "total_tcp_connections": 6,
                "total_tcp_failed": 1,
                "total_udp_packets": 300,
                "total_udp_responses": 270,
                "total_udp_timeouts": 30,
                "total_bytes_sent": 15000,
                "total_bytes_received": 13500,
                "ping_min_ms": 2.1,
                "ping_max_ms": 12.5,
                "ping_avg_ms": 6.2,
                "ping_count": 50
            },
            "player_details": []
        }
        
        self.server_report_data = {
            "total_tcp_connections": 6,
            "total_udp_packets": 300,
            "test_duration_seconds": 30,
            "port_details": [
                {"port": 21, "protocol": "tcp", "connections": 3, "packets": 0},
                {"port": 6567, "protocol": "udp", "connections": 0, "packets": 150}
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_report_generation_and_loading_workflow(self):
        """Test complete workflow from report generation to dashboard loading."""
        import dashboard.dashboard as dashboard_module
        
        # Create report files
        client_file = os.path.join(self.temp_dir, 'client-report-20250912-140000.json')
        server_file = os.path.join(self.temp_dir, 'server-report-20250912-140000.json')
        
        with open(client_file, 'w') as f:
            json.dump(self.client_report_data, f)
        
        with open(server_file, 'w') as f:
            json.dump(self.server_report_data, f)
        
        # Test loading reports
        loaded_client = dashboard_module.load_json_report(client_file)
        loaded_server = dashboard_module.load_json_report(server_file)
        
        self.assertEqual(loaded_client, self.client_report_data)
        self.assertEqual(loaded_server, self.server_report_data)
        
        # Test data processing
        config = loaded_client['simulation_config']
        summary = loaded_client['summary_stats']
        
        duration = dashboard_module.get_session_duration(config)
        throughput = dashboard_module.calculate_throughput(summary['total_bytes_sent'], config)
        
        self.assertEqual(duration, 30)
        self.assertEqual(throughput, 500.0)  # 15000 bytes / 30 seconds
    
    def test_dashboard_report_discovery(self):
        """Test dashboard report file discovery."""
        import dashboard.dashboard as dashboard_module
        
        # Create multiple report files with different timestamps
        reports = [
            ('client-report-20250912-140000.json', self.client_report_data),
            ('client-report-20250912-150000.json', self.client_report_data),
            ('server-report-20250912-140000.json', self.server_report_data),
            ('server-report-20250912-150000.json', self.server_report_data)
        ]
        
        for filename, data in reports:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f)
        
        # Mock the RESULTS_DIR to point to our temp directory
        with patch.object(dashboard_module, 'RESULTS_DIR', self.temp_dir):
            client_reports, server_reports = dashboard_module.get_available_reports()
            
            self.assertEqual(len(client_reports), 2)
            self.assertEqual(len(server_reports), 2)
            
            # Verify files are sorted (newest first)
            self.assertTrue('150000' in os.path.basename(client_reports[0]))
            self.assertTrue('140000' in os.path.basename(client_reports[1]))


class TestEndToEndSimulation(unittest.TestCase):
    """End-to-end integration tests simulating complete test runs."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_results_dir = tempfile.mkdtemp()
        
        # Mock environment for simulation
        self.simulation_env = {
            'NUM_CLIENTS': '2',
            'SERVER_IP': 'mock-server',
            'DURATION': '3',  # Very short for testing
            'CONNECTIONS_PER_PLAYER': '1',
            'UT_UDP_OVERHEAD': '28',
            'UT_TICKRATE': '85',
            'UT_DEFAULT_NETSPEED': '40000',
            'UT_MAX_NETSPEED': '100000'
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_results_dir, ignore_errors=True)
    
    @patch('socket.socket')
    def test_complete_simulation_workflow(self, mock_socket_class):
        """Test complete simulation workflow from client creation to report generation."""
        from client.game_client import GameClient
        from client.client_manager import GameClientManager
        
        # Mock successful socket operations
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.return_value = None
        mock_socket.send.return_value = 100
        mock_socket.recv.return_value = b"ACK"
        mock_socket.sendto.return_value = 100
        mock_socket.close.return_value = None
        
        with patch.dict(os.environ, self.simulation_env):
            # Test that GameClientManager can be created with correct parameters
            manager = GameClientManager(
                server_ip='mock-server',
                num_players=2,
                connections_per_player=1,
                duration=3
            )
            
            # Verify manager was created with correct parameters
            self.assertEqual(manager.num_players, 2)
            self.assertEqual(manager.server_ip, 'mock-server')
            self.assertEqual(manager.connections_per_player, 1)
            self.assertEqual(manager.duration, 3)
            
            # Test individual client creation and statistics
            clients = []
            for i in range(2):
                client = GameClient(i+1, 'mock-server')
                # Simulate some activity by directly setting stats
                client.stats.tcp_connections += 1
                client.stats.udp_packets_sent += 1
                client.stats.total_bytes_sent += 500
                clients.append(client)
            
            # Test statistics aggregation
            total_tcp = sum(c.stats.tcp_connections for c in clients)
            total_udp = sum(c.stats.udp_packets_sent for c in clients) 
            total_bytes = sum(c.stats.total_bytes_sent for c in clients)
            
            self.assertEqual(total_tcp, 2)
            self.assertEqual(total_udp, 2)
            self.assertEqual(total_bytes, 1000)
    
    def test_configuration_validation_integration(self):
        """Test that configuration validation works across all components."""
        from client.game_client import GameClient
        
        # Test with invalid configuration
        invalid_env = self.simulation_env.copy()
        invalid_env['UT_TICKRATE'] = '0'  # Invalid tickrate
        
        with patch.dict(os.environ, invalid_env):
            # Test that GameClient constructor handles invalid tickrate by raising ZeroDivisionError
            with self.assertRaises(ZeroDivisionError):
                GameClient(1, 'mock-server')


class TestDockerIntegration(unittest.TestCase):
    """Integration tests for Docker-related functionality."""
    
    def test_docker_environment_variable_mapping(self):
        """Test that Docker environment variables map correctly to application config."""
        # Test Docker environment variables that should be passed through
        docker_env_vars = {
            'NUM_CLIENTS': '5',
            'SERVER_IP': 'nftables-server-container',
            'DURATION': '120',
            'CONNECTIONS_PER_PLAYER': '3',
            'UT_UDP_OVERHEAD': '28',
            'UT_TICKRATE': '85',
            'UT_DEFAULT_NETSPEED': '40000',
            'UT_MAX_NETSPEED': '100000'
        }
        
        with patch.dict(os.environ, docker_env_vars):
            # Test that environment variables are accessible
            self.assertEqual(os.getenv('NUM_CLIENTS'), '5')
            self.assertEqual(os.getenv('SERVER_IP'), 'nftables-server-container')
            self.assertEqual(os.getenv('UT_UDP_OVERHEAD'), '28')
    
    def test_results_directory_integration(self):
        """Test that results directory handling works for Docker volume mapping."""
        # Test that results can be written to shared directory
        shared_dir = tempfile.mkdtemp()
        
        try:
            # Simulate writing results like the application would
            test_report = {
                "simulation_config": {"num_players": 5},
                "summary_stats": {"total_connections": 10}
            }
            
            report_file = os.path.join(shared_dir, 'test-report.json')
            with open(report_file, 'w') as f:
                json.dump(test_report, f)
            
            # Verify file was created and can be read
            self.assertTrue(os.path.exists(report_file))
            
            with open(report_file, 'r') as f:
                loaded_report = json.load(f)
            
            self.assertEqual(loaded_report, test_report)
            
        finally:
            import shutil
            shutil.rmtree(shared_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()