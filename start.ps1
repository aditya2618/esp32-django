# Quick Start Script for ESP32 Smart Home Platform

Write-Host "🏠 ESP32 Smart Home Platform - Quick Start" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

$PYTHON_PATH = "h:\aditya\esp32-django\esp32\Scripts\python.exe"
$PROJECT_DIR = "h:\aditya\esp32-django\smarthome"

# Check if Python exists
if (-not (Test-Path $PYTHON_PATH)) {
    Write-Host "❌ Python not found at: $PYTHON_PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python found" -ForegroundColor Green

# Navigate to project directory
Set-Location $PROJECT_DIR

# Check if migrations are applied
Write-Host ""
Write-Host "Checking database..." -ForegroundColor Cyan
& $PYTHON_PATH manage.py migrate --check

if ($LASTEXITCODE -ne 0) {
    Write-Host "Applying migrations..." -ForegroundColor Yellow
    & $PYTHON_PATH manage.py migrate
}

Write-Host ""
Write-Host "✓ Database ready" -ForegroundColor Green

# Check if superuser exists
Write-Host ""
Write-Host "📋 Important URLs:" -ForegroundColor Cyan
Write-Host "   Web UI:     http://localhost:8000" -ForegroundColor White
Write-Host "   Admin:      http://localhost:8000/admin" -ForegroundColor White
Write-Host ""

# MQTT Configuration reminder
Write-Host "⚙️  MQTT Configuration:" -ForegroundColor Cyan
Write-Host "   Edit config/settings.py and set:" -ForegroundColor White
Write-Host "   - MQTT_BROKER = 'your-mqtt-broker-ip'" -ForegroundColor Yellow
Write-Host "   - MQTT_USERNAME (if needed)" -ForegroundColor Yellow
Write-Host "   - MQTT_PASSWORD (if needed)" -ForegroundColor Yellow
Write-Host ""

# Start server
Write-Host "🚀 Starting Django development server..." -ForegroundColor Green
Write-Host ""
& $PYTHON_PATH manage.py runserver
