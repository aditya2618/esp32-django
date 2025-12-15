import json
import logging
import paho.mqtt.client as mqtt
from django.conf import settings

logger = logging.getLogger(__name__)

# Global MQTT client instance
mqtt_client = None


def get_mqtt_client():
    """Get or create MQTT client instance"""
    global mqtt_client
    
    if mqtt_client is None:
        mqtt_client = mqtt.Client(client_id="django_smarthome")
        
        # Get MQTT settings from Django settings
        mqtt_broker = getattr(settings, 'MQTT_BROKER', 'localhost')
        mqtt_port = getattr(settings, 'MQTT_PORT', 1883)
        mqtt_username = getattr(settings, 'MQTT_USERNAME', None)
        mqtt_password = getattr(settings, 'MQTT_PASSWORD', None)
        
        if mqtt_username and mqtt_password:
            mqtt_client.username_pw_set(mqtt_username, mqtt_password)
        
        try:
            mqtt_client.connect(mqtt_broker, mqtt_port, 60)
            mqtt_client.loop_start()
            logger.info(f"Connected to MQTT broker at {mqtt_broker}:{mqtt_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
    
    return mqtt_client


def send_command(entity, value):
    """
    Send command to ESPHome device via MQTT.
    
    Args:
        entity: Entity instance
        value: Command value (ON/OFF for switches, 0-100 for dimmers, etc.)
    """
    client = get_mqtt_client()
    topic = entity.command_topic()
    
    if not topic:
        logger.warning(f"Entity {entity} has no command topic")
        return False
    
    try:
        # Convert value to appropriate format
        if entity.entity_type in ['switch', 'light']:
            payload = str(value).upper() if isinstance(value, str) else ("ON" if value else "OFF")
        else:
            payload = str(value)
        
        result = client.publish(topic, payload, qos=1, retain=False)
        logger.info(f"Published to {topic}: {payload}")
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    except Exception as e:
        logger.error(f"Failed to publish command: {e}")
        return False


def send_gpio_command(device, logical_id, value):
    """
    Send GPIO command to ESP32 device.
    
    Args:
        device: Device instance
        logical_id: Logical GPIO identifier
        value: Value to set (0/1)
    """
    client = get_mqtt_client()
    topic = f"{device.base_topic()}/cmd"
    
    payload = {
        "target": logical_id,
        "value": value
    }
    
    try:
        result = client.publish(topic, json.dumps(payload), qos=1)
        logger.info(f"Published GPIO command to {topic}: {payload}")
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    except Exception as e:
        logger.error(f"Failed to publish GPIO command: {e}")
        return False


def push_gpio_mapping(device):
    """
    Push GPIO mapping configuration to ESP32 device.
    
    Args:
        device: Device instance
    """
    from .models import GPIOMapping
    
    client = get_mqtt_client()
    topic = f"{device.base_topic()}/config"
    
    mappings = GPIOMapping.objects.filter(device=device)
    
    payload = {
        "gpios": [
            {
                "logical_id": m.logical_id,
                "pin": m.gpio_pin,
                "type": m.type,
                "default": m.default_value
            }
            for m in mappings
        ]
    }
    
    try:
        result = client.publish(topic, json.dumps(payload), qos=1, retain=True)
        logger.info(f"Published GPIO config to {topic}")
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    except Exception as e:
        logger.error(f"Failed to publish GPIO config: {e}")
        return False


def trigger_ota(device, firmware):
    """
    Trigger OTA update on ESP32 device.
    
    Args:
        device: Device instance
        firmware: Firmware instance
    """
    from .models import OTAStatus
    
    client = get_mqtt_client()
    topic = f"{device.base_topic()}/ota"
    
    # Build absolute URL for firmware file
    from django.contrib.sites.models import Site
    try:
        current_site = Site.objects.get_current()
        base_url = f"http://{current_site.domain}"
    except:
        base_url = "http://localhost:8000"
    
    firmware_url = f"{base_url}{firmware.file.url}"
    
    payload = {
        "version": firmware.version,
        "url": firmware_url
    }
    
    # Create OTA status record
    ota_status = OTAStatus.objects.create(
        device=device,
        firmware=firmware,
        version=firmware.version,
        status='pending'
    )
    
    try:
        result = client.publish(topic, json.dumps(payload), qos=1)
        logger.info(f"Triggered OTA update for {device.name}: {payload}")
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            ota_status.status = 'started'
            ota_status.save()
            return True
        else:
            ota_status.status = 'failed'
            ota_status.message = 'Failed to publish MQTT message'
            ota_status.save()
            return False
    except Exception as e:
        logger.error(f"Failed to trigger OTA: {e}")
        ota_status.status = 'failed'
        ota_status.message = str(e)
        ota_status.save()
        return False


def trigger_factory_reset(device):
    """
    Trigger factory reset on ESP32 device.
    
    Args:
        device: Device instance
    """
    client = get_mqtt_client()
    topic = f"{device.base_topic()}/reset"
    
    payload = {"action": "factory_reset"}
    
    try:
        result = client.publish(topic, json.dumps(payload), qos=1)
        logger.info(f"Triggered factory reset for {device.name}")
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    except Exception as e:
        logger.error(f"Failed to trigger factory reset: {e}")
        return False


def push_automation_rules(device, rules):
    """
    Push automation rules to ESP32 device.
    
    Args:
        device: Device instance
        rules: List of rule dictionaries
    """
    client = get_mqtt_client()
    topic = f"{device.base_topic()}/rules"
    
    payload = {"rules": rules}
    
    try:
        result = client.publish(topic, json.dumps(payload), qos=1, retain=True)
        logger.info(f"Published rules to {device.name}")
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    except Exception as e:
        logger.error(f"Failed to publish rules: {e}")
        return False
