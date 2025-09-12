# NFTables Testing Framework Makefile

.PHONY: help game basic direct clean build setup logs

# Default target
help:
	@echo "NFTables Testing Framework"
	@echo "========================="
	@echo ""
	@echo "Available commands:"
	@echo "  make game    - Run complete game simulation (18 players, 2 minutes)"
	@echo "  make basic   - Run basic rule testing"
	@echo "  make direct  - Run direct Linux execution (requires sudo)"
	@echo "  make build   - Build Docker images"
	@echo "  make clean   - Clean up containers and results"
	@echo "  make logs    - Show recent test results"
	@echo "  make setup   - Initial project setup"
	@echo ""

# Run complete game simulation
game:
	@echo "🎮 Starting game simulation..."
	./scripts/run-game-simulation.sh

# Run basic testing
basic:
	@echo "🔧 Starting basic rule testing..."
	docker-compose -f docker/docker-compose.yml up --build

# Run direct execution
direct:
	@echo "🖥️  Starting direct execution..."
	@if [ "$$(id -u)" -eq 0 ]; then \
		./scripts/run-direct.sh; \
	else \
		sudo ./scripts/run-direct.sh; \
	fi

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose -f docker/docker-compose-game.yml build

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f docker/docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker-compose -f docker/docker-compose-game.yml down --remove-orphans 2>/dev/null || true
	docker system prune -f
	@echo "Results preserved in ./results/"

# Show logs
logs:
	@echo "📊 Recent test results:"
	@ls -la results/ 2>/dev/null || echo "No results found. Run a test first."
	@echo ""
	@if [ -f results/nftables-test-results.log ]; then \
		echo "Latest log (last 20 lines):"; \
		tail -n 20 results/nftables-test-results.log; \
	fi

# Initial setup
setup:
	@echo "⚙️  Setting up project..."
	mkdir -p results
	chmod +x scripts/*.sh launcher.sh
	@echo "✅ Project setup complete!"
	@echo ""
	@echo "Quick start:"
	@echo "  make game    # Full simulation"
	@echo "  make basic   # Basic testing"
	@echo "  ./launcher.sh # Interactive menu"