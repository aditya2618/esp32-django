# Generated manually to remove node_name unique constraint

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0004_entity_close_duration_entity_color_mode_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='node_name',
            field=models.CharField(help_text='ESPHome node name (e.g., home1_livingroom_node1)', max_length=100),
        ),
    ]
