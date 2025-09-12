#!/bin/bash

# NFTables Testing Framework Launcher

echo "🔥 NFTables Testing Framework"
echo "================================"
echo ""
echo "Select testing mode:"
echo "1. Complete Game Simulation (18 players, 2 minutes) [Recommended]"
echo "2. Basic Rule Testing (no client simulation)"
echo "3. Direct Linux Execution (requires sudo)"
echo "4. Interactive Server Mode (keeps running)"
echo "5. Show Project Structure"
echo "0. Exit"
echo ""
read -p "Enter your choice (0-5): " choice

case $choice in
    1)
        echo "Starting complete game simulation..."
        ./scripts/run-game-simulation.sh
        ;;
    2)
        echo "Starting basic rule testing..."
        docker-compose -f docker/docker-compose.yml up --build
        ;;
    3)
        echo "Starting direct execution (requires sudo)..."
        if [ "$EUID" -ne 0 ]; then
            echo "Switching to sudo..."
            sudo ./scripts/run-direct.sh
        else
            ./scripts/run-direct.sh
        fi
        ;;
    4)
        echo "Starting interactive server mode..."
        KEEP_RUNNING=true docker-compose -f docker/docker-compose.yml up --build
        ;;
    5)
        echo ""
        echo "📁 Project Structure:"
        tree -L 3 -I 'results|__pycache__'
        echo ""
        echo "📊 Results Location: ./results/"
        ls -la results/ 2>/dev/null || echo "  (No results yet - run a test first)"
        ;;
    0)
        echo "Goodbye! 👋"
        ;;
    *)
        echo "Invalid choice. Please run again."
        exit 1
        ;;
esac