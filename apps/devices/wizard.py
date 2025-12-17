"""
Device Provisioning Wizard

Step-by-step wizard to configure ESP32 devices for smart home integration.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import Device, Entity
from .forms import DeviceForm, EntityForm
from .esphome_generator import generate_esphome_yaml
from .firmware_builder import compile_and_prepare_firmware
from .validators import validate_entity_name
import json


def wizard_start(request):
    """Start the provisioning wizard"""
    # Clear any existing wizard session data
    request.session.pop('wizard_data', None)
    return render(request, 'wizard/start.html')


def wizard_step1_device_info(request):
    """Step 1: Device Information"""
    wizard_data = request.session.get('wizard_data', {})
    
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            # Save device info to session
            wizard_data['device'] = {
                'home_id': form.cleaned_data['home_id'],
                'name': form.cleaned_data['name'],
                'node_name': form.cleaned_data['node_name'],
                'platform': form.cleaned_data['platform'],  # Save platform choice
            }
            request.session['wizard_data'] = wizard_data
            return redirect('wizard_step2_wifi')
    else:
        initial_data = wizard_data.get('device', {})
        form = DeviceForm(initial=initial_data)
    
    context = {
        'form': form,
        'step': 1,
        'total_steps': 6,
        'step_title': 'Device Information',
        'step_description': 'Enter basic information about your ESP32/ESP8266 device',
    }
    return render(request, 'wizard/step1_device_info.html', context)


def wizard_step2_wifi(request):
    """Step 2: WiFi Configuration"""
    wizard_data = request.session.get('wizard_data', {})
    
    if not wizard_data.get('device'):
        return redirect('wizard_step1_device_info')
    
    if request.method == 'POST':
        ssid = request.POST.get('wifi_ssid')
        password = request.POST.get('wifi_password')
        
        if ssid:
            wizard_data['wifi'] = {
                'ssid': ssid,
                'password': password,
            }
            request.session['wizard_data'] = wizard_data
            return redirect('wizard_step3_mqtt')
        else:
            messages.error(request, 'WiFi SSID is required')
    
    wifi_data = wizard_data.get('wifi', {})
    context = {
        'wifi_data': wifi_data,
        'step': 2,
        'total_steps': 6,
        'step_title': 'WiFi Configuration',
        'step_description': 'Configure WiFi connection for your ESP32',
    }
    return render(request, 'wizard/step2_wifi.html', context)


def wizard_step3_mqtt(request):
    """Step 3: MQTT Configuration"""
    wizard_data = request.session.get('wizard_data', {})
    
    if not wizard_data.get('wifi'):
        return redirect('wizard_step2_wifi')
    
    if request.method == 'POST':
        broker = request.POST.get('mqtt_broker')
        port = request.POST.get('mqtt_port', '1883')
        username = request.POST.get('mqtt_username', '')
        password = request.POST.get('mqtt_password', '')
        
        if broker:
            wizard_data['mqtt'] = {
                'broker': broker,
                'port': port,
                'username': username,
                'password': password,
            }
            request.session['wizard_data'] = wizard_data
            return redirect('wizard_step4_entities')
        else:
            messages.error(request, 'MQTT Broker address is required')
    
    mqtt_data = wizard_data.get('mqtt', {})
    context = {
        'mqtt_data': mqtt_data,
        'step': 3,
        'total_steps': 6,
        'step_title': 'MQTT Configuration',
        'step_description': 'Configure MQTT broker for device communication',
    }
    return render(request, 'wizard/step3_mqtt.html', context)


def wizard_step4_entities(request):
    """Step 4: Add Entities"""
    wizard_data = request.session.get('wizard_data', {})
    
    if not wizard_data.get('mqtt'):
        return redirect('wizard_step3_mqtt')
    
    # Get platform from wizard data
    platform = wizard_data.get('device', {}).get('platform', 'esp32')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_entity':
            # Use EntityForm with platform support
            form = EntityForm(request.POST, platform=platform)
            
            if form.is_valid():
                # Add entity to wizard data
                # Prepare entity data
                hardware_type = form.cleaned_data.get('hardware_type', '')
                entity = {
                    'entity_name': form.cleaned_data['entity_name'],
                    'entity_type': form.cleaned_data['entity_type'],
                    'hardware_type': hardware_type,
                    'update_interval': form.cleaned_data.get('update_interval', 60),
                    'i2c_address': form.cleaned_data.get('i2c_address', ''),
                    'inverted': form.cleaned_data.get('inverted', False),
                    'friendly_name': request.POST.get('friendly_name', ''),
                    'icon': request.POST.get('icon', ''),
                    'room': request.POST.get('room', ''),
                }
                
                # Handle Push Pin Configuration
                from .constants import SENSOR_TYPES, ACTUATOR_TYPES
                all_components = {**SENSOR_TYPES, **ACTUATOR_TYPES}
                component = all_components.get(hardware_type, {})
                pins_required = component.get('pins_required', 1)
                
                if pins_required > 1:
                    # Multi-pin component
                    entity['gpio_pin'] = None # No single main pin
                    entity['pin_config'] = {}
                    pin_keys = component.get('pin_keys', [])
                    
                    for i, key in enumerate(pin_keys):
                        # Get pin_1, pin_2, etc.
                        pin_val = form.cleaned_data.get(f'pin_{i+1}')
                        if pin_val:
                            entity['pin_config'][key] = int(pin_val)
                else:
                    # Single pin component
                    gpio_val = form.cleaned_data.get('gpio_pin')
                    entity['gpio_pin'] = int(gpio_val) if gpio_val else None
                    entity['pin_config'] = {}

                # Derive friendly name if missing
                if not entity['friendly_name']:
                    entity['friendly_name'] = entity['entity_name'].replace('_', ' ').title()

                if not wizard_data.get('entities'):
                    wizard_data['entities'] = []
                
                wizard_data['entities'].append(entity)
                request.session['wizard_data'] = wizard_data
                messages.success(request, f'Entity {entity["entity_name"]} added successfully')
                return redirect('wizard_step4_entities')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            
        elif action == 'remove_entity':
            index = int(request.POST.get('index'))
            if wizard_data.get('entities') and 0 <= index < len(wizard_data['entities']):
                removed = wizard_data['entities'].pop(index)
                request.session['wizard_data'] = wizard_data
                messages.success(request, f'Entity {removed["entity_name"]} removed')
        
        elif action == 'continue':
            if wizard_data.get('entities'):
                return redirect('wizard_step5_review')
            else:
                messages.error(request, 'Please add at least one entity')
    
    # Create form with platform support for GET request
    form = EntityForm(platform=platform)
    entities = wizard_data.get('entities', [])
    
    # Import constants for component info
    from .constants import SENSOR_TYPES, ACTUATOR_TYPES
    all_components = {**SENSOR_TYPES, **ACTUATOR_TYPES}
    
    context = {
        'form': form,
        'entities': entities,
        'entity_types': Entity.ENTITY_TYPES,
        'platform': platform,
        'all_components': all_components,
        'step': 4,
        'total_steps': 6,
        'step_title': 'Add Entities',
        'step_description': f'Add components to your {platform.upper()} device',
    }
    return render(request, 'wizard/step4_entities.html', context)


def wizard_step5_review(request):
    """Step 5: Review Configuration"""
    wizard_data = request.session.get('wizard_data', {})
    
    if not wizard_data.get('entities'):
        return redirect('wizard_step4_entities')
    
    if request.method == 'POST':
        # Create device and entities in database
        try:
            device = Device.objects.create(
                home_id=wizard_data['device']['home_id'],
                name=wizard_data['device']['name'],
                node_name=wizard_data['device']['node_name'],
            )
            
            for entity_data in wizard_data['entities']:
                # Handle GPIO pin - convert to int if present, None if empty string or None
                gpio_pin_val = entity_data.get('gpio_pin')
                if gpio_pin_val and str(gpio_pin_val).strip():
                    gpio_pin = int(gpio_pin_val)
                else:
                    gpio_pin = None

                Entity.objects.create(
                    device=device,
                    entity_name=entity_data['entity_name'],
                    entity_type=entity_data['entity_type'],
                    hardware_type=entity_data.get('hardware_type', ''),
                    gpio_pin=gpio_pin,
                    pin_config=entity_data.get('pin_config', {}),
                    friendly_name=entity_data.get('friendly_name', ''),
                    icon=entity_data.get('icon', ''),
                    room=entity_data.get('room', ''),
                    update_interval=int(entity_data.get('update_interval', 60)),
                    i2c_address=entity_data.get('i2c_address', ''),
                    inverted=bool(entity_data.get('inverted', False)),
                )
            
            # Store device ID for next step
            wizard_data['device_id'] = device.id
            request.session['wizard_data'] = wizard_data
            
            messages.success(request, f'Device {device.name} created successfully!')
            return redirect('wizard_step6_complete')
            
        except Exception as e:
            messages.error(request, f'Error creating device: {str(e)}')
    
    context = {
        'wizard_data': wizard_data,
        'step': 5,
        'total_steps': 6,
        'step_title': 'Review Configuration',
        'step_description': 'Review your device configuration before finalizing',
    }
    return render(request, 'wizard/step5_review.html', context)


def wizard_step6_complete(request):
    """Step 6: Complete - Download YAML or Flash Firmware"""
    wizard_data = request.session.get('wizard_data', {})
    device_id = wizard_data.get('device_id')
    
    if not device_id:
        return redirect('wizard_start')
    
    device = get_object_or_404(Device, id=device_id)
    
    # Get platform from wizard data (default to esp32 for backward compatibility)
    platform = wizard_data.get('device', {}).get('platform', 'esp32')
    
    # Generate YAML with WiFi and MQTT config from wizard data
    wifi_ssid = wizard_data.get('wifi', {}).get('ssid', 'YOUR_WIFI_SSID')
    wifi_password = wizard_data.get('wifi', {}).get('password', 'YOUR_WIFI_PASSWORD')
    mqtt_broker = wizard_data.get('mqtt', {}).get('broker', 'YOUR_MQTT_BROKER_IP')
    mqtt_port = wizard_data.get('mqtt', {}).get('port', 1883)
    
    yaml_content = generate_esphome_yaml(
        device,
        wifi_ssid=wifi_ssid,
        wifi_password=wifi_password,
        mqtt_broker=mqtt_broker,
        mqtt_port=mqtt_port,
        platform=platform
    )
    
    # Check if user wants to compile firmware
    compile_firmware_flag = request.GET.get('compile', 'false') == 'true'
    firmware_result = None
    
    if compile_firmware_flag:
        try:
            from .firmware_builder import compile_and_prepare_firmware
            import logging
            logger = logging.getLogger(__name__)
            
            messages.info(request, 'Compiling firmware... This may take a few minutes.')
            
            # Use the helper function that handles everything
            firmware_result = compile_and_prepare_firmware(device, yaml_content, platform=platform)
            
            if firmware_result['success']:
                messages.success(request, f'Firmware compiled successfully! You can now flash your {platform.upper()}.')
            else:
                messages.error(request, f'Firmware compilation failed. Check the logs below.')
            
        except Exception as e:
            firmware_result = {
                'success': False,
                'error': str(e),
                'logs': str(e)
            }
            messages.error(request, f'Firmware compilation error: {str(e)}')
    
    context = {
        'device': device,
        'yaml_content': yaml_content,
        'firmware_result': firmware_result,
        'step': 6,
        'total_steps': 6,
        'step_title': 'Configuration Complete!',
        'step_description': 'Your device is configured and ready to flash',
    }
    return render(request, 'wizard/step6_complete.html', context)
