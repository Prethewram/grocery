from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_auto_20241002_1717'),
    ]

    operations = [
        # Commenting out or removing the remove field operation
        # migrations.RemoveField(
        #     model_name='order',
        #     name='unique_order_serial',
        # ),
        migrations.AddField(
            model_name='order',
            name='order_ids',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
