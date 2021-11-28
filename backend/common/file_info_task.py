
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




def checkFileInfo(server, url):
    fshareI  = FS(server)
    res = fshareI.is_exist(url)
    if res != False:
        fileName = fshareI.get_file_name(res)
        fileSize = fshareI.get_file_size(res)
        passwordFile = fshareI.is_file_protected(res)
        if passwordFile:
            return {"file_name": "unknown", "file_size":fileSize, "password": passwordFile}
        elif fileName and fileSize:
            return {"file_name": fileName, "file_size":fileSize, "password": passwordFile}
        elif fileName :
            return {"file_name": fileName, "file_size":'unknown', "password": passwordFile}
        elif fileSize :
            return {"file_name": "unknown", "file_size": fileSize, "password": passwordFile}
        else :
            return { "errors" : "Không thể lấy thông tin file. vui lòng thử lại"}
    else:
        return { "errors" : "File không tồn tại"}

@shared_task
def checkfileInfoTask(server,url):
    if "folder" in str(url) :
        raise Exception("this link is folder link")
    if "fshare.vn/file" in str(url) == False:
        raise Exception("this link is not valid link")

    print("file_name_info", server)

    return checkFileInfo(server, url)


@shared_task
def checkaccountInfoTask(server):
    print("checkaccountInfoTask", server)

    return checkAccountInfo(server)



def checkAccountInfo(server):
    fshareI  = FS(server)
    res = fshareI.checkAccountStorage(server)
    if res != False:
        return {"used": res.get("used"), "avaiable": res.get("available")}
    else:
        return { "errors" : "Lỗi"}
