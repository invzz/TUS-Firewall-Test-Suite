# TUS Firewall Test Suite - Professional Folder Structure Plan

## Current Structure Issues:
- Root directory is cluttered with temporary Python files
- Configuration files scattered across multiple locations
- No clear separation between tools, configs, and documentation
- Mixed development and production files

## New Professional Structure:

```
TUS-Firewall-Test-Suite/
├── README.md                    # Main project documentation
├── LICENSE                      # Project license
├── Makefile                     # Build automation
├── .gitignore                   # Git ignore rules
│
├── cmd/                         # Main applications and launchers
│   ├── launcher.bat            # Windows launcher
│   ├── launcher.sh             # Linux launcher
│   └── setup.ps1               # Windows setup script
│
├── configs/                     # All configuration files
│   ├── environments/           # Environment-specific configs
│   │   ├── .env.example
│   │   ├── .env.light
│   │   ├── .env.normal
│   │   ├── .env.stress
│   │   ├── .env.performance
│   │   └── .env.ut-specs
│   ├── nftables/               # NFTables configurations
│   │   └── nftables.conf
│   └── docker/                 # Docker configurations
│       ├── docker-compose.yml
│       ├── docker-compose-game.yml
│       ├── docker-compose-dashboard.yml
│       ├── Dockerfile.client
│       ├── Dockerfile.server
│       └── Dockerfile.dashboard
│
├── src/                         # Source code
│   ├── client/                 # Game client simulator
│   │   ├── __init__.py
│   │   ├── game_client.py
│   │   ├── client_manager.py
│   │   ├── player_stats.py
│   │   └── game-client-simulator.py
│   ├── server/                 # NFTables test server
│   │   ├── __init__.py
│   │   └── nftables-test-server.py
│   ├── dashboard/              # Dashboard application
│   │   ├── __init__.py
│   │   └── dashboard.py
│   └── utils/                  # Shared utilities
│       ├── __init__.py
│       ├── test-nftables.sh
│       ├── enhanced-test.sh
│       └── authentic_ut_specs.py
│
├── scripts/                     # Build and deployment scripts
│   ├── linux/                 # Linux-specific scripts
│   │   ├── run-auto-tests.sh
│   │   ├── run-direct.sh
│   │   ├── run-game-simulation.sh
│   │   ├── dashboard-launcher.sh
│   │   └── dashboard-launcher-venv.sh
│   └── windows/               # Windows-specific scripts
│       ├── dashboard-launcher.bat
│       └── dashboard-launcher-venv.bat
│
├── docs/                       # Documentation
│   ├── README.md
│   ├── README.pdf
│   ├── DASHBOARD_SETUP.md
│   ├── SCRIPT_ORGANIZATION.md
│   ├── api/                   # API documentation
│   └── deployment/            # Deployment guides
│
├── tests/                      # Test files
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data
│
├── build/                      # Build artifacts
├── dist/                       # Distribution packages
├── results/                    # Test results output
└── tools/                      # Development tools and helpers
    ├── requirements.txt
    ├── requirements-dashboard.txt
    └── dev-requirements.txt
```

## Benefits of This Structure:
1. **Clear separation of concerns** - configs, source, docs, scripts
2. **Industry standard layout** - follows common practices
3. **Scalable and maintainable** - easy to add new components
4. **CI/CD friendly** - clear build and deployment paths
5. **Docker optimized** - organized for container builds
6. **Development friendly** - clear tool and utility organization

## Migration Plan:
1. Create new directory structure
2. Move files to appropriate locations
3. Update all path references in scripts
4. Update Docker configurations
5. Update documentation
6. Test all functionality