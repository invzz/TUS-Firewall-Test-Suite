#!/bin/bash

echo "=== NFTables Testing Script ==="

# Function to display current nftables rules
show_rules() {
    echo ""
    echo "Current NFTables Rules:"
    nft list ruleset
}

# Function to load the nftables configuration
load_rules() {
    echo ""
    echo "Loading nftables configuration..."
    if nft -f /etc/nftables/nftables.conf; then
        echo "✓ NFTables rules loaded successfully"
    else
        echo "✗ Failed to load NFTables rules"
        exit 1
    fi
}

# Function to test connectivity
test_connectivity() {
    local port=$1
    local protocol=${2:-tcp}
    local host=${3:-127.0.0.1}
    
    echo ""
    echo "Testing ${protocol}/${port} connectivity to ${host}..."
    
    if [ "$protocol" = "tcp" ]; then
        if nc -z -w3 $host $port 2>/dev/null; then
            echo "✓ TCP port $port is accessible"
        else
            echo "✗ TCP port $port is blocked or unreachable"
        fi
    elif [ "$protocol" = "udp" ]; then
        # UDP test is trickier, we'll use nc with a timeout
        if timeout 3 nc -u -z $host $port 2>/dev/null; then
            echo "✓ UDP port $port seems accessible"
        else
            echo "✗ UDP port $port appears blocked"
        fi
    fi
}

# Function to test ping limits
test_ping_limits() {
    echo ""
    echo "Testing ping rate limiting..."
    echo "Sending 5 pings rapidly:"
    ping -c 5 -i 0.1 127.0.0.1 2>/dev/null || echo "Ping test failed or limited"
}

# Function to simulate various connection tests
run_connection_tests() {
    echo ""
    echo "Running connection tests for configured ports..."
    
    # Test some of the allowed TCP ports
    test_connectivity 21 tcp    # FTP
    test_connectivity 1194 tcp  # VPN
    test_connectivity 6567 tcp  # Custom service
    test_connectivity 22 tcp    # SSH (should be rejected)
    
    # Test some UDP ports
    test_connectivity 6962 udp
    test_connectivity 9090 udp
    test_connectivity 19999 udp
    
    # Test blocked ports
    test_connectivity 80 tcp   # Should be dropped
    test_connectivity 443 tcp  # Should be dropped
}

# Function to show network interfaces and routes
show_network_info() {
    echo ""
    echo "Network Information:"
    echo "Interfaces:"
    ip addr show
    echo -e "\nRoutes:"
    ip route show
}

# Function to monitor traffic
monitor_traffic() {
    echo ""
    echo "Starting traffic monitoring (Ctrl+C to stop)..."
    echo "This will show packets matching nftables rules:"
    nft monitor
}

# Function to test specific game server ports
test_game_servers() {
    echo ""
    echo "Testing game server ports..."
    
    # UT server ports based on your config
    local ut_ports=(6962 6963 9696 9697 7787 7797 9090 9091 5555 5556 7766 7767)
    
    for port in "${ut_ports[@]}"; do
        test_connectivity $port udp
    done
}

# Function to simulate DOS attack (for testing rate limiting)
test_rate_limiting() {
    echo ""
    echo "Testing rate limiting on UDP port 6962..."
    echo "Sending rapid UDP packets to test rate limiting:"
    
    for i in {1..40}; do
        echo "test packet $i" | nc -u -w1 127.0.0.1 6962 &
    done
    wait
    echo "Rate limiting test completed"
}

# Main menu
show_menu() {
    echo ""
    echo "Available actions:"
    echo "1. Load nftables rules"
    echo "2. Show current rules"
    echo "3. Test basic connectivity"
    echo "4. Test ping rate limiting"
    echo "5. Test game server ports"
    echo "6. Test rate limiting"
    echo "7. Show network information"
    echo "8. Monitor traffic (live)"
    echo "9. Run all tests"
    echo "0. Exit"
}

# Main execution
case "${1:-menu}" in
    "load")
        load_rules
        ;;
    "show")
        show_rules
        ;;
    "test")
        run_connection_tests
        ;;
    "ping")
        test_ping_limits
        ;;
    "game")
        test_game_servers
        ;;
    "rate")
        test_rate_limiting
        ;;
    "network")
        show_network_info
        ;;
    "monitor")
        monitor_traffic
        ;;
    "all")
        load_rules
        show_rules
        run_connection_tests
        test_ping_limits
        test_game_servers
        show_network_info
        ;;
    "menu"|*)
        show_menu
        echo ""
        echo "Usage: $0 [load|show|test|ping|game|rate|network|monitor|all|menu]"
        echo "Or run interactively and choose from the menu"
        ;;
esac