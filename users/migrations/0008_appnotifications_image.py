# Generated by Django 3.2.10 on 2024-10-08 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_road_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='appnotifications',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='notification_images/'),
        ),
    ]
