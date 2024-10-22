# Generated by Django 5.1 on 2024-10-21 23:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_imagedata_alter_eventimagedata_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopdata',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shops', to='api.organizationdata'),
        ),
    ]