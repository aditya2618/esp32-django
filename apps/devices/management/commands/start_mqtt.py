import subprocess
import os
import signal
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Start Mosquitto MQTT broker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--stop',
            action='store_true',
            help='Stop the running Mosquitto broker',
        )

    def handle(self, *args, **options):
        mosquitto_path = r"C:\Program Files\mosquitto\mosquitto.exe"
        config_path = os.path.join(settings.BASE_DIR, 'mosquitto.conf')
        
        if options['stop']:
            self.stop_mosquitto()
            return

        # Check if Mosquitto is already running
        if self.is_mosquitto_running():
            self.stdout.write(self.style.WARNING('Mosquitto is already running'))
            return

        # Start Mosquitto
        try:
            self.stdout.write('Starting Mosquitto MQTT broker...')
            
            # Start Mosquitto in a subprocess
            process = subprocess.Popen(
                [mosquitto_path, '-c', config_path, '-v'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE  # Opens in new window
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Mosquitto started successfully (PID: {process.pid})'
            ))
            self.stdout.write(f'Config: {config_path}')
            self.stdout.write('Check the Mosquitto console window for logs')
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'✗ Mosquitto not found at: {mosquitto_path}'
            ))
            self.stdout.write('Install Mosquitto: choco install mosquitto')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error starting Mosquitto: {e}'))

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
