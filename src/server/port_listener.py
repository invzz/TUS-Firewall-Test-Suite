#!/usr/bin/env python3

"""
Port listener module for handling TCP and UDP connections.
"""

import socket
from datetime import datetime


class PortListener:
    """Handles listening on a specific port for either TCP or UDP traffic."""
    
    def __init__(self, port, protocol='tcp'):
        self.port = port
        self.protocol = protocol.lower()
        self.socket = None
        self.running = False
        self.connections = 0
        self.packets_received = 0

    def start(self):
        """Start listening on the configured port and protocol."""
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
        """Start TCP server and handle connections."""
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
        """Start UDP server and handle packets."""
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