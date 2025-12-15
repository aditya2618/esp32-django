"""
Device deletion view
"""
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Device


def delete_device(request, device_id):
    """Delete a device and all its entities"""
    device = get_object_or_404(Device, id=device_id)
    
    if request.method == 'POST':
        device_name = device.name
        device.delete()  # This will cascade delete all entities
        messages.success(request, f'Device "{device_name}" has been deleted successfully.')
        return redirect('dashboard')
    
    # If not POST, redirect to dashboard
    return redirect('dashboard')
