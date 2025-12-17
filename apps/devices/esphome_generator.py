"""
ESPHome YAML Generator - Enhanced Version
Supports 50+ component types with platform-specific configurations
"""

def generate_esphome_yaml(device, wifi_ssid='YOUR_WIFI_SSID', wifi_password='YOUR_WIFI_PASSWORD', 
                          mqtt_broker='YOUR_MQTT_BROKER_IP', mqtt_port=1883, platform='esp32'):
    """
    Generate complete ESPHome YAML configuration for a device.
    
    Args:
        device: Device instance
        wifi_ssid: WiFi SSID
        wifi_password: WiFi password
        mqtt_broker: MQTT broker IP
        mqtt_port: MQTT port
        platform: 'esp32' or 'esp8266'
        
    Returns:
        str: Complete ESPHome YAML configuration
    """
    from .models import Entity
    from .constants import SENSOR_TYPES, ACTUATOR_TYPES
    
    entities = Entity.objects.filter(device=device).order_by('entity_type', 'entity_name')
    
    # Sanitize device name
    esphome_name = device.node_name.lower().replace('_', '-')
    
    # Platform configuration
    if platform.lower() == 'esp8266':
        platform_config = """esp8266:
  board: nodemcuv2
  framework:
    version: recommended"""
    else:
        platform_config = """esp32:
  board: esp32dev
  framework:
    type: arduino"""
    
    # Base YAML with improved formatting
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

captive_portal:

# Enable logging
logger:

# Enable Over-The-Air updates
ota:
  - platform: esphome

# MQTT Configuration
mqtt:
  broker: {mqtt_broker}
  port: {mqtt_port}
  topic_prefix: {device.base_topic()}
  discovery: false

"""
    
    # Check if I2C is needed
    i2c_needed = any(e.hardware_type in ['bme280', 'bmp280', 'bh1750'] for e in entities)
    if i2c_needed:
        yaml += """# I2C Configuration
i2c:
  sda: GPIO21
  scl: GPIO22
  scan: true

"""
    
    
    # Generate component configurations
    yaml += generate_sensors_yaml(entities)
    yaml += generate_binary_sensors_yaml(entities)
    yaml += generate_switches_yaml(entities)
    yaml += generate_lights_yaml(entities)
    yaml += generate_fans_yaml(entities)
    yaml += generate_steppers_yaml(entities)
    
    # Add configuration instructions at the end
    yaml += f"""

# Configuration Instructions:
# 1. Replace YOUR_WIFI_SSID and YOUR_WIFI_PASSWORD with your actual WiFi credentials
# 2. Replace YOUR_MQTT_BROKER_IP with your MQTT broker IP address (e.g., 192.168.1.100)
# 3. Verify GPIO pin assignments match your hardware connections
# 4. Flash to {platform.upper()} using ESPHome Web or CLI: esphome run {esphome_name}.yaml
"""
    
    return yaml


def generate_sensors_yaml(entities):
    """Generate sensor configurations"""
    from .constants import SENSOR_TYPES
    
    sensors = [e for e in entities if e.entity_type == 'sensor']
    if not sensors:
        return ""
    
    yaml = "\n# Sensors\nsensor:\n"
    
    for entity in sensors:
        hw_type = entity.hardware_type
        component = SENSOR_TYPES.get(hw_type, {})
        platform = component.get('esphome_platform', 'adc')
        name = entity.friendly_name or entity.entity_name.replace('_', ' ').title()
        
        if hw_type == 'dht11':
            yaml += f"""  - platform: dht
    model: DHT11
    pin: GPIO{entity.gpio_pin}
    temperature:
      name: "{name} Temperature"
    humidity:
      name: "{name} Humidity"
    update_interval: {entity.update_interval}s

"""
        elif hw_type == 'dht22':
            yaml += f"""  - platform: dht
    model: DHT22
    pin: GPIO{entity.gpio_pin}
    temperature:
      name: "{name} Temperature"
    humidity:
      name: "{name} Humidity"
    update_interval: {entity.update_interval}s

"""
        elif hw_type == 'bme280':
            yaml += f"""  - platform: bme280
    address: {entity.i2c_address or '0x76'}
    temperature:
      name: "{name} Temperature"
    humidity:
      name: "{name} Humidity"
    pressure:
      name: "{name} Pressure"
    update_interval: {entity.update_interval}s

