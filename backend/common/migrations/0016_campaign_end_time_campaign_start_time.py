# Generated by Django 4.0.6 on 2022-07-09 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0015_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
