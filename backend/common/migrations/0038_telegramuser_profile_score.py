# Generated by Django 4.1.3 on 2022-11-30 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0037_campaign_alter_message_text_userforminfo_schedule_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="telegramuser",
            name="profile_score",
            field=models.CharField(default="", max_length=300, null=True),
        ),
    ]