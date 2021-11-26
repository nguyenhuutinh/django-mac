
# project/tasks/sample_tasks.py

from __future__ import print_function
import time
from argparse import Namespace
from bs4 import BeautifulSoup
import threading
from django.http import JsonResponse
from oauth2client import file
import requests
import pprint
from http.cookiejar import MozillaCookieJar
from pathlib import Path

from celery import shared_task
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.timezone import now
from googleapiclient.http import MediaIoBaseDownload
from common.fshare import FS




def checkFileName(server, url):
    fshareI  = FS(server)
    isExist = fshareI.is_exist(url)
    print(isExist)

    if isExist:
        return fshareI.get_file_name(url)
    else:
        pass
def checkFileSize(server, url):
    fshareI  = FS(server)
    isExist = fshareI.is_exist(url)
    if isExist:
        return fshareI.get_file_size(url)
    else:
        pass
@shared_task
def fileNameTask(server,url):
    if "folder" in str(url) :
        raise Exception("this link is folder link")
    if "fshare.vn/file" in str(url) == False:
        raise Exception("this link is not valid link")

    print("file_name_info", server)
    return checkFileName(server, url)

@shared_task
def fileSizeTask(server,url):
    if "folder" in str(url) :
        raise Exception("this link is folder link")
    if "fshare.vn/file" in str(url) == False:
        raise Exception("this link is not valid link")

    print("file_name_info", server)
    return checkFileSize(server, url)
