# Generated by Django 4.0.6 on 2022-07-09 21:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0016_campaign_end_time_campaign_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='form',
        ),
    ]
