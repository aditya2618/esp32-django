import re
from django.core.exceptions import ValidationError
from .constants import ESP32_RESERVED_PINS, ESP32_GPIO_CAPABILITIES


def validate_entity_name(name):
    """
    Validate entity name for ESPHome compatibility.
    
    Rules:
    - Cannot be purely numeric (must contain at least one letter or underscore)
    - Can only contain letters, numbers, and underscores
    - Must start with a letter or underscore (not a number)
    - Length: 1-50 characters
    
    Args:
        name: Entity name to validate
        
    Raises:
        ValidationError: If name is invalid
    """
    if not name:
        raise ValidationError("Entity name cannot be empty.")
    
    # Check if purely numeric
    if name.isdigit():
        raise ValidationError(
            "Entity name cannot be purely numeric (e.g., '1', '123'). "
            "Please include at least one letter or underscore (e.g., 'light_1', 'relay1')."
        )
    
    # Check if starts with a number
    if name[0].isdigit():
        raise ValidationError(
            f"Entity name '{name}' cannot start with a number. "
            "Please start with a letter or underscore (e.g., 'light_1', 'relay1')."
        )
    
    # Check for valid characters (alphanumeric and underscore only)
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValidationError(
            f"Entity name '{name}' contains invalid characters. "
            "Only letters (a-z, A-Z), numbers (0-9), and underscores (_) are allowed. "
            "Spaces and special characters are not permitted."
        )
    
    return True


def validate_gpio_pin(pin, device_type):
    """
    Validate GPIO pin for safety and capability.
    
    Args:
        pin: GPIO pin number
        device_type: Type of device (relay, switch, dht22, pwm, etc.)
        
    Raises:
        ValidationError: If pin is invalid
    """
    # Check if pin is reserved
    if pin in ESP32_RESERVED_PINS:
        raise ValidationError(
            f"GPIO {pin} is reserved/unsafe and cannot be used. "
            f"Reserved pins: {ESP32_RESERVED_PINS}"
        )
    
    # Check if pin is within valid range
    if pin < 0 or pin > 39:
        raise ValidationError(f"GPIO {pin} is out of range (0-39)")
    
    # Check if pin supports the device type
    if device_type in ESP32_GPIO_CAPABILITIES:
        if pin not in ESP32_GPIO_CAPABILITIES[device_type]:
            raise ValidationError(
                f"GPIO {pin} does not support {device_type}. "
                f"Valid pins: {ESP32_GPIO_CAPABILITIES[device_type]}"
            )
    
    return True


def validate_unique_gpio(device, pin, exclude_id=None):
    """
    Ensure GPIO pin is not already used by another entity on this device.
    
    Args:
        device: Device instance
        pin: GPIO pin number
        exclude_id: Optional entity ID to exclude from check (for updates)
        
    Raises:
        ValidationError: If pin is already in use
    """
    from .models import Entity
    
    existing = Entity.objects.filter(device=device, gpio_pin__isnull=False, gpio_pin=pin)
    
    if exclude_id:
        existing = existing.exclude(id=exclude_id)
    
    if existing.exists():
        entity = existing.first()
        raise ValidationError(
            f"GPIO {pin} is already assigned to '{entity.entity_name}' ({entity.entity_type})"
        )
    
    return True
