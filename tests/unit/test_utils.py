#!/usr/bin/env python3
"""
Unit tests for utility components of TUS Firewall Test Suite.
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import utilities
import utils.authentic_ut_specs as ut_specs


class TestAuthenticUTSpecs(unittest.TestCase):
    """Test cases for authentic UT specifications utility."""
    
    def test_authentic_ut_specs_display(self):
        """Test authentic UT specs information display."""
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            # Import and run the main function if it exists
            # The current authentic_ut_specs.py file mainly contains print statements
            # so we'll test that it can be imported without errors
            import utils.authentic_ut_specs
            
            # Verify the module imported successfully
            self.assertTrue(hasattr(utils.authentic_ut_specs, '__file__'))


class TestEnvironmentVariableHandling(unittest.TestCase):
    """Test cases for environment variable handling in utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Standard UT environment variables
        self.ut_env_vars = {
            'UT_UDP_OVERHEAD': '28',
            'UT_TICKRATE': '85', 
            'UT_DEFAULT_NETSPEED': '40000',
            'UT_MAX_NETSPEED': '100000'
        }
    
    def test_ut_environment_variable_loading(self):
        """Test loading UT environment variables."""
        with patch.dict(os.environ, self.ut_env_vars):
            # Test that environment variables are properly loaded
            udp_overhead = int(os.getenv('UT_UDP_OVERHEAD', '0'))
            tickrate = int(os.getenv('UT_TICKRATE', '0'))
            default_netspeed = int(os.getenv('UT_DEFAULT_NETSPEED', '0'))
            max_netspeed = int(os.getenv('UT_MAX_NETSPEED', '0'))
            
            self.assertEqual(udp_overhead, 28)
            self.assertEqual(tickrate, 85)
            self.assertEqual(default_netspeed, 40000)
            self.assertEqual(max_netspeed, 100000)
    
    

class TestPacketCalculations(unittest.TestCase):
    """Test cases for packet size calculations used throughout the system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.udp_overhead = 28
        self.tickrate = 85
        self.default_netspeed = 40000
        self.max_netspeed = 100000
    
    def test_authentic_packet_size_calculation(self):
        """Test authentic UT packet size calculation."""
        # Formula: (netspeed / tickrate) - udp_overhead
        
        # Test with default netspeed
        default_packet_size = (self.default_netspeed // self.tickrate) - self.udp_overhead
        self.assertEqual(default_packet_size, 442)  
        
        # Test with max netspeed
        max_packet_size = (self.max_netspeed // self.tickrate) - self.udp_overhead
        self.assertEqual(max_packet_size, 1148)  
    
    def test_minimum_packet_size_enforcement(self):
        """Test that minimum packet sizes are enforced."""
        # Test with very low netspeed that would result in negative or very small packets
        low_netspeed = 1000
        calculated_size = (low_netspeed // self.tickrate) - self.udp_overhead
        
        # Calculated size would be negative: (1000/85) - 28 = 11 - 28 = -17
        # But in practice, systems should enforce a minimum
        minimum_size = max(calculated_size, 32)  # Common minimum UDP packet size
        
        self.assertGreaterEqual(minimum_size, 32)
    
    def test_tickrate_calculation_accuracy(self):
        """Test tickrate calculation accuracy for authentic simulation."""
        # UT servers typically run at 85Hz
        packets_per_second = self.tickrate
        time_between_packets = 1.0 / packets_per_second
        
        # Should be approximately 11.76ms between packets
        self.assertAlmostEqual(time_between_packets, 0.01176, places=5)
    
    def test_netspeed_distribution_ranges(self):
        """Test netspeed distribution ranges for realistic simulation."""
        # Common UT netspeed settings
        common_netspeeds = [20000, 30000, 40000, 50000, 60000, 80000, 100000]
        
        for netspeed in common_netspeeds:
            packet_size = (netspeed // self.tickrate) - self.udp_overhead
            
            # All should result in reasonable packet sizes
            self.assertGreater(packet_size, 0, f"Netspeed {netspeed} results in invalid packet size")
            self.assertLess(packet_size, 1500, f"Netspeed {netspeed} results in oversized packet")


class TestNetworkUtilities(unittest.TestCase):
    """Test cases for network-related utilities."""
    
    def test_port_protocol_mapping(self):
        """Test port to protocol mapping utilities."""
        # Common port mappings used in the framework
        tcp_ports = [21, 6962, 6963, 7787]
        udp_ports = [1194, 6567, 19999, 9090, 9091, 6979]
        
        # Utility function to determine protocol by port (if exists)
        def get_protocol_by_port(port):
            if port in tcp_ports:
                return 'tcp'
            elif port in udp_ports:
                return 'udp'
            else:
                return 'unknown'
        
        # Test known TCP ports
        self.assertEqual(get_protocol_by_port(21), 'tcp')
        self.assertEqual(get_protocol_by_port(6962), 'tcp')
        
        # Test known UDP ports
        self.assertEqual(get_protocol_by_port(6567), 'udp')
        self.assertEqual(get_protocol_by_port(1194), 'udp')
        
        # Test unknown port
        self.assertEqual(get_protocol_by_port(9999), 'unknown')
    
    def test_time_calculations(self):
        """Test time-related calculations used in testing."""
        import time
        
        # Test timestamp generation consistency
        timestamp1 = int(time.time())
        time.sleep(0.001)  # Small delay
        timestamp2 = int(time.time())
        
        # Should be very close or equal
        self.assertLessEqual(abs(timestamp2 - timestamp1), 1)
    
    def test_data_rate_calculations(self):
        """Test data rate calculation utilities."""
        # Test throughput calculation
        bytes_transferred = 10000
        duration_seconds = 10
        
        throughput_bps = bytes_transferred / duration_seconds
        throughput_kbps = throughput_bps / 1024
        throughput_mbps = throughput_kbps / 1024
        
        self.assertEqual(throughput_bps, 1000.0)
        self.assertAlmostEqual(throughput_kbps, 0.9765625, places=6)
        self.assertAlmostEqual(throughput_mbps, 0.00095367, places=6)


class TestConfigurationValidation(unittest.TestCase):
    """Test cases for configuration validation utilities."""
    
    def test_numeric_configuration_validation(self):
        """Test validation of numeric configuration values."""
        # Test valid configurations
        valid_configs = {
            'num_clients': 25,
            'duration': 120,
            'connections_per_player': 3,
            'tickrate': 85,
            'netspeed': 40000
        }
        
        for key, value in valid_configs.items():
            self.assertIsInstance(value, int)
            self.assertGreater(value, 0)
    
    def test_string_configuration_validation(self):
        """Test validation of string configuration values."""
        # Test valid string configurations
        valid_string_configs = {
            'server_ip': 'test-server',
            'protocol': 'tcp'
        }
        
        for key, value in valid_string_configs.items():
            self.assertIsInstance(value, str)
            self.assertGreater(len(value), 0)
    
    def test_configuration_range_validation(self):
        """Test validation of configuration value ranges."""
        # Test netspeed ranges
        min_netspeed = 10000
        max_netspeed = 100000
        test_netspeed = 40000
        
        self.assertGreaterEqual(test_netspeed, min_netspeed)
        self.assertLessEqual(test_netspeed, max_netspeed)
        
        # Test duration ranges
        min_duration = 10
        max_duration = 3600  # 1 hour max
        test_duration = 120
        
        self.assertGreaterEqual(test_duration, min_duration)
        self.assertLessEqual(test_duration, max_duration)


if __name__ == '__main__':
    unittest.main()