"""
USB Device Detection Utility

Detects connected ESP32 devices via USB serial ports.
"""

import serial.tools.list_ports


def get_esp32_ports():
    """
    Detect connected ESP32 devices
    
    Returns:
        list: List of dicts with port info
    """
    esp32_ports = []
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        # ESP32 typically shows up with these identifiers
        if any(keyword in port.description.lower() for keyword in ['cp210', 'ch340', 'usb serial', 'uart', 'esp32']):
            esp32_ports.append({
                'port': port.device,
                'description': port.description,
                'hwid': port.hwid,
            })
    
    return esp32_ports


def is_esp32_connected():
    """Check if any ESP32 device is connected"""
    return len(get_esp32_ports()) > 0
