
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

    print('aaaaaaaaaa')
    print(resp.headers)
    print(resp.json())
    linkCode = resp.json().get("linkcode")
    if linkCode == None:
        return resp.json()

    # deleteFshareFile.apply_async(kwargs={ "code": linkCode},eta=now() + timedelta(seconds=5*60))
    heartBeating.apply_async(eta=now() + timedelta(seconds=1*30))
    resp = requests.get('https://www.fshare.vn/api/v3/files/download-zip?linkcodes=' + linkCode, cookies=jar, headers=headers_api)
    print(resp.request.url)
    print(resp.request.body)
    print(resp.request.headers)

    print('bbbbbbbbbb')
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
    print(resp.request.url)
    print(resp.request.body)
    print(resp.request.headers)
    print(resp.json())
    return resp

def parseCookieFile(cookiefile):
    cookies = Path(cookiefile)

    jar = MozillaCookieJar(cookies)
    jar.load()
    # print(jar)
    return jar




def heartbeat():
    threading.Timer(60.0, heartbeat).start()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/' + FILE_NAME
    jar = parseCookieFile(url_path)

    headers_api = {
        'Authorization': 'Bearer ' + BEARER_KEY,
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', cookies=jar, headers=headers_api)
    print("heartbeat", resp)
    return resp
