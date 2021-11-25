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

from common.fshare_task import doFshareFlow
from common.fshare_task2 import doFshareFlow2
from common.fshare_task2 import heartBeating

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
        url_path='rest_check_2',
    )
    @csrf_exempt
    def rest_check_2(self, request):


        try:
            code = request.data['code']
            server = request.data['server']
        except:
            return JsonResponse({"error_message": "fshare code is not exist" }, status=400)
        print(code, server)


        res = doFshareFlow2.apply(kwargs={ "code":code, "server": server})
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


