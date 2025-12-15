from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Device management
    path('device/add/', views.add_device, name='add_device'),
    path('device/<int:device_id>/', views.device_detail, name='device_detail'),
    path('device/<int:device_id>/edit/', views.edit_device, name='edit_device'),
    
    # Entity management
    path('device/<int:device_id>/entity/add/', views.add_entity, name='add_entity'),
    path('entity/<int:entity_id>/edit/', views.edit_entity, name='edit_entity'),
    path('entity/<int:entity_id>/delete/', views.delete_entity, name='delete_entity'),
    
    # GPIO mapping
    path('device/<int:device_id>/gpio/', views.gpio_mapping, name='gpio_mapping'),
    path('gpio-mapping/<int:mapping_id>/delete/', views.delete_gpio_mapping, name='delete_gpio_mapping'),
    path('device/<int:device_id>/pinout/', views.esp32_pinout, name='esp32_pinout'),
    
    # Firmware and OTA
    path('device/<int:device_id>/firmware/', views.firmware_page, name='firmware_page'),
    path('firmware/', views.firmware_list, name='firmware_list'),
    path('firmware/upload/', views.upload_firmware, name='upload_firmware'),
    path('firmware/bulk-ota/', views.bulk_ota, name='bulk_ota'),
    path('ota/status/', views.ota_status, name='ota_status'),
    
    # Factory reset
    path('device/<int:device_id>/reset/', views.factory_reset, name='factory_reset'),
    
    # ESPHome YAML generation
    path('device/<int:device_id>/yaml/download/', views.generate_yaml, name='generate_yaml'),
    path('device/<int:device_id>/yaml/view/', views.view_yaml, name='view_yaml'),
]
