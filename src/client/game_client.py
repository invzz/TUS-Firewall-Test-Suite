#!/usr/bin/env python3

import socket
import time
import random
from datetime import datetime
from player_stats import PlayerStats


class GameClient:
    """Represents a single game client that simulates player behavior."""
    
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

    def ping_server(self, count=1, timeout=1.0):
        """Ping the server using a UDP echo and measure round-trip time in ms."""
        port = 9696  # Use a known open UDP port
        for _ in range(count):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(timeout)
                message = f"ping-{self.player_id}-{time.time()}".encode()
                start = time.time()
                sock.sendto(message, (self.server_ip, port))
                _data, _addr = sock.recvfrom(1024)
                end = time.time()
                rtt = (end - start) * 1000.0  # ms
                self.stats.ping_times.append(rtt)
            except Exception:
                self.stats.ping_times.append(None)
            finally:
                sock.close()
        
    def log(self, message):
        """Log a message with timestamp and player ID."""
        print(f"[{datetime.now()}] Player {self.player_id}: {message}")
        
    def simulate_game_traffic(self, duration_seconds=120):
        """Simulate realistic game traffic patterns"""
        self.running = True
        self.log("Starting game simulation...")

        start_time = time.time()
        end_time = start_time + duration_seconds
        last_ping = 0
        ping_interval = 5  # seconds

        while time.time() < end_time and self.running:
            now = time.time()
            # Ping server every ping_interval seconds
            if now - last_ping > ping_interval:
                self.ping_server(count=1)
                last_ping = now
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
                except Exception:
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
                response, _ = sock.recvfrom(1024)
                self.stats.udp_responses += 1
                self.stats.total_bytes_received += len(response)
            except socket.timeout:
                self.stats.udp_timeouts += 1
                
            sock.close()
            
        except Exception as e:
            self.stats.errors.append(f"UDP {port}: {str(e)}")
            
    def get_stats_dict(self):
        """Return stats as dictionary for JSON serialization"""
        return self.stats.get_stats_dict()