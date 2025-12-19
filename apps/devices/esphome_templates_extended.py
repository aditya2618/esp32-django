"""
Additional ESPHome YAML Templates for New Sensors
Following standardized MQTT convention: home/{home_id}/{node_name}/{entity_type}/{entity_name}/state
"""

def generate_new_sensor_templates(entity, name):
    """Generate YAML for new sensor types"""
    hw_type = entity.hardware_type
    yaml = ""
    
    # INDUSTRIAL & HIGH-PRECISION SENSORS
    if hw_type == 'sht30':
        yaml = f"""  - platform: sht3xd
    address: {entity.i2c_address or '0x44'}
    temperature:
      name: "{name} Temperature"
    humidity:
      name: "{name} Humidity"
    update_interval: {entity.update_interval}s

"""
    
    elif hw_type == 'bme680':
        yaml = f"""  - platform: bme680
    address: {entity.i2c_address or '0x76'}
    temperature:
      name: "{name} Temperature"
    humidity:
      name: "{name} Humidity"
    pressure:
      name: "{name} Pressure"
    gas_resistance:
      name: "{name} Air Quality"
    update_interval: {entity.update_interval}s

"""
    
    elif hw_type == 'max31865':
        cs_pin = entity.pin_config.get('cs_pin', 5) if entity.pin_config else 5
        yaml = f"""  - platform: max31865
    cs_pin: GPIO{cs_pin}
    reference_resistance: 430 Ω
    rtd_nominal_resistance: 100 Ω
    name: "{name}"
    update_interval: {entity.update_interval}s

"""
    
    # AIR QUALITY SENSORS
    elif hw_type == 'ccs811':
        yaml = f"""  - platform: ccs811
    address: {entity.i2c_address or '0x5A'}
    eco2:
      name: "{name} CO2"
    tvoc:
      name: "{name} TVOC"
    update_interval: {entity.update_interval}s

"""
    
    elif hw_type == 'mq135':
        yaml = f"""  - platform: adc
    pin: GPIO{entity.gpio_pin}
    name: "{name}"
    update_interval: {entity.update_interval}s
    filters:
      - calibrate_linear:
          - 0.0 -> 0.0
          - 3.3 -> 1000.0

"""
    
    # ENERGY MONITORING
    elif hw_type == 'ina219':
        yaml = f"""  - platform: ina219
    address: {entity.i2c_address or '0x40'}
    shunt_resistance: 0.1 ohm
    current:
      name: "{name} Current"
    power:
      name: "{name} Power"
    bus_voltage:
      name: "{name} Voltage"
    shunt_voltage:
      name: "{name} Shunt Voltage"
    max_voltage: 32V
    max_current: 3.2A
    update_interval: {entity.update_interval}s

"""
    
    elif hw_type == 'ina226':
        yaml = f"""  - platform: ina226
    address: {entity.i2c_address or '0x40'}
    shunt_resistance: 0.1 ohm
    current:
      name: "{name} Current"
    power:
      name: "{name} Power"
    bus_voltage:
      name: "{name} Voltage"
    shunt_voltage:
      name: "{name} Shunt Voltage"
    max_current: 3.2A
    update_interval: {entity.update_interval}s

"""
    
    elif hw_type == 'hlw8012':
        pin_config = entity.pin_config or {}
        sel_pin = pin_config.get('sel_pin', 12)
        cf_pin = pin_config.get('cf_pin', 4)
        cf1_pin = pin_config.get('cf1_pin', 5)
        yaml = f"""  - platform: hlw8012
    sel_pin: GPIO{sel_pin}
    cf_pin: GPIO{cf_pin}
    cf1_pin: GPIO{cf1_pin}
    current:
      name: "{name} Current"
    voltage:
      name: "{name} Voltage"
    power:
      name: "{name} Power"
    update_interval: {entity.update_interval}s

"""
    
    # SYSTEM HEALTH SENSORS
    elif hw_type == 'wifi_signal':
        yaml = f"""  - platform: wifi_signal
    name: "{name}"
    update_interval: {entity.update_interval}s

"""
    
    elif hw_type == 'uptime':
        yaml = f"""  - platform: uptime
    name: "{name}"
    update_interval: {entity.update_interval}s

"""
    
    elif hw_type == 'internal_temperature':
        yaml = f"""  - platform: internal_temperature
    name: "{name}"
    update_interval: {entity.update_interval}s

"""
    
    # SMART FARMING - ADVANCED
    elif hw_type == 'soil_npk_modbus':
        yaml = f"""  # NPK Sensor requires Modbus configuration (see modbus section)
  - platform: modbus_controller
    modbus_controller_id: modbus1
    name: "{name} Nitrogen"
    address: 0x001E
    register_type: holding
    value_type: U_WORD
    unit_of_measurement: "mg/kg"
  
  - platform: modbus_controller
    modbus_controller_id: modbus1
    name: "{name} Phosphorus"
    address: 0x001F
    register_type: holding
    value_type: U_WORD
    unit_of_measurement: "mg/kg"
  
  - platform: modbus_controller
    modbus_controller_id: modbus1
    name: "{name} Potassium"
    address: 0x0020
    register_type: holding
    value_type: U_WORD
    unit_of_measurement: "mg/kg"

"""
    
    return yaml


def generate_new_binary_sensor_templates(entity, name):
    """Generate YAML for new binary sensor types"""
    hw_type = entity.hardware_type
    yaml = ""
    
    if hw_type == 'vibration_sw420':
        yaml = f"""  - platform: gpio
    pin: GPIO{entity.gpio_pin}
    name: "{name}"
    device_class: vibration

"""
    
    elif hw_type == 'rain_sensor':
        yaml = f"""  - platform: gpio
    pin: GPIO{entity.gpio_pin}
    name: "{name}"
    device_class: moisture

"""
    
    elif hw_type == 'ble_presence':
        mac_address = entity.pin_config.get('mac_address', 'AA:BB:CC:DD:EE:FF') if entity.pin_config else 'AA:BB:CC:DD:EE:FF'
        yaml = f"""  - platform: ble_presence
    mac_address: {mac_address}
    name: "{name}"

"""
    
    return yaml
