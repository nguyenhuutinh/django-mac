# Generated by Django 4.0.5 on 2022-07-03 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_userforminfo_target_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userforminfo',
            name='target_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