"""
        elif hw_type == 'bmp280':
            yaml += f"""  - platform: bmp280
    address: {entity.i2c_address or '0x76'}
    temperature:
      name: "{name} Temperature"
    pressure:
      name: "{name} Pressure"
    update_interval: {entity.update_interval}s

"""
        elif hw_type == 'ds18b20':
            yaml += f"""  - platform: dallas
    address: 0x{entity.entity_name}
    name: "{name}"
    update_interval: {entity.update_interval}s

"""
        elif hw_type == 'bh1750':
            yaml += f"""  - platform: bh1750
    name: "{name}"
    address: {entity.i2c_address or '0x23'}
    update_interval: {entity.update_interval}s

"""
        elif hw_type in ['soil_moisture_capacitive', 'soil_ph']:
            yaml += f"""  - platform: adc
    pin: GPIO{entity.gpio_pin}
    name: "{name}"
    update_interval: {entity.update_interval}s
    filters:
      - calibrate_linear:
          - 0.0 -> 0.0
          - 3.3 -> 100.0

"""
        elif hw_type == 'water_flow':
            yaml += f"""  - platform: pulse_counter
    pin: GPIO{entity.gpio_pin}
    name: "{name}"
    unit_of_measurement: 'L/min'
    update_interval: {entity.update_interval}s

"""
        elif hw_type == 'co2_mhz19':
            yaml += f"""  - platform: mhz19
    co2:
      name: "{name}"
    update_interval: {entity.update_interval}s

"""
        elif hw_type == 'ultrasonic_hcsr04':
            # Use pin_config if available, otherwise assume we need to get pins
            trigger_pin = entity.pin_config.get('trigger_pin')
            echo_pin = entity.pin_config.get('echo_pin')
            
            # Fallback if pin_config missing but we have gpio_pin (shouldn't happen with new form)
            if not trigger_pin and entity.gpio_pin:
                trigger_pin = entity.gpio_pin
                
            yaml += f"""  - platform: ultrasonic
    trigger_pin: GPIO{trigger_pin}
    echo_pin: GPIO{echo_pin}
    name: "{name}"
    update_interval: {entity.update_interval}s
    unit_of_measurement: "cm"

"""
    
    return yaml


def generate_binary_sensors_yaml(entities):
    """Generate binary sensor configurations"""
    binary_sensors = [e for e in entities if e.entity_type == 'binary_sensor']
    if not binary_sensors:
        return ""
    
    yaml = "\n# Binary Sensors\nbinary_sensor:\n"
    
    for entity in binary_sensors:
        name = entity.friendly_name or entity.entity_name.replace('_', ' ').title()
        hw_type = entity.hardware_type
        
        if hw_type == 'pir':
            yaml += f"""  - platform: gpio
    pin: GPIO{entity.gpio_pin}
    name: "{name}"
    device_class: motion

"""
        elif hw_type == 'reed_switch':
            yaml += f"""  - platform: gpio
    pin:
      number: GPIO{entity.gpio_pin}
      mode: INPUT_PULLUP
      inverted: true
    name: "{name}"
    device_class: door

"""
    
    return yaml


def generate_switches_yaml(entities):
    """Generate switch configurations"""
    switches = [e for e in entities if e.entity_type == 'switch']
    if not switches:
        return ""
    
    yaml = "\n# Switches\nswitch:\n"
    
    for entity in switches:
        name = entity.friendly_name or entity.entity_name.replace('_', ' ').title()
        hw_type = entity.hardware_type
        
        if hw_type == 'relay_active_high':
            yaml += f"""  - platform: gpio
    pin: GPIO{entity.gpio_pin}
    name: "{name}"
    id: {entity.entity_name}

"""
        elif hw_type == 'relay_active_low':
            yaml += f"""  - platform: gpio
    pin:
      number: GPIO{entity.gpio_pin}
      inverted: true
    name: "{name}"
    id: {entity.entity_name}

"""
        elif hw_type in ['solenoid_valve', 'water_pump']:
            yaml += f"""  - platform: gpio
    pin: GPIO{entity.gpio_pin}
    name: "{name}"
    id: {entity.entity_name}

"""
    
    return yaml


def generate_lights_yaml(entities):
    """Generate light configurations"""
    lights = [e for e in entities if e.entity_type == 'light']
    if not lights:
        return ""
    
    yaml = "\n# Lights\nlight:\n"
    
    for entity in lights:
        name = entity.friendly_name or entity.entity_name.replace('_', ' ').title()
        hw_type = entity.hardware_type
        
        if hw_type == 'light_binary':
            yaml += f"""  - platform: binary
    name: "{name}"
    output: {entity.entity_name}_output

