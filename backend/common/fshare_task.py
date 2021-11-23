
# project/tasks/sample_tasks.py

from __future__ import print_function
import time
from argparse import Namespace
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

@shared_task
def doFshareFlow(code):
    print("do Fshare Download Flow")
    # Opening JSON file
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/' + "fshare.vn_cookies.txt"
    jar = parseCookieFile(url_path)

    myobj = {'linkcode': code, 'clone_to_folder':'/', 'secure': 0}
    print("code" , code)
    headers_api = {
        'Authorization': 'Bearer ' + "jcrnprtt0l9vlt10p0ous2a6d9",
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


    resp = requests.get('https://www.fshare.vn/api/v3/files/download-zip?linkcodes=' + linkCode, cookies=jar, headers=headers_api)
    print(resp.request.url)
    print(resp.request.body)
    print(resp.request.headers)

    print('bbbbbbbbbb')
    print(resp.headers)
    print(resp.json())

    return resp.json()



def parseCookieFile(cookiefile):
    cookies = Path(cookiefile)

    jar = MozillaCookieJar(cookies)
    jar.load()
    # print(jar)
    return jar

