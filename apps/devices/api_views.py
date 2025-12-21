from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from apps.devices.models import Device, Entity
import json


def _get_auth_user(request):
    """Helper to get authenticated user from token"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Token '):
        return None
    
    token_key = auth_header.replace('Token ', '')
    try:
        from django.contrib.auth.models import User
        # Simple token validation - you may want to use a proper token model
        user = User.objects.get(username=token_key.split('_')[0])  # Basic token handling
        return user
    except (User.DoesNotExist, IndexError):
        return None


@csrf_exempt
def login_view(request):
    """API endpoint for mobile app login"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            # Generate simple token (username_timestamp)
            import time
            token = f"{username}_{int(time.time())}"
            return JsonResponse({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
def logout_view(request):
    """API endpoint for mobile app logout"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    return JsonResponse({'message': 'Logged out successfully'})


def homes_list(request):
    """Get list of unique home_ids from devices"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = _get_auth_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get unique home_ids from all devices
    home_ids = Device.objects.values_list('home_id', flat=True).distinct()
    
    # Return as simple list of home objects
    homes = [{'id': home_id, 'name': home_id} for home_id in home_ids]
    return JsonResponse(homes, safe=False)


def devices_list(request):
    """Get list of devices, optionally filtered by home"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = _get_auth_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    home_id = request.GET.get('home')
    devices = Device.objects.all()
    
    if home_id:
        devices = devices.filter(home_id=home_id)
    
    devices_data = [{
        'id': d.id,
        'node_name': d.node_name,
        'home_id': d.home_id,
        'is_online': d.is_online,
        'last_seen': d.last_seen.isoformat() if d.last_seen else None,
        'entities': list(d.entities.values())
    } for d in devices]
    
    return JsonResponse(devices_data, safe=False)


def entities_list(request):
    """Get list of entities, optionally filtered by home"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = _get_auth_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    home_id = request.GET.get('home')
    entities = Entity.objects.all()
    
    if home_id:
        entities = entities.filter(device__home_id=home_id)
    
    entities_data = list(entities.values())
    return JsonResponse(entities_data, safe=False)


@csrf_exempt
def control_entity(request, entity_id):
    """Control an entity (turn on/off, set brightness, etc.)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = _get_auth_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        entity = Entity.objects.get(id=entity_id)
    except Entity.DoesNotExist:
        return JsonResponse({'error': 'Entity not found'}, status=404)
    
    # Import here to avoid circular imports
    from apps.devices.mqtt_manager import publish_command
    
    try:
        data = json.loads(request.body)
        
        # Extract control data
        new_state = data.get('state')
        brightness = data.get('brightness')
        speed = data.get('speed')
        
        # Publish MQTT command
        device = entity.device
        topic = f"home/{device.home_id}/device/{device.node_name}/command"
        
        payload = {'entity_id': entity.id}
        if new_state:
            payload['state'] = new_state
        if brightness is not None:
            payload['brightness'] = brightness
        if speed is not None:
            payload['speed'] = speed
        
        publish_command(topic, payload)
        
        return JsonResponse({'message': 'Command sent successfully'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
