"""
ESP32 Flash Reader Service

Reads information from ESP32 devices connected via USB using esptool.
"""

import subprocess
import json
import logging
import serial.tools.list_ports
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def detect_esp32_ports() -> List[Dict[str, str]]:
    """
    Detect all available COM ports that might have ESP32/ESP8266 devices.
    
    Returns:
        List of dicts with port info: [{'port': 'COM3', 'description': '...'}]
    """
    ports = []
    for port in serial.tools.list_ports.comports():
        # Common ESP32/ESP8266 USB-to-Serial chips
        esp_identifiers = [
            'CP210',  # Silicon Labs CP2102
            'CH340',  # WCH CH340
            'CH341',  # WCH CH341
            'FTDI',   # FTDI chips
            'USB-SERIAL',
            'USB Serial',
            'UART',   # Generic UART
        ]
        
        description = port.description.upper()
        if any(identifier.upper() in description for identifier in esp_identifiers):
            ports.append({
                'port': port.device,
                'description': port.description,
                'hwid': port.hwid
            })
    
    return ports


def read_esp32_info(port: str = 'auto') -> Dict:
    """
    Read ESP32/ESP8266 chip and flash information using esptool.
    
    Args:
        port: COM port (e.g., 'COM3') or 'auto' to auto-detect
        
    Returns:
        dict: {
            'success': bool,
            'chip_type': str,  # ESP32, ESP8266, ESP32-C3, etc.
            'mac_address': str,
            'flash_size': str,
            'flash_mode': str,
            'flash_freq': str,
            'port': str,
            'error': str (if failed)
        }
    """
    try:
        # Auto-detect port if needed
        if port == 'auto':
            detected_ports = detect_esp32_ports()
            if not detected_ports:
                return {
                    'success': False,
                    'error': 'No ESP32/ESP8266 device detected. Please connect your device via USB.'
                }
            port = detected_ports[0]['port']
            logger.info(f"Auto-detected ESP device on port: {port}")
        
        # Use esptool to read chip info
        import sys
        venv_python = sys.executable
        venv_dir = venv_python.replace('python.exe', '').replace('python', '')
        
        # Run esptool flash_id command
        cmd = [
            venv_python, '-m', 'esptool',
            '--port', port,
            '--baud', '115200',
            'flash_id'
        ]
        
        logger.info(f"Running esptool command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        logger.info(f"Esptool output: {output}")
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'Failed to read ESP32: {output}',
                'port': port
            }
        
        # Parse output
        info = {
            'success': True,
            'port': port,
            'chip_type': 'Unknown',
            'mac_address': 'Unknown',
            'flash_size': 'Unknown',
            'flash_mode': 'Unknown',
            'flash_freq': 'Unknown'
        }
        
        # Extract chip type
        if 'Chip is' in output:
            for line in output.split('\n'):
                if 'Chip is' in line:
                    info['chip_type'] = line.split('Chip is')[1].strip().split()[0]
                    break
        
        # Extract MAC address
        if 'MAC:' in output:
            for line in output.split('\n'):
                if 'MAC:' in line:
                    mac = line.split('MAC:')[1].strip().split()[0]
                    info['mac_address'] = mac
                    break
        
        # Extract flash size
        if 'Detected flash size:' in output:
            for line in output.split('\n'):
                if 'Detected flash size:' in line:
                    info['flash_size'] = line.split('Detected flash size:')[1].strip()
                    break
        
        # Extract flash mode and frequency
        if 'Flash mode:' in output:
            for line in output.split('\n'):
                if 'Flash mode:' in line:
                    parts = line.split(',')
                    for part in parts:
                        if 'Flash mode:' in part:
                            info['flash_mode'] = part.split(':')[1].strip()
                        elif 'Flash frequency:' in part:
                            info['flash_freq'] = part.split(':')[1].strip()
        
        logger.info(f"Successfully read ESP32 info: {info}")
        return info
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Timeout reading ESP32. Please check connection and try again.',
            'port': port
        }
    except Exception as e:
        logger.error(f"Error reading ESP32: {str(e)}")
        return {
            'success': False,
            'error': f'Error: {str(e)}',
            'port': port
        }


def read_partition_table(port: str) -> Optional[Dict]:
    """
    Read ESP32 partition table.
    
    Args:
        port: COM port
        
    Returns:
        dict with partition info or None if failed
    """
    try:
        import sys
        venv_python = sys.executable
        
        cmd = [
            venv_python, '-m', 'esptool',
            '--port', port,
            '--baud', '115200',
            'read_flash', '0x8000', '0xC00', 'partition_table.bin'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse partition table (simplified)
            return {'success': True, 'message': 'Partition table read successfully'}
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error reading partition table: {str(e)}")
        return None
