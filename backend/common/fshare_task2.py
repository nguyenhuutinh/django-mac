
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

from common.models import DownloadInfo
ID_COOKIE_1 = "59c108aa4c43567619a72dc33330726179d26678b721b33c78e3ee75cefe1181a%3A2%3A%7Bi%3A0%3Bs%3A13%3A%22_identity-app%22%3Bi%3A1%3Bs%3A56%3A%22%5B17968929%2C%22Zb5Y1cu3jmvTbCq76URkunJU_rfe6Ij9%22%2C1634889338%5D%22%3B%7D"
TOKEN_KEY_1 = ""
COOKIE_1 = ""

ID_COOKIE_2 = "811fca809ca392717e052e50701d47aa9a84e0e83b20958544912aeb49599493a%3A2%3A%7Bi%3A0%3Bs%3A13%3A%22_identity-app%22%3Bi%3A1%3Bs%3A55%3A%22%5B6565416%2C%22HRTqYQSx0tOWmSo9tbqX7IZc8tTBjbOg%22%2C1637910010%5D%22%3B%7D"
TOKEN_KEY_2 = ""
COOKIE_2 = ""

ID_COOKIE_3 = "811fca809ca392717e052e50701d47aa9a84e0e83b20958544912aeb49599493a%3A2%3A%7Bi%3A0%3Bs%3A13%3A%22_identity-app%22%3Bi%3A1%3Bs%3A55%3A%22%5B6565416%2C%22HRTqYQSx0tOWmSo9tbqX7IZc8tTBjbOg%22%2C1637910010%5D%22%3B%7D"
TOKEN_KEY_3 = ""
COOKIE_3 = ""

TOKEN_KEY = TOKEN_KEY_2
COOKIE_DATA = COOKIE_2


def checkVariable(server):
    global TOKEN_KEY_1,COOKIE_1, COOKIE_DATA, TOKEN_KEY,TOKEN_KEY_2, COOKIE_2,TOKEN_KEY_3,COOKIE_3, ID_COOKIE_1, ID_COOKIE_2, ID_COOKIE_3

    if server == 1:
        if(TOKEN_KEY_1 == ""):
            res = doLoginAgain(ID_COOKIE_1)
            if res:
                TOKEN_KEY_1 = res.get("token")
                COOKIE_1 = res.get("cookies")

            else:
                raise Exception("error login")
        COOKIE_DATA = COOKIE_1
        TOKEN_KEY = TOKEN_KEY_1

    elif server == 2:

        if(TOKEN_KEY_2 == ""):
            res = doLoginAgain(ID_COOKIE_2)
            print(res)
            if res:
                TOKEN_KEY_2 = res.get("token")
                COOKIE_2 = res.get("cookies")

            else:
                raise Exception("error login")
        COOKIE_DATA = COOKIE_2
        TOKEN_KEY = TOKEN_KEY_2
    else:

        if(TOKEN_KEY_3 == ""):
            res = doLoginAgain(ID_COOKIE_3)
            if res:
                TOKEN_KEY_3 = res("token")
                COOKIE_3 = res("cookies")

            else:
                raise Exception("error login")
        COOKIE_DATA = COOKIE_3
        TOKEN_KEY = TOKEN_KEY_3

@shared_task
def doFshareFlow2(code, server):
    print("doFshareFlow2")
    checkVariable(server)
    global  COOKIE_DATA, TOKEN_KEY

    # print(COOKIE_DATA, TOKEN_KEY)



    myobj = {'linkcode': code, 'withFcode5':0}
    headers_api = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "sec-ch-ua-platform":"macOS","sec-ch-ua-mobile":"?0","sec-ch-ua":"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
        'x-csrf-token': TOKEN_KEY
    }
    # print(COOKIE_DATA, TOKEN_KEY)
    resp = requests.post('https://www.fshare.vn/download/get',data = myobj, cookies=COOKIE_DATA, headers=headers_api)
    print("get file status code: ", resp.status_code)
    if resp.status_code == 200:

        response = resp.json().get("url")
        print("get file response", response,  resp.json())
        return response
    else :
        return

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
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "sec-ch-ua-platform":"macOS","sec-ch-ua-mobile":"?0","sec-ch-ua":"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
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
    global startedHeartBeat1
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
        'x-csrf-token':TOKEN_KEY_1,
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "sec-ch-ua-platform":"macOS","sec-ch-ua-mobile":"?0","sec-ch-ua":"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
        # 'Cookie': COOKIE_1
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', cookies=COOKIE_1, headers=headers_api)
    isSuccess = resp.json().get("success")
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    if isSuccess != True:
        thread.cancel()
        startedHeartBeat1 = False
        print("cancel thread 1")
        doLoginAgain(ID_COOKIE_1)

    print(resp.json())
    return resp


def heartbeat2():

    global startedHeartBeat2,TOKEN_KEY_2
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
        'x-csrf-token':TOKEN_KEY_2,
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "sec-ch-ua-platform":"macOS","sec-ch-ua-mobile":"?0","sec-ch-ua":"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\""
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', cookies=COOKIE_2, headers=headers_api)
    isSuccess = resp.json().get("success")
    print("heartbeat2 result",resp.status_code, resp.content)
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    if isSuccess != True:
        thread.cancel()
        startedHeartBeat2 = False
        TOKEN_KEY_2 = ""
        checkVariable(2)
        print("cancel thread 2")
    print(resp.json())
    return resp


def heartbeat3():
    global startedHeartBeat3, TOKEN_KEY_1
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
        'x-csrf-token':TOKEN_KEY_3,
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "sec-ch-ua-platform":"macOS","sec-ch-ua-mobile":"?0","sec-ch-ua":"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
    }

    resp = requests.get('https://www.fshare.vn/site/motion-auth', cookies=COOKIE_3, headers=headers_api)
    isSuccess = resp.json().get("success")
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)
    if isSuccess != True:
        print("cancel thread 3")
        thread.cancel()
        TOKEN_KEY_1 = ""
        checkVariable(3)
        startedHeartBeat3 = False
    print(resp.json())
    return resp


def doLoginAgain(idCookie):
    fshareI  = FS(idCookie)
    return fshareI.login()
