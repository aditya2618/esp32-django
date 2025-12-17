# ESP32 Smart Home Platform

A complete Django-based web application for managing ESP32 smart home devices using ESPHome and MQTT with real-time control and monitoring.

## 🌟 Features

### Device Management
- ✅ **Setup Wizard** - Step-by-step device configuration with WiFi and entity setup
- ✅ **Real-time Status** - Automatic online/offline detection (60-second timeout)
- ✅ **Auto-discovery** - Devices automatically register via MQTT
- ✅ **Live Dashboard** - Auto-refreshing device list (every 5 seconds)

### Entity Control
- ✅ **Switches** - ON/OFF control with real-time state updates
- ✅ **Lights** - ON/OFF control (dimming support ready)
- ✅ **Fans** - Speed control capabilities
- ✅ **Sensors** - Temperature, humidity, and custom sensors
- ✅ **Real-time Updates** - Device detail page refreshes every 2 seconds

### MQTT Integration
- ✅ **Bidirectional Communication** - ESP32 ↔ Django via MQTT
- ✅ **Auto-create Entities** - Devices and entities created automatically from MQTT messages
- ✅ **State Synchronization** - Instant state updates across all clients
- ✅ **Command Publishing** - Send commands to devices via MQTT

### ESPHome Integration
- ✅ **YAML Generation** - Auto-generate ESPHome configurations
- ✅ **Multi-pin Components** - Support for RGB, RGBW, DHT sensors, steppers
- ✅ **ESP32/ESP8266 Support** - Compatible with both platforms
- ✅ **Flash Reader** - Read connected ESP32 device information

### Firmware & OTA
- ✅ **OTA Updates** - Over-the-air firmware updates
- ✅ **Factory Reset** - Remote device reset capability
- ✅ **Firmware Management** - Upload and manage firmware versions

## 🛠️ Technology Stack

- **Backend**: Django 5.2.9
- **Database**: SQLite (development) / PostgreSQL (production)
- **Messaging**: MQTT (Mosquitto) with paho-mqtt
- **Frontend**: Server-rendered HTML with JavaScript auto-refresh
- **Device Firmware**: ESPHome
- **Python**: 3.13+

## 📋 Prerequisites

- **Python 3.13** or higher
- **MQTT Broker** (Mosquitto recommended)
- **ESP32/ESP8266** development boards
- **Windows** (for current setup) or Linux/macOS

## 🚀 Installation

### 1. Clone and Setup Virtual Environment

```powershell
# Navigate to project directory
cd d:\PROJECT\esp32-flasher\esp32-django

# Create virtual environment (if not exists)
python -m venv esp32

# Activate virtual environment
.\esp32\Scripts\activate
```

### 2. Install Dependencies

```powershell
# Install Python packages
pip install -r requirements.txt

# Key packages:
# - Django==5.2.9
# - paho-mqtt==2.1.0
# - esphome
# - pyserial
```

### 3. Database Setup

```powershell
# Apply migrations
python manage.py migrate

# Create superuser (optional, for admin panel)
python manage.py createsuperuser
```

### 4. MQTT Broker Setup (Mosquitto)

#### Install Mosquitto (Windows)

```powershell
# Using Chocolatey
choco install mosquitto

# Or download from: https://mosquitto.org/download/
```

#### Configure Mosquitto for External Access

Create `mosquitto.conf` in project root:

```conf
listener 1883 0.0.0.0
allow_anonymous true
protocol mqtt
```

#### Start Mosquitto

**Option 1: Use the provided batch script (Recommended)**

```powershell
# Run as Administrator
.\start_mqtt_server.bat
```

This script will:
- Stop any existing Mosquitto instances
- Add Windows Firewall rule for port 1883
- Start Mosquitto with the correct configuration

**Option 2: Manual start**

```powershell
# Run as Administrator
"C:\Program Files\mosquitto\mosquitto.exe" -c "d:\PROJECT\esp32-flasher\esp32-django\mosquitto.conf" -v
```

### 5. Configure Django MQTT Settings

Edit `config/settings.py`:

```python
# Find your local IP address first
# Run: ipconfig
# Look for IPv4 Address under your active network adapter

MQTT_BROKER = '192.168.29.91'  # Replace with YOUR local IP
MQTT_PORT = 1883
MQTT_USERNAME = None  # Set if using authentication
MQTT_PASSWORD = None  # Set if using authentication
```

