"""
ESPHome YAML Generator

Automatically generates ESPHome YAML configuration from Django entities.
"""


def generate_esphome_yaml(device):
    """
    Generate complete ESPHome YAML configuration for a device.
    
    Args:
        device: Device instance
        
    Returns:
        str: Complete ESPHome YAML configuration
    """
    from .models import Entity
    
    entities = Entity.objects.filter(device=device).order_by('entity_type', 'entity_name')
    
    yaml = f"""# ESPHome Configuration for {device.name}
# Generated automatically by Django Smart Home

esphome:
  name: {device.node_name}
  platform: ESP32
  board: esp32dev

# WiFi Configuration
wifi:
  ssid: "YOUR_WIFI_SSID"
  password: "YOUR_WIFI_PASSWORD"
  
  # Enable fallback hotspot (captive portal) in case wifi connection fails
  ap:
    ssid: "{device.node_name}"
    password: "12345678"

captive_portal:

# Enable logging
logger:
  level: INFO

# Enable Home Assistant API
api:
  encryption:
    key: "YOUR_API_KEY"

# Enable Over-The-Air updates
ota:
  on_begin:
    - mqtt.publish:
        topic: {device.base_topic()}/status/ota
        payload: "STARTED"
  on_end:
    - mqtt.publish:
        topic: {device.base_topic()}/status/ota
        payload: '{"{"}"status":"SUCCESS","version":"${{compile_version}}"{"}}"}'

# MQTT Configuration
mqtt:
  broker: YOUR_MQTT_BROKER_IP
  port: 1883
  username: YOUR_MQTT_USERNAME
  password: YOUR_MQTT_PASSWORD
  topic_prefix: {device.base_topic()}
  discovery: false
  
  # Subscribe to control topics
  on_message:
    - topic: {device.base_topic()}/+/+/command
      then:
        - logger.log: "Received command"

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
    
    # Generate switch configurations
    if switches:
        yaml += "\n# Switches\nswitch:\n"
        for entity in switches:
            pin = entity.gpio_pin if entity.gpio_pin else 'GPIO_PIN_HERE'
            yaml += f"""  - platform: gpio
    name: "{entity.entity_name.replace('_', ' ').title()}"
    id: {entity.entity_name}
    pin: {pin}
    on_turn_on:
      - mqtt.publish:
          topic: {entity.state_topic()}
          payload: "ON"
    on_turn_off:
      - mqtt.publish:
          topic: {entity.state_topic()}
          payload: "OFF"

"""
    
    # Generate light configurations
    if lights:
        yaml += "\n# Lights\noutput:\n"
        for idx, entity in enumerate(lights):
            pin = entity.gpio_pin if entity.gpio_pin else 'GPIO_PIN_HERE'
            yaml += f"""  - platform: ledc
    id: {entity.entity_name}_output
    pin: {pin}
    frequency: 1000 Hz

"""
        
        yaml += "\nlight:\n"
        for entity in lights:
            yaml += f"""  - platform: monochromatic
    name: "{entity.entity_name.replace('_', ' ').title()}"
    id: {entity.entity_name}
    output: {entity.entity_name}_output
    on_turn_on:
      - mqtt.publish:
          topic: {entity.state_topic()}
          payload: "ON"
    on_turn_off:
      - mqtt.publish:
          topic: {entity.state_topic()}
          payload: "OFF"

"""
    
    # Generate fan configurations
    if fans:
        yaml += "\n# Fans\noutput:\n"
        for entity in fans:
            pin = entity.gpio_pin if entity.gpio_pin else 'GPIO_PIN_HERE'
            yaml += f"""  - platform: ledc
    id: {entity.entity_name}_output
    pin: {pin}
    frequency: 25000 Hz

"""
        
        yaml += "\nfan:\n"
        for entity in fans:
            yaml += f"""  - platform: speed
    name: "{entity.entity_name.replace('_', ' ').title()}"
    id: {entity.entity_name}
    output: {entity.entity_name}_output
    speed_count: 5
    on_turn_on:
      - mqtt.publish:
          topic: {entity.state_topic()}
          payload: "ON"
    on_turn_off:
      - mqtt.publish:
          topic: {entity.state_topic()}
          payload: "OFF"
    on_speed_set:
      - mqtt.publish:
          topic: {device.base_topic()}/fan/{entity.entity_name}/speed/state
          payload: !lambda 'return to_string(id({entity.entity_name}).speed);'

"""
    
    # Generate binary sensor configurations
    if binary_sensors:
        yaml += "\n# Binary Sensors\nbinary_sensor:\n"
        for entity in binary_sensors:
            pin = entity.gpio_pin if entity.gpio_pin else 'GPIO_PIN_HERE'
            yaml += f"""  - platform: gpio
    name: "{entity.entity_name.replace('_', ' ').title()}"
    id: {entity.entity_name}
    pin: 
      number: {pin}
      mode: INPUT_PULLUP
      inverted: true
    on_press:
      - mqtt.publish:
          topic: {entity.state_topic()}
          payload: "ON"
    on_release:
      - mqtt.publish:
          topic: {entity.state_topic()}
          payload: "OFF"

"""
    
    # Generate sensor configurations
    if sensors:
        yaml += "\n# Sensors\nsensor:\n"
        for entity in sensors:
            pin = entity.gpio_pin if entity.gpio_pin else 'GPIO_PIN_HERE'
            # Default to DHT sensor as an example
            yaml += f"""  - platform: dht
    pin: {pin}
    temperature:
      name: "{entity.entity_name.replace('_', ' ').title()} Temperature"
      on_value:
        - mqtt.publish:
            topic: {device.base_topic()}/sensor/{entity.entity_name}_temperature/state
            payload: !lambda 'return to_string(x);'
    humidity:
      name: "{entity.entity_name.replace('_', ' ').title()} Humidity"
      on_value:
        - mqtt.publish:
            topic: {device.base_topic()}/sensor/{entity.entity_name}_humidity/state
            payload: !lambda 'return to_string(x);'
    model: DHT22
    update_interval: 60s

"""
    
    yaml += """# Instructions:
# 1. Replace YOUR_WIFI_SSID and YOUR_WIFI_PASSWORD with your WiFi credentials
# 2. Replace YOUR_MQTT_BROKER_IP with your MQTT broker address
# 3. Replace YOUR_MQTT_USERNAME and YOUR_MQTT_PASSWORD if using authentication
# 4. Replace YOUR_API_KEY with a secure API key (or remove api section)
# 5. Verify GPIO pin assignments match your hardware
# 6. Flash to ESP32 using: esphome run {device.node_name}.yaml
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
    
    config = {
        "device_id": device.node_name,
        "home_id": device.home_id,
        "gpios": [
            {
                "logical_id": m.logical_id,
                "pin": m.gpio_pin,
                "type": m.type,
                "default": m.default_value
            }
            for m in mappings
        ]
    }
    
    return json.dumps(config, indent=2)
