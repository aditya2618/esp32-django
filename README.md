# ESP32 Smart Home Platform

A complete Django web application for managing ESP32-based smart home devices using ESPHome and MQTT.

## Features

✅ **Device Management**
- Add and manage multiple ESP32 devices
- Real-time device status monitoring
- Auto-discovery via MQTT

✅ **Entity Control**
- Switches (ON/OFF)
- Lights (ON/OFF with dimming support)
- Fans (Speed control)
- Sensors (Temperature, humidity, etc.)

✅ **GPIO Pin Mapping**
- Visual ESP32 pinout display
- GPIO validation (reserved pins, capabilities)
- Dynamic pin assignment
- Push configuration to devices

✅ **Firmware & OTA Updates**
- Upload firmware files (.bin)
- Single device OTA
- Bulk OTA for multiple devices
- OTA status tracking

✅ **ESPHome Integration**
- Auto-generate ESPHome YAML from entities
- Download ready-to-flash configurations
- MQTT topic standardization

✅ **Factory Reset**
- Remote factory reset capability
- Clears all device configuration

## Technology Stack

- **Backend**: Django 5.2.9
- **Database**: SQLite (default)
- **Messaging**: MQTT (paho-mqtt)
- **Frontend**: Server-rendered HTML templates
- **Device Firmware**: ESPHome

## Installation

### Prerequisites

- Python 3.11
- MQTT Broker (Mosquitto, EMQX, or similar)
- ESPHome devices or ESP32 boards

### Setup Steps

1. **Navigate to project directory**
   ```powershell
   cd h:\aditya\esp32-django\smarthome
   ```

2. **Activate virtual environment** (already created as `esp32`)
   ```powershell
   h:\aditya\esp32-django\esp32\Scripts\python.exe
   ```

3. **Apply migrations** (already done)
   ```powershell
   h:\aditya\esp32-django\esp32\Scripts\python.exe manage.py migrate
   ```

4. **Create superuser**
   ```powershell
   h:\aditya\esp32-django\esp32\Scripts\python.exe manage.py createsuperuser
   ```

5. **Configure MQTT settings**
   
   Edit `config/settings.py` and update:
   ```python
   MQTT_BROKER = 'your-mqtt-broker-ip'  # e.g., '192.168.1.100'
   MQTT_PORT = 1883
   MQTT_USERNAME = 'your-username'  # Optional
   MQTT_PASSWORD = 'your-password'  # Optional
   ```

6. **Run development server**
   ```powershell
   h:\aditya\esp32-django\esp32\Scripts\python.exe manage.py runserver
   ```

7. **Access the application**
   - Web UI: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## Quick Start Guide

### 1. Add Your First Device

1. Go to Dashboard → "Add New Device"
2. Fill in:
   - **Home ID**: e.g., `home1`
   - **Name**: e.g., `Living Room`
   - **Node Name**: e.g., `home1_livingroom_node1`
3. Click "Save"

### 2. Add Entities

1. Open your device detail page
2. Click "Add Entity"
3. Fill in:
   - **Entity Name**: e.g., `living_room_fan`
   - **Entity Type**: Select `Fan`, `Light`, `Switch`, or `Sensor`
   - **GPIO Pin**: Assign GPIO number (optional for sensors)
4. Click "Save Entity"

### 3. Generate ESPHome Configuration

1. Go to device detail page
2. Click "Generate YAML"
3. Download the `.yaml` file
4. Edit WiFi and MQTT settings in the YAML
5. Flash to your ESP32:
   ```bash
   esphome run yourdevice.yaml
   ```

### 4. Control Your Devices

Once your ESP32 is online and publishing to MQTT:
- Device status updates automatically
- Use ON/OFF buttons to control switches, lights, fans
- View sensor data in real-time

## MQTT Topic Structure

The application uses standardized MQTT topics:

### State Topics (ESP32 → Django)
```
home/{home_id}/{node_name}/{entity_type}/{entity_name}/state
```

