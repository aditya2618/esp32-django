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
            
            logger.info(f"Starting ESPHome compilation for {self.device.node_name}")
            logger.info(f"Using ESPHome command: {esphome_cmd}")
            logger.info(f"YAML path: {yaml_path}")
            
            # Run ESPHome compile command
            result = subprocess.run(
                [esphome_cmd, 'compile', str(yaml_path)],
                cwd=str(self.build_dir),
                capture_output=True,
                text=True,
                timeout=900  # 15 minute timeout (increased from 5)
            )
            
            logs = result.stdout + result.stderr
            logger.info(f"ESPHome compilation completed with return code: {result.returncode}")
            
            if result.returncode == 0:
                # ESPHome sanitizes names by replacing underscores with hyphens
                esphome_name = self.device.node_name.replace('_', '-')
                
                # Find the compiled .bin file - try multiple possible locations
                # Prefer firmware.factory.bin (complete image with bootloader+partitions)
                possible_paths = [
                    self.build_dir / '.esphome' / 'build' / esphome_name / '.pioenvs' / esphome_name / 'firmware.factory.bin',
                    self.build_dir / '.esphome' / 'build' / self.device.node_name / '.pioenvs' / self.device.node_name / 'firmware.factory.bin',
                    self.build_dir / '.esphome' / 'build' / esphome_name / '.pioenvs' / esphome_name / 'firmware.bin',
                    self.build_dir / '.esphome' / 'build' / self.device.node_name / '.pioenvs' / self.device.node_name / 'firmware.bin',
                    self.build_dir / '.esphome' / 'build' / esphome_name / 'firmware.bin',
                    self.build_dir / '.esphome' / 'build' / self.device.node_name / 'firmware.bin',
                    self.build_dir / f'{self.device.node_name}.bin',
                ]
                
                bin_path = None
                for path in possible_paths:
                    logger.info(f"Checking path: {path}")
                    if path.exists():
                        bin_path = path
                        logger.info(f"Found .bin file at: {bin_path}")
                        break
                
                if bin_path:
                    logger.info(f"Firmware compiled successfully: {bin_path}")
                    return True, str(bin_path), logs
                else:
                    logger.error("Compilation succeeded but .bin file not found in expected locations")
                    logger.error(f"Searched paths: {[str(p) for p in possible_paths]}")
                    return False, None, logs + "\n\nError: Compiled .bin file not found"
            else:
                logger.error(f"Compilation failed: {logs}")
                return False, None, logs
                
        except subprocess.TimeoutExpired:
            error_msg = "Compilation timed out after 15 minutes"
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
    
    def create_manifest(self, bin_path, platform='esp32'):
        """
        Create manifest.json for ESPHome Web Tools
        
        This allows web-based flashing via https://web.esphome.io/
        
        Args:
            bin_path: Path to firmware.bin file
            platform: 'esp32' or 'esp8266'
        """
        import json
        
        # Determine chip family for manifest
        chip_family = "ESP8266" if platform.lower() == 'esp8266' else "ESP32"
        
        manifest = {
            "name": self.device.name,
            "version": "1.0.0",
            "home_assistant_domain": "esphome",
            "new_install_prompt_erase": True,
            "builds": [
                {
                    "chipFamily": chip_family,
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


def compile_and_prepare_firmware(device, yaml_content, platform='esp32'):
    """
    Compile firmware and prepare for flashing
    
    Args:
        device: Device instance
        yaml_content: ESPHome YAML configuration
        platform: 'esp32' or 'esp8266' (default: 'esp32')
    
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
        # Copy the .bin file to a predictable location for download
        import shutil
        
        # Use firmware.factory.bin if available (contains bootloader+partitions+app)
        # Otherwise fall back to firmware.bin
        source_path = Path(bin_path)
        if 'firmware.factory.bin' in str(bin_path):
            dest_bin = builder.build_dir / 'firmware.factory.bin'
            bin_filename = 'firmware.factory.bin'
        else:
            dest_bin = builder.build_dir / 'firmware.bin'
            bin_filename = 'firmware.bin'
            
        shutil.copy2(bin_path, dest_bin)
        logger.info(f"Copied firmware from {bin_path} to {dest_bin}")
        
        # Create manifest for web flashing with correct platform
        builder.create_manifest(str(dest_bin), platform=platform)
        
        # Get URLs - use the copied file location
        bin_url = f"{settings.MEDIA_URL}esphome_builds/{device.node_name}/{bin_filename}"
        web_flasher_url = f"https://web.esphome.io/?configuration={settings.SITE_URL}{bin_url}"
        
        return {
            'success': True,
            'bin_path': str(dest_bin),
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