### 6. Run Django Server

```powershell
python manage.py runserver
```

Access the application:
- **Web UI**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin

## 📱 Quick Start Guide

### Step 1: Setup Your First Device

1. Open http://127.0.0.1:8000
2. Click **"🚀 Setup New Device (Wizard)"**
3. Follow the wizard:
   - **Step 1**: Enter device name and home ID
   - **Step 2**: Configure WiFi credentials
   - **Step 3**: Select platform (ESP32/ESP8266)
   - **Step 4**: Add entities (lights, switches, sensors)
   - **Step 5**: Review and generate YAML

### Step 2: Flash Your ESP32

#### Method 1: Using ESPHome CLI (Recommended)

```powershell
# Navigate to generated YAML location
cd media\esphome_builds\your-device-name

# Flash via USB
esphome run your-device-name.yaml

# Select "Plug into this computer"
# Choose your COM port
```

#### Method 2: Using Web Flash Reader

1. Click **"🔍 Read Connected ESP32/ESP8266"**
2. Select COM port
3. Click **"Detect & Read Device Info"**
4. Follow on-screen instructions

### Step 3: Verify MQTT Connection

#### Check Mosquitto Logs

You should see:
```
New connection from 192.168.29.XXX on port 1883.
```

#### Check Django Logs

You should see:
```
Connected to MQTT broker successfully
Subscribed to MQTT topics
Received: home/your_home/your_device/sensor/temperature/state -> 23.5
Created new entity: temperature
Updated your_device - temperature: 23.5
```

### Step 4: Control Your Devices

1. Go to Dashboard
2. Click **"View"** on your device
3. Use ON/OFF buttons to control switches and lights
4. View real-time sensor data

## 🔧 MQTT Topic Structure

### State Topics (ESP32 → Django)
```
home/{home_id}/{node_name}/{entity_type}/{entity_name}/state
home/{home_id}/{node_name}/status  (online/offline)
```

### Command Topics (Django → ESP32)
```
home/{home_id}/{node_name}/{entity_type}/{entity_name}/command
```

### Examples
```
# State updates from ESP32
home/home_test_1/node_1/sensor/room_temp_and_humidity_temperature/state → "21.0"
home/home_test_1/node_1/switch/living_room_light_01/state → "ON"
home/home_test_1/node_1/status → "online"

# Commands from Django
home/home_test_1/node_1/switch/living_room_light_01/command → "OFF"
```

## 🔌 GPIO Pin Reference

### Reserved Pins (DO NOT USE)
```
GPIO 0, 2, 6, 7, 8, 9, 10, 11, 12, 15
```

### Recommended Pins
- **Digital Output (Relays/Switches)**: 13, 14, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
- **PWM (Lights/Fans)**: 4, 5, 13, 14, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
- **Sensors (DHT22, etc.)**: 4, 5, 13, 14, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
- **I2C**: SDA=21, SCL=22
- **SPI**: MOSI=23, MISO=19, CLK=18, CS=5

## 🐛 Troubleshooting

### MQTT Connection Issues

**Problem**: ESP32 shows "MQTT Disconnected: TCP disconnected"

**Solution**:
1. Verify Mosquitto is running with external access:
   ```powershell
   Test-NetConnection -ComputerName YOUR_IP -Port 1883
   # Should show: TcpTestSucceeded : True
   ```

2. Check Windows Firewall:
   - Run `start_mqtt_server.bat` as Administrator
   - Or manually add rule: `netsh advfirewall firewall add rule name="Allow MQTT" dir=in action=allow protocol=TCP localport=1883`

3. Verify ESP32 YAML has correct broker IP:
   ```yaml
   mqtt:
     broker: 192.168.29.91  # Your computer's IP, not localhost!
     port: 1883
   ```

4. Check your IP hasn't changed:
   ```powershell
   ipconfig
   # Look for IPv4 Address
   ```

### Device Shows Offline

**Problem**: Device was online but now shows offline

**Explanation**: Devices are considered offline if `last_seen` timestamp is older than 60 seconds.

**Solution**:
1. Check ESP32 is powered and connected to WiFi
2. Verify MQTT broker is running
3. Check ESP32 logs: `esphome logs your-device.yaml`
4. Restart ESP32 device

### ESP32 Flashing Issues

