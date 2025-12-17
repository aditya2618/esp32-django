# Generated manually to remove unique_together constraint on Entity

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0005_remove_node_name_unique'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='entity',
            unique_together=set(),
        ),
    ]
