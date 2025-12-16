"""
ESPHome CLI Flash Service

Handles ESPHome firmware compilation and flashing via command-line interface.
"""

import subprocess
import logging
from pathlib import Path
import serial.tools.list_ports

logger = logging.getLogger(__name__)


def detect_esp_ports():
    """
    Detect connected ESP32/ESP8266 devices via USB
    
    Returns:
        list: List of dicts with port info [{'port': 'COM3', 'description': '...'}]
    """
    ports = []
    
    for port in serial.tools.list_ports.comports():
        # Look for common ESP USB-to-Serial chips
        if any(keyword in port.description.upper() for keyword in 
               ['CP210', 'CH340', 'CH341', 'FTDI', 'USB-SERIAL', 'UART', 'SILICON LABS']):
            ports.append({
                'port': port.device,
                'description': port.description,
                'hwid': port.hwid
            })
            logger.info(f"Found ESP device: {port.device} - {port.description}")
    
    return ports


def compile_firmware(yaml_path):
    """
    Compile ESPHome firmware from YAML
    
    Args:
        yaml_path: Path to YAML configuration file
        
    Returns:
        dict: {'success': bool, 'logs': str, 'bin_path': str}
    """
    try:
        logger.info(f"Compiling firmware: {yaml_path}")
        
        result = subprocess.run(
            ['esphome', 'compile', str(yaml_path)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            cwd=str(Path(yaml_path).parent)
        )
        
        logs = result.stdout + result.stderr
        success = result.returncode == 0
        
        if success:
            logger.info("Firmware compilation successful")
            # Find the compiled binary
            node_name = Path(yaml_path).stem.replace('_', '-')
            bin_path = Path(yaml_path).parent / '.esphome' / 'build' / node_name / '.pioenvs' / node_name / 'firmware.bin'
            
            return {
                'success': True,
                'logs': logs,
                'bin_path': str(bin_path) if bin_path.exists() else None
            }
        else:
            logger.error(f"Firmware compilation failed: {logs}")
            return {
                'success': False,
                'logs': logs,
                'bin_path': None
            }
            
    except subprocess.TimeoutExpired:
        error_msg = "Compilation timed out after 10 minutes"
        logger.error(error_msg)
        return {'success': False, 'logs': error_msg, 'bin_path': None}
    except FileNotFoundError:
        error_msg = "ESPHome not found. Please install: pip install esphome"
        logger.error(error_msg)
        return {'success': False, 'logs': error_msg, 'bin_path': None}
    except Exception as e:
        error_msg = f"Compilation error: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'logs': error_msg, 'bin_path': None}


def flash_firmware(yaml_path, port=None):
    """
    Flash compiled firmware to ESP device
    
    Args:
        yaml_path: Path to YAML configuration file
        port: Serial port (e.g., 'COM3' or '/dev/ttyUSB0'). If None, auto-detect.
        
    Returns:
        dict: {'success': bool, 'logs': str, 'port': str}
    """
    try:
        logger.info(f"Flashing firmware to port: {port or 'auto-detect'}")
        
        cmd = ['esphome', 'upload', str(yaml_path)]
        if port:
            cmd.extend(['--device', port])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=str(Path(yaml_path).parent)
        )
        
        logs = result.stdout + result.stderr
        success = result.returncode == 0
        
        if success:
            logger.info("Firmware flashed successfully")
        else:
            logger.error(f"Firmware flash failed: {logs}")
        
        return {
            'success': success,
            'logs': logs,
            'port': port
        }
        
    except subprocess.TimeoutExpired:
        error_msg = "Flash timeout after 5 minutes"
        logger.error(error_msg)
        return {'success': False, 'logs': error_msg, 'port': port}
    except Exception as e:
        error_msg = f"Flash error: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'logs': error_msg, 'port': port}


def compile_and_flash(yaml_path, port=None):
    """
    Compile and flash firmware in one operation (uses 'esphome run')
    
    Args:
        yaml_path: Path to YAML configuration file
        port: Serial port. If None, auto-detect.
        
    Returns:
        dict: {'success': bool, 'logs': str, 'port': str}
    """
    try:
        logger.info(f"Compiling and flashing firmware: {yaml_path}")
        
        # Use --no-logs to prevent interactive mode and speed up process
        cmd = ['esphome', 'run', str(yaml_path), '--no-logs']
        if port:
            cmd.extend(['--device', port])
        
        # Run subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout (reduced from 15)
            cwd=str(Path(yaml_path).parent)
        )
        
        logs = result.stdout + result.stderr
        success = result.returncode == 0
        
        if success:
            logger.info("Firmware compiled and flashed successfully")
        else:
            logger.error(f"Compile and flash failed: {logs}")
        
        return {
            'success': success,
            'logs': logs,
            'port': port
        }
        
    except subprocess.TimeoutExpired:
        error_msg = "Compile and flash timed out after 10 minutes"
        logger.error(error_msg)
        return {'success': False, 'logs': error_msg, 'port': port}
    except FileNotFoundError:
        error_msg = "ESPHome not found. Please install: pip install esphome"
        logger.error(error_msg)
        return {'success': False, 'logs': error_msg, 'port': port}
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'logs': error_msg, 'port': port}
