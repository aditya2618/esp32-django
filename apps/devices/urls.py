from django.urls import path
from . import views
from . import wizard
from . import connection_views
from . import delete_views

urlpatterns = [
    # Dashboard
    # Wizard URLs
    path('wizard/', wizard.wizard_start, name='wizard_start'),
    path('wizard/step1/', wizard.wizard_step1_device_info, name='wizard_step1_device_info'),
    path('wizard/step2/', wizard.wizard_step2_wifi, name='wizard_step2_wifi'),
    path('wizard/step3/', wizard.wizard_step3_mqtt, name='wizard_step3_mqtt'),
    path('wizard/step4/', wizard.wizard_step4_entities, name='wizard_step4_entities'),
    path('wizard/step5/', wizard.wizard_step5_review, name='wizard_step5_review'),
    path('wizard/step6/', wizard.wizard_step6_complete, name='wizard_step6_complete'),
    
    # Connection check
    path('api/check-esp32/', connection_views.check_esp32_connection, name='check_esp32_connection'),
    
    # Existing URLs
    path('', views.dashboard, name='dashboard'),
    
    # Device management
    path('device/add/', views.add_device, name='add_device'),
    path('device/<int:device_id>/', views.device_detail, name='device_detail'),
    path('device/<int:device_id>/edit/', views.edit_device, name='edit_device'),
    path('device/<int:device_id>/delete/', delete_views.delete_device, name='delete_device'),
    
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
