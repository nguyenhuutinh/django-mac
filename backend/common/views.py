from django.views import generic
from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils.timezone import now
import pprint
from http.cookiejar import MozillaCookieJar
from pathlib import Path

import os
import re
import requests

from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult

from common.upload_task import upload_task

from common.upload_task import download_task
import jsons
import json
from common.upload_task import doDownloadFlow



from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny



class IndexView(generic.TemplateView):
    template_name = 'common/index.html'


class RestViewSet(viewsets.ViewSet):
    # @action(
    #     detail=False,
    #     methods=['post'],
    #     permission_classes=[AllowAny],
    #     url_path='rest-check',
    # )
    # @csrf_exempt
    # def rest_check(self, request):
    #     print("ooo")
    #     return Response(
    #         {"result": "If you're seeing this, the REST API is working!"},
    #         status=status.HTTP_200_OK,
    #     )
    # def home(request):
    #     return render(request, "home.html")

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='run-task',
    )
    @csrf_exempt
    def run_task(self, request):
        ip = get_client_ip(request)
        print(ip)
        body_unicode = request.body.decode('utf-8')
        body = jsons.loads(body_unicode)

        try:
            file_slug = body['file_slug']
        except:
            return JsonResponse({"error_message": "file is not exist" }, status=400)
        print(file_slug)
        task = doDownloadFlow.apply(kwargs={"file_slug":file_slug, "ip" : ip})
        print("doDownloadFlow done", task)
        result = task.result
        if(type(result) == str and result.startswith("error")):
            return JsonResponse({"result": result }, status=400)
        else:
            # task_result = AsyncResult(task.id)
            # print(task_result.result)
            downloadLink = 'https://drive.google.com/uc?id={}&export=download'.format(task.result)
            # task_id = task.info["id"]
            print("downloadLink")
            print(downloadLink)
            return JsonResponse({"result": downloadLink }, status=200)



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


    # @csrf_exempt
    # def get_status(request, task_id):
    #     task_result = AsyncResult(task_id)
    #     result = {
    #         "task_id": task_id,
    #         "task_status": task_result.status,
    #         "task_result": task_result..
    #     }
    #     return JsonResponse(result, status=200)




class AuthViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='rest_check',
    )
    @csrf_exempt
    def rest_check(self, request):
        # Opening JSON file
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        url_path = BASE_DIR + '/static/' + "fshare.vn_cookies.txt"
        jar = parseCookieFile(url_path)

        myobj = {'linkcode': 'DUUINH64UOH7', 'clone_to_folder':'/', 'secure': 0}
        print("ooo")
        headers_api = {
            'Authorization': 'Bearer ' + "jcrnprtt0l9vlt10p0ous2a6d9",
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
        }

        resp = requests.post('https://www.fshare.vn/api/v3/downloads/clone-file', cookies=jar, data=myobj, headers=headers_api)
        print(resp.request.url)
        print(resp.request.body)
        print(resp.request.headers)

        print('aaaaaaaaaa')
        print(resp.headers)
        linkCode = resp.json().get("linkcode")
        if linkCode == None:
            return  Response(
            {"result": "Error 400 - Cannot download File"},
            status=status.HTTP_400_BAD_REQUEST,
        )

        resp = requests.get('https://www.fshare.vn/api/v3/files/download-zip?linkcodes=' + linkCode, cookies=jar, headers=headers_api)
        print(resp.request.url)
        print(resp.request.body)
        print(resp.request.headers)

        print('bbbbbbbbbb')
        print(resp.headers)
        print(resp.json())


        return Response(
            {"result": resp.json()},
            status=status.HTTP_200_OK,
        )
    def home(request):
        return render(request, "home.html")





def parseCookieFile(cookiefile):
    cookies = Path(cookiefile)

    jar = MozillaCookieJar(cookies)
    jar.load()
    # print(jar)
    return jar

