
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
CSRF_1 = "GJT4JS85sLKIQFT18Oq2ETYWCPK2rdS2"
BEARER_KEY_1 = "6ivddn6ase7ckmn0bjcnrffpjj"
FILE_NAME_1 = "fshare.vn_cookies.txt"
COOKIE_1 = "_fbp=fb.1.1637416756636.822035357; _ga=GA1.2.780574709.1637416756; _gid=GA1.2.1725019688.1637416756; ajs_group_id=null; fpt_uuid=%2215cc3bf0-d723-421c-81ca-7dc278b76e56%22; _uidcms=1637416755053161666; __gads=ID=0e4cfce35e6f747f-2281df7134cf0088:T=1637416756:RT=1637635837:S=ALNI_MavgVG8wZ18XvH7QvfUTm5jycvuBA; VIP_USER17443112=364ddc37cef322dfb17a9cd96abce91f5a19902046e30724bf1e066c4243e8a2a%3A2%3A%7Bi%3A0%3Bs%3A16%3A%22VIP_USER17443112%22%3Bi%3A1%3Ba%3A6%3A%7Bs%3A13%3A%22timesToAppear%22%3Bi%3A99%3Bs%3A16%3A%22timesToLoadPopUp%22%3Bi%3A3%3Bs%3A8%3A%22dayToday%22%3Bi%3A3%3Bs%3A16%3A%22timeToApearAgain%22%3Bi%3A1630631242%3Bs%3A12%3A%22timeToAppear%22%3Bi%3A1630687994%3Bs%3A4%3A%22show%22%3Bb%3A1%3B%7D%7D; _identity-app=59c108aa4c43567619a72dc33330726179d26678b721b33c78e3ee75cefe1181a%3A2%3A%7Bi%3A0%3Bs%3A13%3A%22_identity-app%22%3Bi%3A1%3Bs%3A56%3A%22%5B17968929%2C%22Zb5Y1cu3jmvTbCq76URkunJU_rfe6Ij9%22%2C1634889338%5D%22%3B%7D; fshare-app="+ BEARER_KEY_1 +"; _ftitfsi=3137393638393239; _gat_gtag_UA_97071061_1=1; _gat_UA-97071061-1=1; _csrf=" + CSRF_1

CSRF_2 = "Ynx9v_1H6RZLMf4zkIRbaQK41Hczttdz"
BEARER_KEY_2 = "eh7aeldg5u5gpsnmttdtbakcro"
FILE_NAME_2 = "fshare.vn_cookies2.txt"
COOKIE_2 = "_uidcms=1601864159616834536; fs_same_site=sameSite; _ga=GA1.2.504762787.1601864160; ajs_group_id=null; fpt_uuid=\"bf9df483-4a74-4479-aadd-b3f3a3c4cc6c\"; _gid=GA1.2.2097226903.1637504167; _fbp=fb.1.1637504167210.508549578; __gads=ID=be91e8f23e2a503a-22a775b833cf008b:T=1637504167:RT=1637504167:S=ALNI_MYMR59VmDHBm4UnIfTlwy6EjnHR0A; __yoid__=8941ce3caac7018bc56cdf633fcb411f; _ftitfsi=36353635343136; showPopupMemRegBeginTime=0a4a1bba24faf41c61d412300a499a137235ab8b05d3b508ba4a73313fc2e721a:2:{i:0;s:24:\"showPopupMemRegBeginTime\";i:1;i:1637643277;}; showPopupMemRegLastTime=dcb2f05f2125f3d00d594301ae640d36674e7e73a689a450f436c87b1a786cb9a:2:{i:0;s:23:\"showPopupMemRegLastTime\";i:1;i:1637643277;}; showPopupMemReg=fbef979f496638a917becd07db77635fbb7ecc3957e8dee12415ec2a2eb41024a:2:{i:0;s:15:\"showPopupMemReg\";i:1;i:1;}; fshare-app="+ BEARER_KEY_2 +"; _gat_gtag_UA_97071061_1=1; _gat_UA-97071061-1=1; _csrf="+ CSRF_2

