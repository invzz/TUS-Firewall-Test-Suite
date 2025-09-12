#!/usr/bin/env python3
"""
TUS Firewall Test Suite - Results Dashboard
Real-time visualization of client and server test reports
"""

import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from pathlib import Path
import glob

# Page configuration
st.set_page_config(
    page_title="TUS Firewall Test Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
RESULTS_DIR = "results"
REFRESH_INTERVAL = 2  # seconds

def load_json_report(file_path):
    """Load and parse JSON report file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return None

def get_available_reports():
    """Get list of available report files."""
    if not os.path.exists(RESULTS_DIR):
        return [], []
    
    client_reports = glob.glob(f"{RESULTS_DIR}/client-report-*.json")
    server_reports = glob.glob(f"{RESULTS_DIR}/server-report-*.json")
    
    # Sort by modification time (newest first)
    client_reports.sort(key=os.path.getmtime, reverse=True)
    server_reports.sort(key=os.path.getmtime, reverse=True)
    
    return client_reports, server_reports

def format_timestamp(timestamp_str):
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return timestamp_str

def get_session_duration(config):
    """Get session duration from config, with fallbacks."""
    return config.get('duration_seconds', 0) or config.get('original_duration_setting', 0) or 0

def calculate_throughput(bytes_sent, config):
    """Calculate throughput using proper duration."""
    duration = get_session_duration(config) or 1  # Avoid division by zero
    return bytes_sent / duration if duration > 0 else 0

def get_server_load_info(total_traffic):
    """Get server load level and color based on traffic"""
    if total_traffic < 100:
        return "Low", "green"
    elif total_traffic < 500:
        return "Medium", "orange" 
    else:
        return "High", "red"

def create_protocol_chart(tcp_total, udp_total, title):
    """Create protocol distribution pie chart"""
    if tcp_total > 0 or udp_total > 0:
        return px.pie(
            values=[tcp_total, udp_total],
            names=['TCP', 'UDP'],
            title=title,
            color_discrete_sequence=['#FF6B6B', '#4ECDC4']
        )
    return None

def create_success_chart(success_count, failure_count, title, colors=None):
    """Create success/failure pie chart"""
    if colors is None:
        colors = ['#95E1D3', '#F38BA8']
    
    if success_count > 0 or failure_count > 0:
        return px.pie(
            values=[success_count, failure_count],
            names=['Successful', 'Failed'],
            title=title,
            color_discrete_sequence=colors
        )
    return None

def display_client_overview_metrics(config, summary):
    """Display client overview metrics section"""
    st.subheader("📊 Simulation Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Players", config.get('num_players', 0))
        # Use actual session duration if available, otherwise fall back to original setting
        duration = config.get('duration_seconds', 0) or config.get('original_duration_setting', 0)
        st.metric("Duration", f"{duration}s")
        
    with col2:
        tcp_total = summary.get('total_tcp_connections', 0)
        tcp_failed = summary.get('total_tcp_failed', 0)
        tcp_success_rate = ((tcp_total - tcp_failed) / tcp_total * 100) if tcp_total > 0 else 0
        st.metric("TCP Connections", tcp_total)
        st.metric("TCP Success Rate", f"{tcp_success_rate:.1f}%")
        
    with col3:
        udp_sent = summary.get('total_udp_packets', 0)
        udp_responses = summary.get('total_udp_responses', 0)
        udp_success_rate = (udp_responses / udp_sent * 100) if udp_sent > 0 else 0
        st.metric("UDP Packets Sent", udp_sent)
        st.metric("UDP Response Rate", f"{udp_success_rate:.1f}%")
        
    with col4:
        bytes_sent = summary.get('total_bytes_sent', 0)
        bytes_received = summary.get('total_bytes_received', 0)
        throughput = bytes_sent / config.get('duration_seconds', 1) if config.get('duration_seconds', 1) > 0 else 0
        st.metric("Total Data Sent", f"{bytes_sent:,} bytes")
        st.metric("Avg Throughput", f"{throughput:.0f} bytes/s")

def display_ping_analysis(summary):
    """Display ping analysis section"""
    ping_min = summary.get('ping_min_ms')
    ping_max = summary.get('ping_max_ms')  
    ping_avg = summary.get('ping_avg_ms')
    ping_count = summary.get('ping_count', 0)
    
    # Check if ping data is available (not null and count > 0)
    if ping_count > 0 and ping_min is not None:
        st.subheader("🏓 Network Latency Analysis")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ping Count", ping_count)
        with col2:
            st.metric("Min Latency", f"{ping_min:.1f}ms" if ping_min else "N/A")
        with col3:
            st.metric("Avg Latency", f"{ping_avg:.1f}ms" if ping_avg else "N/A")
        with col4:
            st.metric("Max Latency", f"{ping_max:.1f}ms" if ping_max else "N/A")
    else:
        st.info("ℹ️ Ping data not available - consider enabling ping collection in the client simulator")

def display_traffic_analysis_charts(summary):
    """Display traffic analysis charts section"""
    st.subheader("📈 Traffic Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    # Protocol Distribution
    with col1:
        tcp_total = summary.get('total_tcp_connections', 0) + summary.get('total_tcp_failed', 0)
        udp_total = summary.get('total_udp_packets', 0)
        fig_protocol = create_protocol_chart(tcp_total, udp_total, "Protocol Distribution")
        if fig_protocol:
            st.plotly_chart(fig_protocol, use_container_width=True)
    
    # TCP Success Analysis  
    with col2:
        tcp_success = summary.get('total_tcp_connections', 0)
        tcp_failed = summary.get('total_tcp_failed', 0)
        fig_tcp = create_success_chart(tcp_success, tcp_failed, "TCP Connection Success")
        if fig_tcp:
            st.plotly_chart(fig_tcp, use_container_width=True)
    
    # UDP Response Analysis
    with col3:
        udp_responses = summary.get('total_udp_responses', 0)
        udp_timeouts = summary.get('total_udp_timeouts', 0)
        fig_udp = create_success_chart(udp_responses, udp_timeouts, "UDP Response Analysis", 
                                     ['#A8E6CF', '#FFD93D'])
        if fig_udp:
            st.plotly_chart(fig_udp, use_container_width=True)

def display_efficiency_metrics(summary, config):
    """Display network efficiency metrics section"""
    st.subheader("⚡ Network Efficiency Metrics")
    
    bytes_sent = summary.get('total_bytes_sent', 0)
    bytes_received = summary.get('total_bytes_received', 0)
    udp_sent = summary.get('total_udp_packets', 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Data efficiency 
        efficiency = (bytes_received / bytes_sent * 100) if bytes_sent > 0 else 0
        st.metric("Data Efficiency", f"{efficiency:.1f}%", 
                 help="Percentage of sent data that was successfully received")
        
    with col2:
        # Average packet size
        avg_packet_size = bytes_sent / udp_sent if udp_sent > 0 else 0
        st.metric("Avg Packet Size", f"{avg_packet_size:.0f} bytes",
                 help="Average UDP packet size")
        
    with col3:
        # Packets per second
        duration = config.get('duration_seconds', 1)
        packets_per_sec = udp_sent / duration if duration > 0 else 0
        st.metric("Packets/Second", f"{packets_per_sec:.1f}",
                 help="Average UDP packets sent per second")

def display_player_details(data):
    """Display player performance details section"""
    st.subheader("👥 Player Performance Details")
    
    players = data.get('player_details', [])
    if not players:
        return
        
    # Create dataframe for player stats
    player_data = []
    for player in players:
        player_data.append({
            'Player ID': player.get('player_id'),
            'TCP Connections': player.get('tcp_connections', 0),
            'TCP Failed': player.get('tcp_failed', 0),
            'UDP Sent': player.get('udp_packets_sent', 0),
            'UDP Responses': player.get('udp_responses', 0),
            'UDP Timeouts': player.get('udp_timeouts', 0),
            'Bytes Sent': player.get('total_bytes_sent', 0),
            'Bytes Received': player.get('total_bytes_received', 0),
            'Errors': player.get('error_count', 0)
        })
    
    df_players = pd.DataFrame(player_data)
    
    # Player performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bytes = px.bar(
            df_players,
            x='Player ID',
            y=['Bytes Sent', 'Bytes Received'],
            title="Data Transfer by Player",
            barmode='group'
        )
        st.plotly_chart(fig_bytes, use_container_width=True)
        
    with col2:
        fig_udp_perf = px.bar(
            df_players,
            x='Player ID', 
            y=['UDP Responses', 'UDP Timeouts'],
            title="UDP Performance by Player",
            barmode='group'
        )
        st.plotly_chart(fig_udp_perf, use_container_width=True)
    
    # Player details table
    st.subheader("📋 Detailed Player Statistics")
    st.dataframe(df_players, use_container_width=True)

def create_ping_timeline_chart(player_details):
    """Create a time-series chart showing ping over time for all clients"""
    ping_data = []
    
    for player in player_details:
        ping_history = player.get('ping_history', [])
        if ping_history:
            for point in ping_history:
                if point['ping_ms'] is not None:
                    ping_data.append({
                        'Player': f"Client {player['player_id']}",
                        'Time (seconds)': point['timestamp'],
                        'Ping (ms)': point['ping_ms']
                    })
    
    if not ping_data:
        return None
        
    df = pd.DataFrame(ping_data)
    
    # Create line chart with different color for each player
    fig = px.line(df, 
                  x='Time (seconds)', 
                  y='Ping (ms)',
                  color='Player',
                  title="Client Ping Over Time",
                  labels={'Time (seconds)': 'Time (seconds)', 'Ping (ms)': 'Ping (ms)'}
                  )
    
    fig.update_traces(mode='markers+lines')
    fig.update_layout(
        xaxis_title="Time (seconds)",
        yaxis_title="Ping (ms)",
        legend_title="Players",
        hovermode='x unified'
    )
    
    return fig

def create_throughput_timeline_chart(player_details):
    """Create a time-series chart showing throughput over time for all clients"""
    throughput_data = []
    
    for player in player_details:
        throughput_history = player.get('throughput_history', [])
        if throughput_history:
            for point in throughput_history:
                throughput_data.append({
                    'Player': f"Client {player['player_id']}",
                    'Time (seconds)': point['timestamp'],
                    'Packets/sec': point['packets_per_sec'],
                    'Total Packets': point['total_packets']
                })
    
    if not throughput_data:
        return None
        
    df = pd.DataFrame(throughput_data)
    
    # Create line chart showing packets per second
    fig = px.line(df, 
                  x='Time (seconds)', 
                  y='Packets/sec',
                  color='Player',
                  title="Client Throughput Over Time",
                  labels={'Time (seconds)': 'Time (seconds)', 'Packets/sec': 'Packets/Second'}
                  )
    
    fig.update_traces(mode='markers+lines')
    fig.update_layout(
        xaxis_title="Time (seconds)",
        yaxis_title="Packets per Second",
        legend_title="Players",
        hovermode='x unified'
    )
    
    return fig

def create_aggregate_timeline_charts(player_details):
    """Create aggregated timeline charts showing average ping and total throughput"""
    # Collect all timestamps from all players
    all_timestamps = set()
    for player in player_details:
        ping_history = player.get('ping_history', [])
        throughput_history = player.get('throughput_history', [])
        all_timestamps.update(point['timestamp'] for point in ping_history)
        all_timestamps.update(point['timestamp'] for point in throughput_history)
    
    if not all_timestamps:
        return None, None
    
    sorted_timestamps = sorted(all_timestamps)
    
    # Aggregate data by time intervals
    aggregate_data = []
    
    for timestamp in sorted_timestamps:
        # Find ping values at this timestamp
        pings_at_time = []
        throughput_at_time = 0
        
        for player in player_details:
            # Get ping closest to this timestamp
            ping_history = player.get('ping_history', [])
            closest_ping = None
            min_time_diff = float('inf')
            
            for point in ping_history:
                time_diff = abs(point['timestamp'] - timestamp)
                if time_diff < min_time_diff and point['ping_ms'] is not None:
                    min_time_diff = time_diff
                    closest_ping = point['ping_ms']
            
            if closest_ping is not None and min_time_diff < 1.0:  # Within 1 second
                pings_at_time.append(closest_ping)
            
            # Get throughput at this timestamp
            throughput_history = player.get('throughput_history', [])
            for point in throughput_history:
                if abs(point['timestamp'] - timestamp) < 0.5:  # Within 0.5 seconds
                    throughput_at_time += point['packets_per_sec']
        
        if pings_at_time or throughput_at_time > 0:
            aggregate_data.append({
                'Time (seconds)': timestamp,
                'Avg Ping (ms)': sum(pings_at_time) / len(pings_at_time) if pings_at_time else None,
                'Total Throughput (packets/sec)': throughput_at_time
            })
    
    if not aggregate_data:
        return None, None
    
    df = pd.DataFrame(aggregate_data)
    
    # Create ping chart
    ping_fig = None
    if df['Avg Ping (ms)'].notna().any():
        ping_fig = px.line(df, 
                          x='Time (seconds)', 
                          y='Avg Ping (ms)',
                          title="Average Client Ping Over Time",
                          labels={'Time (seconds)': 'Time (seconds)', 'Avg Ping (ms)': 'Average Ping (ms)'}
                          )
        ping_fig.update_traces(mode='markers+lines', line_color='#FF6B6B')
        ping_fig.update_layout(
            xaxis_title="Time (seconds)",
            yaxis_title="Average Ping (ms)",
            hovermode='x'
        )
    
    # Create throughput chart  
    throughput_fig = None
    if df['Total Throughput (packets/sec)'].max() > 0:
        throughput_fig = px.line(df,
                                x='Time (seconds)',
                                y='Total Throughput (packets/sec)', 
                                title="Total Client Throughput Over Time",
                                labels={'Time (seconds)': 'Time (seconds)', 'Total Throughput (packets/sec)': 'Total Packets/Second'}
                                )
        throughput_fig.update_traces(mode='markers+lines', line_color='#4ECDC4')
        throughput_fig.update_layout(
            xaxis_title="Time (seconds)",
            yaxis_title="Total Packets per Second",
            hovermode='x'
        )
    
    return ping_fig, throughput_fig

def display_time_series_analysis(data):
    """Display time-series analysis section"""
    st.subheader("📈 Time-Series Analysis")
    
    player_details = data.get('player_details', [])
    if not player_details:
        st.info("No player time-series data available")
        return
    
    # Check if any player has time-series data
    has_ping_data = any(player.get('ping_history') for player in player_details)
    has_throughput_data = any(player.get('throughput_history') for player in player_details)
    
    if not has_ping_data and not has_throughput_data:
        st.info("⏰ Time-series data not available - this requires running the enhanced client simulation")
        return
    
    # Individual client charts
    st.subheader("📊 Individual Client Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        if has_ping_data:
            ping_chart = create_ping_timeline_chart(player_details)
            if ping_chart:
                st.plotly_chart(ping_chart, use_container_width=True)
        else:
            st.info("No ping time-series data available")
    
    with col2:
        if has_throughput_data:
            throughput_chart = create_throughput_timeline_chart(player_details)
            if throughput_chart:
                st.plotly_chart(throughput_chart, use_container_width=True)
        else:
            st.info("No throughput time-series data available")
    
    # Aggregated charts
    if has_ping_data or has_throughput_data:
        st.subheader("🔄 Aggregated Performance Trends")
        ping_agg_fig, throughput_agg_fig = create_aggregate_timeline_charts(player_details)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if ping_agg_fig:
                st.plotly_chart(ping_agg_fig, use_container_width=True)
            else:
                st.info("No aggregated ping data available")
        
        with col2:
            if throughput_agg_fig:
                st.plotly_chart(throughput_agg_fig, use_container_width=True)
            else:
                st.info("No aggregated throughput data available")

def display_client_report(data):
    """Display client report visualization."""
    st.header("🎮 Client Report Analysis")
    
    # Basic info
    config = data.get('simulation_config', {})
    summary = data.get('summary_stats', {})
    
    # Enhanced metrics section
    st.subheader("📊 Simulation Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Players", config.get('num_players', 0))
        # Use actual session duration if available, otherwise fall back to original setting
        duration = config.get('duration_seconds', 0) or config.get('original_duration_setting', 0)
        st.metric("Duration", f"{duration}s")
        
    with col2:
        tcp_total = summary.get('total_tcp_connections', 0)
        tcp_failed = summary.get('total_tcp_failed', 0)
        tcp_success_rate = ((tcp_total - tcp_failed) / tcp_total * 100) if tcp_total > 0 else 0
        st.metric("TCP Connections", tcp_total)
        st.metric("TCP Success Rate", f"{tcp_success_rate:.1f}%")
        
    with col3:
        udp_sent = summary.get('total_udp_packets', 0)
        udp_responses = summary.get('total_udp_responses', 0)
        udp_success_rate = (udp_responses / udp_sent * 100) if udp_sent > 0 else 0
        st.metric("UDP Packets Sent", udp_sent)
        st.metric("UDP Response Rate", f"{udp_success_rate:.1f}%")
        
    with col4:
        bytes_sent = summary.get('total_bytes_sent', 0)
        bytes_received = summary.get('total_bytes_received', 0)
        throughput = bytes_sent / config.get('duration_seconds', 1) if config.get('duration_seconds', 1) > 0 else 0
        st.metric("Total Data Sent", f"{bytes_sent:,} bytes")
        st.metric("Avg Throughput", f"{throughput:.0f} bytes/s")
    
    # Ping statistics if available
    ping_min = summary.get('ping_min_ms')
    ping_max = summary.get('ping_max_ms')  
    ping_avg = summary.get('ping_avg_ms')
    ping_count = summary.get('ping_count', 0)
    
    if ping_count > 0:
        st.subheader("🏓 Network Latency Analysis")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ping Count", ping_count)
        with col2:
            st.metric("Min Latency", f"{ping_min:.1f}ms" if ping_min else "N/A")
        with col3:
            st.metric("Avg Latency", f"{ping_avg:.1f}ms" if ping_avg else "N/A")
        with col4:
            st.metric("Max Latency", f"{ping_max:.1f}ms" if ping_max else "N/A")
    
    # Enhanced Traffic Analysis
    st.subheader("� Traffic Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Protocol Distribution
        tcp_total = summary.get('total_tcp_connections', 0) + summary.get('total_tcp_failed', 0)
        udp_total = summary.get('total_udp_packets', 0)
        
        if tcp_total > 0 or udp_total > 0:
            fig_protocol = px.pie(
                values=[tcp_total, udp_total],
                names=['TCP', 'UDP'],
                title="Protocol Distribution",
                color_discrete_sequence=['#FF6B6B', '#4ECDC4']
            )
            st.plotly_chart(fig_protocol, use_container_width=True)
    
    with col2:
        # Connection Success Analysis  
        tcp_success = summary.get('total_tcp_connections', 0)
        tcp_failed = summary.get('total_tcp_failed', 0)
        
        if tcp_success > 0 or tcp_failed > 0:
            fig_tcp = px.pie(
                values=[tcp_success, tcp_failed],
                names=['Successful', 'Failed'],
                title="TCP Connection Success",
                color_discrete_sequence=['#95E1D3', '#F38BA8']
            )
            st.plotly_chart(fig_tcp, use_container_width=True)
    
    with col3:
        # UDP Response Analysis
        udp_responses = summary.get('total_udp_responses', 0)
        udp_timeouts = summary.get('total_udp_timeouts', 0)
        
        if udp_responses > 0 or udp_timeouts > 0:
            fig_udp = px.pie(
                values=[udp_responses, udp_timeouts],
                names=['Responses', 'Timeouts'],
                title="UDP Response Analysis",
                color_discrete_sequence=['#A8E6CF', '#FFD93D']
            )
            st.plotly_chart(fig_udp, use_container_width=True)
    
    # Network Efficiency Metrics
    st.subheader("⚡ Network Efficiency Metrics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Data efficiency 
        efficiency = (bytes_received / bytes_sent * 100) if bytes_sent > 0 else 0
        st.metric("Data Efficiency", f"{efficiency:.1f}%", 
                 help="Percentage of sent data that was successfully received")
        
    with col2:
        # Average packet size
        avg_packet_size = bytes_sent / udp_sent if udp_sent > 0 else 0
        st.metric("Avg Packet Size", f"{avg_packet_size:.0f} bytes",
                 help="Average UDP packet size")
        
    with col3:
        # Packets per second
        duration = config.get('duration_seconds', 1)
        packets_per_sec = udp_sent / duration if duration > 0 else 0
        st.metric("Packets/Second", f"{packets_per_sec:.1f}",
                 help="Average UDP packets sent per second")
    
    # Player details
    st.subheader("👥 Player Performance Details")
    
    players = data.get('player_details', [])
    if players:
        # Create dataframe for player stats
        player_data = []
        for player in players:
            player_data.append({
                'Player ID': player.get('player_id'),
                'TCP Connections': player.get('tcp_connections', 0),
                'TCP Failed': player.get('tcp_failed', 0),
                'UDP Sent': player.get('udp_packets_sent', 0),
                'UDP Responses': player.get('udp_responses', 0),
                'UDP Timeouts': player.get('udp_timeouts', 0),
                'Bytes Sent': player.get('total_bytes_sent', 0),
                'Bytes Received': player.get('total_bytes_received', 0),
                'Errors': player.get('error_count', 0)
            })
        
        df_players = pd.DataFrame(player_data)
        
        # Player performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_bytes = px.bar(
                df_players,
                x='Player ID',
                y=['Bytes Sent', 'Bytes Received'],
                title="Data Transfer by Player",
                barmode='group'
            )
            st.plotly_chart(fig_bytes, use_container_width=True)
            
        with col2:
            fig_udp_perf = px.bar(
                df_players,
                x='Player ID', 
                y=['UDP Responses', 'UDP Timeouts'],
                title="UDP Performance by Player",
                barmode='group'
            )
            st.plotly_chart(fig_udp_perf, use_container_width=True)
        
        # Player details table
        st.subheader("📋 Detailed Player Statistics")
        st.dataframe(df_players, use_container_width=True)
    
    # Time-series analysis section
    display_time_series_analysis(data)

def display_aggregated_statistics(client_data, server_data):
    """Display aggregated statistics across client and server reports"""
    st.header("📊 Aggregated Test Statistics")
    
    if not (client_data and server_data):
        st.warning("Both client and server data required for aggregated statistics")
        return
    
    # Overall test summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Use correct field names from simulation_config and summary_stats
        total_clients = client_data.get('simulation_config', {}).get('num_players', 0)
        st.metric("Total Clients", total_clients)
        
    with col2:
        test_duration = get_session_duration(client_data.get('simulation_config', {}))
        st.metric("Test Duration", f"{test_duration}s")
        
    with col3:
        server_connections = server_data.get('total_tcp_connections', 0)
        st.metric("Server Connections", server_connections)
        
    with col4:
        if total_clients > 0:
            conn_per_client = server_connections / total_clients
            st.metric("Conn/Client", f"{conn_per_client:.1f}")
    
    # Cross-analysis metrics
    st.subheader("🔄 Cross-Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Client vs Server comparison using correct field names
        client_summary = client_data.get('summary_stats', {})
        client_success = (client_summary.get('total_tcp_connections', 0) + 
                         client_summary.get('total_udp_responses', 0))
        
        server_success = 0
        if 'port_details' in server_data:
            for port in server_data['port_details']:
                server_success += port.get('connections', 0) + port.get('packets', 0)
        
        success_ratio = (min(client_success, server_success) / max(client_success, 1)) * 100
        st.metric("Client-Server Sync", f"{success_ratio:.1f}%",
                 help=f"Client: {client_success}, Server: {server_success}")
    
    with col2:
        # Overall system efficiency
        total_attempts = client_success
        total_handled = server_success
        system_efficiency = 0
        if total_attempts > 0:
            system_efficiency = (total_handled / total_attempts) * 100
            st.metric("System Efficiency", f"{system_efficiency:.1f}%",
                     help="Overall percentage of client requests handled by server")
        else:
            st.metric("System Efficiency", "N/A", help="No client attempts recorded")
    
    # Performance trending (if multiple tests exist)
    st.subheader("📈 Performance Insights")
    
    # Calculate key performance indicators
    throughput = 0
    if test_duration > 0:
        total_server_activity = server_data.get('total_tcp_connections', 0) + server_data.get('total_udp_packets', 0)
        throughput = total_server_activity / test_duration
        st.info(f"**Average Throughput**: {throughput:.2f} transactions/second")
        
    if total_clients > 0 and test_duration > 0:
        client_efficiency = (server_connections / (total_clients * test_duration)) * 100
        st.info(f"**Client Efficiency**: {client_efficiency:.2f}% utilization")
    
    # Recommendations based on data
    st.subheader("💡 Optimization Recommendations")
    
    recommendations = []
    
    if success_ratio < 90:
        recommendations.append("🔧 Consider reviewing firewall rules - client-server synchronization below 90%")
    
    if system_efficiency < 80:
        recommendations.append("⚡ Server performance may need optimization - handling less than 80% of requests")
        
    if throughput < 10:
        recommendations.append("🚀 Low throughput detected - consider increasing server capacity or client distribution")
        
    if not recommendations:
        recommendations.append("✅ System performing well - all metrics within acceptable ranges")
    
    for rec in recommendations:
        st.info(rec)

def display_server_report(data):
    """Display server report visualization."""
    st.header("🛡️ Server Report Analysis")
    
    # Enhanced server metrics
    session_duration = data.get('session_duration', 0)
    tcp_connections = data.get('total_tcp_connections', 0)
    udp_packets = data.get('total_udp_packets', 0)
    
    st.subheader("🖥️ Server Performance Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Session Duration", f"{session_duration}s")
        conn_rate = tcp_connections / session_duration if session_duration > 0 else 0
        st.metric("TCP Conn/sec", f"{conn_rate:.2f}")
        
    with col2:
        st.metric("Total TCP Connections", tcp_connections)
        packet_rate = udp_packets / session_duration if session_duration > 0 else 0
        st.metric("UDP Packets/sec", f"{packet_rate:.2f}")
        
    with col3:
        st.metric("Total UDP Packets", udp_packets)
        total_traffic = tcp_connections + udp_packets
        st.metric("Total Traffic Events", total_traffic)
        
    with col4:
        # Server load analysis
        load_level, load_color = get_server_load_info(total_traffic)
        st.metric("Server Load", load_level)
        st.markdown(f"<span style='color: {load_color}'>●</span> {load_level} traffic volume", 
                   unsafe_allow_html=True)
    
    # Port activity analysis
    st.subheader("🔌 Port Activity Analysis")
    
    port_details = data.get('port_details', [])
    if port_details:
        # Separate TCP and UDP ports
        tcp_ports = [p for p in port_details if p.get('protocol') == 'tcp']
        udp_ports = [p for p in port_details if p.get('protocol') == 'udp']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if tcp_ports:
                tcp_data = pd.DataFrame(tcp_ports)
                tcp_data = tcp_data[tcp_data['connections'] > 0]  # Only show active ports
                
                if not tcp_data.empty:
                    fig_tcp = px.bar(
                        tcp_data,
                        x='port',
                        y='connections',
                        title="TCP Port Activity",
                        labels={'port': 'Port', 'connections': 'Connections'}
                    )
                    st.plotly_chart(fig_tcp, use_container_width=True)
                else:
                    st.info("No active TCP ports")
        
        with col2:
            if udp_ports:
                udp_data = pd.DataFrame(udp_ports)
                udp_data = udp_data[udp_data['packets'] > 0]  # Only show active ports
                
                if not udp_data.empty:
                    fig_udp = px.bar(
                        udp_data,
                        x='port',
                        y='packets',
                        title="UDP Port Activity",
                        labels={'port': 'Port', 'packets': 'Packets'}
                    )
                    st.plotly_chart(fig_udp, use_container_width=True)
                else:
                    st.info("No active UDP ports")
        
        # Advanced Port Analysis
        st.subheader("� Advanced Port Analysis")
        
        # Filter active ports
        active_ports = [p for p in port_details if 
                       (p.get('protocol') == 'tcp' and p.get('connections', 0) > 0) or
                       (p.get('protocol') == 'udp' and p.get('packets', 0) > 0)]
        
        if active_ports:
            df_ports = pd.DataFrame(active_ports)
            
            # Add calculated fields
            df_ports['Activity_Score'] = df_ports.apply(
                lambda row: row.get('connections', 0) if row['protocol'] == 'tcp' 
                else row.get('packets', 0), axis=1
            )
            df_ports['Usage_Percent'] = (df_ports['Activity_Score'] / 
                                       df_ports['Activity_Score'].sum() * 100).round(1)
            
            # Create enhanced table
            display_df = df_ports.rename(columns={
                'port': 'Port',
                'protocol': 'Protocol', 
                'connections': 'Connections',
                'packets': 'Packets',
                'Activity_Score': 'Activity Score',
                'Usage_Percent': 'Usage %'
            })
            
            st.dataframe(display_df, use_container_width=True)
            
            # Port utilization heatmap
            col1, col2 = st.columns(2)
            
            with col1:
                # Top ports by activity
                top_ports = df_ports.nlargest(5, 'Activity_Score')[['port', 'protocol', 'Activity_Score']]
                fig_top = px.bar(
                    top_ports, 
                    x='port', 
                    y='Activity_Score',
                    color='protocol',
                    title="Top 5 Most Active Ports",
                    labels={'Activity_Score': 'Activity Score', 'port': 'Port Number'}
                )
                st.plotly_chart(fig_top, use_container_width=True)
                
            with col2:
                # Protocol distribution pie chart
                protocol_stats = df_ports.groupby('protocol')['Activity_Score'].sum().reset_index()
                fig_proto = px.pie(
                    protocol_stats,
                    values='Activity_Score',
                    names='protocol',
                    title="Activity by Protocol",
                    color_discrete_sequence=['#FF9F9B', '#95E1D3']
                )
                st.plotly_chart(fig_proto, use_container_width=True)
                
        else:
            st.info("No active ports detected")
            
        # Firewall Effectiveness Analysis
        st.subheader("🛡️ Firewall Effectiveness Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            active_port_count = len(active_ports)
            total_monitored = len(port_details)
            blocked_ports = total_monitored - active_port_count
            st.metric("Active Ports", active_port_count)
            st.metric("Blocked/Inactive", blocked_ports)
            
        with col2:
            if total_monitored > 0:
                effectiveness = (blocked_ports / total_monitored * 100)
                st.metric("Firewall Effectiveness", f"{effectiveness:.1f}%",
                         help="Percentage of monitored ports that remained inactive")
                
        with col3:
            if active_port_count > 0:
                avg_activity = sum(p.get('connections', 0) + p.get('packets', 0) 
                                 for p in active_ports) / active_port_count
                st.metric("Avg Port Activity", f"{avg_activity:.1f}",
                         help="Average activity score per active port")

def main():
    """Main dashboard application."""
    st.title("🔥 TUS Firewall Test Suite Dashboard")
    st.markdown("Real-time visualization of firewall test results")
    
    # Sidebar for file selection and controls
    st.sidebar.header("📁 Report Selection")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh", value=True)
    
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 10, REFRESH_INTERVAL)
        time.sleep(refresh_interval)
        st.rerun()
    
    # Get available reports
    client_reports, server_reports = get_available_reports()
    
    if not client_reports and not server_reports:
        st.warning("No report files found in the `results` directory. Run some tests first!")
        st.info("Reports will appear here automatically once tests are completed.")
        return
    
    # File selection
    st.sidebar.subheader("📊 Available Reports")
    
    selected_client = None
    selected_server = None
    
    if client_reports:
        client_options = [os.path.basename(f) for f in client_reports]
        selected_client_idx = st.sidebar.selectbox(
            "Client Reports",
            range(len(client_options)),
            format_func=lambda i: f"{client_options[i]} ({format_timestamp(client_options[i].split('-')[2].split('.')[0])})"
        )
        selected_client = client_reports[selected_client_idx]
    
    if server_reports:
        server_options = [os.path.basename(f) for f in server_reports]
        selected_server_idx = st.sidebar.selectbox(
            "Server Reports", 
            range(len(server_options)),
            format_func=lambda i: f"{server_options[i]} ({format_timestamp(server_options[i].split('-')[2].split('.')[0])})"
        )
        selected_server = server_reports[selected_server_idx]
    
    # Display reports
    tab1, tab2, tab3, tab4 = st.tabs(["🎮 Client Analysis", "🛡️ Server Analysis", "� Aggregated Stats", "�📄 Raw Data"])
    
    with tab1:
        if selected_client:
            client_data = load_json_report(selected_client)
            if client_data:
                display_client_report(client_data)
        else:
            st.info("No client reports available")
    
    with tab2:
        if selected_server:
            server_data = load_json_report(selected_server)
            if server_data:
                display_server_report(server_data)
        else:
            st.info("No server reports available")
    
    with tab3:
        if selected_client and selected_server:
            client_data = load_json_report(selected_client)
            server_data = load_json_report(selected_server)
            if client_data and server_data:
                display_aggregated_statistics(client_data, server_data)
        else:
            st.info("Both client and server reports needed for aggregated statistics")
    
    with tab4:
        st.subheader("📄 Raw Report Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if selected_client:
                st.subheader("Client Data")
                client_data = load_json_report(selected_client)
                if client_data:
                    st.json(client_data)
        
        with col2:
            if selected_server:
                st.subheader("Server Data") 
                server_data = load_json_report(selected_server)
                if server_data:
                    st.json(server_data)
    
    # Footer info
    st.sidebar.markdown("---")
    st.sidebar.info(f"📂 Monitoring: `{RESULTS_DIR}/`")
    st.sidebar.info(f"🔄 Last updated: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()