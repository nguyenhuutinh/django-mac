from django.views import generic
from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils.timezone import now
import pprint
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from rest_captcha import VERSION

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

from common.fshare_task import doFshareFlow
from common.fshare_task2 import doFshareFlow2
from common.fshare_task2 import heartBeating

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from common.captcha import RestCaptchaSerializer
from macos.settings import base

cache_template = base.REST_CAPTCHA["CAPTCHA_CACHE_KEY"]

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
    serializer_class = RestCaptchaSerializer

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='rest_check',
    )
    @csrf_exempt
    def rest_check(self, request):
        try:
            code = request.data['code']
            server = request.data['server']
        except:
            return JsonResponse({"error_message": "fshare code is not exist" }, status=400)
        print(code, server)

        res = doFshareFlow.apply(kwargs={"code":code, "server": server})
        print("res", res.result)
        if res :
            return Response(
                {"result": res.result},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"result": "error"},
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='download_direct',
    )
    @csrf_exempt
    def download_direct(self, request):
        print("download_direct")
        try:
            code = request.data.get('code')
            server = request.data.get('server')
            password = request.data.get('password')
            token = request.data.get('token')
            capchaKey = request.data.get('captcha_key')
            capchaValue = request.data.get('captcha_value')
        except:
            return JsonResponse({"error_message": "fshare code is not exist" }, status=400)



        data = dict(captcha_key=capchaKey, captcha_value= capchaValue)
        serial = RestCaptchaSerializer(data=data)
        key = get_cache_key(capchaValue)
        value = cache.get(capchaKey)
        print(key, value)
        print(code, server, password, token)
        print(capchaKey, capchaValue,serial.is_valid())
        # if serial.is_valid() == False:
        #     return Response(
        #                     {"result": "captcha hết hạn hoặc không đúng. vui lòng thử lại"},
        #                     status=status.HTTP_401_UNAUTHORIZED)




        res = doFshareFlow2.apply(kwargs={ "code":code, "server": server, "password" : password, 'token': token})
        print("res", res.result)
        if res :
            return Response(
                {"result": res.result},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"result": "error"},
                status=status.HTTP_400_BAD_REQUEST)

    def home(request):
        return render(request, "home.html")



def get_cache_key(captcha_key):
    cache_key = cache_template.format(key=captcha_key, version=VERSION.major)
    return cache_key
