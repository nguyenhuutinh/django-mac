
# project/tasks/sample_tasks.py

from __future__ import print_function
import time
from argparse import Namespace
from bs4 import BeautifulSoup
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

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36\", \"sec-ch-ua-platform\":\"macOS\",\"sec-ch-ua-mobile\":\"?0\",\"sec-ch-ua\":\"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",

def checkVariable(server):
    fshareI  = FS(server)
    tokenInfo = fshareI.readCookieDB()
    if(tokenInfo == None):
        res = doLoginAgain(server)
        if res == None:
            raise Exception("error login")
        else:
            return res
    else:
        return tokenInfo
@shared_task
def doFshareFlow2(code, server):
    print("doFshareFlow2")
    tokenInfo = checkVariable(server)
    if tokenInfo is None:
        raise Exception("token is empty")
    cookie_share_app = getattr(tokenInfo,"cookie_share_app")
    cookie_csrf = getattr(tokenInfo,"cookie_csrf")
    print("token info: ", cookie_csrf, cookie_share_app)

    heartBeating.apply_async(kwargs={ "server": server,'csrf': cookie_csrf, 'app': cookie_share_app}, eta=now() + timedelta(seconds=1*10))

    myobj = {'linkcode': code, 'withFcode5':0}
    headers_api = {
        'User-Agent': USER_AGENT,
        'x-csrf-token': cookie_csrf,
        'Cookie':'fshare-app=' + cookie_share_app
    }
    # print(COOKIE_DATA, TOKEN_KEY)
    resp = requests.post('https://www.fshare.vn/download/get',data = myobj, headers=headers_api)
    print("get file status code: ", resp.status_code)
    if resp.status_code == 200:

        response = resp.json().get("url")
        print("get file response", response,  resp.json())
        return response
    else :
        return

@shared_task
def heartBeating(server, csrf, app ):
    print("heartBeating in acc " + str(server),csrf, app )
    if server == 1:
        global startedHeartBeat1
        if startedHeartBeat1 == True:
            return
        startedHeartBeat1 = True
        heartbeat1(csrf, app)
    elif server == 2:
        global startedHeartBeat2
        if startedHeartBeat2 == True:
            return
        startedHeartBeat2 = True
        heartbeat2(csrf, app)
    else:
        global startedHeartBeat3
        if startedHeartBeat3 == True:
            return
        startedHeartBeat3 = True
        heartbeat3(csrf, app)

# @shared_task
# def deleteFshareFile(code):
#     # credentials = get_credentials()
#     # http = credentials.authorize(httplib2.Http())
#     # service = build('drive', 'v3', http=http)
#     # response = service.files().update(fileId=task_id, addParents= STORE_DRIVE_ID,
#     # removeParents= SOURCE_DRIVE_ID,
#     # fields= 'id, parents'
#     # ).execute()

#     print("deleteFshareFile : "+ code)
#     # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     # url_path = BASE_DIR + '/static/' + FILE_NAME
#     # jar = parseCookieFile(url_path)

#     myobj = {'files' : [{'linkcode': code}]}
#     body = json.dumps(myobj)
#     # print("myobj" , myobj)
#     headers_api = {
#         'Authorization': 'Bearer ' + BEARER_KEY,
#         'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "sec-ch-ua-platform":"macOS","sec-ch-ua-mobile":"?0","sec-ch-ua":"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
#         'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
#         'Cookie': COOKIE_DATA
#     }

#     resp = requests.delete('https://www.fshare.vn/api/v3/files/delete-files',  data= body, headers=headers_api)
#     # print(resp.request.url)
#     # print(resp.request.body)
#     # print(resp.request.headers)
#     print(resp.json())
#     return resp

# def parseCookieFile(cookiefile):
#     cookies = Path(cookiefile)

#     jar = MozillaCookieJar(cookies)
#     jar.load()
#     # print(jar)
#     return jar



startedHeartBeat1 = False
startedHeartBeat2 = False
startedHeartBeat3 = False

def heartbeat1(csrf, app):

    global startedHeartBeat1
    if(csrf == ""):
        return
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
        'x-csrf-token':csrf,
        'Cookie':'fshare-app='+ app,
        'User-Agent': USER_AGENT
        # 'Cookie': COOKIE_1
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
        doLoginAgain(1)

    print(resp.json())
    return resp


def heartbeat2(csrf, app):

    global startedHeartBeat2
    print("heartbeat2", csrf)
    if(csrf == ""):
        return
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
        'x-csrf-token':csrf,
        'Cookie':'fshare-app=' + app,
        'User-Agent': USER_AGENT
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth',  headers=headers_api)
    isSuccess = resp.json().get("success")
    print("heartbeat2 result",resp.status_code, resp.content)
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    if isSuccess != True:
        thread.cancel()
        startedHeartBeat2 = False
        checkVariable(2)
        print("cancel thread 2")
    print(resp.json())
    return resp


def heartbeat3(csrf, app):


    global startedHeartBeat3
    if(csrf == ""):
        return
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
        'x-csrf-token':csrf,
        'Cookie':'fshare-app=' + app,
        'User-Agent': USER_AGENT,
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', headers=headers_api)
    isSuccess = resp.json().get("success")
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    if isSuccess != True:
        print("cancel thread 3")
        thread.cancel()
        doLoginAgain(3)
        startedHeartBeat3 = False
    print(resp.json())
    return resp


def doLoginAgain(server):
    fshareI  = FS(server)
    return fshareI.login()
