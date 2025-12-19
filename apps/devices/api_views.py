from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from apps.devices.models import Device, Entity
from .serializers import (UserSerializer, LoginSerializer, DeviceSerializer, 
                         EntitySerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    API endpoint for mobile app login
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=401)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    API endpoint for mobile app logout
    """
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def homes_list(request):
    """
    Get list of unique home_ids from devices
    """
    # Get unique home_ids from all devices
    home_ids = Device.objects.values_list('home_id', flat=True).distinct()
    
    # Return as simple list of home objects
    homes = [{'id': home_id, 'name': home_id} for home_id in home_ids]
    return Response(homes)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def devices_list(request):
    """
    Get list of devices, optionally filtered by home
    """
    home_id = request.GET.get('home')
    devices = Device.objects.all()
    
    if home_id:
        devices = devices.filter(home_id=home_id)
    
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def entities_list(request):
    """
    Get list of entities, optionally filtered by home
    """
    home_id = request.GET.get('home')
    entities = Entity.objects.all()
    
    if home_id:
        entities = entities.filter(device__home_id=home_id)
    
    serializer = EntitySerializer(entities, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def control_entity(request, entity_id):
    """
    Control an entity (turn on/off, set brightness, etc.)
    """
    try:
        entity = Entity.objects.get(id=entity_id)
    except Entity.DoesNotExist:
        return Response({'error': 'Entity not found'}, status=404)
    
    # Import here to avoid circular imports
    from apps.devices.mqtt_manager import publish_command
    
    # Extract control data
    new_state = request.data.get('state')
    brightness = request.data.get('brightness')
    speed = request.data.get('speed')
    
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
    
    return Response({'message': 'Command sent successfully'})
