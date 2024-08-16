# Generated by Django 5.1 on 2024-08-14 11:28

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.product_image_upload_path),
        ),
    ]
