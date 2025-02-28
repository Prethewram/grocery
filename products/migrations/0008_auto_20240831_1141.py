# Generated by Django 3.2.10 on 2024-08-31 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20240828_1429'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='base_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='product',
            name='weight_measurement',
        ),
        migrations.AddField(
            model_name='product',
            name='weights',
            field=models.TextField(default='[]', help_text='Store different weights, quantities, and prices in JSON format'),
        ),
    ]
