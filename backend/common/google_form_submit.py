
# project/tasks/sample_tasks.py

from __future__ import print_function
from time import sleep
import urllib
from django.db.models import Count

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
from common.models import GoogleFormInfo
from common.models import GoogleFormField
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
def lockForm(id):
    forms = UserFormInfo.objects.get(auto_increment_id=id)

    if forms is None:
        raise Exception("form is empty")

    forms.status = "queued"
    forms.save()

    sleep(5)

    # print("do submitForm Flow", id)

    # print(userFormInfo)


    forms.status = ""
    forms.save()

@shared_task
def googleSubmitForm(id):

    # print("do submitForm Flow", id)
    forms = UserFormInfo.objects.select_related("campaign").get(auto_increment_id=id)
    # print(userFormInfo)
    if forms is None:
        raise Exception("form is empty")

    if forms.campaign.status == "ready":
            # print("update status")
            camp = Campaign.objects.get(id= forms.campaign.id)
            camp.status = "running"
            camp.save()
    if forms.auto_increment_id == forms.campaign.last_item_id:
            camp = Campaign.objects.get(id= forms.campaign.id)
            camp.status = "finished"
            camp.save()


    googleFormInfo = GoogleFormInfo.objects.get(campaign_id = forms.campaign.id)
    print(googleFormInfo)
    fields = GoogleFormField.objects.filter(google_form_id= googleFormInfo.id, campaign_id = forms.campaign.id).order_by("key_index")
    print(fields)
    payload = ''
    index = 1
    if forms.field1 == "" and forms.field2 == "":
        raise Exception("data is empty")
    for field in fields:
        if(index == 1):
            payload = payload + f'{field.key_name}={urllib.parse.quote(forms.field1)}'
        if(index == 2):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field2)}'
        if(index == 3):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field3)}'
        if(index == 4):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field4)}'
        if(index == 5):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field5)}'
        if(index == 6):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field6)}'
        if(index == 7):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field7)}'
        if(index == 8):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field8)}'
        if(index == 9):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field9)}'
        if(index == 10):
            payload = payload + f'&{field.key_name}={urllib.parse.quote(forms.field10)}'
        index = index + 1
    payload = payload + f'&{"fvv"}={urllib.parse.quote(googleFormInfo.fvv)}' + f'&{"pageHistory"}={urllib.parse.quote(googleFormInfo.page_history)}' + f'&{"fbzx"}={urllib.parse.quote(googleFormInfo.fbzx)}' + f'&{"partialResponse"}={urllib.parse.quote(googleFormInfo.partial_response)}'
    print(payload)

    # print(payload)
    headers = {
        'User-Agent':'PostmanRuntime/7.29.0',
        'X-Appengine-Default-Namespace':'gmail.com',
        'X-Appengine-Country':'VN',
        'X-Appengine-City':'ho chi minh city',
        'Content-Type': 'application/x-www-form-urlencoded',

    }

    resp = requests.post(googleFormInfo.action_link, data=payload.encode("utf-8"), headers=headers)
    # print(resp.request.url)
    # print(resp.request.body)
    # print(resp.request.headers)

    print(f'submitted form {forms.field1} - {forms.field2} with result {resp.status_code}')
    UserFormInfo.objects.filter(auto_increment_id=id).update(sent_status = f"{resp.status_code}",  sent = True, sent_date= datetime.now(), sent_date_time= datetime.now(), sent_time= datetime.now())
    try:
        numberSent = UserFormInfo.objects.filter(sent=True)
        print(len(numberSent))
        camp = Campaign.objects.get(id= forms.campaign.id)
        camp.completed_forms = len(numberSent)
        if camp.total_forms == 0:
            camp.total_forms = camp.total_schedules
        camp.save()
    except:
        print("error ")
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

