# Generated by Django 3.2.10 on 2024-08-31 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_alter_product_weight_measurement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='weights',
            field=models.JSONField(default=list, help_text='Store different weights with their respective prices in JSON format'),
        ),
    ]
