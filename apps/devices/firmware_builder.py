"""
Firmware Builder Service

Handles ESPHome firmware compilation and flashing directly from Django.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FirmwareBuilder:
    """Service for building and flashing ESPHome firmware"""
    
    def __init__(self, device):
        self.device = device
        self.build_dir = Path(settings.MEDIA_ROOT) / 'esphome_builds' / device.node_name
        self.build_dir.mkdir(parents=True, exist_ok=True)
    
    def save_yaml(self, yaml_content):
        """Save YAML configuration to file"""
        yaml_path = self.build_dir / f"{self.device.node_name}.yaml"
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        return yaml_path
    
    def compile_firmware(self, yaml_path):
        """
        Compile ESPHome firmware
        
        Returns:
            tuple: (success: bool, bin_path: str, logs: str)
        """
        try:
            # Get path to esphome in virtual environment
            import sys
            venv_python = sys.executable
            venv_dir = Path(venv_python).parent
            esphome_exe = venv_dir / 'esphome.exe' if os.name == 'nt' else venv_dir / 'esphome'
            
            # Use esphome from venv if it exists, otherwise try system esphome
            esphome_cmd = str(esphome_exe) if esphome_exe.exists() else 'esphome'
            
            # Run ESPHome compile command
            result = subprocess.run(
                [esphome_cmd, 'compile', str(yaml_path)],
                cwd=str(self.build_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            logs = result.stdout + result.stderr
            
            if result.returncode == 0:
                # Find the compiled .bin file
                bin_path = self.build_dir / '.esphome' / 'build' / self.device.node_name / 'firmware.bin'
                if bin_path.exists():
                    logger.info(f"Firmware compiled successfully: {bin_path}")
                    return True, str(bin_path), logs
                else:
                    logger.error("Compilation succeeded but .bin file not found")
                    return False, None, logs + "\n\nError: Compiled .bin file not found"
            else:
                logger.error(f"Compilation failed: {logs}")
                return False, None, logs
                
        except subprocess.TimeoutExpired:
            error_msg = "Compilation timed out after 5 minutes"
            logger.error(error_msg)
            return False, None, error_msg
        except FileNotFoundError as e:
            error_msg = f"ESPHome not found. Please ensure ESPHome is installed in your virtual environment.\nRun: pip install esphome\nError: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Compilation error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def get_web_flasher_url(self, bin_path):
        """
        Generate URL for web-based flashing using ESPHome Web Tools
        
        Returns:
            str: URL to web flasher with firmware
        """
        # ESPHome Web Tools allows flashing via browser
        # We'll provide the .bin file for download and use ESP Web Tools
        from django.urls import reverse
        bin_url = settings.MEDIA_URL + f'esphome_builds/{self.device.node_name}/firmware.bin'
        return bin_url
    
    def create_manifest(self, bin_path):
        """
        Create manifest.json for ESPHome Web Tools
        
        This allows web-based flashing via https://web.esphome.io/
        """
        import json
        
        manifest = {
            "name": self.device.name,
            "version": "1.0.0",
            "home_assistant_domain": "esphome",
            "new_install_prompt_erase": True,
            "builds": [
                {
                    "chipFamily": "ESP32",
                    "parts": [
                        {
                            "path": f"firmware.bin",
                            "offset": 0
                        }
                    ]
                }
            ]
        }
        
        manifest_path = self.build_dir / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest_path


def compile_and_prepare_firmware(device, yaml_content):
    """
    Compile firmware and prepare for flashing
    
    Args:
        device: Device instance
        yaml_content: ESPHome YAML configuration
    
    Returns:
        dict: {
            'success': bool,
            'bin_path': str,
            'bin_url': str,
            'logs': str,
            'web_flasher_url': str
        }
    """
    builder = FirmwareBuilder(device)
    
    # Save YAML
    yaml_path = builder.save_yaml(yaml_content)
    
    # Compile firmware
    success, bin_path, logs = builder.compile_firmware(yaml_path)
    
    if success:
        # Create manifest for web flashing
        builder.create_manifest(bin_path)
        
        # Get URLs
        bin_url = builder.get_web_flasher_url(bin_path)
        web_flasher_url = f"https://web.esphome.io/?configuration={settings.SITE_URL}{bin_url}"
        
        return {
            'success': True,
            'bin_path': bin_path,
            'bin_url': bin_url,
            'logs': logs,
            'web_flasher_url': web_flasher_url,
            'manifest_url': f"{settings.MEDIA_URL}esphome_builds/{device.node_name}/manifest.json"
        }
    else:
        return {
            'success': False,
            'bin_path': None,
            'bin_url': None,
            'logs': logs,
            'web_flasher_url': None,
            'manifest_url': None
        }
