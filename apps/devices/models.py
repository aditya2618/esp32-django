from django.db import models
from django.utils import timezone
from .validators import validate_entity_name


class Device(models.Model):
    """ESPHome Device"""
    home_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    node_name = models.CharField(max_length=100, unique=True, help_text="ESPHome node name (e.g., home1_livingroom_node1)")
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.node_name})"
    
    def base_topic(self):
        """Generate base MQTT topic for this device"""
        return f"home/{self.home_id}/{self.node_name}"
    
    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen = timezone.now()
        self.is_online = True
        self.save(update_fields=['last_seen', 'is_online'])


class Entity(models.Model):
    """Device Entity (switch, light, fan, sensor)"""
    ENTITY_TYPES = (
        ("switch", "Switch"),
        ("light", "Light"),
        ("fan", "Fan"),
        ("sensor", "Sensor"),
        ("binary_sensor", "Binary Sensor"),
        ("cover", "Cover/Blind"),
        ("climate", "Climate/Thermostat"),
        ("lock", "Lock"),
        ("button", "Button"),
    )
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='entities')
    entity_name = models.CharField(
        max_length=50, 
        validators=[validate_entity_name],
        help_text="Entity name (e.g., living_room_fan). Must start with letter/underscore, contain only letters, numbers, and underscores."
    )
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    gpio_pin = models.IntegerField(null=True, blank=True, help_text="GPIO pin number (if applicable)")
    
    # Metadata for external app integration
    friendly_name = models.CharField(max_length=100, blank=True, help_text="Display name (e.g., Living Room Fan)")
    icon = models.CharField(max_length=50, blank=True, help_text="Material Design Icon (e.g., mdi:fan)")
    room = models.CharField(max_length=50, blank=True, help_text="Room location (e.g., Living Room)")
    device_class = models.CharField(max_length=50, blank=True, help_text="Device class for sensors (e.g., temperature, humidity)")
    unit_of_measurement = models.CharField(max_length=20, blank=True, help_text="Unit for sensors (e.g., °C, %)")
    attributes = models.JSONField(default=dict, blank=True, help_text="Additional metadata")
    enabled = models.BooleanField(default=True, help_text="Enable/disable entity")
    
    # State tracking
    state = models.CharField(max_length=50, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('device', 'entity_name')
        ordering = ['device', 'entity_type', 'entity_name']
    
    def __str__(self):
        return f"{self.device.name} - {self.entity_name}"
    
    def state_topic(self):
        """Generate MQTT state topic"""
        return f"{self.device.base_topic()}/{self.entity_type}/{self.entity_name}/state"
    
    def command_topic(self):
        """Generate MQTT command topic"""
        if self.entity_type in ['switch', 'light', 'fan']:
            return f"{self.device.base_topic()}/{self.entity_type}/{self.entity_name}/command"
        return None
    
    def update_state(self, new_state):
        """Update entity state"""
        self.state = new_state
        self.last_updated = timezone.now()
        self.save(update_fields=['state', 'last_updated'])
    
    def get_friendly_name(self):
        """Get friendly name or generate from entity_name"""
        if self.friendly_name:
            return self.friendly_name
        return self.entity_name.replace('_', ' ').title()
    
    def get_icon(self):
        """Get icon or default based on entity type"""
        if self.icon:
            return self.icon
        
        # Default icons by entity type
        default_icons = {
            'switch': 'mdi:light-switch',
            'light': 'mdi:lightbulb',
            'fan': 'mdi:fan',
            'sensor': 'mdi:thermometer',
            'binary_sensor': 'mdi:motion-sensor',
            'cover': 'mdi:window-shutter',
            'climate': 'mdi:thermostat',
            'lock': 'mdi:lock',
            'button': 'mdi:gesture-tap-button',
        }
        return default_icons.get(self.entity_type, 'mdi:help-circle')
    
    def is_controllable(self):
        """Check if entity can receive commands"""
        return self.entity_type in ['switch', 'light', 'fan', 'cover', 'climate', 'lock']
    
    def is_sensor(self):
        """Check if entity is a sensor"""
        return self.entity_type in ['sensor', 'binary_sensor']


class GPIOMapping(models.Model):
    """GPIO Pin Mapping for a Device"""
    DEVICE_TYPES = (
        ("relay", "Relay"),
        ("switch", "Switch"),
        ("dht22", "DHT22 Sensor"),
        ("pwm", "PWM Output"),
        ("light", "Light"),
        ("fan", "Fan"),
    )
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='gpio_mappings')
    logical_id = models.CharField(max_length=32, help_text="Logical identifier (e.g., relay_1)")
    gpio_pin = models.IntegerField(help_text="Physical GPIO pin number")
    type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    default_value = models.IntegerField(default=0, help_text="Default state (0 or 1)")
    
    class Meta:
        unique_together = ('device', 'gpio_pin')
        ordering = ['device', 'gpio_pin']
    
    def __str__(self):
        return f"{self.device.name} - GPIO {self.gpio_pin} ({self.logical_id})"


class Firmware(models.Model):
    """Firmware versions for OTA updates"""
    version = models.CharField(max_length=20, unique=True)
    file = models.FileField(upload_to='firmware/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Firmware v{self.version}"


class OTAStatus(models.Model):
    """OTA Update Status Tracking"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='ota_history')
    firmware = models.ForeignKey(Firmware, on_delete=models.SET_NULL, null=True)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "OTA Status"
        verbose_name_plural = "OTA Statuses"
    
    def __str__(self):
        return f"{self.device.name} - v{self.version} - {self.status}"
