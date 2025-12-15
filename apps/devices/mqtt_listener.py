import json
import logging
import re
import paho.mqtt.client as mqtt
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def extract_parts_from_topic(topic):
    """
    Extract device node name, entity type, and entity name from MQTT topic.
    
    Expected format: home/{home_id}/{node_name}/{entity_type}/{entity_name}/state
    """
    pattern = r'home/([^/]+)/([^/]+)/([^/]+)/([^/]+)/(state|command)'
    match = re.match(pattern, topic)
    
    if match:
        return {
            'home_id': match.group(1),
            'node_name': match.group(2),
            'entity_type': match.group(3),
            'entity_name': match.group(4),
            'suffix': match.group(5)
        }
    return None


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback when MQTT client connects"""
    if rc == 0:
        logger.info("Connected to MQTT broker successfully")
        
        # Subscribe to all state topics
        client.subscribe("home/+/+/+/+/state", qos=1)
        client.subscribe("home/+/+/status/#", qos=1)
        logger.info("Subscribed to MQTT topics")
    else:
        logger.error(f"Failed to connect to MQTT broker: {rc}")


def on_message(client, userdata, msg):
    """Callback when MQTT message is received"""
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logger.debug(f"Received: {topic} -> {payload}")
        
        # Handle OTA status updates
        if '/status/ota' in topic:
            handle_ota_status(topic, payload)
            return
        
        # Handle device status
        if '/status/' in topic:
            handle_device_status(topic, payload)
            return
        
        # Handle entity state updates
        if topic.endswith('/state'):
            handle_entity_state(topic, payload)
            return
            
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}", exc_info=True)


def handle_entity_state(topic, payload):
    """Handle entity state update"""
    from .models import Device, Entity
    
    parts = extract_parts_from_topic(topic)
    if not parts:
        logger.warning(f"Could not parse topic: {topic}")
        return
    
    try:
        # Find or create device
        device, created = Device.objects.get_or_create(
            node_name=parts['node_name'],
            defaults={'home_id': parts['home_id'], 'name': parts['node_name']}
        )
        
        if created:
            logger.info(f"Created new device: {device.node_name}")
        
        # Update device last seen
        device.update_last_seen()
        
        # Find or create entity
        entity, created = Entity.objects.get_or_create(
            device=device,
            entity_name=parts['entity_name'],
            defaults={'entity_type': parts['entity_type']}
        )
        
        if created:
            logger.info(f"Created new entity: {entity.entity_name}")
        
        # Update entity state
        entity.update_state(payload)
        logger.debug(f"Updated {entity}: {payload}")
        
    except Exception as e:
        logger.error(f"Error handling entity state: {e}", exc_info=True)


def handle_ota_status(topic, payload):
    """Handle OTA status update from device"""
    from .models import Device, OTAStatus
    
    try:
        # Extract node name from topic (home/{home_id}/{node_name}/status/ota)
        parts = topic.split('/')
        if len(parts) >= 3:
            node_name = parts[2]
            
            device = Device.objects.filter(node_name=node_name).first()
            if not device:
                logger.warning(f"Device not found: {node_name}")
                return
            
            # Parse OTA status payload
            try:
                data = json.loads(payload)
                version = data.get('version')
                status = data.get('status', 'unknown').lower()
                message = data.get('message', '')
            except json.JSONDecodeError:
                # Simple text status
                status = payload.lower()
                version = None
                message = ''
            
            # Update latest OTA status for this device
            ota_status = OTAStatus.objects.filter(device=device).order_by('-started_at').first()
            
            if ota_status:
                ota_status.status = status
                ota_status.message = message
                if version:
                    ota_status.version = version
                ota_status.save()
                logger.info(f"Updated OTA status for {device.name}: {status}")
            else:
                logger.warning(f"No OTA status record found for {device.name}")
                
    except Exception as e:
        logger.error(f"Error handling OTA status: {e}", exc_info=True)


def handle_device_status(topic, payload):
    """Handle general device status updates"""
    from .models import Device
    
    try:
        parts = topic.split('/')
        if len(parts) >= 3:
            node_name = parts[2]
            
            device = Device.objects.filter(node_name=node_name).first()
            if device:
                device.update_last_seen()
                logger.debug(f"Updated status for {device.name}")
                
    except Exception as e:
        logger.error(f"Error handling device status: {e}", exc_info=True)


def start_mqtt_listener():
    """Start MQTT listener in background thread"""
    try:
        mqtt_broker = getattr(settings, 'MQTT_BROKER', 'localhost')
        mqtt_port = getattr(settings, 'MQTT_PORT', 1883)
        mqtt_username = getattr(settings, 'MQTT_USERNAME', None)
        mqtt_password = getattr(settings, 'MQTT_PASSWORD', None)
        
        client = mqtt.Client(client_id="django_listener", protocol=mqtt.MQTTv5)
        client.on_connect = on_connect
        client.on_message = on_message
        
        if mqtt_username and mqtt_password:
            client.username_pw_set(mqtt_username, mqtt_password)
        
        client.connect(mqtt_broker, mqtt_port, 60)
        client.loop_start()
        
        logger.info(f"MQTT listener started on {mqtt_broker}:{mqtt_port}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to start MQTT listener: {e}", exc_info=True)
        return None
