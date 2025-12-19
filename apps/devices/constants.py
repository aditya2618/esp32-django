# ESP32/ESP8266 GPIO Constants and Component Definitions
# For Smart Home, Smart Garden, Smart Farming, and Industrial Automation

# ============================================================================
# COMPREHENSIVE SENSOR TYPE DEFINITIONS
# ============================================================================

SENSOR_TYPES = {
    # Temperature & Humidity Sensors
    'dht11': {
        'name': 'DHT11 (Temperature + Humidity)',
        'category': 'home',
        'description': 'Basic temp/humidity sensor (±2°C, ±5% RH)',
        'icon': '🌡️',
        'pins_required': 1,
        'interface': 'digital',
        'update_interval_default': 60,
        'esphome_platform': 'dht',
        'esphome_model': 'DHT11',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'dht22': {
        'name': 'DHT22/AM2302 (Temperature + Humidity)',
        'category': 'home',
        'description': 'Accurate temp/humidity sensor (±0.5°C, ±2% RH)',
        'icon': '🌡️',
        'pins_required': 1,
        'interface': 'digital',
        'update_interval_default': 60,
        'esphome_platform': 'dht',
        'esphome_model': 'DHT22',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'bme280': {
        'name': 'BME280 (Temp + Humidity + Pressure)',
        'category': 'home',
        'description': 'I2C sensor for temp, humidity, and barometric pressure',
        'icon': '🌡️',
        'pins_required': 0,  # Uses I2C bus
        'interface': 'i2c',
        'update_interval_default': 60,
        'esphome_platform': 'bme280',
        'i2c_address_default': '0x76',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'bmp280': {
        'name': 'BMP280 (Temperature + Pressure)',
        'category': 'home',
        'description': 'I2C sensor for temp and barometric pressure',
        'icon': '🌡️',
        'pins_required': 0,
        'interface': 'i2c',
        'update_interval_default': 60,
        'esphome_platform': 'bmp280',
        'i2c_address_default': '0x76',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'ds18b20': {
        'name': 'DS18B20 (Waterproof Temperature)',
        'category': 'home',
        'description': '1-Wire waterproof temperature sensor',
        'icon': '🌡️',
        'pins_required': 1,
        'interface': '1-wire',
        'update_interval_default': 60,
        'esphome_platform': 'dallas',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # Light Sensors
    'bh1750': {
        'name': 'BH1750 (Light Intensity)',
        'category': 'home',
        'description': 'I2C ambient light sensor (lux)',
        'icon': '💡',
        'pins_required': 0,
        'interface': 'i2c',
        'update_interval_default': 60,
        'esphome_platform': 'bh1750',
        'i2c_address_default': '0x23',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # Motion & Presence Sensors
    'pir': {
        'name': 'PIR Motion Sensor',
        'category': 'home',
        'description': 'Passive infrared motion detector',
        'icon': '👁️',
        'pins_required': 1,
        'interface': 'digital',
        'esphome_platform': 'binary_sensor',
        'device_class': 'motion',
        'esp32_compatible': True,
        'esp8266_compatible': True,
        'esp8266_note': 'Cannot use GPIO16 (D0) - no interrupt support',
    },
    
    # Door/Window Sensors
    'reed_switch': {
        'name': 'Magnetic Reed Switch',
        'category': 'home',
        'description': 'Door/window open/close sensor',
        'icon': '🚪',
        'pins_required': 1,
        'interface': 'digital',
        'esphome_platform': 'binary_sensor',
        'device_class': 'door',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # SMART GARDEN SENSORS
    'soil_moisture_capacitive': {
        'name': 'Capacitive Soil Moisture Sensor',
        'category': 'garden',
        'description': 'Corrosion-resistant soil moisture sensor',
        'icon': '💧',
        'pins_required': 1,
        'interface': 'adc',
        'update_interval_default': 300,
        'esphome_platform': 'adc',
        'unit': '%',
        'esp32_compatible': True,
        'esp8266_compatible': True,
        'esp8266_note': 'Only ONE analog sensor allowed (A0 pin)',
    },
    'soil_ph': {
        'name': 'Soil pH Sensor',
        'category': 'garden',
        'description': 'Measures soil acidity/alkalinity',
        'icon': '🧪',
        'pins_required': 1,
        'interface': 'adc',
        'update_interval_default': 600,
        'esphome_platform': 'adc',
        'unit': 'pH',
        'esp32_compatible': True,
        'esp8266_compatible': True,
        'esp8266_note': 'Only ONE analog sensor allowed (A0 pin)',
    },
    'water_flow': {
        'name': 'Water Flow Sensor (YF-S201)',
        'category': 'garden',
        'description': 'Measures water flow rate',
        'icon': '🚰',
        'pins_required': 1,
        'interface': 'pulse_counter',
        'esphome_platform': 'pulse_counter',
        'unit': 'L/min',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # SMART FARMING SENSORS
    'co2_mhz19': {
        'name': 'MH-Z19 CO2 Sensor',
        'category': 'farming',
        'description': 'NDIR CO2 sensor for greenhouses',
        'icon': '🌿',
        'pins_required': 2,  # TX, RX
        'interface': 'uart',
        'update_interval_default': 60,
        'esphome_platform': 'mhz19',
        'unit': 'ppm',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # Distance Sensors
    'ultrasonic_hcsr04': {
        'name': '📏 Ultrasonic Distance (HC-SR04 - 2-pin)',
        'category': 'home',
        'description': 'Ultrasonic distance sensor (2cm-400cm range)',
        'icon': '📏',
        'pins_required': 2,
        'pin_labels': ['Trigger Pin', 'Echo Pin'],
        'pin_keys': ['trigger_pin', 'echo_pin'],
        'interface': 'ultrasonic',
        'update_interval_default': 60,
        'esphome_platform': 'ultrasonic',
        'unit': 'cm',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # INDUSTRIAL & HIGH-PRECISION SENSORS
    'sht30': {
        'name': 'SHT30/SHT31 (Industrial Temp + Humidity)',
        'category': 'industrial',
        'description': 'High-precision I2C temp/humidity sensor (±0.2°C, ±2% RH)',
        'icon': '🌡️',
        'pins_required': 0,
        'interface': 'i2c',
        'update_interval_default': 60,
        'esphome_platform': 'sht3xd',
        'i2c_address_default': '0x44',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'bme680': {
        'name': 'BME680 (Temp + Humidity + Pressure + Gas)',
        'category': 'industrial',
        'description': 'Multi-sensor: temp, humidity, pressure, air quality (VOC)',
        'icon': '🌡️',
        'pins_required': 0,
        'interface': 'i2c',
        'update_interval_default': 60,
        'esphome_platform': 'bme680',
        'i2c_address_default': '0x76',
        'multi_value': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'max31865': {
        'name': 'MAX31865 (PT100/PT1000 Industrial)',
        'category': 'industrial',
        'description': 'High-precision RTD temperature sensor for industrial use',
        'icon': '🌡️',
        'pins_required': 0,
        'interface': 'spi',
        'update_interval_default': 60,
        'esphome_platform': 'max31865',
        'esp32_compatible': True,
        'esp8266_compatible': False,
        'esp8266_note': 'Requires SPI - not recommended for ESP8266',
    },
    
    # AIR QUALITY SENSORS
    'ccs811': {
        'name': 'CCS811 (CO2 + TVOC)',
        'category': 'home',
        'description': 'Air quality sensor - CO2 equivalent and TVOC',
        'icon': '🌿',
        'pins_required': 0,
        'interface': 'i2c',
        'update_interval_default': 60,
        'esphome_platform': 'ccs811',
        'i2c_address_default': '0x5A',
        'multi_value': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'mq135': {
        'name': 'MQ-135 (Air Quality)',
        'category': 'home',
        'description': 'Analog air quality sensor (NH3, NOx, alcohol, benzene, smoke, CO2)',
        'icon': '🌿',
        'pins_required': 1,
        'interface': 'adc',
        'update_interval_default': 60,
        'esphome_platform': 'adc',
        'unit': 'ppm',
        'esp32_compatible': True,
        'esp8266_compatible': True,
        'esp8266_note': 'Only ONE analog sensor allowed (A0 pin)',
    },
    
    # ENERGY MONITORING
    'ina219': {
        'name': 'INA219 (Voltage + Current + Power)',
        'category': 'industrial',
        'description': 'I2C power monitor - voltage, current, and power measurement',
        'icon': '⚡',
        'pins_required': 0,
        'interface': 'i2c',
        'update_interval_default': 60,
        'esphome_platform': 'ina219',
        'i2c_address_default': '0x40',
        'multi_value': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'ina226': {
        'name': 'INA226 (High Precision Energy)',
        'category': 'industrial',
        'description': 'High-precision I2C power monitor',
        'icon': '⚡',
        'pins_required': 0,
        'interface': 'i2c',
        'update_interval_default': 60,
        'esphome_platform': 'ina226',
        'i2c_address_default': '0x40',
        'multi_value': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'hlw8012': {
        'name': 'HLW8012 (Power Consumption)',
        'category': 'home',
        'description': 'Power consumption monitor (used in Sonoff POW)',
        'icon': '⚡',
        'pins_required': 3,
        'pin_labels': ['SEL Pin', 'CF Pin', 'CF1 Pin'],
        'pin_keys': ['sel_pin', 'cf_pin', 'cf1_pin'],
        'interface': 'digital',
        'esphome_platform': 'hlw8012',
        'multi_value': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # SECURITY & SAFETY
    'vibration_sw420': {
        'name': 'SW-420 Vibration Sensor',
        'category': 'home',
        'description': 'Detects vibration/shock',
        'icon': '📳',
        'pins_required': 1,
        'interface': 'digital',
        'esphome_platform': 'binary_sensor',
        'device_class': 'vibration',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'rain_sensor': {
        'name': 'Rain Sensor',
        'category': 'garden',
        'description': 'Detects rain/water',
        'icon': '🌧️',
        'pins_required': 1,
        'interface': 'digital',
        'esphome_platform': 'binary_sensor',
        'device_class': 'moisture',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'ble_presence': {
        'name': 'Bluetooth Presence (ESP32 only)',
        'category': 'home',
        'description': 'Detect Bluetooth devices (phones, beacons)',
        'icon': '📱',
        'pins_required': 0,
        'interface': 'bluetooth',
        'esphome_platform': 'ble_presence',
        'esp32_compatible': True,
        'esp8266_compatible': False,
        'esp8266_note': 'ESP8266 does not have Bluetooth',
    },
    
    # SYSTEM HEALTH SENSORS
    'wifi_signal': {
        'name': 'WiFi Signal Strength',
        'category': 'system',
        'description': 'Monitor WiFi signal strength (RSSI)',
        'icon': '📶',
        'pins_required': 0,
        'interface': 'internal',
        'update_interval_default': 60,
        'esphome_platform': 'wifi_signal',
        'unit': 'dBm',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'uptime': {
        'name': 'Device Uptime',
        'category': 'system',
        'description': 'Track device uptime since last boot',
        'icon': '⏱️',
        'pins_required': 0,
        'interface': 'internal',
        'update_interval_default': 60,
        'esphome_platform': 'uptime',
        'unit': 's',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'internal_temperature': {
        'name': 'ESP32 CPU Temperature',
        'category': 'system',
        'description': 'Internal CPU temperature',
        'icon': '🌡️',
        'pins_required': 0,
        'interface': 'internal',
        'update_interval_default': 60,
        'esphome_platform': 'internal_temperature',
        'unit': '°C',
        'esp32_compatible': True,
        'esp8266_compatible': False,
        'esp8266_note': 'ESP8266 does not have internal temperature sensor',
    },
    
    # SMART FARMING - ADVANCED
    'soil_npk_modbus': {
        'name': 'NPK Soil Sensor (RS485/Modbus)',
        'category': 'farming',
        'description': 'Professional soil nutrient sensor (Nitrogen, Phosphorus, Potassium)',
        'icon': '🌱',
        'pins_required': 2,  # TX, RX
        'interface': 'uart',
        'update_interval_default': 300,
        'esphome_platform': 'modbus_controller',
        'multi_value': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
}

# ============================================================================
# ACTUATOR TYPE DEFINITIONS
# ============================================================================

ACTUATOR_TYPES = {
    # Switches & Relays
    'relay_active_high': {
        'name': 'Relay (Active High)',
        'category': 'home',
        'description': 'Standard relay, HIGH = ON',
        'icon': '🔌',
        'pins_required': 1,
        'esphome_platform': 'gpio',
        'inverted': False,
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'relay_active_low': {
        'name': 'Relay (Active Low)',
        'category': 'home',
        'description': 'Inverted relay, LOW = ON',
        'icon': '🔌',
        'pins_required': 1,
        'esphome_platform': 'gpio',
        'inverted': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # Lights
    'light_binary': {
        'name': 'Binary Light (ON/OFF)',
        'category': 'home',
        'description': 'Simple ON/OFF light',
        'icon': '💡',
        'pins_required': 1,
        'esphome_platform': 'binary',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'light_dimmable': {
        'name': 'Dimmable Light (PWM)',
        'category': 'home',
        'description': 'Brightness control via PWM',
        'icon': '💡',
        'pins_required': 1,
        'esphome_platform': 'monochromatic',
        'supports_brightness': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
        'esp8266_note': 'Software PWM may flicker during WiFi activity',
    },
    'light_rgb': {
        'name': '🌈 RGB Light (3-pin)',
        'category': 'home',
        'description': '3-channel color light (Red, Green, Blue)',
        'icon': '🌈',
        'pins_required': 3,
        'pin_labels': ['Red Pin', 'Green Pin', 'Blue Pin'],
        'pin_keys': ['red_pin', 'green_pin', 'blue_pin'],
        'esphome_platform': 'rgb',
        'supports_color': True,
        'esp32_compatible': True,
        'esp8266_compatible': True,
        'esp8266_note': 'Software PWM may flicker during WiFi activity',
    },
    'light_rgbw': {
        'name': '🌈 RGBW Light (4-pin)',
        'category': 'home',
        'description': '4-channel color light with white (Red, Green, Blue, White)',
        'icon': '🌈',
        'pins_required': 4,
        'pin_labels': ['Red Pin', 'Green Pin', 'Blue Pin', 'White Pin'],
        'pin_keys': ['red_pin', 'green_pin', 'blue_pin', 'white_pin'],
        'esphome_platform': 'rgbw',
        'supports_color': True,
        'supports_brightness': True,
        'esp32_compatible': True,
        'esp8266_compatible': False,  # Too many PWM channels
        'esp8266_note': 'Not recommended - requires 4 PWM channels',
    },
    
    # Stepper Motors
    'stepper_uln2003': {
        'name': '🔄 Stepper Motor (ULN2003 - 4-pin)',
        'category': 'industrial',
        'description': '28BYJ-48 stepper with ULN2003 driver (4-wire control)',
        'icon': '🔄',
        'pins_required': 4,
        'pin_labels': ['IN1', 'IN2', 'IN3', 'IN4'],
        'pin_keys': ['in1', 'in2', 'in3', 'in4'],
        'esphome_platform': 'uln2003',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'stepper_a4988': {
        'name': '🔄 Stepper Motor (A4988/DRV8825 - 2-pin)',
        'category': 'industrial',
        'description': 'Stepper with A4988/DRV8825 driver (Step + Direction)',
        'icon': '🔄',
        'pins_required': 2,
        'pin_labels': ['Step Pin', 'Direction Pin'],
        'pin_keys': ['step_pin', 'dir_pin'],
        'esphome_platform': 'a4988',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # Valves & Pumps
    'solenoid_valve': {
        'name': 'Solenoid Valve (Water/Gas)',
        'category': 'garden',
        'description': 'Electrically controlled valve',
        'icon': '🚰',
        'pins_required': 1,
        'esphome_platform': 'gpio',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'water_pump': {
        'name': 'Water Pump',
        'category': 'garden',
        'description': 'Electric water pump',
        'icon': '💧',
        'pins_required': 1,
        'esphome_platform': 'gpio',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # Climate Control
    'fan_binary': {
        'name': 'Fan (ON/OFF)',
        'category': 'home',
        'description': 'Simple ON/OFF fan',
        'icon': '🌀',
        'pins_required': 1,
        'esphome_platform': 'binary',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'heater': {
        'name': 'Heater',
        'category': 'farming',
        'description': 'Electric heater control',
        'icon': '🔥',
        'pins_required': 1,
        'esphome_platform': 'gpio',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    
    # ACCESS CONTROL & SECURITY
    'servo_lock': {
        'name': 'Servo Door Lock',
        'category': 'home',
        'description': 'Servo motor for door lock control',
        'icon': '🔐',
        'pins_required': 1,
        'esphome_platform': 'servo',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
    'buzzer': {
        'name': 'Buzzer/Alarm',
        'category': 'home',
        'description': 'Audible alarm or notification',
        'icon': '🔊',
        'pins_required': 1,
        'esphome_platform': 'gpio',
        'esp32_compatible': True,
        'esp8266_compatible': True,
    },
}

# ============================================================================
# GPIO CAPABILITIES - ESP32
# ============================================================================

ESP32_GPIO_CAPABILITIES = {
    'digital': [1, 2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33],
    'pwm': [2, 4, 5, 12, 13, 14, 15, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33],
    'adc': [32, 33, 34, 35, 36, 39],
    'i2c_sda': [21, 4, 15, 13, 16, 17, 25, 26, 27],
    'i2c_scl': [22, 5, 14, 18, 19, 23, 32, 33],
    'uart_tx': [1, 17, 25],
    'uart_rx': [3, 16, 26],
}

ESP32_RESERVED_PINS = [0, 6, 7, 8, 9, 10, 11]

# ============================================================================
# GPIO CAPABILITIES - ESP8266
# ============================================================================

ESP8266_GPIO_CAPABILITIES = {
    'digital': [0, 1, 2, 3, 4, 5, 12, 13, 14, 15, 16],
    'pwm': [0, 1, 2, 3, 4, 5, 12, 13, 14, 15, 16],
    'adc': [17],  # A0 pin - ONLY ONE!
    'i2c_sda': [4, 5, 12, 13, 14],
    'i2c_scl': [4, 5, 12, 13, 14],
    'uart_tx': [1, 15],
    'uart_rx': [3, 13],
}

ESP8266_RESERVED_PINS = [6, 7, 8, 9, 10, 11]

ESP8266_NOTES = {
    'adc': 'ESP8266 has only ONE ADC pin (A0). Multiple analog sensors require multiplexing.',
    'pwm': 'ESP8266 uses software PWM. May flicker during WiFi activity.',
    'gpio0': 'GPIO0 is boot mode pin. Avoid using for critical functions.',
    'gpio15': 'GPIO15 must be LOW at boot. Use pull-down resistor.',
    'gpio2': 'GPIO2 must be HIGH at boot. Use pull-up resistor.',
    'gpio16': 'GPIO16 (D0) has no interrupt support. Cannot be used for PIR/motion sensors.',
}

# NodeMCU D-pin mapping for ESP8266
ESP8266_D_PIN_MAP = {
    16: 'D0', 5: 'D1', 4: 'D2', 0: 'D3', 2: 'D4',
    14: 'D5', 12: 'D6', 13: 'D7', 15: 'D8'
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_gpio_capabilities(platform='esp32'):
    """Get GPIO capabilities for specified platform"""
    if platform.lower() == 'esp8266':
        return ESP8266_GPIO_CAPABILITIES
    return ESP32_GPIO_CAPABILITIES

def get_reserved_pins(platform='esp32'):
    """Get reserved pins for specified platform"""
    if platform.lower() == 'esp8266':
        return ESP8266_RESERVED_PINS
    return ESP32_RESERVED_PINS

def get_platform_notes(platform='esp8266'):
    """Get platform-specific notes and warnings"""
    if platform.lower() == 'esp8266':
        return ESP8266_NOTES
    return {}

def get_d_pin_label(gpio_pin, platform='esp8266'):
    """Get NodeMCU D-pin label for ESP8266"""
    if platform.lower() == 'esp8266' and gpio_pin in ESP8266_D_PIN_MAP:
        return ESP8266_D_PIN_MAP[gpio_pin]
    return None

def get_components_by_category(category, platform='esp32'):
    """Get all components for a specific category and platform"""
    all_components = {**SENSOR_TYPES, **ACTUATOR_TYPES}
    filtered = {}
    
    for key, component in all_components.items():
        if component.get('category') == category:
            # Check platform compatibility
            platform_key = f'{platform.lower()}_compatible'
            if component.get(platform_key, True):
                filtered[key] = component
    
    return filtered

def is_component_compatible(component_type, platform='esp32'):
    """Check if component is compatible with platform"""
    all_components = {**SENSOR_TYPES, **ACTUATOR_TYPES}
    component = all_components.get(component_type)
    
    if not component:
        return False
    
    platform_key = f'{platform.lower()}_compatible'
    return component.get(platform_key, True)
