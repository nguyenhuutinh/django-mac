from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class IndexedTimeStampedModel(models.Model):
    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)

    class Meta:
        abstract = True


class TelegramUser(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=300, default="" )
    firstname = models.CharField(max_length=300, default="", null=True,  )
    lastname = models.CharField(max_length=300, default="" , null=True)
    username = models.CharField(max_length=300, default="", null=True )
    status = models.CharField(max_length=300, default="" )
    ban_reason = models.CharField(max_length=300, default="" )

    isBot  = models.BooleanField(default=False)
    user_avatar_link = models.CharField(max_length=300, default="" , null=True, )
    profile_score = models.CharField(max_length=300, default="" , null=True, )
class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'
class Message(models.Model):
    message_id = models.CharField(max_length=200 ,  primary_key=True)
    user = models.ForeignKey(
        "TelegramUser", on_delete=models.CASCADE)
    text = models.TextField( default="", null=True,  )
    date_timestamp = models.CharField(max_length=300, default="" )
    status = models.CharField(max_length=300, default="" )



class MessageCounter(models.Model):
    date = models.DateField(unique=True)
    checking_messages = models.IntegerField(default=0)
    deleted_messages = models.IntegerField(default=0)
