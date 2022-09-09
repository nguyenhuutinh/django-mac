from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from model_utils.fields import AutoCreatedField, AutoLastModifiedField


# class IndexedTimeStampedModel(models.Model):
#     created = AutoCreatedField(_("created"), db_index=True)
#     modified = AutoLastModifiedField(_("modified"), db_index=True)

#     class Meta:
#         abstract = True

# class GoogleFormField(models.Model):
#     id = models.AutoField(primary_key=True)
#     key_name = models.CharField(max_length=200 )
#     key_index = models.IntegerField(default=1)
#     google_form = models.ForeignKey(
#         "GoogleFormInfo", on_delete=models.CASCADE)
#     campaign = models.ForeignKey(
#         "Campaign", on_delete=models.CASCADE)
# class GoogleFormInfo(models.Model):
#     id = models.AutoField(primary_key=True)
#     link = models.CharField(max_length=300, default="" )
#     action_link = models.CharField(max_length=300, default="" )
#     num_fields = models.IntegerField(default=1 )
#     partial_response = models.CharField(max_length=300, default="" )
#     fbzx = models.CharField(max_length=300, default="" )
#     fvv  = models.CharField(max_length=300, default="" )
#     page_history = models.CharField(max_length=300, default="" )
#     campaign = models.ForeignKey(
#         "Campaign", on_delete=models.CASCADE)
# class Campaign(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=200 )
#     file_name = models.CharField(max_length=300, default="" )
#     start_date = models.DateTimeField(blank=True, null=True)
#     end_date = models.DateTimeField(blank=True, null=True)
#     start_time = models.TimeField(blank=True, null=True)
#     end_time = models.TimeField(blank=True, null=True)
#     status = models.CharField(max_length=50, default="")
#     created = AutoCreatedField(_("created"), db_index=True)
#     modified = AutoLastModifiedField(_("modified"), db_index=True)
#     total_schedules = models.IntegerField(default= 0)
#     total_forms = models.IntegerField(default= 0)
#     completed_forms = models.IntegerField(default= 0)
#     google_form_id = models.IntegerField(default= -1)
#     last_item_id = models.IntegerField(default= -1)

# class Schedule(models.Model):
#     id = models.AutoField(primary_key=True)
#     campaign = models.ForeignKey(
#         "Campaign", on_delete=models.CASCADE)
#     target_date = models.DateTimeField(blank=True, null=True)
#     start_time = models.TimeField(blank=True, null=True)
#     end_time = models.TimeField(blank=True, null=True)
#     status = models.CharField(max_length=50, default="")
#     finished_time = models.TimeField(blank=True, null=True)
#     items = models.IntegerField(default=1)

# class CampaignSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Campaign
#         fields = '__all__'

# class GoogleFormInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GoogleFormInfo
#         fields = '__all__'

# class UserFormInfo(models.Model):
#     # define department name and description columns, the id column will be added automatically.
#     auto_increment_id = models.AutoField(primary_key=True)
#     field1 = models.CharField(max_length=200 , default="")
#     field2 = models.CharField(max_length=200, default="")
#     field3 = models.CharField(max_length=200, default="")
#     field4 = models.CharField(max_length=200, default="")
#     field5 = models.CharField(max_length=200 ,default="")
#     field6 = models.CharField(max_length=200,default="")
#     field7 = models.CharField(max_length=200, default="")
#     field8 = models.CharField(max_length=200, default="")
#     field9 = models.CharField(max_length=200, default="")
#     field10 = models.CharField(max_length=200, default="")

#     status = models.CharField(max_length=50, default="")
#     sent = models.BooleanField(default=False)

#     target_date = models.DateTimeField(blank=True, null=True)

#     sent_date = models.DateField(blank=True, null=True)
#     sent_date_time = models.DateTimeField(blank=True, null=True)
#     sent_time = models.TimeField(blank=True, null=True)
#     sent_status = models.CharField(max_length=50)

#     # last_item = models.BooleanField(default=False)
#     created = AutoCreatedField(_("created"), db_index=True)
#     modified = AutoLastModifiedField(_("modified"), db_index=True)
#     campaign = models.ForeignKey(
#         "Campaign", on_delete=models.CASCADE)
