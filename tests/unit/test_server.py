#!/usr/bin/env python3
"""
Unit tests for server components of TUS Firewall Test Suite.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import socket
import threading
import time
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from server.port_listener import PortListener
from server.server_config import TCP_PORTS, UDP_PORTS, DEFAULT_TCP_PORTS, DEFAULT_UDP_PORTS, TEST_TCP_PORTS, TEST_UDP_PORTS
from server.test_server import NFTablesTestServer


class TestServerConfig(unittest.TestCase):
    """Test cases for server configuration constants."""
    
    def test_tcp_ports_list(self):
        """Test TCP ports configuration."""
        self.assertIsInstance(TCP_PORTS, list)
        self.assertTrue(len(TCP_PORTS) > 0)
        self.assertIn(21, TCP_PORTS)  # FTP port should be included
        self.assertIn(1194, TCP_PORTS)  # OpenVPN port should be included
    
    def test_udp_ports_list(self):
        """Test UDP ports configuration."""
        self.assertIsInstance(UDP_PORTS, list)
        self.assertTrue(len(UDP_PORTS) > 0)
        self.assertIn(6962, UDP_PORTS)  # Unreal port should be included
        self.assertIn(9090, UDP_PORTS)  # Common game port should be included
    
    def test_default_tcp_ports(self):
        """Test default TCP ports are subset of all TCP ports."""
        for port in DEFAULT_TCP_PORTS:
            self.assertIn(port, TCP_PORTS, f"Default TCP port {port} not in TCP_PORTS")
    
    def test_default_udp_ports(self):
        """Test default UDP ports are subset of all UDP ports."""
        for port in DEFAULT_UDP_PORTS:
            self.assertIn(port, UDP_PORTS, f"Default UDP port {port} not in UDP_PORTS")
    
    def test_port_ranges(self):
        """Test that ports are in valid ranges."""
        for port in TCP_PORTS + UDP_PORTS:
            self.assertGreater(port, 0)
            self.assertLess(port, 65536)
    
    def test_test_ports_validity(self):
        """Test that test port configurations are valid."""
        for port in TEST_TCP_PORTS:
            self.assertIn(port, TCP_PORTS + [22, 80, 443])  # Some test ports may not be in main list
        for port in TEST_UDP_PORTS:
            self.assertIn(port, UDP_PORTS + [53])  # DNS port may not be in main list


class TestPortListener(unittest.TestCase):
    """Test cases for PortListener class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.port = 6567
        self.protocol = 'udp'
        
    @patch('socket.socket')
    def test_initialization(self, mock_socket_class):
        """Test PortListener initialization."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        listener = PortListener(self.port, self.protocol)
        
        self.assertEqual(listener.port, self.port)
        self.assertEqual(listener.protocol, self.protocol)
        self.assertEqual(listener.connections, 0)
        self.assertEqual(listener.packets_received, 0)
        self.assertFalse(listener.running)
        
    @patch('socket.socket')
    def test_tcp_listener_setup(self, mock_socket_class):
        """Test TCP listener socket setup."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        PortListener(21, 'tcp')
        
        # Verify socket configuration calls
        mock_socket.setsockopt.assert_called()
        mock_socket.bind.assert_called_with(('0.0.0.0', 21))
        mock_socket.listen.assert_called()
    
    @patch('socket.socket')
    def test_udp_listener_setup(self, mock_socket_class):
        """Test UDP listener socket setup."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        PortListener(6567, 'udp')
        
        # Verify socket configuration calls
        mock_socket.setsockopt.assert_called()
        mock_socket.bind.assert_called_with(('0.0.0.0', 6567))
        # UDP doesn't call listen()
        mock_socket.listen.assert_not_called()
    
    @patch('socket.socket')
    def test_tcp_connection_handling(self, mock_socket_class):
        """Test TCP connection handling."""
        mock_socket = Mock()
        mock_client_socket = Mock()
        
        # Setup socket mocks
        mock_socket_class.return_value = mock_socket
        mock_socket.accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))
        mock_client_socket.recv.return_value = b'test data'
        mock_client_socket.send.return_value = 9
        
        listener = PortListener(21, 'tcp')
        
        # Simulate handling one connection
        listener._handle_tcp_connection(mock_client_socket, ('127.0.0.1', 12345))
        
        # Verify connection was handled
        mock_client_socket.recv.assert_called()
        mock_client_socket.send.assert_called_with(b'ACK_21')
        mock_client_socket.close.assert_called()
    
    @patch('socket.socket')
    def test_udp_packet_handling(self, mock_socket_class):
        """Test UDP packet handling."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recvfrom.return_value = (b'test packet', ('127.0.0.1', 12345))
        mock_socket.sendto.return_value = 8
        
        listener = PortListener(6567, 'udp')
        
        # Simulate handling one packet
        listener._handle_udp_packet()
        
        # Verify packet was handled
        mock_socket.recvfrom.assert_called()
        mock_socket.sendto.assert_called_with(b'ACK_6567', ('127.0.0.1', 12345))
        self.assertEqual(listener.packets_received, 1)
    
    @patch('socket.socket')
    def test_start_stop_listener(self, mock_socket_class):
        """Test starting and stopping listener."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        listener = PortListener(6567, 'udp')
        
        # Test start
        listener.start()
        self.assertTrue(listener.running)
        
        # Test stop
        listener.stop()
        self.assertFalse(listener.running)
        mock_socket.close.assert_called()
    
    @patch('socket.socket')
    def test_get_stats(self, mock_socket_class):
        """Test getting listener statistics."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        listener = PortListener(6567, 'udp')
        listener.packets_received = 10
        
        stats = listener.get_stats()
        
        expected_stats = {
            'port': 6567,
            'protocol': 'udp',
            'connections': 0,
            'packets': 10
        }
        
        self.assertEqual(stats, expected_stats)
    
    @patch('socket.socket')
    def test_error_handling_bind_failure(self, mock_socket_class):
        """Test handling bind failure (port already in use)."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.bind.side_effect = OSError("Address already in use")
        
        listener = PortListener(80, 'tcp')  # Common port that might be in use
        
        # Should handle the error gracefully
        listener.start()
        # Listener should not be running if bind failed
        self.assertFalse(listener.running)
    
    @patch('socket.socket')
    def test_socket_timeout_handling(self, mock_socket_class):
        """Test socket timeout handling."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.accept.side_effect = socket.timeout("Socket timeout")
        
        listener = PortListener(21, 'tcp')
        listener.running = True
        
        # Should handle timeout gracefully and continue
        # This would normally be tested in integration, but we can verify
        # the socket timeout is set
        mock_socket.settimeout.assert_called_with(1.0)