CSRF_3 = "YhEB7HJGyxaQdJhKd6Kp5J-aiA9vV-7V"
BEARER_KEY_3 = "0b3glgm02o09bh11o9ccuprm6v"
FILE_NAME_3 = "fshare.vn_cookies3.txt"
COOKIE_3 = '_fbp=fb.1.1637416756636.822035357; _ga=GA1.2.780574709.1637416756; _gid=GA1.2.1725019688.1637416756; ajs_group_id=null; fpt_uuid="15cc3bf0-d723-421c-81ca-7dc278b76e56"; _uidcms=1637416755053161666; __gads=ID=0e4cfce35e6f747f-2281df7134cf0088:T=1637416756:RT=1637635837:S=ALNI_MavgVG8wZ18XvH7QvfUTm5jycvuBA; VIP_USER17443112=364ddc37cef322dfb17a9cd96abce91f5a19902046e30724bf1e066c4243e8a2a:2:{i:0;s:16:"VIP_USER17443112";i:1;a:6:{s:13:"timesToAppear";i:99;s:16:"timesToLoadPopUp";i:3;s:8:"dayToday";i:3;s:16:"timeToApearAgain";i:1630631242;s:12:"timeToAppear";i:1630687994;s:4:"show";b:1;}}; __yoid__=5d88082137ad2ee441760bc208a5c7f6; _identity-app=548b9be2965aa9f0702a974ab7f13b0d66558433de06d9ddc249ca3937d31fbea:2:{i:0;s:13:"_identity-app";i:1;s:56:"[17443112,"Jfkh8PhRTiRiv-zqFqqqxrANIV9tzyj3",1637031972]";}; fshare-app='+ BEARER_KEY_3 +'; _ftitfsi=3137343433313132; _gat_gtag_UA_97071061_1=1; _gat_UA-97071061-1=1; _csrf='+ CSRF_3
FILE_NAME = FILE_NAME_2
BEARER_KEY = BEARER_KEY_2
COOKIE_DATA = COOKIE_2

@shared_task
def doFshareFlow(code, server):
    if server == 1:
        FILE_NAME = FILE_NAME_1
        BEARER_KEY = BEARER_KEY_1
        COOKIE_DATA = COOKIE_1
    elif server == 2:
        FILE_NAME = FILE_NAME_2
        BEARER_KEY = BEARER_KEY_2
        COOKIE_DATA = COOKIE_2
    else:
        FILE_NAME = FILE_NAME_3
        BEARER_KEY = BEARER_KEY_3
        COOKIE_DATA = COOKIE_3
    print("do Fshare Download Flow")
    # Opening JSON file
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # url_path = BASE_DIR + '/static/' + FILE_NAME
    # jar = parseCookieFile(url_path)

    myobj = {'linkcode': code, 'clone_to_folder':'/', 'secure': 0}
    print("code" , code, FILE_NAME, BEARER_KEY)
    headers_api = {
        'Authorization': 'Bearer ' + BEARER_KEY,
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': COOKIE_DATA
    }

    resp = requests.post('https://www.fshare.vn/api/v3/downloads/clone-file', data=myobj, headers=headers_api)
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)

    print('downloaded file to my drive')
    # print(resp.headers)
    print(resp.json())
    linkCode = resp.json().get("linkcode")
    if linkCode == None:
        return resp.json()

    # deleteFshareFile.apply_async(kwargs={ "code": linkCode},eta=now() + timedelta(seconds=5*60))
    heartBeating.apply_async(kwargs={ "server": server}, eta=now() + timedelta(seconds=1*30))
    resp = requests.get('https://www.fshare.vn/api/v3/files/download-zip?linkcodes=' + linkCode,  headers=headers_api)
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)

    print('downloaded zip')
    # print(resp.headers)
    print(resp.json())

    return resp.json()

