# Generated by Django 3.2.3 on 2021-05-21 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_comment_state'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='spokencomment',
            options={'verbose_name': 'Spoken Comment', 'verbose_name_plural': 'Spoken Comments'},
        ),
        migrations.AlterModelOptions(
            name='writtencomment',
            options={'verbose_name': 'Written Comment', 'verbose_name_plural': 'Written Comments'},
        ),
    ]