class TestServerIntegration(unittest.TestCase):
    """Integration tests for server components."""
    
    def test_server_config_port_listener_integration(self):
        """Test integration between server config constants and PortListener."""
        # Test that all configured ports can create listeners
        for port in DEFAULT_TCP_PORTS[:2]:  # Test first 2 TCP ports
            with patch('socket.socket'):
                listener = PortListener(port, 'tcp')
                self.assertEqual(listener.port, port)
                self.assertEqual(listener.protocol, 'tcp')
        
        for port in DEFAULT_UDP_PORTS[:2]:  # Test first 2 UDP ports
            with patch('socket.socket'):
                listener = PortListener(port, 'udp')
                self.assertEqual(listener.port, port)
                self.assertEqual(listener.protocol, 'udp')
    
    def test_port_statistics_aggregation(self):
        """Test aggregating statistics from multiple port listeners."""
        with patch('socket.socket'):
            listeners = []
            
            # Create listeners for a few ports
            for port in [21, 6567]:
                protocol = self.config.get_port_protocol(port)
                listener = PortListener(port, protocol)
                
                # Simulate some activity
                if protocol == 'tcp':
                    listener.connections = 5
                else:
                    listener.packets_received = 100
                
                listeners.append(listener)
            
            # Aggregate statistics
            total_tcp_connections = sum(
                l.connections for l in listeners if l.protocol == 'tcp'
            )
            total_udp_packets = sum(
                l.packets_received for l in listeners if l.protocol == 'udp'
            )
            
            self.assertEqual(total_tcp_connections, 5)
            self.assertEqual(total_udp_packets, 100)


if __name__ == '__main__':
    unittest.main()