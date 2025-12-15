"""
Device Connection Status View

Shows connected ESP32 devices and their serial ports.
"""

from django.shortcuts import render
from django.http import JsonResponse
from .usb_detector import get_esp32_ports, is_esp32_connected


def check_esp32_connection(request):
    """
    AJAX endpoint to check ESP32 connection status
    
    Returns JSON with connected devices
    """
    ports = get_esp32_ports()
    
    return JsonResponse({
        'connected': len(ports) > 0,
        'count': len(ports),
        'ports': ports,
    })
