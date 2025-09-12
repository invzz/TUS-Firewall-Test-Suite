# Dashboard Setup Guide

## Quick Start

### Windows
```bash
# Option 1: Automatic setup via main launcher
.\launcher.bat
# Select option 4: Results Dashboard

# Option 2: Manual setup
.\scripts\windows\setup-dashboard-venv.bat        # One-time setup
.\scripts\windows\dashboard-launcher-venv.bat     # Launch dashboard
```

### Linux/macOS
```bash
# Option 1: Automatic setup via main launcher
./launcher.sh
# Select option 5: Results Dashboard

# Option 2: Manual setup
chmod +x scripts/linux/setup-dashboard-venv.sh
./scripts/linux/setup-dashboard-venv.sh         # One-time setup
./scripts/linux/dashboard-launcher-venv.sh      # Launch dashboard
```

## What Gets Installed

The setup creates a Python virtual environment with these packages:
- `streamlit` - Web dashboard framework
- `plotly` - Interactive charts
- `pandas` - Data processing
- `watchdog` - File system monitoring

## Virtual Environment Details

- **Location**: `venv-dashboard/` (automatically created)
- **Isolated**: Doesn't affect your system Python
- **Persistent**: Created once, reused for future launches
- **Auto-managed**: Setup and activation handled automatically

## Accessing the Dashboard

Once launched, the dashboard opens at: **http://localhost:8501**

## Features

- 🔄 **Auto-refresh**: Monitors `results/` folder for new reports
- 📊 **Interactive Charts**: Real-time visualization of test data
- 🎮 **Client Analysis**: Player performance, traffic patterns
- 🛡️ **Server Analysis**: Port activity, connection metrics
- 📱 **Web-based**: Access from any browser on your network

## Troubleshooting

If you encounter issues:

1. **Python not found**: Install Python 3.8+ and ensure it's in your PATH
2. **Permission errors**: On Linux, run `chmod +x *.sh` to make scripts executable
3. **Network issues**: Check if port 8501 is available
4. **Dependencies fail**: Ensure you have internet access for package installation

The virtual environment keeps everything clean and isolated from your system Python installation!