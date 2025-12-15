from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import Device, Entity, GPIOMapping, Firmware, OTAStatus
from .forms import (
    DeviceForm, EntityForm, GPIOMappingForm, EntityControlForm,
    FirmwareUploadForm, OTATriggerForm, BulkOTAForm, FactoryResetForm
)
from .services import send_command, push_gpio_mapping, trigger_ota, trigger_factory_reset
from .esphome_generator import generate_esphome_yaml, generate_gpio_mapping_yaml
from .constants import ESP32_RESERVED_PINS


def dashboard(request):
    """Main dashboard showing all devices"""
    devices = Device.objects.all().prefetch_related('entities')
    
    context = {
        'devices': devices,
        'total_devices': devices.count(),
        'online_devices': devices.filter(is_online=True).count(),
    }
    return render(request, 'dashboard.html', context)


def device_detail(request, device_id):
    """Device detail page with entity controls"""
    device = get_object_or_404(Device, id=device_id)
    entities = Entity.objects.filter(device=device).order_by('entity_type', 'entity_name')
    
    if request.method == 'POST':
        form = EntityControlForm(request.POST)
        if form.is_valid():
            entity_id = form.cleaned_data['entity_id']
            value = form.cleaned_data['value']
            
            entity = get_object_or_404(Entity, id=entity_id, device=device)
            
            # Send command via MQTT
            success = send_command(entity, value)
            
            if success:
                messages.success(request, f'Command sent to {entity.entity_name}')
            else:
                messages.error(request, f'Failed to send command to {entity.entity_name}')
            
            return redirect('device_detail', device_id=device_id)
    
    # Separate entities by type
    switches = entities.filter(entity_type='switch')
    lights = entities.filter(entity_type='light')
    fans = entities.filter(entity_type='fan')
    sensors = entities.filter(entity_type='sensor')
    binary_sensors = entities.filter(entity_type='binary_sensor')
    
    context = {
        'device': device,
        'switches': switches,
        'lights': lights,
        'fans': fans,
        'sensors': sensors,
        'binary_sensors': binary_sensors,
    }
    return render(request, 'device_detail.html', context)


def add_device(request):
    """Add new device"""
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            messages.success(request, f'Device {device.name} created successfully')
            return redirect('device_detail', device_id=device.id)
    else:
        form = DeviceForm()
    
    return render(request, 'device_form.html', {'form': form, 'title': 'Add Device'})


def edit_device(request, device_id):
    """Edit device"""
    device = get_object_or_404(Device, id=device_id)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, f'Device {device.name} updated successfully')
            return redirect('device_detail', device_id=device.id)
    else:
        form = DeviceForm(instance=device)
    
    return render(request, 'device_form.html', {'form': form, 'title': 'Edit Device', 'device': device})


def add_entity(request, device_id):
    """Add entity to device"""
    device = get_object_or_404(Device, id=device_id)
    
    if request.method == 'POST':
        form = EntityForm(request.POST, device=device)
        if form.is_valid():
            entity = form.save(commit=False)
            entity.device = device
            entity.save()
            messages.success(request, f'Entity {entity.entity_name} added successfully')
            return redirect('device_detail', device_id=device.id)
    else:
        form = EntityForm(device=device)
    
    return render(request, 'entity_form.html', {'form': form, 'device': device, 'title': 'Add Entity'})


def edit_entity(request, entity_id):
    """Edit entity"""
    entity = get_object_or_404(Entity, id=entity_id)
    device = entity.device
    
    if request.method == 'POST':
        form = EntityForm(request.POST, instance=entity, device=device)
        if form.is_valid():
            form.save()
            messages.success(request, f'Entity {entity.entity_name} updated successfully')
            return redirect('device_detail', device_id=device.id)
    else:
        form = EntityForm(instance=entity, device=device)
    
    return render(request, 'entity_form.html', {'form': form, 'device': device, 'entity': entity, 'title': 'Edit Entity'})


def delete_entity(request, entity_id):
    """Delete entity"""
    entity = get_object_or_404(Entity, id=entity_id)
    device_id = entity.device.id
    entity_name = entity.entity_name
    
    entity.delete()
    messages.success(request, f'Entity {entity_name} deleted successfully')
    return redirect('device_detail', device_id=device_id)


def gpio_mapping(request, device_id):
    """GPIO mapping page"""
    device = get_object_or_404(Device, id=device_id)
    mappings = GPIOMapping.objects.filter(device=device).order_by('gpio_pin')
    
    if request.method == 'POST':
        form = GPIOMappingForm(request.POST, device=device)
        if form.is_valid():
            mapping = form.save(commit=False)
            mapping.device = device
            mapping.save()
            
            # Push config to device
            push_gpio_mapping(device)
            
            messages.success(request, f'GPIO mapping added and pushed to device')
            return redirect('gpio_mapping', device_id=device_id)
    else:
        form = GPIOMappingForm(device=device)
    
    context = {
        'device': device,
        'mappings': mappings,
        'form': form,
    }
    return render(request, 'gpio_mapping.html', context)


def delete_gpio_mapping(request, mapping_id):
    """Delete GPIO mapping"""
    mapping = get_object_or_404(GPIOMapping, id=mapping_id)
    device_id = mapping.device.id
    
    mapping.delete()
    
    # Push updated config to device
    push_gpio_mapping(mapping.device)
    
    messages.success(request, 'GPIO mapping deleted and config updated on device')
    return redirect('gpio_mapping', device_id=device_id)


