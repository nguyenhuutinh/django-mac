# Generated by Django 4.0.6 on 2022-07-10 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0025_remove_campaign_google_form_campaign_google_form_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userforminfo',
            name='age',
        ),
        migrations.RemoveField(
            model_name='userforminfo',
            name='email',
        ),
        migrations.RemoveField(
            model_name='userforminfo',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='userforminfo',
            name='lucky_number',
        ),
        migrations.RemoveField(
            model_name='userforminfo',
            name='name',
        ),
        migrations.RemoveField(
            model_name='userforminfo',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='userforminfo',
            name='status',
        ),
        migrations.AddField(
            model_name='googleforminfo',
            name='num_fields',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='userforminfo',
            name='field1',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='userforminfo',
            name='field2',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='userforminfo',
            name='field3',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='userforminfo',
            name='field4',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='userforminfo',
            name='field5',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='userforminfo',
            name='field6',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='userforminfo',
            name='field7',
            field=models.CharField(default='', max_length=200),
        ),
    ]