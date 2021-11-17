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
import requests

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



@shared_task
def download_task(file_id):
    print(file_id)
    file_name = downloadFile(file_id)
    response = upload_task.apply(kwargs={"file_name":file_name})
    print("response ---")
    print(response.result)
    return response.result


@shared_task
def upload_task(file_name):
   print("upload_task : "+file_name)
   fileId = uploadFile(file_name)
   print("fileId : "+ fileId)
   delete_task.apply_async(kwargs={"task_id":fileId, "file_name": file_name},eta=now() + timedelta(seconds=60))
   return fileId
@shared_task
def delete_task(task_id, file_name):
    print("delete_task : "+task_id)
    response = deleteFile(task_id, file_name)
    return response


SCOPES = "https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.appdata"
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Upload2Drive'

def get_credentials():
    args = Namespace(noauth_local_webserver= 'false',
                         logging_level='ERROR')
    credential_dir = os.getcwd()
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                'drive_credential.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, args)
        print('Storing credentials to ' + credential_path)
    return credentials

def uploadFile(file_name):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v3', http=http)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/'

    mFile = url_path + file_name
    chunk_size = 10
    if os.name == "posix":
        filename = os.path.basename(mFile)
    else:
        if os.name == "nt":
            filename = ntpath.basename(mFile)
    gdrive_id = ""
    if gdrive_id != "":
        file_metadata = {'name': filename,
                        'parents': [gdrive_id]
                        }
    else:
        file_metadata = {'name': filename}

    media = MediaFileUpload(mFile,
                            chunksize=int(chunk_size)*1024*1024,
                            resumable=True)
    request = service.files().create(body=file_metadata,
                                    media_body=media,
                                    )
    response = None
    i = 1
    starttime = datetime.now()
    while response is None:
        # print("aaaa")
        status, response = request.next_chunk()
        # print(response)
        if status:
            progresstime = datetime.now()
            print("%d %s Uploaded %d%%." %
                (i, (progresstime - starttime), int(status.progress() * 100)))
            i = i+1
    stoptime = datetime.now()
    filesize = os.path.getsize(mFile)
    print("File %s Size %.2f MB Duration %s " %
        (filename, float(filesize/(1000*1000)), (stoptime - starttime)))
    print("Upload Complete!")


    file_id = response["id"]
    print(file_id)
    batch = service.new_batch_http_request()
    user_permission = {
        'type': 'anyone',
        'role': 'reader',
        'value': 'default',
    }
    batch.add(service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
    ))
    domain_permission = {
        'type': 'domain',
        'role': 'reader',
        'domain': 'example.com'
    }
    batch.add(service.permissions().create(
            fileId= file_id,
            body=domain_permission,
            fields='id',
    ))
    batch.execute()
    # deleteFile(response.id)
    return file_id

def deleteFile(fileID, fileName):
    print("delete" + fileID)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v3', http=http)
    file = service.files().delete(fileId=fileID).execute()
    print("deleted" + file)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/' + fileName
    os.remove(url_path)
    print("deleted" + url_path )
    return file



def downloadFile(file_id):

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v3', http=http)

    data = service.files().get(fileId=file_id, fields='name,mimeType').execute()
    file_name = data["name"]
    mimeType = data["mimeType"]

    # print(data)

    req = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, req)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%" % int(status.progress() * 100))
    # print(file_name)
    # The file has been downloaded into RAM, now save it in a file
    fh.seek(0)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/'

    mFile = url_path + file_name
    print(mFile)
    with open(mFile, 'wb') as f:
        shutil.copyfileobj(fh, f, length=131072)
    return file_name

