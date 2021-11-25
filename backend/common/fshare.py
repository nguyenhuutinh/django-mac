import json
import io

from requests.api import head
from lxml import html
import math
import ntpath
import os
import requests


class FS:
    """
    Get link Fshare with your account. If you have VIP, you will get
    premium download link.
    """
    def __init__(self, idenCookie):
        self.idenCookie = idenCookie
        # self.email = email
        # self.password = password
        self.s = requests.Session()
        self.login_url = "https://www.fshare.vn/site/login"
        self.user_agent = (
            "Chrome/59.0.3071.115 Safari/537.36"
        )
        self.folder_api = (
            'https://www.fshare.vn/api/v3/files/'
            'folder?linkcode={}&sort=type,name'
        )
        self.file_url = 'https://www.fshare.vn/file/{}'
        self.media_api = (
            'https://www.fshare.vn/api/v3/files/'
            'download?dl_type=media&linkcode={}'
        )
        self.token = ""
        self.cookies = None

    def get_token(self, response):
        """
        Get csrf token for POST requests.
        """
        tree = html.fromstring(response.content)
        try:
            token = tree.xpath('//*[@name="csrf-token"]')[0].get('content')
            return token
        except IndexError:
            raise Exception('No token for url {}'.format(response.url))
            pass

    def login(self):
        print("login")
        if(self.idenCookie == ""):
            raise Exception("identity Cookie empty")

        self.s.headers.update({'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36", "sec-ch-ua-platform":"macOS","sec-ch-ua-mobile":"?0","sec-ch-ua":"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\""})

        # self.s.headers.update({'Cookie': "fshare-app=qaedt5nfdjpg810vak0cqn4ir7;police=26ef0cc684c5b335d79b6450a596392fbb9928b55c4264ffff05849595c915f9a%3A2%3A%7Bi%3A0%3Bs%3A6%3A%22police%22%3Bi%3A1%3Bi%3A1%3B%7D"})

        # print("login")
        # r = requests.get(self.login_url)
        # print("email" , self.email, self.password)
        # token = self.get_token(r)
        # cookies = r.cookies
        # data = {
        #     '_csrf-app': token,
        #     'LoginForm[email]': self.email,
        #     'LoginForm[password]': self.password,
        #     'LoginForm[rememberMe]': 1,
        # }
        # print("data", data)
        # res = self.s.post(self.login_url, cookies=cookies, data=data)
        print("self.idenCookie", self.idenCookie)
        self.s.cookies.set("_identity-app", self.idenCookie, domain="www.fshare.vn" ,expires=" 3273977798.958045")

        r = self.s.get('https://www.fshare.vn/file/manager')
        print(r.status_code)
        tree = html.fromstring(r.content)
        if tree.xpath('//*[@href="/signup"]'):
            raise Exception('Login failed. Please check your email & password')
        else:
            self.token = self.get_token(r)
            self.cookies = r.cookies
            # print(self.token, self.cookies)
            d = dict();
            d['token'] = self.token
            d['cookies'] = self.cookies
            return d

    def get_media_link(self, media_id):
        """
        Get direct link for video file from your storage account.
        """
        url = self.media_api.format(media_id)

        authorization_code = self.s.cookies.get_dict()['fshare-app']
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.8,vi;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.fshare.vn/file/manager',
            'Connection': 'keep-alive',
            'Host': 'www.fshare.vn',
            'Authorization': 'Bearer {}'.format(authorization_code)
        }

        r = self.s.get(url, headers=headers)

        try:
            link = r.json()
            return link
        except json.decoder.JSONDecodeError:
            print(r.status_code, r.text, self.movie_token, data)
            raise Exception('Get media link failed.')

    def get_link(self, url):
        print("get link")
        if self.is_exist(url):
            token = self.token
            fshareApp = self.cookies.get("fshare-app")
            print(fshareApp, token)
            if fshareApp == None:
                return

            headers = {
                        'User-Agent': self.user_agent,
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.8,vi;q=0.6',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Referer': 'https://www.fshare.vn/file/manager',
                        'Connection': 'keep-alive',
                        'Host': 'www.fshare.vn',
                        'x-csrf-token': token,
                        'Cookie':'fshare-app='+ fshareApp
                    }
            file_id = url.split("/")[-1]
            dl_data = {
                # '_csrf-app': token,
                "fcode5": "0",
                "linkcode": file_id,
                "withFcode5": 0,
            }
            for c in self.cookies:
                print(c.name, c.value)
            print("token", dl_data )

            r = self.s.post("https://www.fshare.vn/download/get",
                            data=dl_data, headers=headers)
            print(r.json())
            # try:
            #     link = r.json()
            #     return link.get('url')
            # except json.decoder.JSONDecodeError:
            #     raise Exception('Get link failed.')
        else:
            return 'aaa'

    def extract_links(self, folder_url):
        """
        Get all links in Fshare folder.
        Return list of all item with info of each.
        """
        folder_id = folder_url.split('/')[-1]
        data = self.s.get(self.folder_api.format(folder_id)).json()

        folder_data = [
            {
                'file_name': d['name'],
                'file_url': self.file_url.format(d['linkcode']),
                'file_size': d['size']
            }
            for d in data['items']
        ]
        return folder_data

    def get_file_name(self, url):
        """
        Strip extra space out of file's name
        """
        r = requests.get(url)
        tree = html.fromstring(r.content)
        file_name = tree.xpath(
            '//*[@property="og:title"]'
        )[0].get('content').split(' - Fshare')[0]
        return file_name

    def get_file_size(self, url):
        """
        Get file size. If not have, return Unknow
        """
        r = requests.get(url)
        tree = html.fromstring(r.content)
        file_size = tree.xpath('//*[@class="size"]/text()')
        if file_size:
            return file_size[1].strip()
        else:
            return 'Unknown'

    def get_folder_name(self, folder_url):
        """
        Get folder name (title)
        """
        r = self.s.get(folder_url)
        tree = html.fromstring(r.content)
        title = tree.xpath('//title/text()')
        if title:
            return title[0].strip('Fshare - ')
        else:
            return r.url

    def is_alive(self, url):
        """
        Check if link is alive.
        """
        r = self.s.head(url, allow_redirects=True)
        if r.status_code == 200:
            return True
        else:
            return False

    def is_exist(self, url):

        r = self.s.get(url, allow_redirects=False)
        if r.status_code == 200:
            tree = html.fromstring(r.content)
            title = tree.xpath('//title/text()')[0]
            if title == 'Not Found - Fshare':
                return False
            else:
                return True
        else:  # In case auto download is enable in account setting
            return True

    def log_out(self):
        self.s.get('https://www.fshare.vn/site/logout')

    def upload_file(self, file_path, secured=0):

        UPLOAD_URL = 'https://www.fshare.vn/api/session/upload'
        file_name = ntpath.basename(file_path)
        file_size = str(os.path.getsize(file_path))
        try:
            data = io.open(file_path, 'rb', buffering=25000000)
        except FileNotFoundError:
            raise Exception('File does not exist!')

        r1 = self.s.get('https://www.fshare.vn/home?upload=1')
        tree = html.fromstring(r1.content)
        token_data = tree.xpath('//*[@class="pull-left breadscum"]')
        if token_data:
            token = token_data[0].get('data-token')
        else:
            raise Exception('Can not get token')

        payload = {'SESSID': dict(self.s.cookies).get('session_id'),
                   'name': file_name,
                   'path': '/',
                   'secured': secured,
                   'size': file_size,
                   'token': token}

        res = self.s.post(UPLOAD_URL, data=json.dumps(payload))
        body = res.json()

        if body.get('code') != 200:
            raise Exception('Initial handshake errors %r', body)

        location = body['location']

        # OPTIONS for chunk upload configuration
        max_chunk_size = 25000000
        chunk_total = math.ceil(int(file_size)/max_chunk_size)

        for i in range(chunk_total):
            chunk_number = i + 1
            sent = last_index = i * max_chunk_size
            remaining = int(file_size) - sent
            if remaining < max_chunk_size:
                current_chunk = remaining
            else:
                current_chunk = max_chunk_size

            next_index = last_index + current_chunk

            chunk_params = {
                'flowChunkNumber': chunk_number,
                'flowChunkSize': max_chunk_size,
                'flowCurrentChunkSize': current_chunk,
                'flowTotalSize': file_size,
                'flowIdentifier': '{0}-{1}'.format(current_chunk, file_name),
                'flowFilename': file_name,
                'flowRelativePath': file_name,
                'flowTotalChunks': chunk_total
            }

            res = self.s.options(location, params=chunk_params)

            # POST upload data
            headers = {
                'Host': 'up.fshare.vn',
                'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.fshare.vn/transfer',
                'Content-Range': 'bytes {0}-{1}/{2}'.format(
                    last_index,
                    next_index - 1,
                    file_size),
                'Content-Length': str(current_chunk),
                'Origin': 'https://www.fshare.vn',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
            res = self.s.post(location,
                              params=chunk_params,
                              headers=headers,
                              data=data.read(max_chunk_size))
            try:
                if res.json():
                    return res.json()
                pass
            except Exception:
                pass
        data.close()