def esp32_pinout(request, device_id):
    """Visual ESP32 pinout page"""
    device = get_object_or_404(Device, id=device_id)
    
    # Get all used GPIO pins
    used_pins = set(Entity.objects.filter(device=device, gpio_pin__isnull=False).values_list('gpio_pin', flat=True))
    gpio_mappings_pins = set(GPIOMapping.objects.filter(device=device).values_list('gpio_pin', flat=True))
    used_pins.update(gpio_mappings_pins)
    
    # Create pin status list
    pins = []
    for pin in range(0, 40):
        status = 'free'
        assigned_to = None
        
        if pin in ESP32_RESERVED_PINS:
            status = 'reserved'
        elif pin in used_pins:
            status = 'assigned'
            # Find what it's assigned to
            entity = Entity.objects.filter(device=device, gpio_pin=pin).first()
            if entity:
                assigned_to = f"{entity.entity_name} ({entity.entity_type})"
            else:
                mapping = GPIOMapping.objects.filter(device=device, gpio_pin=pin).first()
                if mapping:
                    assigned_to = f"{mapping.logical_id} ({mapping.type})"
        
        pins.append({
            'number': pin,
            'status': status,
            'assigned_to': assigned_to
        })
    
    context = {
        'device': device,
        'pins': pins,
        'reserved_pins': ESP32_RESERVED_PINS,
    }
    return render(request, 'esp32_pinout.html', context)


def firmware_page(request, device_id):
    """Firmware OTA page"""
    device = get_object_or_404(Device, id=device_id)
    firmwares = Firmware.objects.all().order_by('-uploaded_at')
    ota_history = OTAStatus.objects.filter(device=device).order_by('-started_at')[:10]
    
    if request.method == 'POST':
        form = OTATriggerForm(request.POST)
        if form.is_valid():
            firmware = form.cleaned_data['firmware']
            
            # Trigger OTA
            success = trigger_ota(device, firmware)
            
            if success:
                messages.success(request, f'OTA update triggered for {device.name}')
            else:
                messages.error(request, 'Failed to trigger OTA update')
            
            return redirect('firmware_page', device_id=device_id)
    else:
        form = OTATriggerForm()
    
    context = {
        'device': device,
        'form': form,
        'firmwares': firmwares,
        'ota_history': ota_history,
    }
    return render(request, 'firmware.html', context)


def upload_firmware(request):
    """Upload new firmware"""
    if request.method == 'POST':
        form = FirmwareUploadForm(request.POST, request.FILES)
        if form.is_valid():
            firmware = form.save()
            messages.success(request, f'Firmware v{firmware.version} uploaded successfully')
            return redirect('firmware_list')
    else:
        form = FirmwareUploadForm()
    
    return render(request, 'firmware_upload.html', {'form': form})


def firmware_list(request):
    """List all firmware versions"""
    firmwares = Firmware.objects.all().order_by('-uploaded_at')
    return render(request, 'firmware_list.html', {'firmwares': firmwares})


def bulk_ota(request):
    """Bulk OTA update page"""
    if request.method == 'POST':
        form = BulkOTAForm(request.POST)
        if form.is_valid():
            firmware = form.cleaned_data['firmware']
            devices = form.cleaned_data['devices']
            
            success_count = 0
            fail_count = 0
            
            for device in devices:
                if trigger_ota(device, firmware):
                    success_count += 1
                else:
                    fail_count += 1
            
            messages.success(request, f'OTA triggered for {success_count} devices')
            if fail_count > 0:
                messages.warning(request, f'Failed for {fail_count} devices')
            
            return redirect('dashboard')
    else:
        form = BulkOTAForm()
    
    return render(request, 'bulk_ota.html', {'form': form})


def ota_status(request):
    """OTA status overview"""
    recent_ota = OTAStatus.objects.all().order_by('-started_at')[:50]
    
    context = {
        'ota_statuses': recent_ota,
    }
    return render(request, 'ota_status.html', context)


def factory_reset(request, device_id):
    """Factory reset device"""
    device = get_object_or_404(Device, id=device_id)
    
    if request.method == 'POST':
        form = FactoryResetForm(request.POST)
        if form.is_valid():
            # Trigger factory reset
            success = trigger_factory_reset(device)
            
            if success:
                messages.success(request, f'Factory reset triggered for {device.name}')
            else:
                messages.error(request, 'Failed to trigger factory reset')
            
            return redirect('device_detail', device_id=device_id)
    else:
        form = FactoryResetForm()
    
    context = {
        'device': device,
        'form': form,
    }
    return render(request, 'factory_reset.html', context)


def generate_yaml(request, device_id):
    """Generate and download ESPHome YAML"""
    device = get_object_or_404(Device, id=device_id)
    
    yaml_content = generate_esphome_yaml(device)
    
    response = HttpResponse(yaml_content, content_type='text/yaml')
    response['Content-Disposition'] = f'attachment; filename="{device.node_name}.yaml"'
    
    return response


def view_yaml(request, device_id):
    """View ESPHome YAML in browser"""
    device = get_object_or_404(Device, id=device_id)
    
    yaml_content = generate_esphome_yaml(device)
    
    context = {
        'device': device,
        'yaml_content': yaml_content,
    }
    return render(request, 'view_yaml.html', context)
