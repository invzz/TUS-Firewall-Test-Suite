#!/usr/bin/env python3

"""
Port listener module for handling TCP and UDP connections.
"""

import socket
import sys
from datetime import datetime


class PortListener:
    """Handles listening on a specific port for either TCP or UDP traffic."""
    
    def __init__(self, port, protocol='tcp', client_callback=None):
        self.port = port
        self.protocol = protocol.lower()
        self.socket = None
        self.running = False
        self.connections = 0
        self.packets_received = 0
        self.udp_clients = set()  # Track unique UDP client IPs
        self.client_callback = client_callback  # Callback to report client IPs

    def start(self):
        """Start listening on the configured port and protocol."""
        try:
            if self.protocol == 'tcp':
                self._start_tcp()
            elif self.protocol == 'udp':
                self._start_udp()
        except Exception as e:
            print(f"[{datetime.now()}] Failed to start {self.protocol.upper()} server on port {self.port}: {e}")

    def _start_tcp(self):
        """Start TCP server and handle connections."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(5)
        self.running = True
        
        while self.running:
            try:
                conn, addr = self.socket.accept()
                self.connections += 1
                print(f"[{datetime.now()}] Client connected to TCP/{self.port} from {addr[0]}:{addr[1]} (#{self.connections})")
                sys.stdout.flush()
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
        """Start UDP server and handle packets."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.settimeout(1.0)
        self.running = True
        
        while self.running:
            try:
                _, addr = self.socket.recvfrom(1024)
                self.packets_received += 1
                
                # Track new UDP clients
                client_ip = addr[0]
                if client_ip not in self.udp_clients:
                    self.udp_clients.add(client_ip)
                    self.connections += 1  # Count unique clients as "connections"
                    print(f"[{datetime.now()}] Client connected to UDP/{self.port} from {addr[0]}:{addr[1]} (#{self.connections})")
                    sys.stdout.flush()
                    
                    # Report client IP to server for shutdown targeting
                    if self.client_callback:
                        self.client_callback(client_ip)
                
                # Send response back
                self.socket.sendto(f"ACK from port {self.port}".encode(), addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[{datetime.now()}] UDP port {self.port} error: {e}")
                break
            
    def stop(self):
        """Stop the listener and close the socket."""
        self.running = False
        if self.socket:
            self.socket.close()
            
    def get_stats(self):
        """Return statistics string for this listener."""
        if self.protocol == 'tcp':
            return f"TCP/{self.port}: {self.connections} connections"
        else:
            return f"UDP/{self.port}: {self.packets_received} packets"