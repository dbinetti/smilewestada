# Generated by Django 3.2.2 on 2021-05-13 04:25

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20210512_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='zone',
            field=models.IntegerField(blank=True, choices=[(1, 'Zone 1'), (2, 'Zone 2'), (3, 'Zone 3'), (4, 'Zone 4'), (5, 'Zone 5'), (6, 'Outside District')], null=True),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='video',
            field=models.ImageField(blank=True, storage=cloudinary_storage.storage.VideoMediaCloudinaryStorage(), upload_to='videos/'),
        ),
    ]
