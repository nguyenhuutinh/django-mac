# Generated by Django 4.0.5 on 2022-07-07 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0013_rename_enddate_campaign_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='file_name',
            field=models.CharField(default='', max_length=1000),
        ),
    ]