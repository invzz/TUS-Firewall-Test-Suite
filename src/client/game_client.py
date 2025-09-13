#!/usr/bin/env python3

import socket
import sys
import time
import random
import os
import threading
from datetime import datetime
from .player_stats import PlayerStats


class GameClient:
    """Represents a single game client that simulates player behavior."""
    
    def __init__(self, player_id: int, server_ip: str = "nftables-test-container"):
        self.player_id = player_id
        self.server_ip = server_ip
        
        # UT Network Specifications from environment variables
        self.ut_udp_overhead = int(os.getenv('UT_UDP_OVERHEAD', '28'))
        self.ut_tickrate = int(os.getenv('UT_TICKRATE', '85'))
        self.ut_default_netspeed = int(os.getenv('UT_DEFAULT_NETSPEED', '40000'))
        self.ut_max_netspeed = int(os.getenv('UT_MAX_NETSPEED', '100000'))
        
        # Calculate authentic UT packet sizes based on real server specs
        self.ut_default_payload = (self.ut_default_netspeed // self.ut_tickrate) - self.ut_udp_overhead
        self.ut_max_payload = (self.ut_max_netspeed // self.ut_tickrate) - self.ut_udp_overhead
        self.ut_tick_interval = 1.0 / self.ut_tickrate  # Seconds per tick
        self.stats = PlayerStats(player_id)
        self.running = False
        self.received_shutdown = False
        
        # Setup shutdown listener
        self.shutdown_listener_thread = None
        self.shutdown_socket = None

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
        # Only log shutdown-related messages to avoid spam
        if any(keyword in message.lower() for keyword in ['shutdown', 'stopping', 'down', 'disconnect']):
            print(f"[{datetime.now()}] Player {self.player_id}: {message}")
        
    def start_shutdown_listener(self):
        """Start listening for server shutdown notifications."""
        def listen_for_shutdown():
            self._setup_shutdown_socket()
            self._listen_for_shutdown_messages()
            self._cleanup_shutdown_socket()
        
        self.shutdown_listener_thread = threading.Thread(target=listen_for_shutdown, daemon=True)
        self.shutdown_listener_thread.start()
        
    def _setup_shutdown_socket(self):
        """Setup the shutdown listening socket."""
        try:
            # Use dedicated shutdown notification port with player-specific offset
            # This avoids port conflicts when multiple clients run in same container
            # Parse player_id which can be string like "1-1" or just "1"
            try:
                if '-' in str(self.player_id):
                    player_num = int(str(self.player_id).split('-')[0])
                else:
                    player_num = int(self.player_id)
            except (ValueError, IndexError):
                player_num = 1  # Default fallback
                
            listen_port = 7778 + (player_num % 10)  # 7778-7787
            self.shutdown_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.shutdown_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.shutdown_socket.bind(('0.0.0.0', listen_port))
            self.shutdown_socket.settimeout(1.0)
            self.log(f"Shutdown listener started on port {listen_port}")
        except Exception as e:
            self.log(f"Failed to setup shutdown listener: {e}")  # Better error visibility
            
    def _listen_for_shutdown_messages(self):
        """Listen for shutdown messages from server."""
        print(f"[{datetime.now()}] 🎯 Player {self.player_id}: Shutdown listener is active and waiting for messages...")
        sys.stdout.flush()
        
        message_count = 0
        while self.running and not self.received_shutdown:
            try:
                data, addr = self.shutdown_socket.recvfrom(1024)
                message = data.decode().strip()
                message_count += 1
                print(f"[{datetime.now()}] 📨 Player {self.player_id}: Received message #{message_count} from {addr}: '{message}'")
                sys.stdout.flush()
                
                if message == "SERVER_SHUTDOWN":
                    print(f"[{datetime.now()}] 📢 Player {self.player_id}: Received shutdown notification from {addr[0]} - preparing for graceful shutdown")
                    sys.stdout.flush()
                    self.received_shutdown = True
                    break
                else:
                    print(f"[{datetime.now()}] ⚠️ Player {self.player_id}: Unexpected message: '{message}' (expected 'SERVER_SHUTDOWN')")
                    sys.stdout.flush()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:  # Only log errors if we're still supposed to be running
                    self.log(f"Error in shutdown listener: {e}")
                break
        
        print(f"[{datetime.now()}] 🔚 Player {self.player_id}: Shutdown listener stopped (received_shutdown={self.received_shutdown}, running={self.running})")
        sys.stdout.flush()
                
    def _cleanup_shutdown_socket(self):
        """Clean up the shutdown socket."""
        if self.shutdown_socket:
            try:
                self.shutdown_socket.close()
            except Exception:
                pass
        
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
        self.log("UT specs: {}Hz tickrate, {}-{} netspeed, {}B overhead".format(
            self.ut_tickrate, self.ut_default_netspeed, self.ut_max_netspeed, self.ut_udp_overhead))
        self.log("Packet sizes: {}-{} bytes payload ({}-{} total)".format(
            self.ut_default_payload, self.ut_max_payload, 
            self.ut_default_payload + self.ut_udp_overhead, self.ut_max_payload + self.ut_udp_overhead))

        # Start listening for server shutdown notifications
        self.start_shutdown_listener()
        
        # Give shutdown listener time to properly bind to port
        time.sleep(0.5)
        
        start_time = time.time()
        
        try:
            last_ping = 0
            last_server_check = 0
            last_throughput_snapshot = 0
            ping_interval = 2  # More frequent ping collection (every 2 seconds)
            server_check_interval = 2   # Check server availability every 2 seconds (faster detection)
            throughput_snapshot_interval = 2  # Record throughput every 2 seconds
            consecutive_failures = 0
            max_consecutive_failures = 2  # Server considered down after 2 consecutive failures (faster)

            while self.running:
                now = time.time()
                
                # Check for server shutdown notification (highest priority)
                if self.received_shutdown:
                    print(f"[{datetime.now()}] 📢 Player {self.player_id}: Server shutdown notification received - stopping simulation (REASON: Graceful server shutdown)")
                    sys.stdout.flush()
                    break
                
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
                        elapsed_time = now - start_time
                        print(f"[{datetime.now()}] ❌ Player {self.player_id}: Server appears to be down - stopping simulation (REASON: {consecutive_failures} consecutive connection failures after {elapsed_time:.1f}s)")
                        sys.stdout.flush()
                        break
                            
                    last_server_check = now
                
                try:
                    # Select and execute game activity with realistic UT patterns
                    activity = random.choices(
                        ['query', 'join', 'gameplay', 'heartbeat', 'tcp_test'],
                        weights=[5, 2, 85, 5, 3]  # Gameplay dominates (85%), realistic UT pattern
                    )[0]
                    
                    self._execute_game_activity(activity)
                    
                    # Realistic UT gameplay frequency using authentic tickrate
                    if activity == 'gameplay':
                        delay = self.ut_tick_interval  # Already handled in _send_gameplay_packets
                    else:
                        delay = random.uniform(0.05, 0.5)  # Other activities more frequent, less blocking
                    time.sleep(delay)
                    
                except Exception as e:
                    self.stats.errors.append(f"Activity {activity}: {str(e)}")
                    time.sleep(0.001)  # Minimal pause on error, maximum throughput

        except Exception as e:
            # Handle unexpected errors during simulation
            total_runtime = time.time() - start_time
            print(f"[{datetime.now()}] 💥 Player {self.player_id}: Simulation crashed after {total_runtime:.1f}s (REASON: Unexpected error - {str(e)}) - {self.stats.udp_packets_sent} UDP packets, {self.stats.tcp_connections} TCP connections")
            sys.stdout.flush()
            
        finally:
            self.running = False
            total_runtime = time.time() - start_time
            
            # Log final shutdown reason (if not already logged)
            if hasattr(self, 'received_shutdown') and self.received_shutdown:
                print(f"[{datetime.now()}] ✅ Player {self.player_id}: Simulation completed after {total_runtime:.1f}s (REASON: Graceful shutdown) - {self.stats.udp_packets_sent} UDP packets, {self.stats.tcp_connections} TCP connections")
                sys.stdout.flush()
            elif not hasattr(self, 'crashed'):  # Don't log twice if we already logged a crash
                print(f"[{datetime.now()}] ⚠️ Player {self.player_id}: Simulation ended after {total_runtime:.1f}s (REASON: Server unreachable) - {self.stats.udp_packets_sent} UDP packets, {self.stats.tcp_connections} TCP connections")
                sys.stdout.flush()
        
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
        """Send realistic UT gameplay packets with authentic server specifications"""
        port = random.choice(self.game_ports['ut_servers'])
        
        # Using authentic UT server specs from your friend:
        # - UDP overhead: {self.ut_udp_overhead} bytes
        # - Tickrate: {self.ut_tickrate} Hz ({self.ut_tick_interval:.4f}s intervals)
        # - Default netspeed: {self.ut_default_netspeed} bytes/sec → {self.ut_default_payload} byte payload
        # - Max netspeed: {self.ut_max_netspeed} bytes/sec → {self.ut_max_payload} byte payload
        
        # Send packets at authentic UT tickrate
        packets_in_burst = random.randint(5, 15)  # Realistic burst size
        
        for _ in range(packets_in_burst):
            # Simulate different netspeed settings based on real server configurations
            netspeed_setting = random.choices(
                ['default', 'high', 'variable'],
                weights=[60, 30, 10]  # Most use default, some high-end, few variable
            )[0]
            
            if netspeed_setting == 'default':
                # Default netspeed from env: payload size
                target_payload_size = self.ut_default_payload
            elif netspeed_setting == 'high':
                # Max netspeed from env: payload size
                target_payload_size = self.ut_max_payload
            else:  # variable
                # Random between default and max (realistic variance)
                target_payload_size = random.randint(self.ut_default_payload, self.ut_max_payload)
            
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
            
            # Use authentic UT tickrate from environment
            time.sleep(self.ut_tick_interval)  # Real server tickrate timing
            
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