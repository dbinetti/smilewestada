# Generated by Django 3.2.3 on 2021-05-18 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_attendee_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
