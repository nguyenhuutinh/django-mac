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
