from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class DevicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.devices'
    
    def ready(self):
        """Initialize MQTT listener when Django starts"""
        # Import here to avoid AppRegistryNotReady error
        from .mqtt_listener import start_mqtt_listener
        
        # Only start in main process, not in reloader
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        try:
            start_mqtt_listener()
            logger.info("MQTT listener started successfully")
        except Exception as e:
            logger.error(f"Failed to start MQTT listener: {e}")
