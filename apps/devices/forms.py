from django import forms
from django.core.exceptions import ValidationError
from .models import Device, Entity, GPIOMapping, Firmware, OTAStatus
from .validators import validate_gpio_pin, validate_unique_gpio, validate_entity_name


class DeviceForm(forms.ModelForm):
    """Form for creating/editing devices"""
    
    PLATFORM_CHOICES = [
        ('esp32', 'ESP32'),
        ('esp8266', 'ESP8266'),
    ]
    
    platform = forms.ChoiceField(
        choices=PLATFORM_CHOICES,
        initial='esp32',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select your device platform',
        required=False  # Not a model field, stored in session
    )
    
    class Meta:
        model = Device
        fields = ['home_id', 'name', 'node_name']  # platform is NOT a model field
        widgets = {
            'home_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., home1'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Living Room Controller'}),
            'node_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., home1_livingroom_node1'}),
        }



class EntityForm(forms.ModelForm):
    """Form for creating/editing entities"""
    class Meta:
        model = Entity
        fields = ['entity_name', 'entity_type', 'gpio_pin']
        widgets = {
            'entity_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., living_room_fan',
                'pattern': '[a-zA-Z_][a-zA-Z0-9_]*',
                'title': 'Must start with letter/underscore, contain only letters, numbers, and underscores'
            }),
            'entity_type': forms.Select(attrs={'class': 'form-control'}),
            'gpio_pin': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'GPIO pin (optional)', 'min': 0, 'max': 39}),
        }
    
    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop('device', None)
        super().__init__(*args, **kwargs)
        
        # Make gpio_pin optional for sensors
        self.fields['gpio_pin'].required = False
    
    def clean_entity_name(self):
        entity_name = self.cleaned_data.get('entity_name')
        
        # Validate entity name
        validate_entity_name(entity_name)
        
        return entity_name
    
    def clean_gpio_pin(self):
        gpio_pin = self.cleaned_data.get('gpio_pin')
        entity_type = self.cleaned_data.get('entity_type')
        
        if gpio_pin is not None:
            # Validate GPIO pin
            validate_gpio_pin(gpio_pin, entity_type)
            
            # Check uniqueness
            if self.device:
                exclude_id = self.instance.id if self.instance.pk else None
                validate_unique_gpio(self.device, gpio_pin, exclude_id)
        
        return gpio_pin


class GPIOMappingForm(forms.ModelForm):
    """Form for GPIO pin mapping"""
    class Meta:
        model = GPIOMapping
        fields = ['logical_id', 'gpio_pin', 'type', 'default_value']
        widgets = {
            'logical_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., relay_1'}),
            'gpio_pin': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 39}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'default_value': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop('device', None)
        super().__init__(*args, **kwargs)
    
    def clean_gpio_pin(self):
        gpio_pin = self.cleaned_data.get('gpio_pin')
        device_type = self.cleaned_data.get('type')
        
        # Validate GPIO pin
        validate_gpio_pin(gpio_pin, device_type)
        
        # Check uniqueness
        if self.device:
            exclude_id = self.instance.id if self.instance.pk else None
            validate_unique_gpio(self.device, gpio_pin, exclude_id)
        
        return gpio_pin


class EntityControlForm(forms.Form):
    """Form for controlling entities (ON/OFF, dimmer, etc.)"""
    entity_id = forms.IntegerField(widget=forms.HiddenInput())
    value = forms.CharField(widget=forms.HiddenInput())


class FirmwareUploadForm(forms.ModelForm):
    """Form for uploading firmware"""
    class Meta:
        model = Firmware
        fields = ['version', 'file', 'description']
        widgets = {
            'version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1.0.0'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.bin'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }


class OTATriggerForm(forms.Form):
    """Form for triggering OTA update"""
    firmware = forms.ModelChoiceField(
        queryset=Firmware.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select firmware version"
    )


class BulkOTAForm(forms.Form):
    """Form for bulk OTA updates"""
    firmware = forms.ModelChoiceField(
        queryset=Firmware.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select firmware version"
    )
    devices = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )


class FactoryResetForm(forms.Form):
    """Form for factory reset confirmation"""
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I understand this will erase all device configuration"
    )