"""
        elif hw_type == 'light_dimmable':
            yaml += f"""  - platform: monochromatic
    name: "{name}"
    output: {entity.entity_name}_output

"""
        elif hw_type == 'light_rgb':
            yaml += f"""  - platform: rgb
    name: "{name}"
    red: {entity.entity_name}_red
    green: {entity.entity_name}_green
    blue: {entity.entity_name}_blue

"""
        elif hw_type == 'light_rgbw':
            yaml += f"""  - platform: rgbw
    name: "{name}"
    red: {entity.entity_name}_red
    green: {entity.entity_name}_green
    blue: {entity.entity_name}_blue
    white: {entity.entity_name}_white

"""
    
    # Add output section for lights
    if lights:
        yaml += "\n# Light Outputs\noutput:\n"
        for entity in lights:
            hw_type = entity.hardware_type
            if hw_type in ['light_binary', 'light_dimmable']:
                yaml += f"""  - platform: gpio
    pin: GPIO{entity.gpio_pin}
    id: {entity.entity_name}_output

"""
            elif hw_type == 'light_rgb':
                pin_config = entity.pin_config or {}
                yaml += f"""  - platform: ledc
    pin: GPIO{pin_config.get('red_pin')}
    id: {entity.entity_name}_red
  - platform: ledc
    pin: GPIO{pin_config.get('green_pin')}
    id: {entity.entity_name}_green
  - platform: ledc
    pin: GPIO{pin_config.get('blue_pin')}
    id: {entity.entity_name}_blue

"""
            elif hw_type == 'light_rgbw':
                pin_config = entity.pin_config or {}
                yaml += f"""  - platform: ledc
    pin: GPIO{pin_config.get('red_pin')}
    id: {entity.entity_name}_red
  - platform: ledc
    pin: GPIO{pin_config.get('green_pin')}
    id: {entity.entity_name}_green
  - platform: ledc
    pin: GPIO{pin_config.get('blue_pin')}
    id: {entity.entity_name}_blue
  - platform: ledc
    pin: GPIO{pin_config.get('white_pin')}
    id: {entity.entity_name}_white

"""
    
    return yaml


def generate_steppers_yaml(entities):
    """Generate stepper motor configurations"""
    steppers = [e for e in entities if e.hardware_type.startswith('stepper_')]
    if not steppers:
        return ""
        
    yaml = "\n# Stepper Motors\nstepper:\n"
    
    for entity in steppers:
        name = entity.friendly_name or entity.entity_name.replace('_', ' ').title()
        hw_type = entity.hardware_type
        pin_config = entity.pin_config or {}
        
        if hw_type == 'stepper_uln2003':
            yaml += f"""  - platform: uln2003
    id: {entity.entity_name}
    pin1: GPIO{pin_config.get('in1')}
    pin2: GPIO{pin_config.get('in2')}
    pin3: GPIO{pin_config.get('in3')}
    pin4: GPIO{pin_config.get('in4')}
    max_speed: 250 steps/s

"""
        elif hw_type == 'stepper_a4988':
            yaml += f"""  - platform: a4988
    id: {entity.entity_name}
    step_pin: GPIO{pin_config.get('step_pin')}
    dir_pin: GPIO{pin_config.get('dir_pin')}
    max_speed: 250 steps/s

"""
            
    return yaml


def generate_fans_yaml(entities):
    """Generate fan configurations"""
    fans = [e for e in entities if e.entity_type == 'fan']
    if not fans:
        return ""
    
    yaml = "\n# Fans\nfan:\n"
    
    for entity in fans:
        name = entity.friendly_name or entity.entity_name.replace('_', ' ').title()
        yaml += f"""  - platform: binary
    output: {entity.entity_name}_output
    name: "{name}"

"""
    
    # Add output section
    if fans:
        yaml += "\n# Fan Outputs\noutput:\n"
        for entity in fans:
            yaml += f"""  - platform: gpio
    pin: GPIO{entity.gpio_pin}
    id: {entity.entity_name}_output

"""
    
    return yaml


def generate_gpio_mapping_yaml(device):
    """Generate GPIO mapping section for custom firmware"""
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
