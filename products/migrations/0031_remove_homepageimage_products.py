# Generated by Django 3.2.10 on 2024-10-28 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_homepageimage_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepageimage',
            name='products',
        ),
    ]
