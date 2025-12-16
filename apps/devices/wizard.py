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
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_entity':
            # Add entity to wizard data
            entity_name = request.POST.get('entity_name')
            
            # Validate entity name before adding
            try:
                validate_entity_name(entity_name)
            except ValidationError as e:
                messages.error(request, f'Invalid entity name: {e.message}')
                return redirect('wizard_step4_entities')
            
            entity = {
                'entity_name': entity_name,
                'entity_type': request.POST.get('entity_type'),
                'gpio_pin': request.POST.get('gpio_pin'),
                'friendly_name': request.POST.get('friendly_name'),
                'icon': request.POST.get('icon'),
                'room': request.POST.get('room'),
            }
            
            if not wizard_data.get('entities'):
                wizard_data['entities'] = []
            
            wizard_data['entities'].append(entity)
            request.session['wizard_data'] = wizard_data
            messages.success(request, f'Entity {entity["entity_name"]} added successfully')
            
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
    
    entities = wizard_data.get('entities', [])
    context = {
        'entities': entities,
        'entity_types': Entity.ENTITY_TYPES,
        'step': 4,
        'total_steps': 6,
        'step_title': 'Add Entities',
        'step_description': 'Add lights, switches, fans, and sensors to your device',
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
                Entity.objects.create(
                    device=device,
                    entity_name=entity_data['entity_name'],
                    entity_type=entity_data['entity_type'],
                    gpio_pin=int(entity_data['gpio_pin']) if entity_data['gpio_pin'] else None,
                    friendly_name=entity_data.get('friendly_name', ''),
                    icon=entity_data.get('icon', ''),
                    room=entity_data.get('room', ''),
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
    
    # Generate YAML with WiFi and MQTT config
    yaml_content = generate_esphome_yaml(
        device,
        platform=platform
    )
    
    # Replace placeholders with actual values
    if wizard_data.get('wifi'):
        yaml_content = yaml_content.replace('YOUR_WIFI_SSID', wizard_data['wifi']['ssid'])
        yaml_content = yaml_content.replace('YOUR_WIFI_PASSWORD', wizard_data['wifi']['password'])
    
    if wizard_data.get('mqtt'):
        yaml_content = yaml_content.replace('YOUR_MQTT_BROKER_IP', wizard_data['mqtt']['broker'])
        yaml_content = yaml_content.replace('1883', str(wizard_data['mqtt'].get('port', 1883)))
        yaml_content = yaml_content.replace('YOUR_MQTT_PASSWORD', wizard_data['mqtt'].get('password', ''))
    
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
