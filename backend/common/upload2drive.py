from __future__ import print_function
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
"""
Developer: Kanakorn Horsiritham
Organization: Computer Center, Prince of Songkla University
Base Code: Python Quickstart
	   https://developers.google.com/drive/v3/web/quickstart/python
"""

# try:
#     import argparse
#     parser = argparse.ArgumentParser(parents=[tools.argparser],
#                                      description="Upload File to Google Drive",
#                                      epilog="Remind to put your Client Secret into the same directory and named it client_secret.json")
#     parser.add_argument("--file", help="File to Upload", required=True)
#     parser.add_argument(
#         "--gdrive-id", help="Destination Google Drive Folder ID", default="1eWANx6KQ89GJk8Hu_hhy3uKZNW6RZzsy")
#     parser.add_argument("--chunk-size", help="Chunk Size in MB", default=20)
#     args = parser.parse_args()

# except ImportError:
#     args = None

SCOPES = "https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.appdata"
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Upload2Drive'

class Upload2Drive:

    def get_credentials():
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
            if args:
                credentials = tools.run_flow(flow, store, args)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials


    def main():
        credentials = Upload2Drive.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = build('drive', 'v3', http=http)
        mFile = "/Users/nguyenhuutinh/Downloads/webOS_SDK_TV_Installer_mac64_full.zip"
        chunk_size = 10
        if os.name == "posix":
            filename = os.path.basename(mFile)
        else:
            if os.name == "nt":
                filename = ntpath.basename(mFile)
        gdrive_id = "1eWANx6KQ89GJk8Hu_hhy3uKZNW6RZzsy"
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
    

