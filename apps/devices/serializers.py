from rest_framework import serializers
from django.contrib.auth.models import User
from apps.devices.models import Device, Entity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'name', 'entity_type', 'subtype', 'state', 'capabilities', 
                  'unit', 'is_controllable', 'device', 'location']


class DeviceSerializer(serializers.ModelSerializer):
    entities = EntitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Device
        fields = ['id', 'name', 'node_name', 'is_online', 'last_seen', 
                  'firmware_version', 'metadata', 'entities', 'home', 'location']

