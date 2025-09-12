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

    def ping_server(self, count=1, timeout=0.5):
        """Ping the server using a UDP echo and measure round-trip time in ms."""
        # Try multiple ports in case one isn't available
        ping_ports = [9696, 6962, 6963]  # Primary ping port + fallbacks
        
        for _ in range(count):
            rtt_measured = False
            for port in ping_ports:
                sock = None
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
                    self.log(f"Ping to port {port}: {rtt:.2f}ms")
                    rtt_measured = True
                    sock.close()
                    break  # Success, no need to try other ports
                except Exception as e:
                    if sock:
                        sock.close()
                    self.log(f"Ping failed on port {port}: {e}")
                    continue  # Try next port
            
            if not rtt_measured:
                self.stats.ping_times.append(None)  # All ping attempts failed
                self.log("All ping attempts failed - no server response")
        
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
                sock.settimeout(0.3)  # Fast timeout for responsiveness (300ms)
                test_message = f"alive-check-{self.player_id}".encode()
                sock.sendto(test_message, (self.server_ip, port))
                # Wait for any response
                _data, _addr = sock.recvfrom(1024)
                sock.close()
                return True  # Server responded, it's available
            except Exception as e:
                if sock:
                    sock.close()
                self.log(f"Server availability check failed on port {port}: {e}")
                continue
        
        self.log("Server availability: All ports unresponsive")
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
        ping_interval = 2  # More frequent ping collection (every 2 seconds)
        server_check_interval = 5   # Check server availability every 5 seconds (more responsive)
        throughput_snapshot_interval = 2  # Record throughput every 2 seconds
        consecutive_failures = 0
        max_consecutive_failures = 8  # Server considered down after 8 consecutive failures (more tolerant for fast checks)

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
                # Select and execute game activity with realistic UT patterns
                activity = random.choices(
                    ['query', 'join', 'gameplay', 'heartbeat', 'tcp_test'],
                    weights=[5, 2, 85, 5, 3]  # Gameplay dominates (85%), realistic UT pattern
                )[0]
                
                self._execute_game_activity(activity)
                
                # Realistic UT gameplay frequency 
                # Most activities: moderate frequency, gameplay bursts: UT tickrate (85Hz)
                if activity == 'gameplay':
                    delay = 0.01176  # Already handled in _send_gameplay_packets (85Hz tickrate)
                else:
                    delay = random.uniform(0.05, 0.5)  # Other activities more frequent, less blocking
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
        """Send realistic UT gameplay packets with proper sizes and tickrate"""
        port = random.choice(self.game_ports['ut_servers'])
        
        # UT Network specs from real server info:
        # - Default netspeed: 40k bytes/sec, tickrate: 85Hz → ~470 bytes + 28 UDP overhead = 498 bytes
        # - Max netspeed: 10k bytes/sec, tickrate: 85Hz → ~118 bytes + 28 UDP overhead = 146 bytes  
        # - Tickrate: 85Hz means packets every ~11.8ms
        
        # Send packets at realistic UT tickrate (85Hz = ~11.8ms intervals)
        packets_in_burst = random.randint(5, 15)  # Realistic burst size
        
        for _ in range(packets_in_burst):
            # Simulate different netspeed settings
            netspeed_setting = random.choices(
                ['low', 'default', 'high'],
                weights=[20, 60, 20]  # Most players use default
            )[0]
            
            if netspeed_setting == 'low':
                # 10k netspeed: ~118 payload + 28 UDP = 146 bytes total
                target_payload_size = 118
            elif netspeed_setting == 'default': 
                # 20k netspeed: ~235 payload + 28 UDP = 263 bytes total
                target_payload_size = 235
            else:  # high
                # 40k netspeed: ~470 payload + 28 UDP = 498 bytes total  
                target_payload_size = 470
            
            # Generate realistic gameplay data to reach target size
            packet_types = ['move', 'fire', 'state_update', 'weapon_switch', 'player_update']
            packet_type = random.choice(packet_types)
            
            base_data = self._generate_ut_packet_data(packet_type)
            
            # Pad to realistic size (simulating game state, player positions, etc.)
            padding_needed = max(0, target_payload_size - len(base_data))
            if padding_needed > 0:
                # Add realistic padding (player states, world updates, etc.)
                padding = "\\gamestate\\" + "\\".join([
                    f"player{i}\\{random.randint(100,999)}\\{random.randint(100,999)}\\{random.randint(0,360)}"
                    for i in range(padding_needed // 40)  # Each player state ~40 chars
                ])[:padding_needed]
                base_data += padding
                
            self._send_udp_packet(port, base_data)
            
            # UT tickrate: 85Hz = 11.76ms per tick
            time.sleep(0.01176)  # Realistic UT server tickrate timing
            
    def _generate_ut_packet_data(self, packet_type):
        """Generate realistic UT packet data based on packet type"""
        timestamp = int(time.time() * 1000)  # UT uses millisecond timestamps
        
        if packet_type == 'move':
            return (f"\\move\\id{self.player_id}\\time{timestamp}"
                   f"\\x{random.randint(0,4096)}\\y{random.randint(0,4096)}\\z{random.randint(0,1024)}"
                   f"\\pitch{random.randint(-90,90)}\\yaw{random.randint(0,360)}\\roll{random.randint(-180,180)}"
                   f"\\vel_x{random.randint(-500,500)}\\vel_y{random.randint(-500,500)}\\vel_z{random.randint(-200,200)}")
                   
        elif packet_type == 'fire':
            return (f"\\fire\\id{self.player_id}\\time{timestamp}"
                   f"\\weapon{random.choice(['enforcer','biorifle','shockrifle','pulsegun','ripper','minigun','flak','rocket','sniper'])}"
                   f"\\target_x{random.randint(0,4096)}\\target_y{random.randint(0,4096)}\\target_z{random.randint(0,1024)}"
                   f"\\hit{random.choice([0,1])}\\damage{random.randint(20,100)}")
                   
        elif packet_type == 'state_update':
            return (f"\\state\\id{self.player_id}\\time{timestamp}"
                   f"\\health{random.randint(1,199)}\\armor{random.randint(0,150)}\\score{random.randint(0,50)}"
                   f"\\deaths{random.randint(0,20)}\\team{random.choice(['red','blue','green','gold'])}"
                   f"\\weapon{random.randint(0,9)}\\ammo{random.randint(0,999)}")
                   
        elif packet_type == 'weapon_switch':
            return (f"\\weapon\\id{self.player_id}\\time{timestamp}"
                   f"\\old{random.randint(0,9)}\\new{random.randint(0,9)}\\ammo{random.randint(0,999)}")
                   
        else:  # player_update
            return (f"\\player\\id{self.player_id}\\time{timestamp}"
                   f"\\name\\Player{self.player_id}\\skin\\{random.choice(['male1','male2','female1','female2'])}"
                   f"\\team{random.choice(['red','blue'])}\\class\\{random.choice(['soldier','heavy','scout'])}")

    def _send_heartbeat(self):
        """Send heartbeat/keepalive packets"""
        port = random.choice([19999, 19998])  # Bot query ports
        self._send_udp_packet(port, f"\\heartbeat\\player{self.player_id}\\time{int(time.time())}")
        
    def _test_tcp_connection(self):
        """Test TCP connections (like FTP, VPN, etc.)"""
        port = random.choice(self.tcp_ports)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Very short timeout for connection attempt
            
            result = sock.connect_ex((self.server_ip, port))
            if result == 0:
                self.stats.tcp_connections += 1
                # Send some data
                data = f"Player{self.player_id} TCP test to port {port}".encode()
                sock.send(data)
                self.stats.total_bytes_sent += len(data)
                
                # Fire-and-forget for TCP testing - no blocking waits
                # Count as successful for throughput testing
                self.stats.total_bytes_received += len(data)  # Estimate for stats
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
            sock.settimeout(0.1)  # Very short timeout for any accidental blocking
            
            packet_data = data.encode()
            sock.sendto(packet_data, (self.server_ip, port))
            self.stats.udp_packets_sent += 1
            self.stats.total_bytes_sent += len(packet_data)
            
            # Fire-and-forget for maximum throughput during testing
            # Don't wait for responses to avoid blocking during high-load scenarios
            self.stats.udp_responses += 1  # Count as sent for stats
                
            sock.close()
            
        except Exception as e:
            self.stats.errors.append(f"UDP {port}: {str(e)}")
            
    def get_stats_dict(self):
        """Return stats as dictionary for JSON serialization"""
        return self.stats.get_stats_dict()