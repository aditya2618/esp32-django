# ESP32 GPIO Constants and Capabilities

# Reserved/Unsafe GPIO pins (boot, flash, etc.)
ESP32_RESERVED_PINS = [0, 2, 6, 7, 8, 9, 10, 11, 12, 15]

# GPIO capabilities per device type
ESP32_GPIO_CAPABILITIES = {
    "relay": list(range(0, 40)),  # Most GPIOs can drive relays
    "switch": list(range(0, 40)),  # Most GPIOs can read switches
    "dht22": [4, 5, 13, 14, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33],
    "pwm": [2, 4, 5, 12, 13, 14, 15, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33],
    "light": [2, 4, 5, 12, 13, 14, 15, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33],
    "fan": [2, 4, 5, 12, 13, 14, 15, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33],
}

# Remove reserved pins from all capabilities
for device_type in ESP32_GPIO_CAPABILITIES:
    ESP32_GPIO_CAPABILITIES[device_type] = [
        pin for pin in ESP32_GPIO_CAPABILITIES[device_type] 
        if pin not in ESP32_RESERVED_PINS
    ]
