# NFTables Testing Framework

Professional firewall rule validation with realistic traffic simulation.

## 🚀 Quick Start

```bash
# Complete game simulation (18 players, 2 minutes)
./scripts/linux/run-game-simulation.sh

# Basic rule testing
docker-compose -f configs/docker/docker-compose.yml up --build

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
✅ Real container integration tests

## 🧪 Testing

```bash
# Unit tests (fast)
pytest tests/unit/ -v

# Integration tests (with mocks)  
pytest tests/integration/ -v -m "not container"

# Container tests (real Docker containers)
pytest tests/integration/test_containers.py -v

# All tests
pytest -v
```

See [Testcontainer Tests Documentation](docs/TESTCONTAINER_TESTS.md) for detailed testing guide.

---

**Quick Links:** [Documentation](docs/README.md) | [Testing Guide](docs/TESTCONTAINER_TESTS.md) | [Configuration](config/) | [Scripts](scripts/)