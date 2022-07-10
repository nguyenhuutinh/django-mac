
# project/tasks/sample_tasks.py

from __future__ import print_function
import urllib
import io
import json
import ntpath
import os
import pprint
import re
import shutil
import threading
import time
from argparse import Namespace
from datetime import datetime, timedelta
from http.cookiejar import MozillaCookieJar
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.utils.timezone import now

import httplib2
import requests
import celery
from celery import shared_task
from common.models import Campaign
# from common.fshare import FS
from common.models import UserFormInfo
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from oauth2client import client, file, tools
from oauth2client.file import Storage
from celery import current_task
from macos import celery_app



@shared_task
def googleSubmitForm(id):

    # print("do submitForm Flow", id)
    userFormInfo = UserFormInfo.objects.select_related("campaign").get(auto_increment_id=id, target_date__lt = datetime.now())
    # print(userFormInfo)
    if userFormInfo is None:
        raise Exception("form is empty")

    if userFormInfo.campaign.status == "ready":
            # print("update status")
            camp = Campaign.objects.get(id= userFormInfo.campaign.id)
            camp.status = "running"
            camp.save()
    if userFormInfo.last_item == True:
            camp = Campaign.objects.get(id= userFormInfo.campaign.id)
            camp.status = "finished"
            camp.save()

    payload=f'entry.1678210758={urllib.parse.quote(userFormInfo.name)}&entry.861103900={userFormInfo.email}&entry.342149314={userFormInfo.phone}&entry.1552925985={userFormInfo.lucky_number}&entry.1416255078={urllib.parse.quote(userFormInfo.age)}&entry.306010364={urllib.parse.quote(userFormInfo.gender)}&partialResponse=[null,null,"-6707872070833591597"]&pageHistory=0&fbzx=-6707872070833591597&fvv=1'

    # print(payload)
    headers = {
        'User-Agent':'PostmanRuntime/7.29.0',
        'X-Appengine-Default-Namespace':'gmail.com',
        'X-Appengine-Country':'VN',
        'X-Appengine-City':'ho chi minh city',
        'Content-Type': 'application/x-www-form-urlencoded',

    }

    resp = requests.post('https://docs.google.com/forms/u/0/d/e/1FAIpQLSePhwWx1wb56QYDKR8cWlAMcq52bbkHakSeAjXi1b2KWM45PA/formResponse', data=payload.encode("utf-8"), headers=headers)
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)

    print(f'submitted form {userFormInfo.name} - {userFormInfo.phone} with result {resp.status_code}')
    UserFormInfo.objects.filter(auto_increment_id=id).update(sent_status = f"{resp.status_code}",  sent = True, sent_date= datetime.now(), sent_date_time= datetime.now(), sent_time= datetime.now())

    # print(resp.headers)
    # print(resp.content)
    # linkCode = resp.json().get("linkcode")
    # if linkCode == None:
    #     return resp.json()

    # # deleteFshareFile.apply_async(kwargs={ "code": linkCode},eta=now() + timedelta(seconds=5*60))
    # # heartBeating.apply_async(kwargs={ "server": server}, eta=now() + timedelta(seconds=1*30))
    # resp = requests.get('https://www.fshare.vn/api/v3/files/download-zip?linkcodes=' + linkCode,  headers=headers_api)
    # # print(resp.request.url)
    # # print(resp.request.body)
    # # print(resp.request.headers)

    # print('downloaded zip')
    # # print(resp.headers)
    # print(resp.json())

    return

