
# # project/tasks/sample_tasks.py

# from __future__ import print_function
# import time

# import json
# import hashlib
# import hmac
# import time
# import urllib
# import json
# from django.http import JsonResponse
# from oauth2client import file
# import requests
# import pprint
# from http.cookiejar import MozillaCookieJar
# from pathlib import Path

# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

# from oauth2client import client
# from oauth2client import tools
# from oauth2client.file import Storage
# from celery import shared_task
# from django.conf import settings
# from datetime import datetime, timedelta
# from django.utils.timezone import now
# from googleapiclient.http import MediaIoBaseDownload
# from common.fshare import FS

# from common.models import TokenInfo

# USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
# AUTH_TYPE = dict(basic=1, hmac=2)
# BASE_HOST = 'https://api.adf.ly'
# SECRET_KEY = '09d4a92a-31d7-48a4-9004-8706628aa412'
# PUBLIC_KEY = '205d65914822b88e5a4961e8617d8c18'
# USER_ID = 8422497
# @shared_task
# def shorten(url):
#     print("shorten", url)

#     data = {"_user_id": USER_ID, "_api_key": PUBLIC_KEY, "url": url}

#     print("data", data)
#     headers_api = {
#         'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
#     }

#     response = requests.post(
#             BASE_HOST+ '/v1/shorten',
#             data= data, headers=headers_api)
#     if(response.status_code == 200):
#         res = response.json().get("data")[0].get("short_url")
#         # print(res)
#         return res
#     else :
#         err = response.json().get("errors")[0].get("msg")
#         print(err)
#         return err




# def _get_params(params={}, auth_type=None):
#     """Populates request parameters with required parameters,
#     such as _user_id, _api_key, etc.
#     """
#     auth_type = auth_type or AUTH_TYPE['basic']

#     params['_user_id'] = USER_ID
#     params['_api_key'] = PUBLIC_KEY

#     if AUTH_TYPE['basic'] == auth_type:
#         pass
#     elif AUTH_TYPE['hmac'] == auth_type:
#         # Get current unix timestamp (UTC time).
#         params['_timestamp'] = int(time.time())
#         params['_hash'] = _do_hmac(params)
#     else:
#         raise RuntimeError

#     return params

# def _do_hmac(params):
#     if type(params) != dict:
#         raise RuntimeError

#     # Get parameter names.
#     keys = params.keys()
#     # Sort them using byte ordering.
#     # So 'param[10]' comes before 'param[2]'.
#     keys.sort()
#     queryParts = []

#     # Url encode query string. The encoding should be performed
#     # per RFC 1738 (http://www.faqs.org/rfcs/rfc1738)
#     # which implies that spaces are encoded as plus (+) signs.
#     for key in keys:
#         quoted_key = urllib.quote_plus(str(key))
#         if params[key] is None:
#             params[key] = ''

#         quoted_value = urllib.quote_plus(str(params[key]))
#         queryParts.append('%s=%s' % (quoted_key, quoted_value))

#     return hmac.new(
#         SECRET_KEY,
#         '&'.join(queryParts),
#         hashlib.sha256).hexdigest()