@shared_task
def heartBeating(server):
    print("heartBeating in acc " + str(server))
    if server == 1:
        global startedHeartBeat1
        if startedHeartBeat1 == True:
            return
        startedHeartBeat1 = True
        heartbeat1()
    elif server == 2:
        global startedHeartBeat2
        if startedHeartBeat2 == True:
            return
        startedHeartBeat2 = True
        heartbeat2()
    else:
        global startedHeartBeat3
        if startedHeartBeat3 == True:
            return
        startedHeartBeat3 = True
        heartbeat3()

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
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # url_path = BASE_DIR + '/static/' + FILE_NAME
    # jar = parseCookieFile(url_path)

    myobj = {'files' : [{'linkcode': code}]}
    body = json.dumps(myobj)
    # print("myobj" , myobj)
    headers_api = {
        'Authorization': 'Bearer ' + BEARER_KEY,
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': COOKIE_DATA
    }

    resp = requests.delete('https://www.fshare.vn/api/v3/files/delete-files',  data= body, headers=headers_api)
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



startedHeartBeat1 = False
startedHeartBeat2 = False
startedHeartBeat3 = False

def heartbeat1():

    print("start heart beat thread 1")

    thread = threading.Timer(60.0, heartbeat1)
    thread.start()
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # url_path = BASE_DIR + '/static/' + FILE_NAME
    # jar = parseCookieFile(url_path)

    headers_api = {
        # 'Authorization': 'Bearer ' + BEARER_KEY,
        "referer":"https://www.fshare.vn/file/manager",
        "x-requested-with":'XMLHttpRequest',
        'x-csrf-token':'A-fWA56bvXMQJOrRU1sfop--caYRmhadenW9lApzQ7A334Rhxt_fPVpluZMCPkXL2tce4XKtUfgJRNn5eD8x6Q==',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Cookie': COOKIE_1
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', headers=headers_api)
    isSuccess = resp.json().get("success")
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    if isSuccess != True:
        thread.cancel()
        startedHeartBeat1 = False
        print("cancel thread 1")
    print(resp.json())
    return resp


def heartbeat2():


    thread = threading.Timer(60.0, heartbeat2)
    thread.start()
    print("start heart beat thread 2")
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # url_path = BASE_DIR + '/static/' + FILE_NAME
    # jar = parseCookieFile(url_path)

    headers_api = {
        # 'Authorization': 'Bearer ' + BEARER_KEY,
        "referer":"https://www.fshare.vn/file/manager",
        "x-requested-with":'XMLHttpRequest',
        'x-csrf-token':'A-fWA56bvXMQJOrRU1sfop--caYRmhadenW9lApzQ7A334Rhxt_fPVpluZMCPkXL2tce4XKtUfgJRNn5eD8x6Q==',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Cookie': COOKIE_2
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', headers=headers_api)
    isSuccess = resp.json().get("success")
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    if isSuccess != True:
        thread.cancel()
        startedHeartBeat2 = False
        print("cancel thread 2")
    print(resp.json())
    return resp


def heartbeat3():

    thread = threading.Timer(60.0, heartbeat3)
    thread.start()
    print("start heart beat thread 3")
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # url_path = BASE_DIR + '/static/' + FILE_NAME
    # jar = parseCookieFile(url_path)

    headers_api = {
        # 'Authorization': 'Bearer ' + BEARER_KEY,
        "referer":"https://www.fshare.vn/file/manager",
        "x-requested-with":'XMLHttpRequest',
        'x-csrf-token':'A-fWA56bvXMQJOrRU1sfop--caYRmhadenW9lApzQ7A334Rhxt_fPVpluZMCPkXL2tce4XKtUfgJRNn5eD8x6Q==',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Cookie': COOKIE_3
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', headers=headers_api)
    isSuccess = resp.json().get("success")
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    if isSuccess != True:
        print("cancel thread 3")
        thread.cancel()
        startedHeartBeat3 = False
    print(resp.json())
    return resp
