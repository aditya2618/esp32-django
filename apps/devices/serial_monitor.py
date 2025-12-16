"""
ESP32 Serial Monitor

Reads serial output from ESP32 to extract configuration information.
"""

import serial
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def read_serial_output(port: str, duration: int = 15) -> Dict:
    """
    Read serial output from ESP32/ESP8266 to extract configuration.
    
    Args:
        port: COM port (e.g., 'COM3')
        duration: How long to read serial output (seconds)
        
    Returns:
        dict: {
            'success': bool,
            'device_name': str,
            'entities': list,
            'gpio_pins': dict,
            'logs': str,
            'error': str (if failed)
        }
    """
    try:
        import time
        
        # First, wait a moment for ESP to fully boot
        logger.info(f"Waiting for ESP device to boot on {port}...")
        time.sleep(3)
        
        # Open serial connection at 115200 (ESPHome default after boot)
        ser = serial.Serial(
            port=port,
            baudrate=115200,
            timeout=1
        )
        
        logger.info(f"Opened serial connection on {port} at 115200 baud")
        
        # Clear any initial garbage
        ser.reset_input_buffer()
        time.sleep(0.5)
        
        # Read for specified duration
        start_time = time.time()
        output = []
        valid_lines = []
        
        while time.time() - start_time < duration:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        output.append(line)
                        # Only keep lines that look like ESPHome logs
                        if any(marker in line for marker in ['[C]', '[I]', '[W]', '[E]', '[D]']):
                            valid_lines.append(line)
                            logger.debug(f"Serial: {line}")
                except Exception as e:
                    logger.debug(f"Error reading line: {e}")
                    continue
        
        ser.close()
        
        # Use valid lines for parsing, full output for display
        full_output = '\n'.join(output)
        
        result = {
            'success': True,
            'device_name': 'Unknown',
            'entities': [],
            'gpio_pins': {},
            'logs': full_output
        }
        
        # If no valid ESPHome logs found, provide helpful message
        if not valid_lines:
            # Check if there's any output at all
            if not output or len(full_output.strip()) < 50:
                result['logs'] = (
                    "[ERROR] No serial output detected.\n\n"
                    "Possible causes:\n"
                    "1. ESP32/ESP8266 is not booting (check power/USB connection)\n"
                    "2. Wrong COM port selected\n"
                    "3. USB cable is charge-only (not data cable)\n\n"
                    "Try:\n"
                    "- Unplug and replug the USB cable\n"
                    "- Try a different USB port\n"
                    "- Use a different USB cable (must support data transfer)"
                )
            else:
                result['logs'] = (
                    full_output + 
                    "\n\n[INFO] No ESPHome logs detected in the output above.\n\n"
                    "This ESP32/ESP8266 may have:\n"
                    "1. Different firmware (not ESPHome)\n"
                    "2. ESPHome firmware that's not booting correctly\n"
                    "3. Corrupted firmware\n\n"
                    "The garbled text at the start is normal - it's from the ESP boot ROM.\n"
                    "ESPHome logs should appear after that, starting with [I], [C], [W], or [E] markers.\n\n"
                    "To check what's programmed:\n"
                    "- Use 'Flash Info' above to see chip type (ESP32/ESP8266) and flash size\n"
                    "- If you programmed this with ESPHome, try re-flashing the firmware"
                )
            return result
        
        # Extract device name from valid lines
        device_name_found = False
        for line in valid_lines:
            # Try to find hostname first (most reliable)
            if 'hostname:' in line.lower() or 'Hostname:' in line:
                import re
                name_match = re.search(r"[Hh]ostname:\s*['\"]?([a-zA-Z0-9_-]+)['\"]?", line)
                if name_match:
                    result['device_name'] = name_match.group(1)
                    device_name_found = True
                    break
            
            # Try esphome name configuration
            if not device_name_found and 'esphome' in line.lower() and 'name:' in line.lower():
                import re
                name_match = re.search(r"name:\s*['\"]?([a-zA-Z0-9_-]+)['\"]?", line, re.IGNORECASE)
                if name_match:
                    result['device_name'] = name_match.group(1)
                    device_name_found = True
                    break
            
            # Try project name as fallback
            if not device_name_found and 'Project' in line and 'version' in line.lower():
                import re
                # Extract project name like "esphome.web"
                project_match = re.search(r"Project\s+([a-zA-Z0-9._-]+)", line)
                if project_match:
                    project_name = project_match.group(1)
                    if project_name != 'esphome.web':  # Skip generic web project
                        result['device_name'] = project_name.replace('.', '_')
                        device_name_found = True
        
        # If still unknown, check for mDNS hostname
        if not device_name_found:
            for line in valid_lines:
                if 'mdns' in line.lower() and 'hostname:' in line.lower():
                    import re
                    name_match = re.search(r"[Hh]ostname:\s*([a-zA-Z0-9_-]+)", line)
                    if name_match:
                        result['device_name'] = name_match.group(1)
                        break
        
        # Extract GPIO configurations from valid lines
        gpio_configs = {}
        
        for line in valid_lines:
            # Look for GPIO configurations in component logs
            # ESPHome logs GPIO info like "[C][gpio.output:XXX]: 'component_name'"
            if ('[C][gpio' in line.lower() or '[C][output' in line.lower() or 
                'pin:' in line.lower() and 'GPIO' in line):
                import re
                # Extract GPIO pin number
                gpio_match = re.search(r'GPIO(\d+)', line, re.IGNORECASE)
                if gpio_match:
                    pin = gpio_match.group(1)
                    # Try to extract component name
                    name_match = re.search(r"['\"]([^'\"]+)['\"]", line)
                    if name_match:
                        component_name = name_match.group(1)
                        if component_name and component_name not in ['GPIO', 'Pin', '']:
                            gpio_configs[pin] = component_name
        
        # If no GPIO configs found, add helpful message
        if not gpio_configs:
            result['gpio_message'] = "No custom GPIO configurations detected. This device may be running base ESPHome Web firmware without custom entities."
        
        result['gpio_pins'] = gpio_configs
        
        # Extract entities from valid lines
        entities = []
        entity_types = {
            'light': 'light',
            'switch': 'switch',
            'sensor': 'sensor',
            'binary_sensor': 'binary_sensor',
            'fan': 'fan',
            'cover': 'cover'
        }
        
        for line in valid_lines:
            for entity_key, entity_type in entity_types.items():
                if f'[C][{entity_key}' in line.lower():
                    import re
                    name_match = re.search(r"['\"]([^'\"]+)['\"]", line)
                    if name_match:
                        entity_name = name_match.group(1)
                        # Avoid duplicates
                        if not any(e['name'] == entity_name for e in entities):
                            entities.append({
                                'name': entity_name,
                                'type': entity_type
                            })
        
        # Add helpful message if no entities found
        if not entities:
            result['entity_message'] = "No custom entities detected. This appears to be base ESPHome Web firmware. You can add entities by flashing custom ESPHome configuration."
        
        result['entities'] = entities
        
        return result
        
    except serial.SerialException as e:
        logger.error(f"Serial error: {str(e)}")
        return {
            'success': False,
            'error': f'Failed to open serial port: {str(e)}'
        }
    except Exception as e:
        logger.error(f"Error reading serial: {str(e)}")
        return {
            'success': False,
            'error': f'Error: {str(e)}'
        }


def trigger_esp32_reboot(port: str) -> bool:
    """
    Trigger ESP32 reboot to get fresh boot logs.
    
    Args:
        port: COM port
        
    Returns:
        bool: Success
    """
    try:
        import subprocess
        import sys
        
        venv_python = sys.executable
        
        # Use esptool to reset ESP32
        cmd = [
            venv_python, '-m', 'esptool',
            '--port', port,
            '--after', 'hard_reset',
            'chip_id'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Error rebooting ESP32: {str(e)}")
        return False
