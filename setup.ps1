# NFTables Testing Framework Setup Script for Windows
# Run this in PowerShell as Administrator if needed

Write-Host "🔥 NFTables Testing Framework Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Create results directory if it doesn't exist
if (!(Test-Path "results")) {
    New-Item -ItemType Directory -Name "results" | Out-Null
    Write-Host "✅ Created results directory" -ForegroundColor Green
}

# Check Docker availability
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check docker-compose availability
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "📁 Project Structure:" -ForegroundColor Yellow
Get-ChildItem -Directory | Select-Object Name | Format-Table -HideTableHeaders

Write-Host ""
Write-Host "🚀 Ready to run tests!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick start options:" -ForegroundColor Cyan
Write-Host "  .\launcher.sh              # Interactive menu (if using WSL/Git Bash)" -ForegroundColor White
Write-Host "  make game                  # Complete simulation (if using WSL/Git Bash)" -ForegroundColor White
Write-Host "  .\scripts\run-game-simulation.sh  # Direct script execution" -ForegroundColor White
Write-Host ""
Write-Host "Windows PowerShell commands:" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker\docker-compose.yml up --build" -ForegroundColor White
Write-Host "  docker-compose -f docker\docker-compose-game.yml up --build" -ForegroundColor White

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green