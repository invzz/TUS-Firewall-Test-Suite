#!/usr/bin/env python3
"""
Unit tests for dashboard components of TUS Firewall Test Suite.
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import os
import sys
import json
import tempfile

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import dashboard functions (they're not in a class)
import dashboard.dashboard as dashboard_module


class TestDashboardFunctions(unittest.TestCase):
    """Test cases for dashboard utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_client_data = {
            "simulation_config": {
                "num_players": 5,
                "server_ip": "test-server", 
                "duration_seconds": 60,
                "connections_per_player": 2
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
        
        self.sample_server_data = {
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
    
    def test_load_json_report_success(self):
        """Test successfully loading JSON report."""
        test_data = {"test": "data"}
        json_content = json.dumps(test_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            result = dashboard_module.load_json_report('/fake/path/report.json')
            self.assertEqual(result, test_data)
    
    def test_load_json_report_file_not_found(self):
        """Test loading JSON report when file doesn't exist."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = dashboard_module.load_json_report('/fake/path/missing.json')
            self.assertIsNone(result)
    
    def test_load_json_report_invalid_json(self):
        """Test loading JSON report with invalid JSON content."""
        invalid_json = "{ invalid json content"
        
        with patch('builtins.open', mock_open(read_data=invalid_json)):
            result = dashboard_module.load_json_report('/fake/path/invalid.json')
            self.assertIsNone(result)
    
    
    
    def test_calculate_throughput(self):
        """Test throughput calculation."""
        config = {"duration_seconds": 60}
        
        throughput = dashboard_module.calculate_throughput(6000, config)
        self.assertEqual(throughput, 100.0)  # 6000 bytes / 60 seconds = 100 bytes/s
        
        # Test with zero duration
        # config = {"duration_seconds": 0}
        # throughput = dashboard_module.calculate_throughput(6000, config)
        # self.assertEqual(throughput, 0)
    

class TestDashboardCharts(unittest.TestCase):
    """Test cases for dashboard chart creation functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_px_patcher = patch('dashboard.dashboard.px')
        self.mock_px = self.mock_px_patcher.start()
        self.mock_px.pie.return_value = Mock()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.mock_px_patcher.stop()
    
    def test_create_protocol_chart(self):
        """Test protocol distribution chart creation."""
        result = dashboard_module.create_protocol_chart(100, 200, "Test Protocol Chart")
        
        # Verify px.pie was called with correct parameters
        self.mock_px.pie.assert_called_once()
        call_args = self.mock_px.pie.call_args[1]
        
        self.assertEqual(call_args['values'], [100, 200])
        self.assertEqual(call_args['names'], ['TCP', 'UDP'])
        self.assertEqual(call_args['title'], "Test Protocol Chart")
    
    def test_create_success_chart(self):
        """Test success/failure chart creation."""
        result = dashboard_module.create_success_chart(90, 10, "Test Success Chart")
        
        # Verify px.pie was called
        self.mock_px.pie.assert_called_once()
        call_args = self.mock_px.pie.call_args[1]
        
        self.assertEqual(call_args['values'], [90, 10])
        self.assertEqual(call_args['names'], ['Successful', 'Failed'])
        self.assertEqual(call_args['title'], "Test Success Chart")
    
    def test_create_success_chart_with_custom_colors(self):
        """Test success chart with custom colors."""
        custom_colors = ['#green', '#red']
        result = dashboard_module.create_success_chart(80, 20, "Custom Chart", custom_colors)
        
        call_args = self.mock_px.pie.call_args[1]
        self.assertEqual(call_args['color_discrete_sequence'], custom_colors)


class TestDashboardDataProcessing(unittest.TestCase):
    """Test cases for dashboard data processing functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock streamlit to avoid import errors during testing
        self.st_patcher = patch('dashboard.dashboard.st')
        self.mock_st = self.st_patcher.start()
        self.mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        self.mock_st.subheader = Mock()
        self.mock_st.metric = Mock()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.st_patcher.stop()
    
    def test_display_client_overview_metrics(self):
        """Test displaying client overview metrics."""
        config = {
            "num_players": 5,
            "duration_seconds": 60
        }
        summary = {
            "total_tcp_connections": 10,
            "total_tcp_failed": 1,
            "total_udp_packets": 100,
            "total_udp_responses": 90,
            "total_bytes_sent": 5000,
            "total_bytes_received": 4500
        }
        
        # Should not raise any exceptions
        dashboard_module.display_client_overview_metrics(config, summary)
        
        # Verify streamlit functions were called
        self.mock_st.subheader.assert_called()
        self.mock_st.columns.assert_called_with(4)
        self.mock_st.metric.assert_called()


class TestDashboardIntegration(unittest.TestCase):
    """Integration tests for dashboard components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the RESULTS_DIR constant
        self.results_dir_patcher = patch.object(
            dashboard_module, 'RESULTS_DIR', self.temp_dir
        )
        self.results_dir_patcher.start()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.results_dir_patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_report_loading_and_processing_workflow(self):
        """Test complete workflow of loading and processing reports."""
        # Create sample report files
        client_report = {
            "simulation_config": {"num_players": 3, "duration_seconds": 30},
            "summary_stats": {"total_tcp_connections": 6}
        }
        
        server_report = {
            "total_tcp_connections": 6,
            "test_duration_seconds": 30
        }
        
        client_file = os.path.join(self.temp_dir, 'client-report-20250912-120000.json')
        server_file = os.path.join(self.temp_dir, 'server-report-20250912-120000.json')
        
        with open(client_file, 'w') as f:
            json.dump(client_report, f)
        
        with open(server_file, 'w') as f:
            json.dump(server_report, f)
        
        # Test report discovery
        client_reports, server_reports = dashboard_module.get_available_reports()
        self.assertEqual(len(client_reports), 1)
        self.assertEqual(len(server_reports), 1)
        
        # Test report loading
        loaded_client = dashboard_module.load_json_report(client_reports[0])
        loaded_server = dashboard_module.load_json_report(server_reports[0])
        
        self.assertEqual(loaded_client, client_report)
        self.assertEqual(loaded_server, server_report)
        
        # Test data extraction
        duration = dashboard_module.get_session_duration(loaded_client['simulation_config'])
        self.assertEqual(duration, 30)


if __name__ == '__main__':
    unittest.main()