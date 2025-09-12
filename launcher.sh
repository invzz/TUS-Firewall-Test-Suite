#!/bin/bash#!/bin/bash



# NFTables Testing Framework - Main Linux Launcher# NFTables Testing Framework - Main Linux Launcher

# This is a convenience wrapper that calls the actual launcher in cmd/# This is a convenience wrapper that calls the actual launcher in cmd/



echo ""echo ""

echo "================================"echo "================================"

echo "NFTables Testing Framework"echo "NFTables Testing Framework"

echo "================================"echo "================================"

echo ""echo ""

echo "Launching main application..."echo "Launching main application..."

echo ""echo ""



# Get the directory of this script# Get the directory of this script

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"



# Change to that directory and run the actual launcher# Change to that directory and run the actual launcher

cd "$DIR"cd "$DIR"

chmod +x cmd/launcher.shchmod +x cmd/launcher.sh

./cmd/launcher.sh./cmd/launcher.sh

echo "Launching main application..."    echo "4. Performance Testing (500 clients, 10min) - Very high load 💪"

echo ""    echo "5. Authentic UT Server Specs (25 clients, 3min) - Real server simulation 🎯🔥"

    echo "6. Default (.env or built-in defaults)"

# Get the directory of this script    echo ""

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"    read -p "Enter configuration (1-6): " env_choice



# Change to that directory and run the actual launcher    case $env_choice in

cd "$DIR"        1)

chmod +x cmd/launcher.sh            echo "Starting light testing configuration..."

./cmd/launcher.sh            docker-compose --env-file .env.light -f docker/docker-compose-game.yml up --build
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
            echo "Starting authentic UT server specification testing..."
            echo "🎯 Using real server specs for authentic network simulation"
            docker-compose --env-file .env.ut-specs -f docker/docker-compose-game.yml up --build
            ;;
        6)
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
echo "1. Complete Game Simulation (with Dashboard) [Recommended] 🎮"
echo "2. Basic Rule Testing (with Dashboard) 🛠️"
echo "3. Direct Linux Execution (requires sudo) 🐧"
echo "4. Interactive Server Mode (keeps running) 🔄"
echo "5. Dashboard Only (view existing results) 📊"
echo "6. Local Dashboard (Python venv) �️"
echo "7. Show Project Structure 📁"
echo "0. Exit 👋"
echo ""
read -p "Enter your choice (0-7): " choice

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
            sudo ./scripts/linux/run-direct.sh
        else
            ./scripts/linux/run-direct.sh
        fi
        ;;
    4)
        echo "Starting interactive server mode..."
        KEEP_RUNNING=true docker-compose -f docker/docker-compose.yml up --build
        ;;
    5)
        echo "Starting Dashboard Only..."
        echo "This will show existing results from previous tests"
        docker-compose -f docker/docker-compose-dashboard.yml up --build
        ;;
    6)
        echo "Starting Local Dashboard with Virtual Environment..."
        chmod +x scripts/linux/dashboard-launcher-venv.sh
        ./scripts/linux/dashboard-launcher-venv.sh
        ;;
    7)
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