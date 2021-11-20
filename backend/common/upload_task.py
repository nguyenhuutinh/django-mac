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
from oauth2client import file
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

from common.models import DownloadInfo

STORE_DRIVE_ID = "1otrYJJbA92reDpUEKEwq3yCu3dbosfki"
SOURCE_DRIVE_ID = "1HKWPUhH2ldoQ5tdkxaj-3jBmZtSy9PHQ"
def contains(list, filter):
    for x in list:
        if filter(x):
            return x
    return

def resolveFileSlug(file_slug):
    print("resolveFileSlug: " + file_slug)
    response = requests.get('https://cmacdrive.com/wp-json/wp/v2/posts?slug=' + file_slug)
    if(response.status_code == 200):
        print(response.json())
        try:
            file_name = response.json()[0].get("acf").get("file_name")
            print(file_name)
            return file_name
        except:
            return

    else:
        return




def checkIfFileIsExist(fileName, fileId, folderId):

    print("checkIfFileIsExist " + fileName + " in "+ folderId)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v3', http=http)
    items = []
    pageToken = ""
    while pageToken is not None:
        response = service.files().list(q="'" + folderId + "' in parents", pageSize=1000, pageToken=pageToken, fields="nextPageToken, files(id, name)").execute()
        items.extend(response.get('files', []))
        pageToken = response.get('nextPageToken')
    print("items" , items)
    account = contains(items, lambda x: x["name"] == fileName)
    print("account", account)
    if(account):
        return account["id"]

    return

@shared_task
def doDownloadFlow(file_slug, ip):
    print("do Download Flow")
    file_name = resolveFileSlug(file_slug)

    if file_name == None:
        return "error: file not found (100)"
    else:
        print("resolved file_name: " + file_name)
        file_id = checkIfFileIsExist(file_name, "", STORE_DRIVE_ID)
        print("file_id", file_id)
        if file_id:
            return file_id
        else :
            file_id = checkIfFileIsExist(file_name, "", SOURCE_DRIVE_ID)
            if(file_id):
                return copy_file.apply(kwargs={"file_id":file_id, "ip": ip, "file_name" : file_name},)
                # return download_task.apply(kwargs={"file_id":file_id, "ip": ip},)
            else :
                return "error: file not found (101)"


@shared_task
def copy_file(file_id, ip, file_name):
    print("copy_file" + file_id +"," + file_name)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v3', http=http)

    newfile = {'title': file_name, 'parents' : [ { "id" : STORE_DRIVE_ID } ]}
    response = service.files().copy(fileId=file_id, body=newfile).execute()
    print("response", response)
    return response["id"]
@shared_task
def download_task(file_id, ip):

    print("download_task",file_id)
    update_values = {"file_id": file_id, "client_ip": ip, "download_count": 1}

    downloadInfo, created = DownloadInfo.objects.get_or_create(file_id=file_id, defaults =update_values)
    if created:
        print("created")
    else :
        print(getattr(downloadInfo,"download_count"))
        newCount = int(getattr(downloadInfo,"download_count")) + 1
        newIP = getattr(downloadInfo,"client_ip") + ", " + ip
        downloadInfo.download_count = newCount
        downloadInfo.client_ip = newIP

        downloadInfo.save(update_fields=['download_count', "client_ip"])
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
   delete_task.apply_async(kwargs={"task_id":fileId, "file_name": file_name},eta=now() + timedelta(seconds=60*60))
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
    gdrive_id = STORE_DRIVE_ID
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
    if(os.path.exists(url_path)):
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
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url_path = BASE_DIR + '/static/' + file_name
    req = service.files().get_media(fileId=file_id)
    fh = io.FileIO(url_path, 'wb')
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