### Command Topics (Django → ESP32)
```
home/{home_id}/{node_name}/{entity_type}/{entity_name}/command
```

### OTA Status (ESP32 → Django)
```
home/{home_id}/{node_name}/status/ota
```

### Examples
```
home/home1/livingroom_node1/switch/fan/state          → "ON"
home/home1/livingroom_node1/switch/fan/command        → "OFF"
home/home1/livingroom_node1/sensor/temperature/state  → "23.5"
```

## GPIO Pin Reference

### Reserved Pins (DO NOT USE)
```
GPIO 0, 2, 6, 7, 8, 9, 10, 11, 12, 15
```

### Recommended Pins
- **Relays/Switches**: GPIO 13, 14, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
- **PWM (Lights/Fans)**: GPIO 4, 5, 12, 13, 14, 15, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
- **Sensors (DHT22)**: GPIO 4, 5, 13, 14, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33

## Firmware Update (OTA)

### Single Device
1. Upload firmware via "Upload Firmware"
2. Go to device → "Firmware/OTA"
3. Select firmware version
4. Click "Trigger OTA Update"

### Bulk Update
1. Go to "Bulk OTA Update"
2. Select firmware version
3. Select devices
4. Click "Start Bulk OTA Update"

## Troubleshooting

### MQTT Not Connecting
1. Check MQTT broker is running
2. Verify `MQTT_BROKER` IP in settings.py
3. Check firewall rules (port 1883)
4. Test with MQTT client: `mosquitto_sub -h YOUR_BROKER_IP -t '#' -v`

### Device Not Showing Online
1. Verify ESP32 is connected to WiFi
2. Check MQTT broker address in ESPHome YAML
3. Verify MQTT topics match expected format
4. Check ESP32 logs: `esphome logs yourdevice.yaml`

### GPIO Validation Errors
- Ensure pin is not in reserved list
- Verify pin supports the device type (e.g., PWM for dimmers)
- Check for duplicate pin assignments

## Project Structure

```
smarthome/
├── config/              # Django settings
│   ├── settings.py
│   └── urls.py
├── apps/
│   └── devices/         # Main app
│       ├── models.py    # Database models
│       ├── views.py     # Views/controllers
│       ├── forms.py     # Form definitions
│       ├── services.py  # MQTT publish logic
│       ├── mqtt_listener.py  # MQTT subscriber
│       ├── validators.py     # GPIO validation
│       ├── constants.py      # ESP32 pin constants
│       ├── esphome_generator.py  # YAML generator
│       └── admin.py     # Django admin config
├── templates/           # HTML templates
├── static/              # CSS, JS files
├── media/               # Uploaded firmware
└── db.sqlite3           # Database

```

## API Endpoints

| URL | Purpose |
|-----|---------|
| `/` | Dashboard |
| `/device/<id>/` | Device detail & control |
| `/device/<id>/gpio/` | GPIO pin mapping |
| `/device/<id>/pinout/` | Visual pinout |
| `/device/<id>/firmware/` | OTA management |
| `/device/<id>/yaml/view/` | Generate ESPHome YAML |
| `/firmware/` | Firmware list |
| `/firmware/upload/` | Upload firmware |
| `/firmware/bulk-ota/` | Bulk OTA update |
| `/ota/status/` | OTA status overview |
| `/admin/` | Django admin panel |

## Security Considerations

⚠️ **For Production Use:**

1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Use proper MQTT authentication
4. Enable TLS/SSL for MQTT (port 8883)
5. Use strong passwords for admin panel
6. Restrict `ALLOWED_HOSTS`
7. Use PostgreSQL instead of SQLite
8. Set up proper firewall rules

## Contributing

This is a production-ready smart home platform. Contributions welcome!

## License

MIT License

## Support

For issues or questions, please refer to the documentation or contact your system administrator.

---

**Built with ❤️ using Django + MQTT + ESPHome**
