# Generated by Django 3.2.10 on 2024-09-12 04:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_sub_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='Sub_category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='products.sub_category'),
        ),
    ]
