# Dashboard Integration Guide

## 🎯 Container-Based Dashboard Options

The TUS Firewall Test Suite now includes integrated Streamlit dashboard containers that automatically serve results visualization alongside your tests.

### **🎮 Game Simulation with Dashboard**
```bash
# Runs: NFTables Server + Game Clients + Dashboard
docker-compose -f docker/docker-compose-game.yml up --build

# Access dashboard at: http://localhost:8501
```

### **🛠️ Basic Testing with Dashboard**  
```bash
# Runs: NFTables Server + Dashboard
docker-compose -f docker/docker-compose.yml up --build

# Access dashboard at: http://localhost:8501
```

### **📊 Dashboard Only Mode**
```bash
# Runs: Dashboard only (views existing results)
docker-compose -f docker/docker-compose-dashboard.yml up --build

# Access dashboard at: http://localhost:8501
```

## 🚀 Easy Access via Launchers

### **Windows**
```bash
.\launcher.bat

# Options:
# 1. Complete Game Simulation (with Dashboard) 
# 2. Basic Rule Testing (with Dashboard)
# 4. Dashboard Only (view existing results)
# 5. Local Dashboard (Python venv)
```

### **Linux/macOS**
```bash
./launcher.sh

# Options:
# 1. Complete Game Simulation (with Dashboard)
# 2. Basic Rule Testing (with Dashboard) 
# 5. Dashboard Only (view existing results)
# 6. Local Dashboard (Python venv)
```

## 📱 Dashboard Features

- **🔄 Real-time Updates**: Automatically detects new test results
- **📊 Interactive Charts**: Client performance, server metrics, port activity
- **🎮 Multi-tab Interface**: Client Analysis, Server Analysis, Raw Data
- **📈 Traffic Visualization**: Protocol distribution, success rates
- **👥 Player Performance**: Individual client statistics and comparisons
- **🛡️ Firewall Analysis**: Port activity, connection patterns

## 🐳 Container Architecture

```
Game Simulation Stack:
├── nftables-server (Ubuntu + NFTables)
├── game-client (Python clients)
└── dashboard (Streamlit + Volume access)

Basic Testing Stack:
├── nftables-test (Ubuntu + NFTables)  
└── dashboard (Streamlit + Volume access)

Dashboard Only:
└── dashboard (Streamlit + Results viewer)
```

## 📂 Volume Mapping

All containers share results via volume mapping:
- **Server/Client containers**: Write to `/shared` → `./results/`
- **Dashboard container**: Read from `/app/results` ← `./results/` (read-only)

## 🌐 Network Access

- **Local**: http://localhost:8501
- **LAN**: http://[your-ip]:8501 (accessible from other devices)
- **Auto-opens**: Browser launches automatically in local mode

## 🔧 Configuration

Dashboard container environment variables:
```yaml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

Health check ensures dashboard reliability:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

Your firewall testing now includes professional web-based visualization right out of the box! 🎉