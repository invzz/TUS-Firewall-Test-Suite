#!/usr/bin/env python3

"""
Main NFTables test server implementation.
"""

import os
import socket
import sys
import threading
import time
import subprocess
import json
from datetime import datetime

from .port_listener import PortListener
from .server_config import TCP_PORTS, UDP_PORTS, DEFAULT_TCP_PORTS, DEFAULT_UDP_PORTS, TEST_TCP_PORTS, TEST_UDP_PORTS


class NFTablesTestServer:
    """Main test server class that coordinates listeners and tests."""
    
    def __init__(self):
        self.listeners = []
        self.threads = []
        self.shutdown_broadcast_port = 9999  # Dedicated port for shutdown notifications
        self.connected_clients = set()  # Track connected client IPs
    
    def _add_connected_client(self, client_ip):
        """Callback to track connected client IPs for shutdown targeting."""
        self.connected_clients.add(client_ip)
        print(f"[{datetime.now()}] 📍 Tracking client IP for shutdown: {client_ip}")
        sys.stdout.flush()
        
    def load_nftables_rules(self):
        """Load nftables configuration from file."""
        try:
            # Check if nftables config file exists
            config_file = '/etc/nftables/nftables.conf'
            if not os.path.exists(config_file):
                print(f"[{datetime.now()}] ✗ NFTables config file not found: {config_file}")
                sys.stdout.flush()
                return False
                
            print(f"[{datetime.now()}] 🔧 Loading NFTables rules from {config_file}...")
            sys.stdout.flush()
            
            subprocess.run(['nft', '-f', config_file], 
                           capture_output=True, text=True, check=True)
            print(f"[{datetime.now()}] ✅ NFTables rules loaded successfully")
            sys.stdout.flush()
            return True
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.now()}] ❌ Failed to load NFTables rules:")
            print(f"  Return code: {e.returncode}")
            if e.stderr:
                print(f"  Error output: {e.stderr.strip()}")
            if e.stdout:
                print(f"  Standard output: {e.stdout.strip()}")
            sys.stdout.flush()
            return False
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Unexpected error loading NFTables: {str(e)}")
            sys.stdout.flush()
            return False
            
    def show_nftables_rules(self):
        """Display current nftables ruleset."""
        try:
            print(f"[{datetime.now()}] 📋 Current NFTables ruleset:")
            result = subprocess.run(['nft', 'list', 'ruleset'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                # Show first few lines of the ruleset
                lines = result.stdout.strip().split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"  {line}")
                total_lines = len(result.stdout.strip().split('\n'))
                if total_lines > 10:
                    print(f"  ... (showing first 10 lines of {total_lines} total)")
            else:
                print("  (No rules loaded)")
            sys.stdout.flush()
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.now()}] ❌ Failed to show NFTables rules: {e.stderr}")
            sys.stdout.flush()
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error showing NFTables rules: {str(e)}")
            sys.stdout.flush()
            
    def start_listeners(self):
        """Start port listeners for TCP and UDP."""
        print(f"[{datetime.now()}] 🚀 Server starting - initializing port listeners...")
        sys.stdout.flush()
        
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
                listener = PortListener(port, 'udp', client_callback=self._add_connected_client)
                self.listeners.append(listener)
                thread = threading.Thread(target=listener.start, daemon=True)
                thread.start()
                self.threads.append(thread)
                time.sleep(0.1)
                
        print(f"[{datetime.now()}] ✅ Server STARTED - {len(self.listeners)} port listeners active and ready for connections")
        sys.stdout.flush()
        
    def test_connectivity(self):
        """Test connectivity to various ports."""        
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
                    sock.close()
            except Exception:
                pass
                
    def _test_udp_ports(self):
        """Test UDP port connectivity."""
        for port in TEST_UDP_PORTS:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                sock.sendto(b"test packet", ('127.0.0.1', port))
                try:
                    _, _ = sock.recvfrom(1024)
                except socket.timeout:
                    pass
                sock.close()
            except Exception:
                pass
                
    def test_rate_limiting(self):
        """Test rate limiting by sending rapid UDP packets."""
        port = 6962
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for i in range(50):
                sock.sendto(f"flood packet {i}".encode(), ('127.0.0.1', port))
                if i % 10 == 0:
                    time.sleep(0.1)  # Small delay every 10 packets
            sock.close()
        except Exception:
            pass
            
    def shutdown_server(self):
        """Gracefully shutdown the server."""
        print(f"[{datetime.now()}] 🛑 Server STOPPING - initiating graceful shutdown...")
        sys.stdout.flush()
        self.broadcast_shutdown()
        
        # Stop all listeners
        for listener in self.listeners:
            listener.stop()
            
        print(f"[{datetime.now()}] ❌ Server STOPPED - all services terminated")
        sys.stdout.flush()

    def broadcast_shutdown(self):
        """Send shutdown message to client container."""
        print(f"[{datetime.now()}] 📢 Broadcasting shutdown notification to clients...")
        sys.stdout.flush()
        
        # Use dedicated shutdown ports (7778-7787) for multiple clients
        shutdown_ports = list(range(7778, 7788))  # Cover ports 7778-7787 for different clients
        shutdown_msg = "SERVER_SHUTDOWN"
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Enable broadcast for UDP socket
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Target the game client container directly via Docker networking
            # Use the most common Docker bridge IP pattern for client containers
            client_targets = [
                '172.19.0.3',             # Most common Docker bridge IP for client
                '172.20.0.3',             # Alternative bridge network  
                'game-client-container',  # Docker container name resolution
            ]
            
            print(f"[{datetime.now()}] 🎯 Targeting {len(client_targets)} client IPs: {client_targets}")
            sys.stdout.flush()
            
            # Try to dynamically discover client container IP
            try:
                import subprocess
                result = subprocess.run(['nslookup', 'game-client-container'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and 'Address:' in result.stdout:
                    # Extract IP from nslookup output
                    for line in result.stdout.split('\n'):
                        if 'Address:' in line and '127.0.0.53' not in line:
                            ip = line.split('Address:')[1].strip()
                            if ip and ip != '127.0.0.53':
                                client_targets.insert(0, ip)  # Put discovered IP first
                                print(f"[{datetime.now()}] 🔍 Discovered client IP: {ip}")
                                break
            except Exception:
                pass  # Continue with static targets if discovery fails
            
            notification_sent = False
            for target in client_targets:
                for port in shutdown_ports:
                    try:
                        sock.sendto(shutdown_msg.encode(), (target, port))
                        print(f"[{datetime.now()}] 📤 Shutdown notification sent to {target}:{port}")
                        notification_sent = True
                    except Exception as e:
                        # Don't log every failure - just the first one per target
                        if port == shutdown_ports[0]:
                            print(f"[{datetime.now()}] ⚠️ Failed to notify {target} - {e}")
                    
            sock.close()
            
            if notification_sent:
                print(f"[{datetime.now()}] ✅ Shutdown notification broadcast complete")
            else:
                print(f"[{datetime.now()}] ❌ Failed to send shutdown notifications to any targets")
            sys.stdout.flush()
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Failed to broadcast shutdown: {e}")
            sys.stdout.flush()
    
    def show_statistics(self):
        """Display current server statistics."""
        print(f"\n[{datetime.now()}] Server Statistics:")
        
        total_tcp_connections = 0
        total_udp_clients = 0
        total_udp_packets = 0
        
        for listener in self.listeners:
            print(f"  {listener.get_stats()}")
            if listener.protocol == 'tcp':
                total_tcp_connections += listener.connections
            else:
                total_udp_clients += listener.connections
                total_udp_packets += listener.packets_received
        
        print(f"  Summary: {total_tcp_connections} TCP connections, {total_udp_clients} UDP clients, {total_udp_packets} UDP packets")
        sys.stdout.flush()
            
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
        time.sleep(10)
        
        self.show_statistics()
        
        # Shutdown after tests
        self.shutdown_server()
        
        print(f"\n=== Tests completed at {datetime.now()} ===")
        return True
        
    def run_game_server_mode(self, duration=120):
        """Run as game server for specified duration."""
        print(f"=== NFTables Game Server Mode Started at {datetime.now()} ===")
        print(f"Running for {duration} seconds...")
        
        if not self.load_nftables_rules():
            return False
            
        self.start_listeners()
        time.sleep(2)
        print(f"[{datetime.now()}] Game server ready - accepting connections")
        
        self._run_duration_with_updates(duration)
        
        # Gracefully shutdown server
        self.shutdown_server()
        time.sleep(1)  # Give clients time to receive shutdown message
        
        print(f"[{datetime.now()}] Game server session completed")
        self.generate_server_report(duration)
        
        return True
    
    def _run_duration_with_updates(self, duration):
        """Run for specified duration with periodic status updates."""
        start_time = time.time()
        end_time = start_time + duration
        last_update = start_time
        
        while time.time() < end_time:
            current_time = time.time()
            if current_time - last_update >= 10:  # Update every 10 seconds
                remaining = int(end_time - current_time)
                print(f"[{datetime.now()}] Server running... {remaining}s remaining")
                sys.stdout.flush()
                self.show_statistics()
                last_update = current_time
            time.sleep(1)
        
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
                time.sleep(10)
                self.show_statistics()
                print(f"[{datetime.now()}] Server running...")
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Interrupt received...")
            self.shutdown_server()
            time.sleep(1)  # Give clients time to receive shutdown message
            
        return True