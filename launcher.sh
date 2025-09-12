#!/bin/bash

# NFTables Testing Framework Launcher

select_env_and_run_game() {
    echo ""
    echo "🎮 Select test configuration:"
    echo "1. Light Testing (5 clients, 30s) - Quick validation ⚡"
    echo "2. Normal Testing (25 clients, 3min) - Realistic load 🎯"  
    echo "3. Stress Testing (100 clients, 5min) - High load 🔥"
    echo "4. Performance Testing (500 clients, 10min) - Very high load 💪"
    echo "5. Default (.env or built-in defaults)"
    echo ""
    read -p "Enter configuration (1-5): " env_choice

    case $env_choice in
        1)
            echo "Starting light testing configuration..."
            docker-compose --env-file .env.light -f docker/docker-compose-game.yml up --build
            ;;
        2)
            echo "Starting normal testing configuration..."
            docker-compose --env-file .env.normal -f docker/docker-compose-game.yml up --build
            ;;
        3)
            echo "Starting stress testing configuration..."
            docker-compose --env-file .env.stress -f docker/docker-compose-game.yml up --build
            ;;
        4)
            echo "Starting performance testing configuration..."
            echo "⚠️  WARNING: This will use significant system resources!"
            read -p "Continue? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                docker-compose --env-file .env.performance -f docker/docker-compose-game.yml up --build
            else
                echo "Performance test cancelled."
            fi
            ;;
        5)
            echo "Starting with default configuration..."
            docker-compose -f docker/docker-compose-game.yml up --build
            ;;
        *)
            echo "Invalid choice, using default configuration..."
            docker-compose -f docker/docker-compose-game.yml up --build
            ;;
    esac
}

echo "🔥 NFTables Testing Framework"
echo "================================"
echo ""
echo "Select testing mode:"
echo "1. Complete Game Simulation [Recommended] 🎮"
echo "2. Basic Rule Testing (no client simulation) 🛠️"
echo "3. Direct Linux Execution (requires sudo) 🐧"
echo "4. Interactive Server Mode (keeps running) 🔄"
echo "5. Show Project Structure 📁"
echo "0. Exit 👋"
echo ""
read -p "Enter your choice (0-5): " choice

case $choice in
    1)
        select_env_and_run_game
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
        tree -L 3 -I 'results|__pycache__' 2>/dev/null || find . -maxdepth 3 -type d | head -20
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