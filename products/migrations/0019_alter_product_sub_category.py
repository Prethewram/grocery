# Generated by Django 3.2.10 on 2024-09-12 04:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_product_sub_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='Sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.sub_category'),
        ),
    ]
