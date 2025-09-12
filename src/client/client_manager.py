#!/usr/bin/env python3

import threading
import time
import random
import json
from datetime import datetime
from .game_client import GameClient


class GameClientManager:
    """Manages multiple game clients and coordinates simulation."""
    
    def __init__(self, num_players=50, server_ip="nftables-test-container", duration=120, connections_per_player=3):
        self.num_players = num_players
        self.server_ip = server_ip
        self.duration = duration
        self.connections_per_player = connections_per_player  # Multiple concurrent connections per player
        self.clients = []
        self.threads = []
        self.session_start_time = None
        self.session_end_time = None
        
    def start_simulation(self):
        """Start the multi-client simulation with multiple connections per player."""
        self.session_start_time = time.time()
        total_connections = self.num_players * self.connections_per_player
        print(f"=== Starting {self.num_players} Player Simulation ({total_connections} total connections) at {datetime.now()} ===")
        print(f"Target Server: {self.server_ip}")
        print(f"Connections per player: {self.connections_per_player}")
        print("Mode: Maximum load - Continuous until server goes down")
        
        # Create multiple connection threads per player
        for player_id in range(1, self.num_players + 1):
            for connection_id in range(1, self.connections_per_player + 1):
                # Create a unique client instance for each connection
                client = GameClient(f"{player_id}-{connection_id}", self.server_ip)
                self.clients.append(client)
                
                thread = threading.Thread(target=client.simulate_game_traffic)
                thread.daemon = True
                self.threads.append(thread)
                thread.start()
                
                # Minimal stagger to avoid overwhelming connection setup
                time.sleep(random.uniform(0.01, 0.05))
            
        print(f"All {self.num_players} players with {total_connections} concurrent connections started in maximum load mode")
        
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()
            
        self.session_end_time = time.time()
        session_duration = self.session_end_time - self.session_start_time if self.session_start_time else 0
        print(f"All connections finished at {datetime.now()}")
        print(f"Session duration: {session_duration:.1f} seconds")
        
    def generate_report(self):
        """Generate comprehensive client-side report"""
        print("\n" + "="*60)
        print("CLIENT SIMULATION REPORT")
        print("="*60)
        
        # Aggregate statistics
        total_stats = self._calculate_aggregate_stats()
        
        # Calculate rates and percentages
        udp_success_rate = self._calculate_udp_success_rate(total_stats)
        tcp_success_rate = self._calculate_tcp_success_rate(total_stats)
        
        self._print_summary(total_stats)
        self._print_traffic_summary(total_stats, udp_success_rate, tcp_success_rate)
        self._print_bandwidth_info(total_stats)
        self._print_performance_metrics(total_stats)
        self._print_top_players()
        
        # Save detailed report to file
        self._save_json_report(total_stats)
        
    def _calculate_aggregate_stats(self):
        """Calculate aggregated statistics from all clients."""
        all_pings = [p for c in self.clients for p in c.stats.ping_times if p is not None]
        
        return {
            'total_players': len(self.clients),
            'total_tcp_connections': sum(c.stats.tcp_connections for c in self.clients),
            'total_tcp_failed': sum(c.stats.tcp_failed for c in self.clients),
            'total_udp_packets': sum(c.stats.udp_packets_sent for c in self.clients),
            'total_udp_responses': sum(c.stats.udp_responses for c in self.clients),
            'total_udp_timeouts': sum(c.stats.udp_timeouts for c in self.clients),
            'total_bytes_sent': sum(c.stats.total_bytes_sent for c in self.clients),
            'total_bytes_received': sum(c.stats.total_bytes_received for c in self.clients),
            'total_errors': sum(len(c.stats.errors) for c in self.clients),
            'ping_min_ms': min(all_pings) if all_pings else None,
            'ping_max_ms': max(all_pings) if all_pings else None,
            'ping_avg_ms': sum(all_pings)/len(all_pings) if all_pings else None,
            'ping_count': len(all_pings)
        }
    
    def _calculate_udp_success_rate(self, total_stats):
        """Calculate UDP success rate percentage."""
        return (total_stats['total_udp_responses'] / total_stats['total_udp_packets'] * 100) \
               if total_stats['total_udp_packets'] > 0 else 0
    
    def _calculate_tcp_success_rate(self, total_stats):
        """Calculate TCP success rate percentage."""
        total_attempts = total_stats['total_tcp_connections'] + total_stats['total_tcp_failed']
        return (total_stats['total_tcp_connections'] / total_attempts * 100) \
               if total_attempts > 0 else 0
    
    def _print_summary(self, total_stats):
        """Print simulation summary."""
        print(f"Simulation Duration: {self.duration} seconds")
        print(f"Active Players: {total_stats['total_players']}")
        print()
    
    def _print_traffic_summary(self, total_stats, udp_success_rate, tcp_success_rate):
        """Print traffic statistics."""
        print("TRAFFIC SUMMARY:")
        print(f"  Total UDP Packets Sent: {total_stats['total_udp_packets']:,}")
        print(f"  UDP Responses Received: {total_stats['total_udp_responses']:,}")
        print(f"  UDP Timeouts: {total_stats['total_udp_timeouts']:,}")
        print(f"  UDP Success Rate: {udp_success_rate:.2f}%")
        print()
        
        total_attempts = total_stats['total_tcp_connections'] + total_stats['total_tcp_failed']
        print(f"  Total TCP Connection Attempts: {total_attempts:,}")
        print(f"  TCP Connections Successful: {total_stats['total_tcp_connections']:,}")
        print(f"  TCP Connections Failed: {total_stats['total_tcp_failed']:,}")
        print(f"  TCP Success Rate: {tcp_success_rate:.2f}%")
        print()
    
    def _print_bandwidth_info(self, total_stats):
        """Print bandwidth statistics."""
        print("BANDWIDTH:")
        print(f"  Total Bytes Sent: {total_stats['total_bytes_sent']:,} ({total_stats['total_bytes_sent']/1024:.2f} KB)")
        print(f"  Total Bytes Received: {total_stats['total_bytes_received']:,} ({total_stats['total_bytes_received']/1024:.2f} KB)")
        print(f"  Average per Player: {total_stats['total_bytes_sent']/total_stats['total_players']:.0f} bytes sent")
        print()
    
    def _print_performance_metrics(self, total_stats):
        """Print performance metrics including ping statistics."""
        print("PERFORMANCE:")
        packets_per_second = total_stats['total_udp_packets'] / self.duration
        print(f"  Packets per Second: {packets_per_second:.2f}")
        print(f"  Bytes per Second: {total_stats['total_bytes_sent']/self.duration:.2f}")
        print(f"  Total Errors: {total_stats['total_errors']}")
        
        if total_stats['ping_count']:
            print(f"  Ping (ms): min={total_stats['ping_min_ms']:.2f}, max={total_stats['ping_max_ms']:.2f}, avg={total_stats['ping_avg_ms']:.2f}, count={total_stats['ping_count']}")
        else:
            print("  Ping (ms): No data")
        print()
    
    def _print_top_players(self):
        """Print top 5 most active players."""
        print("TOP 5 MOST ACTIVE PLAYERS:")
        sorted_clients = sorted(self.clients, key=lambda c: c.stats.udp_packets_sent, reverse=True)
        for client in sorted_clients[:5]:
            print(f"  Player {client.stats.player_id}: {client.stats.udp_packets_sent} UDP, {client.stats.tcp_connections} TCP, {len(client.stats.errors)} errors")
        print()
        
    def _save_json_report(self, summary_stats):
        """Save detailed JSON report"""
        # Calculate actual session duration
        actual_duration = 0
        if self.session_start_time and self.session_end_time:
            actual_duration = self.session_end_time - self.session_start_time
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'simulation_config': {
                'num_players': self.num_players,
                'mode': 'continuous_until_server_down',
                'original_duration_setting': self.duration,  # Keep for compatibility
                'duration_seconds': int(actual_duration),    # Actual session duration for dashboard
                'session_duration': actual_duration,         # Exact duration in seconds
                'target_server': self.server_ip,
                'connections_per_player': self.connections_per_player
            },
            'summary_stats': summary_stats,
            'player_details': [client.stats.get_stats_dict() for client in self.clients]
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