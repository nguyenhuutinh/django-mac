from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class IndexedTimeStampedModel(models.Model):
    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)

    class Meta:
        abstract = True

class DownloadInfo(models.Model):
    # define department name and description columns, the id column will be added automatically.
    file_id = models.CharField(max_length=1000)
    file_desc = models.CharField(max_length=1000)
    client_ip = models.CharField(max_length=1000, default="")

    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)
    download_count = models.IntegerField()
    download_status = models.CharField(max_length=1000, default="")
    # this is a inner class which is used to define unique index columns. You can specify multiple columns in a list or tuple.
    def __str__(self):
        ret = self.file_id + ',' + str(self.download_count)
        return ret
    # class Meta:
    #     unique_together = ['file_id']
class TokenInfo(models.Model):
    # define department name and description columns, the id column will be added automatically.
    account_id = models.CharField(max_length=1000,primary_key = True)
    cookie_share_app = models.CharField(max_length=1000)
    cookie_csrf = models.CharField(max_length=1000)
    # cookie_csrf_2 = models.CharField(max_length=1000)
    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)

    # this is a inner class which is used to define unique index columns. You can specify multiple columns in a list or tuple.
    def __str__(self):
        ret = self.account_id + ',' + str(self.modified)
        return ret
    # class Meta:
    #     unique_together = ['file_id']
class Campaign(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000 )
    file_name = models.CharField(max_length=1000 )
    total = models.IntegerField(default=0)
    sent = models.IntegerField(default=0)
    target_date = models.DateField(blank=True, null=True)
    during_date = models.IntegerField(default=1)
    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)
class UserFormInfo(models.Model):
    # define department name and description columns, the id column will be added automatically.
    auto_increment_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000 )
    phone = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    age = models.CharField(max_length=1000)
    gender = models.CharField(max_length=1000)
    lucky_number = models.CharField(max_length=1000, default="")
    sent = models.BooleanField(default=False)

    target_date = models.DateTimeField(blank=True, null=True)

    sent_date = models.DateField(blank=True, null=True)
    sent_date_time = models.DateTimeField(blank=True, null=True)
    sent_time = models.TimeField(blank=True, null=True)
    sent_status = models.CharField(max_length=1000)

    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)
    campaign = models.ForeignKey(
        "Campaign", on_delete=models.CASCADE)


    # this is a inner class which is used to define unique index columns. You can specify multiple columns in a list or tuple.
    # def __str__(self):
    #     ret = self.name + ',' + self.phone + ',' + self.email  + ',' + str(self.modified)
    #     return ret
