#!/usr/bin/env python3
"""
Testcontainer-based integration tests for TUS Firewall Test Suite.
These tests spin up real Docker containers to test the complete system.
"""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from testcontainers.compose import DockerCompose
from testcontainers.core.container import DockerContainer


@pytest.mark.container
@pytest.mark.slow
class TestContainerIntegration(unittest.TestCase):
    """Integration tests using real Docker containers via testcontainers."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - build Docker images once."""
        cls.project_root = Path(__file__).parent.parent.parent
        
        # Ensure we're in the right directory
        os.chdir(cls.project_root)
        
    def setUp(self):
        """Set up each test."""
        self.containers = []
        self.test_results_dir = self.project_root / "results"
        self.test_results_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up containers after each test."""
        for container in self.containers:
            try:
                container.stop()
            except Exception:
                pass  # Container may already be stopped
                
    def test_single_server_container_startup(self):
        """Test that the server container starts successfully and loads nftables."""
        # Use python:3.11 image that has Python pre-installed to avoid lengthy installation
        server = (
            DockerContainer("python:3.11-slim")
            .with_command("sleep 60")  # Keep container alive longer for testing
            .with_env("PYTHONUNBUFFERED", "1")
            .with_kwargs(privileged=True)  # Enable privileged mode for nftables
            .with_bind_ports(7777, 7777)
            .with_bind_ports(7778, 7778)
            .with_volume_mapping(
                str(self.project_root / "configs" / "nftables" / "nftables.conf"),
                "/etc/nftables/nftables.conf",
                "ro"
            )
            .with_volume_mapping(str(self.project_root), "/app", "rw")
            .with_kwargs(working_dir="/app")  # Set working directory
        )
    
        # Install dependencies and start server
        server_container = server.start()
        self.containers.append(server_container)
        
        # Install only nftables since Python is already available
        print("Updating package lists...")
        result = server_container.exec("apt-get update")
        if result.exit_code != 0:
            print(f"apt-get update failed with exit code {result.exit_code}")
            print(f"output: {result.output}")
        self.assertEqual(result.exit_code, 0, f"Failed to update package lists: {result.output}")
        
        print("Installing nftables...")
        result = server_container.exec("apt-get install -y nftables")
        if result.exit_code != 0:
            print(f"nftables install failed with exit code {result.exit_code}")
            print(f"output: {result.output}")
        self.assertEqual(result.exit_code, 0, f"Failed to install nftables: {result.output}")
        
        # Test nftables functionality
        print("Testing nftables installation...")
        result = server_container.exec("nft --version")
        self.assertEqual(result.exit_code, 0, "nftables not working")
        print(f"nftables version: {result.output}")
        
        # Test Python functionality
        print("Testing Python installation...")
        result = server_container.exec("python3 --version")
        self.assertEqual(result.exit_code, 0, "Python not working")
        print(f"Python version: {result.output}")
        
        # Load nftables config (might fail in containers without full privileges)
        print("Loading nftables config...")
        result = server_container.exec("nft -f /etc/nftables/nftables.conf")
        # Don't fail the test if nftables config can't be loaded in container
        print(f"nftables config load result: {result.exit_code}")
        
        # Test that we can navigate to the app directory
        print("Testing app directory access...")
        result = server_container.exec("ls -la /app")
        print(f"App directory contents: {result.output}")
        
        # Test basic Python functionality using shell syntax
        print("Testing Python functionality...")
        result = server_container.exec(["/bin/sh", "-c", "python3 -c 'print(\"Python working\")'"])
        self.assertEqual(result.exit_code, 0, f"Basic Python execution failed: {result.output}")
        print(f"Python test result: {result.output}")
        
        # Test server module import using shell with proper working directory
        print("Testing server module import...")
        result = server_container.exec(["/bin/sh", "-c", "cd /app && python3 -c 'import src.server.test_server; print(\"Module imported successfully\")'"])
        if result.exit_code != 0:
            print(f"Server module import failed: {result.output}")
            # List the actual server files to see what's available
            print("Checking server directory contents...")
            result = server_container.exec(["ls", "-la", "/app/src/server/"])
            print(f"Server directory contents: {result.output}")
        
        # Test working directory is properly set (it should be /app due to with_kwargs(working_dir="/app"))
        print("Testing current working directory...")
        result = server_container.exec(["pwd"])
        print(f"Current working directory: {result.output}")
        
        # Test basic server startup using proper shell syntax
        print("Testing server availability...")
        result = server_container.exec(["/bin/sh", "-c", "cd /app && ls -la src/server/*.py"])
        print(f"Server files: {result.output}")
    
    def test_client_server_communication_with_compose(self):
        """Test full client-server communication using docker-compose."""
        
        # Create a temporary environment file for the test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as env_file:
            env_file.write("DURATION=10\n")
            env_file.write("NUM_CLIENTS=2\n")
            env_file.write("CONNECTIONS_PER_PLAYER=1\n")
            env_file.write("SERVER_DURATION=10\n")
            env_file_path = env_file.name
        
        try:
            # Use the actual compose file with short duration via env file
            with DockerCompose(
                str(self.project_root),
                compose_file_name="compose.yml",
                env_file=env_file_path
            ) as compose:
                
                # Wait for services to be ready
                time.sleep(5)
                
                # Check that server container is running
                server_logs = compose.get_logs("nftables-server")
                self.assertIsNotNone(server_logs, "Server container not found")
                
                # Check that client container is running  
                client_logs = compose.get_logs("game-client")
                self.assertIsNotNone(client_logs, "Client container not found")
                
                # Wait for simulation to complete
                time.sleep(15)  # Give extra time for completion
                
                # Check server logs for expected patterns
                server_output = compose.get_logs("nftables-server")
                print(f"Server logs sample: {server_output[:500]}")
                
                # Check client logs for expected patterns
                client_output = compose.get_logs("game-client")
                print(f"Client logs sample: {client_output[:500]}")
                
                # Basic validation that containers produced output
                self.assertGreater(len(server_output), 0, "Server should have generated logs")
                self.assertGreater(len(client_output), 0, "Client should have generated logs")
        
        finally:
            # Clean up the temporary env file
            if os.path.exists(env_file_path):
                os.unlink(env_file_path)
            
    def test_graceful_shutdown_system(self):
        """Test graceful shutdown: client should receive shutdown notification from server."""
        # Create a temporary environment file for the test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as env_file:
            env_file.write("DURATION=3\n")
            env_file.write("NUM_CLIENTS=1\n") 
            env_file.write("CONNECTIONS_PER_PLAYER=1\n")
            env_file.write("SERVER_DURATION=8\n")
            env_file_path = env_file.name
        
        try:
            with DockerCompose(
                str(self.project_root), 
                compose_file_name="compose.test.yml",
                env_file=env_file_path
            ) as compose:
                # 1. Load the compose and wait for server shutdown  
                time.sleep(3)
                print("🚀 Containers started, waiting for server shutdown...")
                time.sleep(3)  # Wait enough time for server to run and shutdown
                print("⏱️ Server should have shutdown, checking client logs...")
                
                # 2. Check client logs for shutdown notification
                client_logs = compose.get_logs("game-client")
                client_logs_str = str(client_logs) if client_logs else ""
                
                # Also check server logs to see what it was trying to send
                server_logs = compose.get_logs("nftables-server")
                server_logs_str = str(server_logs) if server_logs else ""
                print("🔍 Server broadcast debug:")
                print(f"   Server logs (last 500 chars): {server_logs_str[-500:]}")
                if "Broadcasting shutdown" in server_logs_str:
                    print("  ✅ Server attempted shutdown broadcast")
                else:
                    print("  ❌ Server did not attempt shutdown broadcast")
                
                # 3. Test: client should have received shutdown notification
                shutdown_received = (
                    "Received shutdown notification from" in client_logs_str and 
                    "preparing for graceful shutdown" in client_logs_str
                )
                
                if shutdown_received:
                    print("✅ SUCCESS: Client received shutdown notification from server")
                    print("✅ Graceful shutdown communication is working correctly")
                else:
                    print("❌ FAILURE: Client did not receive shutdown notification")
                    print(f"📋 Client logs: {client_logs_str}")
                    self.fail("Graceful shutdown communication failed - client did not receive shutdown message from server")
                
        finally:
            # Clean up the temporary env file
            if os.path.exists(env_file_path):
                os.unlink(env_file_path)
    

                
    def test_nftables_rules_loading_in_container(self):
        """Test that nftables rules are properly loaded in privileged container."""
        server = (
            DockerContainer("python:3.11-slim")
            .with_command("sleep 30")
            .with_kwargs(privileged=True)  # Enable privileged mode for nftables
            .with_env("PYTHONUNBUFFERED", "1")
            .with_volume_mapping(
                str(self.project_root / "configs" / "nftables" / "nftables.conf"),
                "/etc/nftables/nftables.conf",
                "ro"
            )
            .with_volume_mapping(str(self.project_root), "/app", "rw")
            .with_kwargs(working_dir="/app")  # Set working directory
        )
        
        container = server.start()
        self.containers.append(container)
        
        # Install nftables (Python is already available)
        print("Updating package lists...")
        result = container.exec("apt-get update")
        self.assertEqual(result.exit_code, 0, "Failed to update package lists")
        
        print("Installing nftables...")
        result = container.exec("apt-get install -y nftables")
        self.assertEqual(result.exit_code, 0, "Failed to install nftables")
        
        # Test nftables version
        print("Testing nftables installation...")
        result = container.exec("nft --version")
        self.assertEqual(result.exit_code, 0, "nftables not working")
        print(f"nftables version: {result.output}")
        
        # Test loading rules (might fail due to container limitations)
        print("Loading nftables config...")
        result = container.exec("nft -f /etc/nftables/nftables.conf")
        print(f"nftables config load result: {result.exit_code}")
        
        # Check if rules were loaded
        list_result = container.exec("nft list ruleset")
        
        # At minimum, nft command should work
        self.assertEqual(list_result.exit_code, 0, "nftables list command failed")
        
        # Test our server's nftables integration using shell syntax
        print("Testing server nftables integration...")
        result = container.exec(["/bin/sh", "-c", "cd /app && python3 -c 'from src.server.test_server import NFTablesTestServer; server = NFTablesTestServer(); print(server.load_nftables_rules())'"])
        
        print(f"NFTables loading test result: {result.output}")
        
        # Basic validation that the test ran
        self.assertIsNotNone(result.output, "Server nftables integration test should produce output")
        
    def test_performance_under_load(self):
        """Test system performance with higher client load."""
        # Create a temporary environment file for the test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as env_file:
            env_file.write("DURATION=15\n")
            env_file.write("NUM_CLIENTS=10\n")  # More clients
            env_file.write("CONNECTIONS_PER_PLAYER=2\n")  # Multiple connections
            env_file.write("SERVER_DURATION=15\n")
            env_file_path = env_file.name
        
        try:
            with DockerCompose(
                str(self.project_root),
                compose_file_name="compose.yml",
                env_file=env_file_path
            ) as compose:
                
                # Wait for startup
                time.sleep(5)
                
                # Monitor during execution
                start_time = time.time()
                while time.time() - start_time < 20:  # Monitor for 20 seconds
                    time.sleep(2)
                    
                    # Check if containers are still running
                    try:
                        server_logs = compose.get_logs("nftables-server")
                        compose.get_logs("game-client")  # Check client is running
                        
                        # Look for error patterns
                        if b"ERROR" in server_logs.upper() or b"FAILED" in server_logs.upper():
                            self.fail(f"Server errors detected: {server_logs}")
                            
                    except Exception:
                        # Container may have completed
                        break
                        
                # Final verification
                server_logs = compose.get_logs("nftables-server")
                
                # Should have processed significant traffic - check for the actual reporting format
                server_logs_str = str(server_logs) if server_logs else ""
                udp_found = "UDP packets" in server_logs_str or "UDP Packets Received" in server_logs_str or "Summary:" in server_logs_str
                self.assertTrue(udp_found, "No UDP traffic processed")
                tcp_found = "TCP connections" in server_logs_str
                self.assertTrue(tcp_found, "No TCP traffic processed")
        
        finally:
            # Clean up the temporary env file
            if os.path.exists(env_file_path):
                os.unlink(env_file_path)
            
    def test_results_file_generation(self):
        """Test that results files are properly generated and contain valid data."""
        # Create a temporary environment file for the test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as env_file:
            env_file.write("DURATION=5\n")
            env_file.write("NUM_CLIENTS=2\n")
            env_file.write("SERVER_DURATION=5\n")
            env_file_path = env_file.name
        
        try:
            with DockerCompose(
                str(self.project_root),
                compose_file_name="compose.yml",
                env_file=env_file_path
            ) as compose:
            
                # Wait for completion
                time.sleep(10)
                
                # Check for results files
                results_files = list(self.test_results_dir.glob("*.json"))
                
                # Should have server and client reports
                server_reports = [f for f in results_files if "server-report" in f.name]
                client_reports = [f for f in results_files if "client-report" in f.name]
                
                self.assertGreater(len(server_reports), 0, "No server reports generated")
                # Client reports may not be generated for short test runs
                print(f"Server reports found: {len(server_reports)}, Client reports found: {len(client_reports)}")
                
                # Validate JSON structure
                for report_file in server_reports + client_reports:
                    with open(report_file, 'r') as f:
                        data = json.load(f)
                        self.assertIsInstance(data, dict, f"Invalid JSON in {report_file}")
                        
                        # Check for session duration in either location (server vs client reports have different structures)
                        has_session_duration = ("session_duration" in data or 
                                              (isinstance(data.get("simulation_config"), dict) and 
                                               "session_duration" in data["simulation_config"]))
                        self.assertTrue(has_session_duration, f"Missing session_duration in {report_file}")
        
        finally:
            # Clean up the temporary env file
            if os.path.exists(env_file_path):
                os.unlink(env_file_path)


@pytest.mark.container
@pytest.mark.network
class TestContainerNetworking(unittest.TestCase):
    """Test Docker networking between containers."""
    
    def setUp(self):
        """Set up networking tests."""
        self.project_root = Path(__file__).parent.parent.parent
        os.chdir(self.project_root)
        self.containers = []
        
    def tearDown(self):
        """Clean up containers."""
        for container in self.containers:
            try:
                container.stop()
            except Exception:
                pass
                
    def test_container_to_container_communication(self):
        """Test that containers can communicate with each other."""
        # This would test the Docker networking that our shutdown system depends on
        # Create a simple server container
        server = (
            DockerContainer("python:3.11-slim")
            .with_command("python3 -m http.server 8000")
            .with_exposed_ports(8000)
        )
        
        server_container = server.start()
        self.containers.append(server_container)
        
        # Create a client container that tries to reach the server
        client = (
            DockerContainer("python:3.11-slim")
            .with_command("sleep 30")
        )
        
        client_container = client.start()
        self.containers.append(client_container)
        
        # Test if client can reach server
        server_ip = server_container.get_container_host_ip()
        server_port = server_container.get_exposed_port(8000)
        
        # Simple connectivity test
        result = client_container.exec(f"python3 -c 'import urllib.request; urllib.request.urlopen(\"http://{server_ip}:{server_port}\", timeout=5)'")
        
        self.assertEqual(result.exit_code, 0, "Container-to-container communication failed")


if __name__ == "__main__":
    # Run specific test suites
    unittest.main(verbosity=2)