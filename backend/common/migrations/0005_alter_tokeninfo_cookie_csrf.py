# Generated by Django 4.0.5 on 2022-07-03 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_auto_20211125_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokeninfo',
            name='cookie_csrf',
            field=models.CharField(max_length=1000),
        ),
    ]
