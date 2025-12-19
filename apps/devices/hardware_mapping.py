# Hardware Type to Entity Type Mapping
# This mapping automatically determines the correct entity_type based on hardware_type

HARDWARE_TO_ENTITY_TYPE = {
    # Sensors -> 'sensor'
    'dht11': 'sensor',
    'dht22': 'sensor',
    'bme280': 'sensor',
    'bmp280': 'sensor',
    'ds18b20': 'sensor',
    'bh1750': 'sensor',
    'soil_moisture_capacitive': 'sensor',
    'soil_ph': 'sensor',
    'water_flow': 'sensor',
    'co2_mhz19': 'sensor',
    'ultrasonic_hcsr04': 'sensor',
    'sht30': 'sensor',
    'bme680': 'sensor',
    'max31865': 'sensor',
    'ccs811': 'sensor',
    'mq135': 'sensor',
    'ina219': 'sensor',
    'ina226': 'sensor',
    'hlw8012': 'sensor',
    'wifi_signal': 'sensor',
    'uptime': 'sensor',
    'internal_temperature': 'sensor',
    'soil_npk_modbus': 'sensor',
    
    # Binary Sensors -> 'binary_sensor'
    'pir': 'binary_sensor',
    'reed_switch': 'binary_sensor',
    'vibration_sw420': 'binary_sensor',
    'rain_sensor': 'binary_sensor',
    'ble_presence': 'binary_sensor',
    
    # Switches/Relays -> 'switch'
    'relay_active_high': 'switch',
    'relay_active_low': 'switch',
    'solenoid_valve': 'switch',
    'water_pump': 'switch',
    'heater': 'switch',
    'buzzer': 'switch',
    
    # Lights -> 'light'
    'light_binary': 'light',
    'light_dimmable': 'light',
    'light_rgb': 'light',
    'light_rgbw': 'light',
    
    # Fans -> 'fan'
    'fan_binary': 'fan',
    
    # Servos/Motors -> 'cover' (for steppers used as blinds/curtains)
    'stepper_uln2003': 'cover',
    'stepper_a4988': 'cover',
    'servo_lock': 'lock',
}

def get_entity_type_for_hardware(hardware_type):
    """
    Get the appropriate entity_type for a given hardware_type.
    This makes entity_type selection automatic based on hardware selection.
    """
    return HARDWARE_TO_ENTITY_TYPE.get(hardware_type, 'sensor')  # Default to sensor
