"""
Test entity name validation
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, r'h:\aditya\home-esp32\esp32-django')
django.setup()

from apps.devices.validators import validate_entity_name
from django.core.exceptions import ValidationError

# Test cases: (name, should_pass)
test_cases = [
    ('light_1', True, 'Valid: letters, numbers, underscore'),
    ('bedroom_fan', True, 'Valid: letters and underscore'),
    ('relay1', True, 'Valid: letters and number'),
    ('_private', True, 'Valid: starts with underscore'),
    ('1', False, 'Invalid: purely numeric'),
    ('123', False, 'Invalid: purely numeric'),
    ('light 1', False, 'Invalid: contains space'),
    ('fan-2', False, 'Invalid: contains hyphen'),
    ('sensor@home', False, 'Invalid: contains special char'),
    ('1_light', False, 'Invalid: starts with number'),
]

print("Testing Entity Name Validation\n" + "="*50)
passed = 0
failed = 0

for name, should_pass, description in test_cases:
    try:
        validate_entity_name(name)
        if should_pass:
            print(f"✓ PASS: '{name}' - {description}")
            passed += 1
        else:
            print(f"✗ FAIL: '{name}' - {description} (should have been rejected)")
            failed += 1
    except ValidationError as e:
        if not should_pass:
            print(f"✓ PASS: '{name}' - {description}")
            print(f"  Error: {e.message}")
            passed += 1
        else:
            print(f"✗ FAIL: '{name}' - {description} (should have passed)")
            print(f"  Error: {e.message}")
            failed += 1

print("\n" + "="*50)
print(f"Results: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
