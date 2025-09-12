#!/usr/bin/env python3


import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import socket
import threading
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from client.player_stats import PlayerStats
from client.game_client import GameClient


class TestPlayerStats(unittest.TestCase):
    """Test cases for PlayerStats class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player_stats = PlayerStats(player_id=1)
    
    def test_initialization(self):
        """Test PlayerStats initialization."""
        self.assertEqual(self.player_stats.player_id, 1)
        self.assertEqual(self.player_stats.tcp_connections, 0)
        self.assertEqual(self.player_stats.tcp_failed, 0)
        self.assertEqual(self.player_stats.udp_packets_sent, 0)
        self.assertEqual(self.player_stats.udp_responses, 0)
        self.assertEqual(self.player_stats.udp_timeouts, 0)
        self.assertEqual(self.player_stats.total_bytes_sent, 0)
        self.assertEqual(self.player_stats.total_bytes_received, 0)
        self.assertEqual(len(self.player_stats.errors), 0)
        self.assertEqual(len(self.player_stats.ping_times), 0)
    
    def test_record_tcp_connection_success(self):
        """Test simulating successful TCP connection."""
        self.player_stats.tcp_connections += 1
        self.assertEqual(self.player_stats.tcp_connections, 1)
        self.assertEqual(self.player_stats.tcp_failed, 0)
    
    def test_record_tcp_connection_failure(self):
        """Test simulating failed TCP connection."""
        self.player_stats.tcp_failed += 1
        self.assertEqual(self.player_stats.tcp_connections, 0)
        self.assertEqual(self.player_stats.tcp_failed, 1)
    
    def test_record_udp_packet(self):
        """Test simulating UDP packet sent."""
        self.player_stats.udp_packets_sent += 1
        self.assertEqual(self.player_stats.udp_packets_sent, 1)
    
    def test_record_udp_response(self):
        """Test simulating UDP response received."""
        self.player_stats.udp_responses += 1
        self.assertEqual(self.player_stats.udp_responses, 1)
    
    def test_record_udp_timeout(self):
        """Test simulating UDP timeout."""
        self.player_stats.udp_timeouts += 1
        self.assertEqual(self.player_stats.udp_timeouts, 1)
    
    def test_record_bytes_sent(self):
        """Test simulating bytes sent."""
        self.player_stats.total_bytes_sent += 1000
        self.assertEqual(self.player_stats.total_bytes_sent, 1000)
        
        self.player_stats.total_bytes_sent += 500
        self.assertEqual(self.player_stats.total_bytes_sent, 1500)
    
    def test_record_bytes_received(self):
        """Test simulating bytes received."""
        self.player_stats.total_bytes_received += 800
        self.assertEqual(self.player_stats.total_bytes_received, 800)
        
        self.player_stats.total_bytes_received += 200
        self.assertEqual(self.player_stats.total_bytes_received, 1000)
    
    def test_record_error(self):
        """Test simulating errors."""
        self.player_stats.errors.append("Test error 1")
        self.assertEqual(len(self.player_stats.errors), 1)
        
        self.player_stats.errors.append("Test error 2")
        self.assertEqual(len(self.player_stats.errors), 2)
    
    def test_record_ping(self):
        """Test recording ping times."""
        self.player_stats.record_ping(10.5)
        self.assertEqual(len(self.player_stats.ping_times), 1)
        self.assertEqual(self.player_stats.ping_times[0], 10.5)
        
        self.player_stats.record_ping(15.2)
        self.assertEqual(len(self.player_stats.ping_times), 2)
    
    def test_get_stats_dict(self):
        """Test getting statistics as dictionary."""
        # Add some test data
        self.player_stats.tcp_connections += 1
        self.player_stats.tcp_failed += 1
        self.player_stats.udp_packets_sent += 1
        self.player_stats.udp_responses += 1
        self.player_stats.total_bytes_sent += 1000
        self.player_stats.total_bytes_received += 800
        self.player_stats.record_ping(12.5)
        
        stats = self.player_stats.get_stats_dict()
        
        self.assertEqual(stats['player_id'], 1)
        self.assertEqual(stats['tcp_connections'], 1)
        self.assertEqual(stats['tcp_failed'], 1)
        self.assertEqual(stats['udp_packets_sent'], 1)
        self.assertEqual(stats['udp_responses'], 1)
        self.assertEqual(stats['total_bytes_sent'], 1000)
        self.assertEqual(stats['total_bytes_received'], 800)
        self.assertEqual(stats['ping_count'], 1)
        self.assertEqual(stats['ping_avg_ms'], 12.5)


class TestGameClient(unittest.TestCase):
    """Test cases for GameClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server_ip = "test-server"
        self.player_id = 1
        self.connections_per_player = 2
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'UT_UDP_OVERHEAD': '28',
            'UT_TICKRATE': '85',
            'UT_DEFAULT_NETSPEED': '40000',
            'UT_MAX_NETSPEED': '100000'
        })
        self.env_patcher.start()
        
        self.game_client = GameClient(
            player_id=self.player_id,
            server_ip=self.server_ip
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.env_patcher.stop()
    
    def test_initialization(self):
        """Test GameClient initialization."""
        self.assertEqual(self.game_client.server_ip, "test-server")
        self.assertEqual(self.game_client.player_id, 1)
        self.assertIsInstance(self.game_client.stats, PlayerStats)
        self.assertEqual(self.game_client.stats.player_id, 1)
        self.assertFalse(self.game_client.running)
        # Check UT specs were loaded from environment
        self.assertEqual(self.game_client.ut_udp_overhead, 28)
        self.assertEqual(self.game_client.ut_tickrate, 85)
    
    def test_ut_specs_loaded(self):
        """Test that UT specifications are loaded from environment."""
        self.assertEqual(self.game_client.ut_udp_overhead, 28)
        self.assertEqual(self.game_client.ut_tickrate, 85)
        self.assertEqual(self.game_client.ut_default_netspeed, 40000)
        self.assertEqual(self.game_client.ut_max_netspeed, 100000)
    
    def test_calculate_packet_sizes(self):
        """Test packet size calculations."""
        # Test default payload calculation
        expected_default = (40000 // 85) - 28  # (netspeed / tickrate) - udp_overhead
        self.assertEqual(self.game_client.ut_default_payload, expected_default)
        
        # Test max payload calculation
        expected_max = (100000 // 85) - 28
        self.assertEqual(self.game_client.ut_max_payload, expected_max)
        
        # Test tick interval
        expected_interval = 1.0 / 85
        self.assertAlmostEqual(self.game_client.ut_tick_interval, expected_interval, places=6)
        
    def test_game_ports_configuration(self):
        """Test that game ports are properly configured."""
        self.assertIn('ut_servers', self.game_client.game_ports)
        self.assertIn(6962, self.game_client.game_ports['ut_servers'])
        self.assertIn(9696, self.game_client.game_ports['ut_servers'])
        
        # Check TCP ports
        self.assertIn(21, self.game_client.tcp_ports)
        self.assertIn(19999, self.game_client.tcp_ports)
    
    @patch('client.game_client.time.time')
    @patch('socket.socket')
    def test_ping_server_success(self, mock_socket_class, mock_time):
        """Test successful ping to server."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recvfrom.return_value = (b"pong", ('127.0.0.1', 9696))
        
        # Mock time to return consistent values for RTT calculation
        # Called for: message creation, start time, end time, and potentially stats timestamp
        mock_time.side_effect = [1000.0, 1000.0, 1000.01, 1000.01]  # 10ms ping
            
        self.game_client.ping_server(count=1)
            
        # Check that ping was recorded
        self.assertEqual(len(self.game_client.stats.ping_times), 1)
        self.assertAlmostEqual(self.game_client.stats.ping_times[0], 10.0, places=1)
    
    @patch('socket.socket')
    def test_ping_server_failure(self, mock_socket_class):
        """Test ping failure (timeout)."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recvfrom.side_effect = socket.timeout("Timeout")
        
        self.game_client.ping_server(count=1)
        
        # Ping failures still might record some data, so just verify method was called
        mock_socket.sendto.assert_called()
        mock_socket.recvfrom.assert_called()
    
    @patch('socket.socket')
    def test_tcp_connection_test_success(self, mock_socket_class):
        """Test TCP connection testing."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect_ex.return_value = 0  # Success
        
        # Call the actual method that exists
        self.game_client._test_tcp_connection()
        
        # Verify socket operations were called
        mock_socket.connect_ex.assert_called()
        mock_socket.send.assert_called()
        mock_socket.close.assert_called()
    
    @patch('socket.socket')
    def test_tcp_connection_test_failure(self, mock_socket_class):
        """Test TCP connection test failure."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect_ex.return_value = 1  # Connection failed
        
        initial_failed = self.game_client.stats.tcp_failed
        
        # This should handle the error gracefully
        self.game_client._test_tcp_connection()
        
        # Verify failure was recorded
        self.assertEqual(self.game_client.stats.tcp_failed, initial_failed + 1)
        mock_socket.close.assert_called()
    
    @patch('socket.socket')
    def test_send_udp_packet(self, mock_socket_class):
        """Test sending UDP packet."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.sendto.return_value = 100
        
        # Test the actual UDP sending method that exists  
        test_data = "test packet data"  # Method expects string, not bytes
        initial_udp_count = self.game_client.stats.udp_packets_sent
        
        self.game_client._send_udp_packet(6567, test_data)
        
        # Verify socket operations and stats
        mock_socket.sendto.assert_called_with(test_data.encode(), (self.game_client.server_ip, 6567))
        mock_socket.close.assert_called()
        self.assertEqual(self.game_client.stats.udp_packets_sent, initial_udp_count + 1)
    
    def test_running_state(self):
        """Test client running state."""
        # Initially should be False
        self.assertFalse(self.game_client.running)
        
        # Can set running state
        self.game_client.running = True
        self.assertTrue(self.game_client.running)
        
        # Can stop
        self.game_client.running = False
        self.assertFalse(self.game_client.running)
    
    def test_get_stats_dict(self):
        """Test getting client statistics."""
        # Add some test data
        self.game_client.stats.tcp_connections += 1
        self.game_client.stats.udp_packets_sent += 1
        self.game_client.stats.total_bytes_sent += 1000
        
        stats = self.game_client.get_stats_dict()
        
        self.assertEqual(stats['player_id'], 1)
        self.assertEqual(stats['tcp_connections'], 1)
        self.assertEqual(stats['udp_packets_sent'], 1)
        self.assertEqual(stats['total_bytes_sent'], 1000)


if __name__ == '__main__':
    unittest.main()