# Generated by Django 4.0.5 on 2022-07-03 17:25

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_alter_tokeninfo_cookie_csrf'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1000)),
                ('file_name', models.CharField(max_length=1000)),
                ('total', models.IntegerField(default=0)),
                ('sent', models.IntegerField(default=0)),
                ('target_date', models.DateField(blank=True, null=True)),
                ('during_date', models.IntegerField(default=1)),
                ('created', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='modified')),
            ],
        ),
        migrations.CreateModel(
            name='UserFormInfo',
            fields=[
                ('auto_increment_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1000)),
                ('phone', models.CharField(max_length=1000)),
                ('email', models.CharField(max_length=1000)),
                ('age', models.CharField(max_length=1000)),
                ('sent', models.BooleanField(default=False)),
                ('sent_date', models.DateField(blank=True, null=True)),
                ('sent_time', models.TimeField(blank=True, null=True)),
                ('sent_status', models.CharField(max_length=1000)),
                ('created', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.campaign')),
            ],
        ),
    ]