#!/usr/bin/env python3

import socket
import threading
import time
import random
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List
import sys

@dataclass
class PlayerStats:
    player_id: int
    tcp_connections: int = 0
    tcp_failed: int = 0
    udp_packets_sent: int = 0
    udp_responses: int = 0
    udp_timeouts: int = 0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class GameClient:
    def __init__(self, player_id: int, server_ip: str = "nftables-test-container"):
        self.player_id = player_id
        self.server_ip = server_ip
        self.stats = PlayerStats(player_id)
        self.running = False
        
        # Game server ports from nftables config
        self.game_ports = {
            'ut_servers': [6962, 6963, 9696, 9697, 7787, 7797],
            'private_servers': [9090, 9091, 5555, 5556, 7766, 7767],
            'tournament': [5858, 5859, 4848, 4849],
            'special': [6669, 6670, 6979, 6996, 6997, 8888, 8889, 9669, 9670, 19999, 19998]
        }
        
        # TCP ports to test
        self.tcp_ports = [21, 1194, 6567, 19999]
        
    def log(self, message):
        print(f"[{datetime.now()}] Player {self.player_id}: {message}")
        
    def simulate_game_traffic(self, duration_seconds=120):
        """Simulate realistic game traffic patterns"""
        self.running = True
        self.log("Starting game simulation...")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        while time.time() < end_time and self.running:
            try:
                # Simulate different game activities with different probabilities
                activity = random.choices(
                    ['query', 'join', 'gameplay', 'heartbeat', 'disconnect'],
                    weights=[10, 5, 60, 20, 5]
                )[0]
                
                if activity == 'query':
                    self._send_server_query()
                elif activity == 'join':
                    self._attempt_server_join()
                elif activity == 'gameplay':
                    self._send_gameplay_packets()
                elif activity == 'heartbeat':
                    self._send_heartbeat()
                elif activity == 'disconnect':
                    self._test_tcp_connection()
                    
                # Variable delay between activities (realistic player behavior)
                delay = random.uniform(0.1, 2.0)
                time.sleep(delay)
                
            except Exception as e:
                self.stats.errors.append(f"Activity {activity}: {str(e)}")
                time.sleep(1)
                
        self.running = False
        self.log(f"Simulation completed. Sent {self.stats.udp_packets_sent} UDP packets, {self.stats.tcp_connections} TCP connections")
        
    def _send_server_query(self):
        """Send query packets to discover servers"""
        for port in random.sample(self.game_ports['ut_servers'], 2):
            self._send_udp_packet(port, f"\\status\\\\info\\Player{self.player_id}")
            
    def _attempt_server_join(self):
        """Simulate joining a game server"""
        port = random.choice(self.game_ports['ut_servers'] + self.game_ports['private_servers'])
        join_packet = f"\\connect\\\\name\\Player{self.player_id}\\team\\red\\skin\\default"
        self._send_udp_packet(port, join_packet)
        
    def _send_gameplay_packets(self):
        """Send multiple gameplay packets (movement, shooting, etc.)"""
        port = random.choice(self.game_ports['ut_servers'])
        
        # Send burst of gameplay packets
        for _ in range(random.randint(3, 8)):
            packet_types = ['move', 'fire', 'reload', 'jump', 'pickup']
            packet_type = random.choice(packet_types)
            
            if packet_type == 'move':
                data = f"\\move\\x{random.randint(0,1024)}\\y{random.randint(0,768)}\\angle{random.randint(0,360)}"
            elif packet_type == 'fire':
                data = f"\\fire\\weapon{random.randint(1,8)}\\target{random.randint(0,32)}\\hit{random.choice([0,1])}"
            elif packet_type == 'reload':
                data = f"\\reload\\weapon{random.randint(1,8)}"
            elif packet_type == 'jump':
                data = f"\\jump\\height{random.randint(50,200)}"
            else:
                data = f"\\pickup\\item{random.randint(1,10)}"
                
            self._send_udp_packet(port, data)
            time.sleep(random.uniform(0.05, 0.2))  # Quick succession
            
    def _send_heartbeat(self):
        """Send heartbeat/keepalive packets"""
        port = random.choice([19999, 19998])  # Bot query ports
        self._send_udp_packet(port, f"\\heartbeat\\player{self.player_id}\\time{int(time.time())}")
        
    def _test_tcp_connection(self):
        """Test TCP connections (like FTP, VPN, etc.)"""
        port = random.choice(self.tcp_ports)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            start_time = time.time()
            
            result = sock.connect_ex((self.server_ip, port))
            if result == 0:
                self.stats.tcp_connections += 1
                # Send some data
                data = f"Player{self.player_id} TCP test to port {port}".encode()
                sock.send(data)
                self.stats.total_bytes_sent += len(data)
                
                # Try to receive response
                try:
                    response = sock.recv(1024)
                    self.stats.total_bytes_received += len(response)
                except:
                    pass
            else:
                self.stats.tcp_failed += 1
                
            sock.close()
            
        except Exception as e:
            self.stats.tcp_failed += 1
            self.stats.errors.append(f"TCP {port}: {str(e)}")
            
    def _send_udp_packet(self, port, data):
        """Send a UDP packet and try to get response"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1.0)
            
            packet_data = data.encode()
            sock.sendto(packet_data, (self.server_ip, port))
            self.stats.udp_packets_sent += 1
            self.stats.total_bytes_sent += len(packet_data)
            
            try:
                response, addr = sock.recvfrom(1024)
                self.stats.udp_responses += 1
                self.stats.total_bytes_received += len(response)
            except socket.timeout:
                self.stats.udp_timeouts += 1
                
            sock.close()
            
        except Exception as e:
            self.stats.errors.append(f"UDP {port}: {str(e)}")
            
    def get_stats_dict(self):
        """Return stats as dictionary for JSON serialization"""
        return {
            'player_id': self.stats.player_id,
            'tcp_connections': self.stats.tcp_connections,
            'tcp_failed': self.stats.tcp_failed,
            'udp_packets_sent': self.stats.udp_packets_sent,
            'udp_responses': self.stats.udp_responses,
            'udp_timeouts': self.stats.udp_timeouts,
            'total_bytes_sent': self.stats.total_bytes_sent,
            'total_bytes_received': self.stats.total_bytes_received,
            'error_count': len(self.stats.errors),
            'errors': self.stats.errors[:10]  # Limit errors in output
        }

class GameClientManager:
    def __init__(self, num_players=18, server_ip="nftables-test-container", duration=120):
        self.num_players = num_players
        self.server_ip = server_ip
        self.duration = duration
        self.clients = []
        self.threads = []
        
    def start_simulation(self):
        print(f"=== Starting {self.num_players} Player Simulation at {datetime.now()} ===")
        print(f"Target Server: {self.server_ip}")
        print(f"Duration: {self.duration} seconds")
        
        # Create and start client threads
        for i in range(1, self.num_players + 1):
            client = GameClient(i, self.server_ip)
            self.clients.append(client)
            
            thread = threading.Thread(target=client.simulate_game_traffic, args=(self.duration,))
            thread.daemon = True
            self.threads.append(thread)
            thread.start()
            
            # Stagger player starts slightly
            time.sleep(random.uniform(0.1, 0.5))
            
        print(f"All {self.num_players} players started")
        
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()
            
        print(f"All players finished at {datetime.now()}")
        
    def generate_report(self):
        """Generate comprehensive client-side report"""
        print("\n" + "="*60)
        print("CLIENT SIMULATION REPORT")
        print("="*60)
        
        # Aggregate statistics
        total_stats = {
            'total_players': len(self.clients),
            'total_tcp_connections': sum(c.stats.tcp_connections for c in self.clients),
            'total_tcp_failed': sum(c.stats.tcp_failed for c in self.clients),
            'total_udp_packets': sum(c.stats.udp_packets_sent for c in self.clients),
            'total_udp_responses': sum(c.stats.udp_responses for c in self.clients),
            'total_udp_timeouts': sum(c.stats.udp_timeouts for c in self.clients),
            'total_bytes_sent': sum(c.stats.total_bytes_sent for c in self.clients),
            'total_bytes_received': sum(c.stats.total_bytes_received for c in self.clients),
            'total_errors': sum(len(c.stats.errors) for c in self.clients)
        }
        
        # Calculate rates and percentages
        udp_success_rate = (total_stats['total_udp_responses'] / total_stats['total_udp_packets'] * 100) if total_stats['total_udp_packets'] > 0 else 0
        tcp_success_rate = (total_stats['total_tcp_connections'] / (total_stats['total_tcp_connections'] + total_stats['total_tcp_failed']) * 100) if (total_stats['total_tcp_connections'] + total_stats['total_tcp_failed']) > 0 else 0
        
        print(f"Simulation Duration: {self.duration} seconds")
        print(f"Active Players: {total_stats['total_players']}")
        print()
        
        print("TRAFFIC SUMMARY:")
        print(f"  Total UDP Packets Sent: {total_stats['total_udp_packets']:,}")
        print(f"  UDP Responses Received: {total_stats['total_udp_responses']:,}")
        print(f"  UDP Timeouts: {total_stats['total_udp_timeouts']:,}")
        print(f"  UDP Success Rate: {udp_success_rate:.2f}%")
        print()
        
        print(f"  Total TCP Connection Attempts: {total_stats['total_tcp_connections'] + total_stats['total_tcp_failed']:,}")
        print(f"  TCP Connections Successful: {total_stats['total_tcp_connections']:,}")
        print(f"  TCP Connections Failed: {total_stats['total_tcp_failed']:,}")
        print(f"  TCP Success Rate: {tcp_success_rate:.2f}%")
        print()
        
        print("BANDWIDTH:")
        print(f"  Total Bytes Sent: {total_stats['total_bytes_sent']:,} ({total_stats['total_bytes_sent']/1024:.2f} KB)")
        print(f"  Total Bytes Received: {total_stats['total_bytes_received']:,} ({total_stats['total_bytes_received']/1024:.2f} KB)")
        print(f"  Average per Player: {total_stats['total_bytes_sent']/total_stats['total_players']:.0f} bytes sent")
        print()
        
        print("PERFORMANCE:")
        packets_per_second = total_stats['total_udp_packets'] / self.duration
        print(f"  Packets per Second: {packets_per_second:.2f}")
        print(f"  Bytes per Second: {total_stats['total_bytes_sent']/self.duration:.2f}")
        print(f"  Total Errors: {total_stats['total_errors']}")
        print()
        
        # Per-player breakdown (top 5 most active)
        print("TOP 5 MOST ACTIVE PLAYERS:")
        sorted_clients = sorted(self.clients, key=lambda c: c.stats.udp_packets_sent, reverse=True)
        for i, client in enumerate(sorted_clients[:5]):
            print(f"  Player {client.stats.player_id}: {client.stats.udp_packets_sent} UDP, {client.stats.tcp_connections} TCP, {len(client.stats.errors)} errors")
        
        print()
        
        # Save detailed report to file
        self._save_json_report(total_stats)
        
    def _save_json_report(self, summary_stats):
        """Save detailed JSON report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'simulation_config': {
                'num_players': self.num_players,
                'duration_seconds': self.duration,
                'target_server': self.server_ip
            },
            'summary_stats': summary_stats,
            'player_details': [client.get_stats_dict() for client in self.clients]
        }
        
        filename = f"/shared/client-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"Detailed JSON report saved to: {filename}")
        except Exception as e:
            print(f"Failed to save JSON report: {e}")
            
    def run_complete_simulation(self):
        """Run the complete simulation and generate report"""
        self.start_simulation()
        self.generate_report()

def main():
    # Parse command line arguments
    num_players = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    server_ip = sys.argv[2] if len(sys.argv) > 2 else "nftables-test-container"
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    
    print(f"Game Client Simulator")
    print(f"Players: {num_players}, Server: {server_ip}, Duration: {duration}s")
    
    manager = GameClientManager(num_players, server_ip, duration)
    manager.run_complete_simulation()

if __name__ == "__main__":
    main()