# Generated by Django 3.2.10 on 2024-10-03 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_auto_20241003_1201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='unique_order_serial',
        ),
    ]
