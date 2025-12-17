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
    """Enhanced form for creating/editing entities with hardware type support"""
    
    # Hardware type dropdown (populated dynamically)
    hardware_type = forms.ChoiceField(
        choices=[('', '--- Select Hardware Type ---')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'hardware-type-select'
        }),
        help_text='Select specific hardware component'
    )
    
    class Meta:
        model = Entity
        fields = [
            'entity_name', 'entity_type', 'hardware_type', 'gpio_pin',
            'update_interval', 'i2c_address', 'inverted'
        ]
        # Note: pin_1, pin_2, pin_3, pin_4 are added dynamically in __init__
        widgets = {
            'entity_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., living_room_fan',
                'pattern': '[a-zA-Z_][a-zA-Z0-9_]*',
                'title': 'Must start with letter/underscore'
            }),
            'entity_type': forms.Select(attrs={'class': 'form-control'}),
            'gpio_pin': forms.Select(attrs={'class': 'form-control'}),
            'update_interval': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'i2c_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 0x76'}),
            'inverted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop('device', None)
        self.platform = kwargs.pop('platform', 'esp32')  # Get platform from session
        super().__init__(*args, **kwargs)
        
        # Import constants
        from .constants import (
            SENSOR_TYPES, ACTUATOR_TYPES,
            get_gpio_capabilities, ESP8266_D_PIN_MAP
        )
        
        # Populate hardware type choices
        all_components = {**SENSOR_TYPES, **ACTUATOR_TYPES}
        hardware_choices = [('', '--- Select Hardware Type ---')]
        
        for key, component in all_components.items():
            platform_key = f'{self.platform.lower()}_compatible'
            if component.get(platform_key, True):
                hardware_choices.append((key, f"{component.get('icon', '')} {component['name']}"))
        
        self.fields['hardware_type'].choices = hardware_choices
        
        # Populate GPIO pin choices
        capabilities = get_gpio_capabilities(self.platform)
        available_pins = capabilities.get('digital', [])
        pin_choices = [('', '--- Select GPIO Pin ---')]
        
        if self.platform.lower() == 'esp8266':
            for pin in available_pins:
                d_label = f" ({ESP8266_D_PIN_MAP[pin]})" if pin in ESP8266_D_PIN_MAP else ""
                pin_choices.append((str(pin), f'GPIO{pin}{d_label}'))
        else:
            for pin in available_pins:
                pin_choices.append((str(pin), f'GPIO{pin}'))
        
        self.fields['gpio_pin'].widget.choices = pin_choices
        
        # Add multi-pin fields dynamically (for RGB LEDs, stepper motors, etc.)
        for i in range(1, 5):  # pin_1, pin_2, pin_3, pin_4
            field_name = f'pin_{i}'
            self.fields[field_name] = forms.ChoiceField(
                choices=pin_choices,
                required=False,
                widget=forms.Select(attrs={
                    'class': 'form-control',
                    'id': f'pin_{i}'
                }),
                label=f'Pin {i}'
            )
        self.fields['gpio_pin'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        hardware_type = cleaned_data.get('hardware_type')
        
        # Import constants for validation
        from .constants import SENSOR_TYPES, ACTUATOR_TYPES
        all_components = {**SENSOR_TYPES, **ACTUATOR_TYPES}
        
        if hardware_type and hardware_type in all_components:
            component = all_components[hardware_type]
            pins_required = component.get('pins_required', 1)
            
            # Validate pin requirements
            if pins_required == 1:
                if not cleaned_data.get('gpio_pin'):
                    self.add_error('gpio_pin', 'This field is required.')
            else:
                # Multi-pin validation
                used_pins_in_form = []
                for i in range(1, pins_required + 1):
                    field_name = f'pin_{i}'
                    pin_val = cleaned_data.get(field_name)
                    if not pin_val:
                        self.add_error(field_name, f'Pin {i} is required for {component["name"]}.')
                    else:
                        pin_int = int(pin_val)
                        if pin_int in used_pins_in_form:
                             self.add_error(field_name, f'Pin {pin_int} is already selected.')
                        used_pins_in_form.append(pin_int)
                        
                        # Validate uniqueness against database
                        if self.device:
                            exclude_id = self.instance.id if self.instance.pk else None
                            # We manually call the validator for each extra pin
                            from .validators import validate_unique_gpio
                            try:
                                validate_unique_gpio(self.device, pin_int, exclude_id)
                            except ValidationError as e:
                                self.add_error(field_name, e)

        return cleaned_data

    def clean_entity_name(self):
        entity_name = self.cleaned_data.get('entity_name')
        validate_entity_name(entity_name)
        return entity_name
    
    def clean_gpio_pin(self):
        # We handle required check in clean() now because it depends on hardware_type
        gpio_pin = self.cleaned_data.get('gpio_pin')
        if gpio_pin:
             if self.device:
                exclude_id = self.instance.id if self.instance.pk else None
                validate_unique_gpio(self.device, int(gpio_pin), exclude_id)
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
