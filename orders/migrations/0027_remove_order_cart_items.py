# Generated by Django 3.2.10 on 2024-10-03 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0026_order_cart_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='cart_items',
        ),
    ]
