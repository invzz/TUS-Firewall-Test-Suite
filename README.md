# NFTables Testing Framework

Professional firewall rule validation with realistic traffic simulation.

## 🚀 Quick Start

```bash
# Complete game simulation (18 players, 2 minutes)
./scripts/linux/run-game-simulation.sh

# Basic rule testing
docker-compose -f docker/docker-compose.yml up --build

# Direct Linux execution (requires sudo)
sudo ./scripts/linux/run-direct.sh
```

## 📁 Project Structure

See `docs/README.md` for complete documentation.

## 📊 Reports

Check `results/` folder after testing:
- `server-report-*.json` - Server performance
- `client-report-*.json` - Client traffic stats  
- `*.log` - Detailed logs

## 🎯 Features

✅ Realistic game traffic simulation  
✅ 18 concurrent players  
✅ Comprehensive reporting  
✅ Rate limiting validation  
✅ Professional Docker setup  

---

**Quick Links:** [Documentation](docs/README.md) | [Configuration](config/) | [Scripts](scripts/)