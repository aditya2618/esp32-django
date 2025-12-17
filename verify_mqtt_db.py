
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.devices.models import Device, Entity

print("Checking database for MQTT test device...")

try:
    test_node = Device.objects.filter(node_name='test-node').first()
    if test_node:
        print(f"✅ FOUND Device: {test_node.name} (node_name: {test_node.node_name})")
        print(f"   Last Seen: {test_node.last_seen}")
        
        entities = Entity.objects.filter(device=test_node)
        print(f"   Entities found: {entities.count()}")
        for e in entities:
             print(f"   - {e.entity_name} ({e.entity_type}): State='{e.state}'")
    else:
        print("❌ Device 'test-node' NOT found yet.")
        print(f"   Total devices in DB: {Device.objects.count()}")

except Exception as e:
    print(f"Error checking DB: {e}")
