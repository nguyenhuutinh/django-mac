# project/tasks/sample_tasks.py

from __future__ import print_function
import time
from argparse import Namespace

import httplib2
import os
import ntpath
import datetime
import json

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from celery import shared_task


@shared_task
def create_task(task_type):
   response = mainFunction()
   return response
@shared_task
def delete_task(task_id):
    print(task_id)
    response = deleteFile(task_id)
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

def mainFunction():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v3', http=http)
    mFile = "/static/test.apk"
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
    starttime = datetime.datetime.now()
    while response is None:
        print("aaaa")
        status, response = request.next_chunk()
        # print(response)
        if status:
            progresstime = datetime.datetime.now()
            print("%d %s Uploaded %d%%." %
                (i, (progresstime - starttime), int(status.progress() * 100)))
            i = i+1
    stoptime = datetime.datetime.now()
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
    return response

def deleteFile(fileID):
    print("delete" + fileID)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v3', http=http)
    file = service.files().delete(fileId=fileID).execute()
    print("deleted" + file)
    return file

