# Quick Start Script for ESP32 Smart Home Platform

Write-Host "ESP32 Smart Home Platform - Quick Start" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Get the directory where the script is located
$SCRIPT_DIR = $PSScriptRoot
$PYTHON_PATH = Join-Path $SCRIPT_DIR "esp32\Scripts\python.exe"
$MOSQUITTO_PATH = "C:\Program Files\mosquitto\mosquitto.exe"
$MOSQUITTO_CONF = Join-Path $SCRIPT_DIR "mosquitto.conf"

# Check if Python exists
if (-not (Test-Path $PYTHON_PATH)) {
    Write-Host "Error: Python not found at: $PYTHON_PATH" -ForegroundColor Red
    Write-Host "Please ensure you have run the setup instructions."
    exit 1
}
Write-Host "Python found" -ForegroundColor Green

# 1. Setup Firewall for MQTT
Write-Host ""
Write-Host "Checking Firewall Rules..." -ForegroundColor Cyan
$ruleName = "Allow MQTT"
$ruleExists = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if (-not $ruleExists) {
    Write-Host "Creating firewall rule '$ruleName' for port 1883..." -ForegroundColor Yellow
    try {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort 1883 -Protocol TCP -Action Allow -Profile Any | Out-Null
        Write-Host "Firewall rule created." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to create firewall rule. Please run as Administrator or add manually." -ForegroundColor Red
    }
} else {
    Write-Host "Firewall rule '$ruleName' exists." -ForegroundColor Green
}

# 2. Start Mosquitto
Write-Host ""
Write-Host "Starting Mosquitto MQTT Broker..." -ForegroundColor Cyan

# Check if Mosquitto is already running
$mqttProcess = Get-Process mosquitto -ErrorAction SilentlyContinue
if ($mqttProcess) {
    Write-Host "Mosquitto is already running." -ForegroundColor Yellow
} else {
    if (Test-Path $MOSQUITTO_PATH) {
        # Start Mosquitto in the background
        Start-Process -FilePath $MOSQUITTO_PATH -ArgumentList "-c `"$MOSQUITTO_CONF`" -v" -WindowStyle Minimized
        Write-Host "Mosquitto started (minimized)." -ForegroundColor Green
    } else {
        Write-Host "Error: Mosquitto executable not found at '$MOSQUITTO_PATH'." -ForegroundColor Red
        Write-Host "Please install Mosquitto or check the path."
    }
}

# 3. Database Check
Write-Host ""
Write-Host "Checking database..." -ForegroundColor Cyan
& $PYTHON_PATH manage.py migrate --check

if ($LASTEXITCODE -ne 0) {
    Write-Host "Applying migrations..." -ForegroundColor Yellow
    & $PYTHON_PATH manage.py migrate
}
Write-Host "Database ready" -ForegroundColor Green

# 4. Start Django
Write-Host ""
Write-Host "Important URLs:" -ForegroundColor Cyan
Write-Host "   Web UI:     http://localhost:8000" -ForegroundColor White
Write-Host "   Admin:      http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "Starting Django development server..." -ForegroundColor Green
Write-Host ""

& $PYTHON_PATH manage.py runserver
