# Generated by Django 4.0.6 on 2022-07-09 21:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_remove_schedule_form'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DownloadInfo',
        ),
        migrations.DeleteModel(
            name='TokenInfo',
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='number',
            new_name='items',
        ),
    ]