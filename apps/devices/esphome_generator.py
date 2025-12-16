"""
ESPHome YAML Generator

Automatically generates ESPHome YAML configuration from Django entities.
"""


def generate_esphome_yaml(device, wifi_ssid='YOUR_WIFI_SSID', wifi_password='YOUR_WIFI_PASSWORD', 
                          mqtt_broker='YOUR_MQTT_BROKER_IP', mqtt_port=1883, platform='esp32'):
    """
    Generate complete ESPHome YAML configuration for a device.
    
    Args:
        device: Device instance
        wifi_ssid: WiFi SSID (from wizard session)
        wifi_password: WiFi password (from wizard session)
        mqtt_broker: MQTT broker IP (from wizard session)
        mqtt_port: MQTT port (from wizard session)
        platform: 'esp32' or 'esp8266' (default: 'esp32')
        
    Returns:
        str: Complete ESPHome YAML configuration
    """
    from .models import Entity
    
    entities = Entity.objects.filter(device=device).order_by('entity_type', 'entity_name')
    
    # Sanitize device name for ESPHome (lowercase, hyphens only)
    esphome_name = device.node_name.lower().replace('_', '-')
    
    # Determine platform configuration
    if platform.lower() == 'esp8266':
        platform_config = """esp8266:
  board: nodemcuv2
  framework:
    version: recommended"""
    else:  # Default to ESP32
        platform_config = """esp32:
  board: esp32dev
  framework:
    type: arduino"""
    
    yaml = f"""# ESPHome Configuration for {device.name}
# Generated automatically by Django Smart Home

esphome:
  name: "{esphome_name}"
  friendly_name: {device.name}

{platform_config}

# WiFi Configuration
wifi:
  ssid: "{wifi_ssid}"
  password: "{wifi_password}"
  
  # Enable fallback hotspot (captive portal) in case wifi connection fails
  ap:
    ssid: "{esphome_name}-fallback"
    password: "12345678"

# Enable captive portal for WiFi configuration
captive_portal:

# Enable logging
logger:

# Enable Home Assistant API
api:

# Enable OTA updates
ota:
  - platform: esphome

# Enable web server
web_server:
  port: 80

# MQTT Configuration
mqtt:
  broker: {mqtt_broker}
  port: {mqtt_port}
  discovery: true
  discovery_prefix: homeassistant

"""
    
    # Group entities by type
    switches = []
    lights = []
    fans = []
    sensors = []
    binary_sensors = []
    
    for entity in entities:
        if entity.entity_type == 'switch':
            switches.append(entity)
        elif entity.entity_type == 'light':
            lights.append(entity)
        elif entity.entity_type == 'fan':
            fans.append(entity)
        elif entity.entity_type == 'sensor':
            sensors.append(entity)
        elif entity.entity_type == 'binary_sensor':
            binary_sensors.append(entity)
    
    # Add consolidated GPIO outputs section
    gpio_entities = switches + lights + fans
    if gpio_entities:
        yaml += "\n# GPIO Outputs\noutput:\n"
        for entity in gpio_entities:
            if entity.gpio_pin:
                # Sanitize entity name for valid ESPHome ID (replace spaces with underscores)
                sanitized_name = entity.entity_name.replace(' ', '_')
                yaml += f"""  - platform: gpio
    pin: GPIO{entity.gpio_pin}
    id: {sanitized_name}_output

"""
    
    # Generate switch configurations
    if switches:
        yaml += "\n# Switches\nswitch:\n"
        for entity in switches:
            # Sanitize entity name for valid ESPHome ID (replace spaces with underscores)
            sanitized_name = entity.entity_name.replace(' ', '_')
            yaml += f"""  - platform: output
    name: "{entity.friendly_name or entity.entity_name.replace('_', ' ').title()}"
    id: {sanitized_name}
    output: {sanitized_name}_output

"""

    
    # Generate light configurations
    if lights:
        yaml += "\n# Lights\nlight:\n"
        for entity in lights:
            # Sanitize entity name for valid ESPHome ID (replace spaces with underscores)
            sanitized_name = entity.entity_name.replace(' ', '_')
            yaml += f"""  - platform: binary
    name: "{entity.friendly_name or entity.entity_name.replace('_', ' ').title()}"
    id: {sanitized_name}
    output: {sanitized_name}_output

"""
    
    # Generate fan configurations
    if fans:
        yaml += "\n# Fans\nfan:\n"
        for entity in fans:
            # Sanitize entity name for valid ESPHome ID (replace spaces with underscores)
            sanitized_name = entity.entity_name.replace(' ', '_')
            yaml += f"""  - platform: binary
    name: "{entity.friendly_name or entity.entity_name.replace('_', ' ').title()}"
    id: {sanitized_name}
    output: {sanitized_name}_output

"""

    
    # Generate binary sensor configurations
    if binary_sensors:
        yaml += "\n# Binary Sensors\nbinary_sensor:\n"
        for entity in binary_sensors:
            if entity.gpio_pin:
                # Sanitize entity name for valid ESPHome ID (replace spaces with underscores)
                sanitized_name = entity.entity_name.replace(' ', '_')
                yaml += f"""  - platform: gpio
    name: "{entity.friendly_name or entity.entity_name.replace('_', ' ').title()}"
    id: {sanitized_name}
    pin: 
      number: GPIO{entity.gpio_pin}
      mode: INPUT_PULLUP
      inverted: true

"""
    
    # Generate sensor configurations
    if sensors:
        yaml += "\n# Sensors\nsensor:\n"
        for entity in sensors:
            if entity.gpio_pin:
                # Default to DHT sensor as an example
                yaml += f"""  - platform: dht
    pin: GPIO{entity.gpio_pin}
    model: DHT22
    temperature:
      name: "{entity.friendly_name or entity.entity_name.replace('_', ' ').title()} Temperature"
    humidity:
      name: "{entity.friendly_name or entity.entity_name.replace('_', ' ').title()} Humidity"
    update_interval: 60s

"""
    
    yaml += f"""
# Configuration Instructions:
# 1. Replace YOUR_WIFI_SSID and YOUR_WIFI_PASSWORD with your actual WiFi credentials
# 2. Replace YOUR_MQTT_BROKER_IP with your MQTT broker IP address (e.g., 192.168.1.100)
# 3. Verify GPIO pin assignments match your hardware connections
# 4. Flash to ESP32 using ESPHome Web or CLI: esphome run {esphome_name}.yaml
"""
    
    return yaml


def generate_gpio_mapping_yaml(device):
    """
    Generate GPIO mapping section for custom firmware.
    
    Args:
        device: Device instance
        
    Returns:
        str: JSON-formatted GPIO mapping
    """
    from .models import GPIOMapping
    import json
    
    mappings = GPIOMapping.objects.filter(device=device)
    
    gpio_map = {}
    for mapping in mappings:
        gpio_map[f"GPIO{mapping.gpio_pin}"] = {
            "entity": mapping.entity.entity_name if mapping.entity else "unassigned",
            "type": mapping.entity.entity_type if mapping.entity else "unknown",
            "description": mapping.description or ""
        }
    
    return json.dumps(gpio_map, indent=2)
