# Generated by Django 3.2.1 on 2021-05-06 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_user_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account', to='app.user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(editable=False, max_length=254),
        ),
    ]