**Problem**: "Wrong boot mode detected (0x13)" error

**Solution**:
1. Hold **BOOT button** on ESP32
2. Click **Flash** in web interface
3. Keep holding BOOT for 5-10 seconds
4. Release when you see "Writing at 0x..." messages

**Alternative**: Use manual esptool command shown in error message

### Dashboard Not Auto-Refreshing

**Solution**:
1. Open browser console (F12)
2. Look for JavaScript errors
3. Verify you see: "Auto-refresh enabled (every 5 seconds)"
4. Hard refresh: Ctrl+Shift+R

## 📁 Project Structure

```
esp32-django/
├── config/                      # Django settings
│   ├── settings.py             # Main configuration
│   └── urls.py                 # URL routing
├── apps/
│   └── devices/                # Main application
│       ├── models.py           # Database models (Device, Entity)
│       ├── views.py            # View controllers
│       ├── wizard.py           # Setup wizard logic
│       ├── services.py         # MQTT publish services
│       ├── mqtt_listener.py    # MQTT subscriber (auto-starts)
│       ├── esphome_generator.py # YAML generation
│       ├── validators.py       # GPIO validation
│       └── constants.py        # ESP32 pin definitions
├── templates/                  # HTML templates
│   ├── dashboard.html          # Main dashboard (auto-refresh)
│   ├── device_detail.html      # Device control (real-time)
│   └── wizard/                 # Setup wizard steps
├── media/
│   └── esphome_builds/         # Generated YAML files
├── mosquitto.conf              # MQTT broker config
├── start_mqtt_server.bat       # MQTT startup script
├── db.sqlite3                  # Database
└── README.md                   # This file
```

## 🔐 Security Considerations

⚠️ **For Production Deployment:**

1. **Django Settings**
   ```python
   DEBUG = False
   SECRET_KEY = 'generate-new-secret-key'
   ALLOWED_HOSTS = ['your-domain.com']
   ```

2. **MQTT Security**
   - Enable authentication in Mosquitto
   - Use TLS/SSL (port 8883)
   - Update `mosquitto.conf`:
     ```conf
     listener 8883
     cafile /path/to/ca.crt
     certfile /path/to/server.crt
     keyfile /path/to/server.key
     require_certificate false
     allow_anonymous false
     password_file /path/to/passwd
     ```

3. **Database**
   - Use PostgreSQL instead of SQLite
   - Regular backups

4. **Firewall**
   - Restrict MQTT port to local network only
   - Use VPN for remote access

5. **Passwords**
   - Strong admin passwords
   - MQTT authentication required

## 🌐 API Endpoints

| URL | Purpose |
|-----|---------|
| `/` | Dashboard with device list |
| `/wizard/start/` | Device setup wizard |
| `/device/<id>/` | Device detail & control |
| `/device/<id>/pinout/` | Visual ESP32 pinout |
| `/device/<id>/firmware/` | OTA management |
| `/device/<id>/yaml/view/` | View/download YAML |
| `/device/<id>/factory-reset/` | Factory reset |
| `/api/check-esp32/` | ESP32 connection check |

## 📊 Real-Time Features

### Dashboard Auto-Refresh (5 seconds)
- Device online/offline status
- Device count statistics
- Last seen timestamps

### Device Detail Auto-Refresh (2 seconds)
- Entity states (ON/OFF)
- Sensor readings
- Visual flash animations on state changes

### MQTT Auto-Discovery
- Devices auto-register on first message
- Entities auto-created from MQTT topics
- State updates in real-time

## 🎯 Supported Components

### Single-Pin Components
- Switch
- Light (ON/OFF)
- Fan
- Binary Sensor
- Sensor (Temperature, Humidity, etc.)

### Multi-Pin Components
- RGB Light (3 pins)
- RGBW Light (4 pins)
- DHT Sensor (Temperature + Humidity)
- Stepper Motor (4 pins)

## 📝 License

MIT License - Feel free to use and modify for your projects.

## 🤝 Contributing

Contributions welcome! This is a production-ready smart home platform.

## 📞 Support

For issues or questions:
1. Check this README
2. Review Django logs
3. Check Mosquitto logs
4. Verify ESP32 serial output

---

**Built with ❤️ using Django + MQTT + ESPHome**

**Key Technologies**: Python • Django • MQTT • ESPHome • JavaScript • SQLite
