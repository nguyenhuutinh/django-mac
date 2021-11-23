
# project/tasks/sample_tasks.py

from __future__ import print_function
import time
from argparse import Namespace

import threading
import io
import re
import httplib2
import os
import ntpath
import json
import shutil
from django.http import JsonResponse
from oauth2client import file
import requests
import pprint
from http.cookiejar import MozillaCookieJar
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from celery import shared_task
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.timezone import now
from googleapiclient.http import MediaIoBaseDownload

from common.models import DownloadInfo

BEARER_KEY_1 = "9ck8scdmnimjvuvhblvhgdg38i"
FILE_NAME_1 = "fshare.vn_cookies.txt"
BEARER_KEY_2 = "d9c7peshf5v2ermmd24hf8liu6"
FILE_NAME_2 = "fshare.vn_cookies2.txt"
BEARER_KEY_3 = "bhui9plvkal757v7fep95ij56k"
FILE_NAME_3 = "fshare.vn_cookies3.txt"
FILE_NAME = FILE_NAME_2
BEARER_KEY = BEARER_KEY_2
@shared_task
def doFshareFlow(code, server):
    if server == 1:
        FILE_NAME = FILE_NAME_1
        BEARER_KEY = BEARER_KEY_1
    elif server == 2:
        FILE_NAME = FILE_NAME_2
        BEARER_KEY = BEARER_KEY_2
    else:
        FILE_NAME = FILE_NAME_3
        BEARER_KEY = BEARER_KEY_3
    print("do Fshare Download Flow")
    # Opening JSON file
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/' + FILE_NAME
    jar = parseCookieFile(url_path)

    myobj = {'linkcode': code, 'clone_to_folder':'/', 'secure': 0}
    print("code" , code, FILE_NAME, BEARER_KEY)
    headers_api = {
        'Authorization': 'Bearer ' + BEARER_KEY,
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
    }

    resp = requests.post('https://www.fshare.vn/api/v3/downloads/clone-file', cookies=jar, data=myobj, headers=headers_api)
    print(resp.request.url)
    print(resp.request.body)
    print(resp.request.headers)

    print('download file to my drive')
    print(resp.headers)
    print(resp.json())
    linkCode = resp.json().get("linkcode")
    if linkCode == None:
        return resp.json()

    # deleteFshareFile.apply_async(kwargs={ "code": linkCode},eta=now() + timedelta(seconds=5*60))
    heartBeating.apply_async(eta=now() + timedelta(seconds=1*30))
    resp = requests.get('https://www.fshare.vn/api/v3/files/download-zip?linkcodes=' + linkCode, cookies=jar, headers=headers_api)
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)

    print('download zip')
    print(resp.headers)
    print(resp.json())

    return resp.json()

@shared_task
def heartBeating():
    heartbeat()

@shared_task
def deleteFshareFile(code):
    # credentials = get_credentials()
    # http = credentials.authorize(httplib2.Http())
    # service = build('drive', 'v3', http=http)
    # response = service.files().update(fileId=task_id, addParents= STORE_DRIVE_ID,
    # removeParents= SOURCE_DRIVE_ID,
    # fields= 'id, parents'
    # ).execute()

    print("deleteFshareFile : "+ code)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/' + FILE_NAME
    jar = parseCookieFile(url_path)

    myobj = {'files' : [{'linkcode': code}]}
    body = json.dumps(myobj)
    print("myobj" , myobj)
    headers_api = {
        'Authorization': 'Bearer ' + BEARER_KEY,
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
    }

    resp = requests.delete('https://www.fshare.vn/api/v3/files/delete-files', cookies=jar, data= body, headers=headers_api)
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    print(resp.json())
    return resp

def parseCookieFile(cookiefile):
    cookies = Path(cookiefile)

    jar = MozillaCookieJar(cookies)
    jar.load()
    # print(jar)
    return jar




def heartbeat():
    thread = threading.Timer(10.0, heartbeat)
    thread.start()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/' + FILE_NAME
    jar = parseCookieFile(url_path)

    headers_api = {
        # 'Authorization': 'Bearer ' + BEARER_KEY,
        "referer":"https://www.fshare.vn/file/manager",
        "x-requested-with":'XMLHttpRequest',
        'x-csrf-token':'A-fWA56bvXMQJOrRU1sfop--caYRmhadenW9lApzQ7A334Rhxt_fPVpluZMCPkXL2tce4XKtUfgJRNn5eD8x6Q==',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Cookie':'_uidcms=1601864159616834536; fs_same_site=sameSite; _ga=GA1.2.504762787.1601864160; ajs_group_id=null; fpt_uuid=%22bf9df483-4a74-4479-aadd-b3f3a3c4cc6c%22; _gid=GA1.2.2097226903.1637504167; _fbp=fb.1.1637504167210.508549578; __gads=ID=be91e8f23e2a503a-22a775b833cf008b:T=1637504167:RT=1637504167:S=ALNI_MYMR59VmDHBm4UnIfTlwy6EjnHR0A; __yoid__=8941ce3caac7018bc56cdf633fcb411f; _ftitfsi=36353635343136; showPopupMemRegBeginTime=0a4a1bba24faf41c61d412300a499a137235ab8b05d3b508ba4a73313fc2e721a%3A2%3A%7Bi%3A0%3Bs%3A24%3A%22showPopupMemRegBeginTime%22%3Bi%3A1%3Bi%3A1637643277%3B%7D; showPopupMemRegLastTime=dcb2f05f2125f3d00d594301ae640d36674e7e73a689a450f436c87b1a786cb9a%3A2%3A%7Bi%3A0%3Bs%3A23%3A%22showPopupMemRegLastTime%22%3Bi%3A1%3Bi%3A1637643277%3B%7D; showPopupMemReg=fbef979f496638a917becd07db77635fbb7ecc3957e8dee12415ec2a2eb41024a%3A2%3A%7Bi%3A0%3Bs%3A15%3A%22showPopupMemReg%22%3Bi%3A1%3Bi%3A1%3B%7D; fshare-app=d9c7peshf5v2ermmd24hf8liu6; _csrf=wo_pV4R-C6AQ1JiJZAnJIaJadoaaXsDm'
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', headers=headers_api)
    isSuccess = resp.json().get("success")
    print(resp.request.url)
    print(resp.request.body)
    print(resp.request.headers)
    if isSuccess != True:
        thread.cancel()
    print(resp.json())
    return resp
