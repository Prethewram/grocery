# Generated by Django 3.2.10 on 2024-10-09 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0025_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='weight_measurement',
            field=models.CharField(choices=[('kg', 'Kilogram'), ('gm', 'Gram'), ('ltr', 'Liter'), ('ml', 'Milliliter'), ('unit', 'Unit')], max_length=10),
        ),
    ]
