# Generated by Django 3.2.9 on 2021-11-18 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadinfo',
            name='client_ip',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='downloadinfo',
            name='download_status',
            field=models.CharField(default='', max_length=1000),
        ),
    ]