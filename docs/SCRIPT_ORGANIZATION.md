# Script Organization Guide

## 🎯 **Clean Main Directory**

The main directory now contains only the essential launcher files:

```
TUS-Firewall-Test-Suite/
├── launcher.bat          # Windows main launcher
├── launcher.sh           # Linux main launcher  
├── dashboard.py          # Dashboard application
├── requirements-dashboard.txt
└── scripts/
    ├── windows/          # Windows-specific utilities
    └── linux/            # Linux-specific utilities
```

## 📁 **Windows Scripts Directory**

Located in `scripts/windows/`:

- **`dashboard-launcher-venv.bat`** - Virtual environment dashboard launcher
- **`dashboard-launcher.bat`** - Basic dashboard launcher
- **`setup-dashboard-venv.bat`** - Virtual environment setup
- **`test-docker-compose.bat`** - Docker compose validation

## 🐧 **Linux Scripts Directory**  

Located in `scripts/linux/`:

- **`dashboard-launcher-venv.sh`** - Virtual environment dashboard launcher
- **`dashboard-launcher.sh`** - Basic dashboard launcher
- **`setup-dashboard-venv.sh`** - Virtual environment setup
- **`run-auto-tests.sh`** - Automated testing script
- **`run-direct.sh`** - Direct execution script
- **`run-game-simulation.sh`** - Game simulation script

## 🚀 **Usage Patterns**

### **Main Launchers (Recommended)**
```bash
# Windows
.\launcher.bat

# Linux  
./launcher.sh
```

### **Direct Platform Scripts**
```bash
# Windows utilities
.\scripts\windows\setup-dashboard-venv.bat
.\scripts\windows\dashboard-launcher-venv.bat

# Linux utilities
./scripts/linux/setup-dashboard-venv.sh
./scripts/linux/dashboard-launcher-venv.sh
```

## ✅ **Benefits of Organization**

1. **Clean Main Directory**: Only essential launchers in root
2. **Platform Separation**: Windows/Linux scripts clearly separated
3. **Correct Path References**: All relative paths updated for new locations
4. **Maintainability**: Easier to find and maintain platform-specific code
5. **Scalability**: Easy to add new platform-specific utilities

## 🔧 **Updated Paths**

All scripts have been updated with correct relative paths:
- Virtual environment: `../../venv-dashboard/`
- Requirements file: `../../requirements-dashboard.txt`  
- Dashboard application: `../../dashboard.py`

## 🐳 **Docker Integration Updates**

Docker files updated to reference new script locations:
- **Dockerfile.server**: `scripts/linux/run-auto-tests.sh`
- **docker-compose.yml**: `scripts/linux/run-auto-tests.sh`
- **launcher.sh**: `scripts/linux/run-direct.sh`

## 📚 **Documentation Updates**

Updated documentation files:
- **README.md**: Script paths corrected
- **docs/README.md**: Script paths corrected  
- **DASHBOARD_SETUP.md**: Platform-specific paths

## ✅ **Validation**

Use the validation script to verify all updates:
```bash
# Windows
.\scripts\windows\validate-docker-updates.bat

# All Docker compose files validated
# All script paths verified
# Ready for deployment
```

Your TUS Firewall Test Suite now has a clean, organized structure with full Docker integration! 🎉