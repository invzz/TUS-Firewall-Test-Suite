#!/usr/bin/env python3

import socket
import threading
import time
import subprocess
import sys
from datetime import datetime

# Ports from nftables configuration
TCP_PORTS = [20, 21, 990, 1194, 3467, 6560, 6567, 6671, 8095, 9075, 9825, 19998, 19999, 44578, 53691, 53990, 58581, 62500, 48481]
UDP_PORTS = [6962, 6963, 7787, 7797, 9696, 9697, 5555, 5556, 7766, 7767, 9090, 9091, 6669, 6670, 6979, 6996, 6997, 8888, 8889, 9669, 9670, 5858, 5859, 4848, 4849]

class PortListener:
    def __init__(self, port, protocol='tcp'):
        self.port = port
        self.protocol = protocol.lower()
        self.socket = None
        self.running = False
        self.connections = 0
        self.packets_received = 0
        

    def start(self):
        try:
            if self.protocol == 'tcp':
                self._start_tcp()
            elif self.protocol == 'udp':
                self._start_udp()
            else:
                print(f"[{datetime.now()}] Unknown protocol: {self.protocol}")
        except Exception as e:
            print(f"[{datetime.now()}] Failed to start {self.protocol.upper()} server on port {self.port}: {e}")

    def _start_tcp(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(5)
        self.running = True
        print(f"[{datetime.now()}] TCP server listening on port {self.port}")
        while self.running:
            try:
                conn, addr = self.socket.accept()
                self.connections += 1
                print(f"[{datetime.now()}] TCP connection #{self.connections} from {addr} to port {self.port}")
                # Send a simple response
                conn.send(f"Hello from nftables test server port {self.port}\n".encode())
                conn.close()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[{datetime.now()}] TCP port {self.port} error: {e}")
                break

    def _start_udp(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.settimeout(1.0)
        self.running = True
        print(f"[{datetime.now()}] UDP server listening on port {self.port}")
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                self.packets_received += 1
                print(f"[{datetime.now()}] UDP packet #{self.packets_received} from {addr} to port {self.port}: {data.decode()[:50]}...")
                # Send response back
                self.socket.sendto(f"ACK from port {self.port}".encode(), addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[{datetime.now()}] UDP port {self.port} error: {e}")
                break
            
    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
            
    def get_stats(self):
        if self.protocol == 'tcp':
            return f"TCP/{self.port}: {self.connections} connections"
        else:
            return f"UDP/{self.port}: {self.packets_received} packets"

class NFTablesTestServer:
    def __init__(self):
        self.listeners = []
        self.threads = []
        
    def load_nftables_rules(self):
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
        print(f"\n[{datetime.now()}] Current NFTables ruleset:")
        try:
            result = subprocess.run(['nft', 'list', 'ruleset'], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error showing rules: {e}")
            
    def start_listeners(self):
        print(f"[{datetime.now()}] Starting port listeners...")
        
        # Start TCP listeners (limited selection to avoid too many)
        selected_tcp = [21, 1194, 6567, 19999]  # Sample of important ports
        for port in selected_tcp:
            if port in TCP_PORTS:
                listener = PortListener(port, 'tcp')
                self.listeners.append(listener)
                thread = threading.Thread(target=listener.start, daemon=True)
                thread.start()
                self.threads.append(thread)
                time.sleep(0.1)  # Small delay between starts
        
        # Start UDP listeners (selection of game server ports)
        selected_udp = [6962, 6963, 9090, 9091, 7787, 19999, 6979]
        for port in selected_udp:
            if port in UDP_PORTS:
                listener = PortListener(port, 'udp')
                self.listeners.append(listener)
                thread = threading.Thread(target=listener.start, daemon=True)
                thread.start()
                self.threads.append(thread)
                time.sleep(0.1)
                
        print(f"[{datetime.now()}] Started {len(self.listeners)} port listeners")
        
    def test_connectivity(self):
        print(f"\n[{datetime.now()}] Testing connectivity to running services...")
        
        # Test TCP ports
        for port in [21, 1194, 6567, 22, 80, 443]:  # Mix of allowed and blocked
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
                
        # Test UDP ports by sending packets
        for port in [6962, 9090, 19999, 53]:  # Mix of allowed and blocked
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
        print(f"\n[{datetime.now()}] Testing rate limiting...")
        
        # Send rapid UDP packets to test rate limiting
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
        print(f"\n[{datetime.now()}] Server Statistics:")
        for listener in self.listeners:
            print(f"  {listener.get_stats()}")
            
    def show_nftables_counters(self):
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
        print(f"=== NFTables Test Server Started at {datetime.now()} ===")
        
        # Load nftables rules
        if not self.load_nftables_rules():
            return False
            
        # Show current rules
        self.show_nftables_rules()
        
        # Start port listeners
        self.start_listeners()
        
        # Wait for listeners to start
        time.sleep(2)
        
        # Run connectivity tests
        self.test_connectivity()
        
        # Test rate limiting
        self.test_rate_limiting()
        
        # Wait a bit more for traffic
        print(f"\n[{datetime.now()}] Waiting 10 seconds for additional traffic...")
        time.sleep(10)
        
        # Show final statistics
        self.show_statistics()
        self.show_nftables_counters()
        
        print(f"\n=== Tests completed at {datetime.now()} ===")
        return True
        
    def run_game_server_mode(self, duration=120):
        """Run as game server for specified duration (2 minutes default)"""
        print(f"=== NFTables Game Server Mode Started at {datetime.now()} ===")
        print(f"Running for {duration} seconds to simulate real game traffic...")
        
        # Load nftables rules
        if not self.load_nftables_rules():
            return False
            
        # Start port listeners
        self.start_listeners()
        
        # Wait for listeners to start
        time.sleep(2)
        print(f"\n[{datetime.now()}] Game server ready - accepting connections for {duration} seconds")
        
        # Run for the specified duration
        start_time = time.time()
        end_time = start_time + duration
        
        # Show periodic updates
        last_update = start_time
        while time.time() < end_time:
            current_time = time.time()
            if current_time - last_update >= 30:  # Update every 30 seconds
                remaining = int(end_time - current_time)
                print(f"\n[{datetime.now()}] Server running... {remaining} seconds remaining")
                self.show_statistics()
                last_update = current_time
            time.sleep(5)
            
        print(f"\n[{datetime.now()}] Game server session completed")
        
        # Generate final comprehensive report
        self.generate_server_report(duration)
        
        return True
        
    def generate_server_report(self, duration):
        """Generate comprehensive server report"""
        print("\n" + "="*60)
        print("SERVER PERFORMANCE REPORT")
        print("="*60)
        
        # Aggregate statistics
        total_tcp_connections = sum(listener.connections for listener in self.listeners if listener.protocol == 'tcp')
        total_udp_packets = sum(listener.packets_received for listener in self.listeners if listener.protocol == 'udp')
        
        print(f"Session Duration: {duration} seconds")
        print(f"Server Start Time: {datetime.now()}")
        print()
        
        print("TRAFFIC SUMMARY:")
        print(f"  Total TCP Connections Handled: {total_tcp_connections:,}")
        print(f"  Total UDP Packets Received: {total_udp_packets:,}")
        print()
        
        print("PORT-BY-PORT BREAKDOWN:")
        for listener in sorted(self.listeners, key=lambda l: (l.protocol, l.port)):
            if listener.protocol == 'tcp':
                rate = listener.connections / duration if duration > 0 else 0
                print(f"  TCP/{listener.port}: {listener.connections:,} connections ({rate:.2f}/sec)")
            else:
                rate = listener.packets_received / duration if duration > 0 else 0
                print(f"  UDP/{listener.port}: {listener.packets_received:,} packets ({rate:.2f}/sec)")
        print()
        
        print("PERFORMANCE METRICS:")
        tcp_rate = total_tcp_connections / duration if duration > 0 else 0
        udp_rate = total_udp_packets / duration if duration > 0 else 0
        print(f"  TCP Connections/sec: {tcp_rate:.2f}")
        print(f"  UDP Packets/sec: {udp_rate:.2f}")
        print(f"  Total Transactions: {total_tcp_connections + total_udp_packets:,}")
        print()
        
        # Show nftables rule statistics
        self.show_nftables_counters()
        
        # Save report to file
        self._save_server_report_json(duration, total_tcp_connections, total_udp_packets)
        
    def _save_server_report_json(self, duration, tcp_connections, udp_packets):
        """Save server report as JSON"""
        import json
        
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
        """Run in server mode - keep listening indefinitely"""
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

def main():
    server = NFTablesTestServer()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'server':
            server.run_server_mode()
        elif sys.argv[1] == 'game':
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 120
            server.run_game_server_mode(duration)
        else:
            print("Usage: python3 nftables-test-server.py [server|game] [duration_seconds]")
            sys.exit(1)
    else:
        server.run_tests()

if __name__ == "__main__":
    main()