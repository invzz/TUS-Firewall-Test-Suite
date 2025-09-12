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
        # Try multiple ports in case one isn't available
        ping_ports = [9696, 6962, 6963]  # Primary ping port + fallbacks
        
        for _ in range(count):
            rtt_measured = False
            for port in ping_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(timeout)
                    message = f"ping-{self.player_id}-{time.time()}".encode()
                    start = time.time()
                    sock.sendto(message, (self.server_ip, port))
                    _data, _addr = sock.recvfrom(1024)
                    end = time.time()
                    rtt = (end - start) * 1000.0  # ms
                    self.stats.record_ping(rtt)  # Use new method for time-series data
                    rtt_measured = True
                    sock.close()
                    break  # Success, no need to try other ports
                except Exception:
                    if sock:
                        sock.close()
                    continue  # Try next port
            
            if not rtt_measured:
                self.stats.ping_times.append(None)  # All ping attempts failed
        
    def log(self, message):
        """Log a message with timestamp and player ID."""
        print(f"[{datetime.now()}] Player {self.player_id}: {message}")
        
    def is_server_available(self):
        """Check if server is still available by attempting a quick connection"""
        # Try multiple ports to determine server availability
        test_ports = [6962, 9696, 6963]  # Primary UDP ports for availability check
        
        for port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2.0)  # Quick timeout
                test_message = f"alive-check-{self.player_id}".encode()
                sock.sendto(test_message, (self.server_ip, port))
                # Wait for any response
                _data, _addr = sock.recvfrom(1024)
                sock.close()
                return True  # Server responded, it's available
            except Exception:
                if sock:
                    sock.close()
                continue
        
        return False  # No response from any port, server likely down

    def _check_server_status(self, consecutive_failures, max_failures, start_time, now):
        """Check server availability and return updated failure count"""
        if self.is_server_available():
            consecutive_failures = 0
            self.log(f"Server availability check: OK (running for {now - start_time:.1f}s)")
        else:
            consecutive_failures += 1
            self.log(f"Server availability check: FAILED ({consecutive_failures}/{max_failures})")
            
        return consecutive_failures

    def _execute_game_activity(self, activity):
        """Execute a specific game activity"""
        if activity == 'query':
            self._send_server_query()
        elif activity == 'join':
            self._attempt_server_join()
        elif activity == 'gameplay':
            self._send_gameplay_packets()
        elif activity == 'heartbeat':
            self._send_heartbeat()
        elif activity == 'tcp_test':
            self._test_tcp_connection()

    def simulate_game_traffic(self):
        """Simulate continuous game traffic until server becomes unavailable"""
        self.running = True
        self.log("Starting continuous game simulation (will run until server goes down)...")

        start_time = time.time()
        last_ping = 0
        last_server_check = 0
        last_throughput_snapshot = 0
        ping_interval = 5  # seconds
        server_check_interval = 10  # Check server availability every 10 seconds
        throughput_snapshot_interval = 2  # Record throughput every 2 seconds
        consecutive_failures = 0
        max_consecutive_failures = 3  # Server considered down after 3 consecutive failures

        while self.running:
            now = time.time()
            
            # Ping server periodically for latency measurement
            if now - last_ping > ping_interval:
                self.ping_server(count=1)
                last_ping = now
            
            # Record throughput snapshot periodically
            if now - last_throughput_snapshot > throughput_snapshot_interval:
                self.stats.record_throughput_snapshot()
                last_throughput_snapshot = now
            
            # Check server availability periodically
            if now - last_server_check > server_check_interval:
                consecutive_failures = self._check_server_status(
                    consecutive_failures, max_consecutive_failures, start_time, now)
                    
                if consecutive_failures >= max_consecutive_failures:
                    self.log("Server appears to be down - stopping simulation")
                    break
                        
                last_server_check = now
            
            try:
                # Select and execute game activity
                activity = random.choices(
                    ['query', 'join', 'gameplay', 'heartbeat', 'tcp_test'],
                    weights=[10, 5, 70, 10, 5]  # Maximum gameplay traffic
                )[0]
                
                self._execute_game_activity(activity)
                
                # Maximum frequency for high-load testing
                delay = random.uniform(0.001, 0.01)  # 100-1000 packets per second
                time.sleep(delay)
                
            except Exception as e:
                self.stats.errors.append(f"Activity {activity}: {str(e)}")
                time.sleep(0.001)  # Minimal pause on error, maximum throughput
                
        self.running = False
        total_runtime = time.time() - start_time
        self.log(f"Simulation ended after {total_runtime:.1f}s. Sent {self.stats.udp_packets_sent} UDP packets, {self.stats.tcp_connections} TCP connections")
        
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
        
        # Send high-intensity burst of gameplay packets
        for _ in range(random.randint(10, 25)):
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
            time.sleep(random.uniform(0.001, 0.01))  # Maximum speed burst
            
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