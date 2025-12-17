from django.contrib import admin
from .models import Device, Entity, GPIOMapping, Firmware, OTAStatus


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_name', 'home_id', 'is_online', 'last_seen', 'created_at')
    list_filter = ('home_id', 'created_at')
    search_fields = ('name', 'node_name', 'home_id')
    readonly_fields = ('created_at', 'last_seen')
    
    fieldsets = (
        ('Device Information', {
            'fields': ('home_id', 'name', 'node_name')
        }),
        ('Status', {
            'fields': ('last_seen', 'created_at')
        }),
    )


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'entity_type', 'device', 'gpio_pin', 'state', 'last_updated')
    list_filter = ('entity_type', 'device')
    search_fields = ('entity_name', 'device__name')
    readonly_fields = ('last_updated',)
    
    fieldsets = (
        ('Entity Information', {
            'fields': ('device', 'entity_name', 'entity_type')
        }),
        ('Hardware', {
            'fields': ('gpio_pin',)
        }),
        ('State', {
            'fields': ('state', 'last_updated')
        }),
    )


@admin.register(GPIOMapping)
class GPIOMappingAdmin(admin.ModelAdmin):
    list_display = ('device', 'logical_id', 'gpio_pin', 'type', 'default_value')
    list_filter = ('type', 'device')
    search_fields = ('logical_id', 'device__name')
    
    fieldsets = (
        ('Device', {
            'fields': ('device',)
        }),
        ('GPIO Configuration', {
            'fields': ('logical_id', 'gpio_pin', 'type', 'default_value')
        }),
    )


@admin.register(Firmware)
class FirmwareAdmin(admin.ModelAdmin):
    list_display = ('version', 'file', 'uploaded_at')
    search_fields = ('version', 'description')
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        ('Firmware Information', {
            'fields': ('version', 'file', 'description')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',)
        }),
    )


@admin.register(OTAStatus)
class OTAStatusAdmin(admin.ModelAdmin):
    list_display = ('device', 'version', 'status', 'started_at', 'updated_at')
    list_filter = ('status', 'started_at')
    search_fields = ('device__name', 'version')
    readonly_fields = ('started_at', 'updated_at')
    
    fieldsets = (
        ('OTA Information', {
            'fields': ('device', 'firmware', 'version')
        }),
        ('Status', {
            'fields': ('status', 'message', 'started_at', 'updated_at')
        }),
    )
