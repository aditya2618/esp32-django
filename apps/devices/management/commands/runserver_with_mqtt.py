import subprocess
import os
import time
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = 'Run Django development server with MQTT broker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=str,
            default='8000',
            help='Port to run Django server on (default: 8000)',
        )

    def handle(self, *args, **options):
        mosquitto_path = r"C:\Program Files\mosquitto\mosquitto.exe"
        config_path = os.path.join(settings.BASE_DIR, 'mosquitto.conf')
        port = options['port']
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('  ESP32 Smart Home Platform - Starting Services'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Step 1: Start Mosquitto MQTT Broker
        self.stdout.write('\n[1/2] Starting Mosquitto MQTT Broker...')
        
        if self.is_mosquitto_running():
            self.stdout.write(self.style.WARNING('  ⚠ Mosquitto is already running'))
        else:
            try:
                # Start Mosquitto in background
                subprocess.Popen(
                    [mosquitto_path, '-c', config_path, '-v'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                time.sleep(1)  # Wait for Mosquitto to start
                
                if self.is_mosquitto_running():
                    self.stdout.write(self.style.SUCCESS('  ✓ Mosquitto MQTT Broker started'))
                    self.stdout.write(f'    Config: {config_path}')
                else:
                    self.stdout.write(self.style.ERROR('  ✗ Failed to start Mosquitto'))
                    return
                    
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ Mosquitto not found at: {mosquitto_path}'
                ))
                self.stdout.write('    Install: choco install mosquitto')
                return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
                return
        
        # Step 2: Start Django Server
        self.stdout.write(f'\n[2/2] Starting Django Development Server on port {port}...')
        self.stdout.write(self.style.SUCCESS('  ✓ Django server starting'))
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('  All Services Running!'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'  Web Interface: http://127.0.0.1:{port}')
        self.stdout.write(f'  MQTT Broker:   localhost:1883')
        self.stdout.write('  Press Ctrl+C to stop both services')
        self.stdout.write('=' * 70 + '\n')
        
        try:
            # Run Django development server (this blocks)
            call_command('runserver', port)
        except KeyboardInterrupt:
            self.stdout.write('\n\nShutting down services...')
            self.stop_mosquitto()
            self.stdout.write(self.style.SUCCESS('✓ All services stopped'))
            sys.exit(0)

    def is_mosquitto_running(self):
        """Check if Mosquitto is already running"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq mosquitto.exe'],
                capture_output=True,
                text=True
            )
            return 'mosquitto.exe' in result.stdout
        except Exception:
            return False

    def stop_mosquitto(self):
        """Stop running Mosquitto instances"""
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'mosquitto.exe'], 
                         capture_output=True)
            self.stdout.write(self.style.SUCCESS('✓ Mosquitto stopped'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error stopping Mosquitto: {e}'))
