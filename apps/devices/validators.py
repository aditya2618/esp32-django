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


def get_reserved_pins_for_interfaces(entities):
    """
    Get list of GPIO pins reserved by special interfaces (UART, I2C, SPI).
    
    Args:
        entities: List of entity dictionaries or Entity objects
        
    Returns:
        dict: {
            'uart': [16, 17],
            'i2c': [21, 22],
            'spi': [18, 19, 23],
            'all_reserved': [16, 17, 21, 22, 18, 19, 23]
        }
    """
    reserved = {
        'uart': [],
        'i2c': [],
        'spi': [],
        'all_reserved': []
    }
    
    # Hardware types that use special interfaces
    UART_COMPONENTS = ['co2_mhz19', 'soil_npk_modbus']
    I2C_COMPONENTS = ['bme280', 'bmp280', 'bh1750', 'sht30', 'bme680', 'ccs811', 'ina219', 'ina226']
    SPI_COMPONENTS = ['max31865']
    
    for entity in entities:
        # Handle both dict and object
        hw_type = entity.get('hardware_type') if isinstance(entity, dict) else entity.hardware_type
        
        if hw_type in UART_COMPONENTS:
            # Default UART pins for ESP32
            reserved['uart'] = [16, 17]  # RX, TX
            
        if hw_type in I2C_COMPONENTS:
            # Default I2C pins for ESP32
            reserved['i2c'] = [21, 22]  # SDA, SCL
            
        if hw_type in SPI_COMPONENTS:
            # Default SPI pins for ESP32
            reserved['spi'] = [18, 19, 23]  # CLK, MISO, MOSI
    
    # Combine all reserved pins
    reserved['all_reserved'] = list(set(reserved['uart'] + reserved['i2c'] + reserved['spi']))
    
    return reserved


def validate_gpio_not_reserved_by_interface(pin, entities, current_entity_name=None):
    """
    Validate that a GPIO pin is not reserved by UART/I2C/SPI interfaces.
    
    Args:
        pin: GPIO pin number to validate
        entities: List of existing entities (dicts or objects)
        current_entity_name: Name of current entity being validated (to skip in check)
        
    Raises:
        ValidationError: If pin is reserved by an interface
    """
    reserved_info = get_reserved_pins_for_interfaces(entities)
    
    if pin in reserved_info['uart']:
        # Find which UART component is using it
        uart_components = [e for e in entities if (e.get('hardware_type') if isinstance(e, dict) else e.hardware_type) in ['co2_mhz19', 'soil_npk_modbus']]
        if uart_components:
            comp = uart_components[0]
            comp_name = comp.get('entity_name') if isinstance(comp, dict) else comp.entity_name
            raise ValidationError(
                f"GPIO {pin} is reserved for UART interface (used by '{comp_name}'). "
                f"UART uses GPIO 16 (RX) and GPIO 17 (TX). "
                f"Please choose a different GPIO pin."
            )
    
    if pin in reserved_info['i2c']:
        # Find which I2C component is using it
        i2c_components = [e for e in entities if (e.get('hardware_type') if isinstance(e, dict) else e.hardware_type) in ['bme280', 'bmp280', 'bh1750', 'sht30', 'bme680', 'ccs811', 'ina219', 'ina226']]
        if i2c_components:
            comp = i2c_components[0]
            comp_name = comp.get('entity_name') if isinstance(comp, dict) else comp.entity_name
            raise ValidationError(
                f"GPIO {pin} is reserved for I2C interface (used by '{comp_name}'). "
                f"I2C uses GPIO 21 (SDA) and GPIO 22 (SCL). "
                f"Please choose a different GPIO pin."
            )
    
    if pin in reserved_info['spi']:
        # Find which SPI component is using it
        spi_components = [e for e in entities if (e.get('hardware_type') if isinstance(e, dict) else e.hardware_type) in ['max31865']]
        if spi_components:
            comp = spi_components[0]
            comp_name = comp.get('entity_name') if isinstance(comp, dict) else comp.entity_name
            raise ValidationError(
                f"GPIO {pin} is reserved for SPI interface (used by '{comp_name}'). "
                f"SPI uses GPIO 18 (CLK), GPIO 19 (MISO), and GPIO 23 (MOSI). "
                f"Please choose a different GPIO pin."
            )
    
    return True
