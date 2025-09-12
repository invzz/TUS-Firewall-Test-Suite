#!/usr/bin/env python3

"""
Main NFTables test server implementation.
"""

import socket
import threading
import time
import subprocess
import json
from datetime import datetime

from port_listener import PortListener
from server_config import TCP_PORTS, UDP_PORTS, DEFAULT_TCP_PORTS, DEFAULT_UDP_PORTS, TEST_TCP_PORTS, TEST_UDP_PORTS


class NFTablesTestServer:
    """Main test server class that coordinates listeners and tests."""
    
    def __init__(self):
        self.listeners = []
        self.threads = []
        
    def load_nftables_rules(self):
        """Load nftables configuration from file."""
        print(f"[{datetime.now()}] Loading nftables configuration...")
        try:
            subprocess.run(['nft', '-f', '/etc/nftables/nftables.conf'], 
                           capture_output=True, text=True, check=True)
            print(f"[{datetime.now()}] ✓ NFTables rules loaded successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.now()}] ✗ Failed to load NFTables rules: {e.stderr}")
            return False
            
    def show_nftables_rules(self):
        """Display current nftables ruleset."""
        print(f"\n[{datetime.now()}] Current NFTables ruleset:")
        try:
            result = subprocess.run(['nft', 'list', 'ruleset'], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error showing rules: {e}")
            
    def start_listeners(self):
        """Start port listeners for TCP and UDP."""
        print(f"[{datetime.now()}] Starting port listeners...")
        
        # Start TCP listeners (limited selection to avoid too many)
        for port in DEFAULT_TCP_PORTS:
            if port in TCP_PORTS:
                listener = PortListener(port, 'tcp')
                self.listeners.append(listener)
                thread = threading.Thread(target=listener.start, daemon=True)
                thread.start()
                self.threads.append(thread)
                time.sleep(0.1)  # Small delay between starts
        
        # Start UDP listeners (selection of game server ports)
        for port in DEFAULT_UDP_PORTS:
            if port in UDP_PORTS:
                listener = PortListener(port, 'udp')
                self.listeners.append(listener)
                thread = threading.Thread(target=listener.start, daemon=True)
                thread.start()
                self.threads.append(thread)
                time.sleep(0.1)
                
        print(f"[{datetime.now()}] Started {len(self.listeners)} port listeners")
        
    def test_connectivity(self):
        """Test connectivity to various ports."""
        print(f"\n[{datetime.now()}] Testing connectivity to running services...")
        
        self._test_tcp_ports()
        self._test_udp_ports()
        
    def _test_tcp_ports(self):
        """Test TCP port connectivity."""
        for port in TEST_TCP_PORTS:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex(('127.0.0.1', port))
                if result == 0:
                    print(f"[{datetime.now()}] ✓ TCP port {port} is accessible")
                    sock.close()
                else:
                    print(f"[{datetime.now()}] ✗ TCP port {port} is blocked/unreachable")
            except Exception as e:
                print(f"[{datetime.now()}] ✗ TCP port {port} test failed: {e}")
                
    def _test_udp_ports(self):
        """Test UDP port connectivity."""
        for port in TEST_UDP_PORTS:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                sock.sendto(b"test packet", ('127.0.0.1', port))
                try:
                    response, _ = sock.recvfrom(1024)
                    print(f"[{datetime.now()}] ✓ UDP port {port} responded: {response.decode()}")
                except socket.timeout:
                    print(f"[{datetime.now()}] ? UDP port {port} sent packet (no response - may be filtered)")
                sock.close()
            except Exception as e:
                print(f"[{datetime.now()}] ✗ UDP port {port} test failed: {e}")
                
    def test_rate_limiting(self):
        """Test rate limiting by sending rapid UDP packets."""
        print(f"\n[{datetime.now()}] Testing rate limiting...")
        
        port = 6962
        packets_sent = 0
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for i in range(50):
                sock.sendto(f"flood packet {i}".encode(), ('127.0.0.1', port))
                packets_sent += 1
                if i % 10 == 0:
                    time.sleep(0.1)  # Small delay every 10 packets
            sock.close()
            print(f"[{datetime.now()}] Sent {packets_sent} rapid UDP packets to test rate limiting")
        except Exception as e:
            print(f"[{datetime.now()}] Rate limiting test error: {e}")
            
    def show_statistics(self):
        """Display current server statistics."""
        print(f"\n[{datetime.now()}] Server Statistics:")
        for listener in self.listeners:
            print(f"  {listener.get_stats()}")
            
    def show_nftables_counters(self):
        """Display nftables rule counters."""
        print(f"\n[{datetime.now()}] NFTables rule counters:")
        try:
            result = subprocess.run(['nft', 'list', 'ruleset'], capture_output=True, text=True)
            # Filter for lines with counters
            lines = result.stdout.split('\n')
            for line in lines:
                if 'counter packets' in line or 'counter bytes' in line:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"Error showing counters: {e}")
            
    def run_tests(self):
        """Run the basic test suite."""
        print(f"=== NFTables Test Server Started at {datetime.now()} ===")
        
        if not self.load_nftables_rules():
            return False
            
        self.show_nftables_rules()
        self.start_listeners()
        
        # Wait for listeners to start
        time.sleep(2)
        
        self.test_connectivity()
        self.test_rate_limiting()
        
        # Wait a bit more for traffic
        print(f"\n[{datetime.now()}] Waiting 10 seconds for additional traffic...")
        time.sleep(10)
        
        self.show_statistics()
        self.show_nftables_counters()
        
        print(f"\n=== Tests completed at {datetime.now()} ===")
        return True
        
    def run_game_server_mode(self, duration=120):
        """Run as game server for specified duration."""
        print(f"=== NFTables Game Server Mode Started at {datetime.now()} ===")
        print(f"Running for {duration} seconds to simulate real game traffic...")
        
        if not self.load_nftables_rules():
            return False
            
        self.start_listeners()
        time.sleep(2)
        print(f"\n[{datetime.now()}] Game server ready - accepting connections for {duration} seconds")
        
        self._run_duration_with_updates(duration)
        
        print(f"\n[{datetime.now()}] Game server session completed")
        self.generate_server_report(duration)
        
        return True
    
    def _run_duration_with_updates(self, duration):
        """Run for specified duration with periodic status updates."""
        start_time = time.time()
        end_time = start_time + duration
        last_update = start_time
        
        while time.time() < end_time:
            current_time = time.time()
            if current_time - last_update >= 30:  # Update every 30 seconds
                remaining = int(end_time - current_time)
                print(f"\n[{datetime.now()}] Server running... {remaining} seconds remaining")
                self.show_statistics()
                last_update = current_time
            time.sleep(5)
        
    def generate_server_report(self, duration):
        """Generate comprehensive server report."""
        print("\n" + "="*60)
        print("SERVER PERFORMANCE REPORT")
        print("="*60)
        
        # Aggregate statistics
        total_tcp_connections = sum(listener.connections for listener in self.listeners if listener.protocol == 'tcp')
        total_udp_packets = sum(listener.packets_received for listener in self.listeners if listener.protocol == 'udp')
        
        self._print_report_summary(duration, total_tcp_connections, total_udp_packets)
        self._print_port_breakdown(duration)
        self._print_performance_metrics(duration, total_tcp_connections, total_udp_packets)
        
        self.show_nftables_counters()
        self._save_server_report_json(duration, total_tcp_connections, total_udp_packets)
    
    def _print_report_summary(self, duration, total_tcp_connections, total_udp_packets):
        """Print report summary section."""
        print(f"Session Duration: {duration} seconds")
        print(f"Server Start Time: {datetime.now()}")
        print()
        
        print("TRAFFIC SUMMARY:")
        print(f"  Total TCP Connections Handled: {total_tcp_connections:,}")
        print(f"  Total UDP Packets Received: {total_udp_packets:,}")
        print()
    
    def _print_port_breakdown(self, duration):
        """Print port-by-port breakdown."""
        print("PORT-BY-PORT BREAKDOWN:")
        for listener in sorted(self.listeners, key=lambda l: (l.protocol, l.port)):
            if listener.protocol == 'tcp':
                rate = listener.connections / duration if duration > 0 else 0
                print(f"  TCP/{listener.port}: {listener.connections:,} connections ({rate:.2f}/sec)")
            else:
                rate = listener.packets_received / duration if duration > 0 else 0
                print(f"  UDP/{listener.port}: {listener.packets_received:,} packets ({rate:.2f}/sec)")
        print()
    
    def _print_performance_metrics(self, duration, total_tcp_connections, total_udp_packets):
        """Print performance metrics."""
        print("PERFORMANCE METRICS:")
        tcp_rate = total_tcp_connections / duration if duration > 0 else 0
        udp_rate = total_udp_packets / duration if duration > 0 else 0
        print(f"  TCP Connections/sec: {tcp_rate:.2f}")
        print(f"  UDP Packets/sec: {udp_rate:.2f}")
        print(f"  Total Transactions: {total_tcp_connections + total_udp_packets:,}")
        print()
        
    def _save_server_report_json(self, duration, tcp_connections, udp_packets):
        """Save server report as JSON."""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'session_duration': duration,
            'total_tcp_connections': tcp_connections,
            'total_udp_packets': udp_packets,
            'port_details': [
                {
                    'port': listener.port,
                    'protocol': listener.protocol,
                    'connections' if listener.protocol == 'tcp' else 'packets': 
                        listener.connections if listener.protocol == 'tcp' else listener.packets_received
                } for listener in self.listeners
            ]
        }
        
        filename = f"/shared/server-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"Server report saved to: {filename}")
        except Exception as e:
            print(f"Failed to save server report: {e}")
        
    def run_server_mode(self):
        """Run in server mode - keep listening indefinitely."""
        print(f"=== NFTables Test Server (Server Mode) Started at {datetime.now()} ===")
        
        if not self.load_nftables_rules():
            return False
            
        self.show_nftables_rules()
        self.start_listeners()
        
        print(f"\n[{datetime.now()}] Server running... Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(30)
                self.show_statistics()
                self.show_nftables_counters()
                print(f"[{datetime.now()}] Server still running...")
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Shutting down server...")
            
        return True