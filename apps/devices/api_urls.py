from django.urls import path
from . import api_views

urlpatterns = [
    # Authentication
    path('auth/login/', api_views.login_view, name='api_login'),
    path('auth/logout/', api_views.logout_view, name='api_logout'),
    
    # Homes
    path('homes/', api_views.homes_list, name='api_homes'),
    
    # Devices
    path('devices/', api_views.devices_list, name='api_devices'),
    
    # Entities
    path('entities/', api_views.entities_list, name='api_entities'),
    path('entities/<int:entity_id>/control/', api_views.control_entity, name='api_control_entity'),
]
