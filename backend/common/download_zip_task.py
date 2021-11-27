
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
from common.fshare import FS

from common.models import TokenInfo



def doLoginAgain(server):
    fshareI  = FS(server)
    return fshareI.login()

def checkVariable(server,password):
    fshareI  = FS(server)
    tokenInfo = fshareI.readCookieDB()
    if(password == None or password == ""):
        res = doLoginAgain(server)
        if res == None:
            raise Exception("error login")
        else:
            return res

    if(tokenInfo == None):
        res = doLoginAgain(server)
        if res == None:
            raise Exception("error login")
        else:
            return res
    else:
        return tokenInfo

@shared_task
def downloadZipFShare(code, server, password, token):

    print("do downloadZipFShare Flow", code, server, password, token)
    # Opening JSON file
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # url_path = BASE_DIR + '/static/' + FILE_NAME
    # jar = parseCookieFile(url_path)
    tokenInfo = checkVariable(server,password)
    if tokenInfo is None:
        raise Exception("token is empty")

    cookie_share_app = getattr(tokenInfo,"cookie_share_app")
    cookie_csrf = getattr(tokenInfo,"cookie_csrf")

    myobj = {'linkcode': code, 'clone_to_folder':'/', 'secure': 0}
    # print("code" , code, FILE_NAME, BEARER_KEY)
    headers_api = {
        'Authorization': 'Bearer ' + cookie_share_app,
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Cookie': COOKIE_DATA
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
    # heartBeating.apply_async(kwargs={ "server": server}, eta=now() + timedelta(seconds=1*30))
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
    if int(server) == 1:
        global startedHeartBeat1
        if startedHeartBeat1 == True:
            return
        startedHeartBeat1 = True
        heartbeat1()
    elif int(server) == 2:
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
