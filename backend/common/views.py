import random
from django.views import generic
from celery.result import AsyncResult
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from datetime import datetime,date, timedelta
from django.utils.timezone import now
import pprint
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from werkzeug.utils import secure_filename
import csv
from io import StringIO
from faker import Faker
from django.core import serializers
from users.tasks import updateForms

from common.google_form_submit import googleSubmitForm
fake = Faker()
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from time import sleep

from datetime import timedelta
from django.utils import timezone

import os
import re
import requests

from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult
from common.models import Campaign
from common.models import UserFormInfo
from django.db.models import Count
# from common.google_drive_task import downloadGoogleDrive
# from common.ads_shorten_task import shorten




# from common.download_direct_task import downloadDirectFshare
# from common.download_zip_task import downloadZipFShare

# from common.file_info_task import checkfileInfoTask
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
# from common.api_captcha import RestCaptchaSerializer
from macos.settings import base

# from common.file_info_task import checkaccountInfoTask

cache_template = base.REST_CAPTCHA["CAPTCHA_CACHE_KEY"]

class IndexView(generic.TemplateView):
    template_name = 'common/index.html'



# class AdsViewSet(viewsets.ViewSet):

#     @action(
#         detail=False,
#         methods=['post'],
#         permission_classes=[AllowAny],
#         url_path='shorten',
#     )
#     @csrf_exempt
#     def shorten(self, request):


#         try:
#             url = request.data['url']
#         except:
#             return JsonResponse({"error_message": "url is not exist" }, status=400)
#         print(url)

#         task = shorten.apply(kwargs={"url":url})
#         print("downloadGoogleDrive done", task)
#         result = task.result
#         if(type(result) == str and result.startswith("error")):
#             return JsonResponse({"result": result }, status=400)
#         else:
#             # task_result = AsyncResult(task.id)
#             # print(task_result.result)
#             downloadLink = task.result
#             # task_id = task.info["id"]
#             print("downloadLink")
#             print(downloadLink)
#             return JsonResponse({"result": downloadLink }, status=200)



# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip


    # @csrf_exempt
    # def get_status(request, task_id):
    #     task_result = AsyncResult(task_id)
    #     result = {
    #         "task_id": task_id,
    #         "task_status": task_result.status,
    #         "task_result": task_result..
    #     }
    #     return JsonResponse(result, status=200)




# class GoogleDriveViewSet(viewsets.ViewSet):

#     # @action(
#     #     detail=False,
#     #     methods=['post'],
#     #     permission_classes=[AllowAny],
#     #     url_path='rest-check',
#     # )
#     # @csrf_exempt
#     # def rest_check(self, request):
#     #     print("ooo")
#     #     return Response(
#     #         {"result": "If you're seeing this, the REST API is working!"},
#     #         status=status.HTTP_200_OK,
#     #     )
#     # def home(request):
#     #     return render(request, "home.html")

#     @action(
#         detail=False,
#         methods=['post'],
#         permission_classes=[AllowAny],
#         url_path='download_direct',
#     )
#     @csrf_exempt
#     def download_direct(self, request):
#         ip = get_client_ip(request)
#         print("google download_direct for ip: ", ip)

#         try:
#             file_slug = request.data['file_slug']
#         except:
#             return JsonResponse({"error_message": "file is not exist" }, status=400)
#         print(file_slug)

#         task = downloadGoogleDrive.apply(kwargs={"file_slug":file_slug, "ip" : ip})
#         print("downloadGoogleDrive done", task)
#         result = task.result
#         if(type(result) == str and result.startswith("error")):
#             return JsonResponse({"result": result }, status=400)
#         else:
#             # task_result = AsyncResult(task.id)
#             # print(task_result.result)
#             downloadLink = 'https://drive.google.com/uc?id={}&export=download'.format(task.result)
#             # task_id = task.info["id"]
#             print("downloadLink")
#             print(downloadLink)
#             return JsonResponse({"result": downloadLink }, status=200)



# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip


#     # @csrf_exempt
#     # def get_status(request, task_id):
#     #     task_result = AsyncResult(task_id)
#     #     result = {
#     #         "task_id": task_id,
#     #         "task_status": task_result.status,
#     #         "task_result": task_result..
#     #     }
#     #     return JsonResponse(result, status=200)




# class FshareViewSet(viewsets.ViewSet):
#     serializer_class = RestCaptchaSerializer

#     @action(
#         detail=False,
#         methods=['post'],
#         permission_classes=[AllowAny],
#         url_path='download_zip',
#     )
#     @csrf_exempt
#     def download_zip(self, request):
#         ip = get_client_ip(request)

#         print("download_zip for ip: ", ip)
#         try:
#             code = request.data.get('code')
#             server = request.data.get('server')
#             password = request.data.get('password')
#             token = request.data.get('token')
#             capchaKey = request.data.get('captcha_key')
#             capchaValue = request.data.get('captcha_value')
#         except:
#             return JsonResponse({"error_message": "fshare code is not exist" }, status=400)
#         print(code, server)
#         data = dict(captcha_key=capchaKey, captcha_value= capchaValue)
#         serial = RestCaptchaSerializer()
#         # print("ccc")
#         isValid = None
#         try:
#             isValid  = serial.validate(data)
#         except Exception as e:
#             print(e)
#         print("captcha", isValid)
#         # if isValid == None:
#         #             return Response(
#         #                             {"result": "Captcha hết hạn hoặc không đúng. vui lòng thử lại"},
#         #                             status=status.HTTP_401_UNAUTHORIZED)

#         res = downloadZipFShare.apply(kwargs={ "code":code, "server": server, "password" : password, 'token': token})
#         print("res", res.result)

#         if type (res.result) is str:
#             return Response(
#                 {"result": {"url":res.result}},
#                 status=status.HTTP_200_OK,
#             )
#         else :
#             return Response(
#                 {"result": {"errors": res.result}},
#                 status=status.HTTP_400_BAD_REQUEST)

#     @action(
#         detail=False,
#         methods=['post'],
#         permission_classes=[AllowAny],
#         url_path='download_direct',
#     )
#     @csrf_exempt
#     def download_direct(self, request):
#         ip = get_client_ip(request)

#         print("download_direct for ip: ", ip)
#         try:
#             print("aa")
#             code = request.data.get('code')
#             server = request.data.get('server')
#             password = request.data.get('password')
#             token = request.data.get('token')
#             capchaKey = request.data.get('captcha_key')
#             capchaValue = request.data.get('captcha_value')
#         except Exception as e:
#             print(e)
#             return JsonResponse({"error_message": "fshare code is not exist" }, status=400)

#         # print("bbb")

#         data = dict(captcha_key=capchaKey, captcha_value= capchaValue)
#         serial = RestCaptchaSerializer()
#         # print("ccc")
#         isValid = None
#         try:
#             isValid  = serial.validate(data)
#         except Exception as e:
#             print(e)

#         # print("ccc")
#         print("isValid", isValid)
#         # key = get_cache_key(capchaValue)
#         # value = cache.get(capchaKey)
#         # isValidCaptcha = "{}.0".format(capchaValue) in key
#         # print(key, value)
#         print(code, server, password, token)
#         # print(capchaKey, capchaValue,serial.is_valid(), serial.validated_data, isValidCaptcha)
#         # if isValid == None:
#         #     return Response(
#         #                     {"result": "captcha hết hạn hoặc không đúng. vui lòng thử lại"},
#         #                     status=status.HTTP_401_UNAUTHORIZED)




#         res = downloadDirectFshare.apply(kwargs={ "code":code, "server": server, "password" : password, 'token': token})
#         print("res", res.result)
#         if res :
#             return Response(
#                 {"result": res.result},
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {"result": "error"},
#                 status=status.HTTP_400_BAD_REQUEST)

#     @action(
#     detail=False,
#     methods=['get'],
#     permission_classes=[AllowAny],
#     url_path='file_info',
#     )
#     @csrf_exempt
#     def file_info(self, request):
#         print("file_info", request)

#         try:
#             url = request.query_params.get('url', '')
#         except:
#             return JsonResponse({"error_message": "url parameter is required" }, status=400)
#         print("url", url)
#         res = checkfileInfoTask.apply(kwargs={"server": 2,  'url': url})
#         if res and res.result.get("errors") == None:
#             return JsonResponse(
#                 {"result": res.result},
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return JsonResponse(
#                 {"result": res.result},
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#     @action(
#     detail=False,
#     methods=['get'],
#     permission_classes=[AllowAny],
#     url_path='account_info',
#     )
#     @csrf_exempt
#     def account_info(self, request):
#         print("account_info", request)

#         try:
#             account = request.query_params.get('account', '')
#         except:
#             return JsonResponse({"error_message": "url parameter is required" }, status=400)
#         print("account", account)
#         res = checkaccountInfoTask.apply(kwargs={"server": account})
#         if res and res.result.get("errors") == None:
#             return JsonResponse(
#                 {"result": res.result},
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return JsonResponse(
#                 {"result": res.result},
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#     def home(request):
#         return render(request, "home.html")



# def get_cache_key(captcha_key):
#     cache_key = cache_template.format(key=captcha_key, version=VERSION.major)
#     return cache_key


def rotate_time(planDate, days):
    newPlanDate = date.fromisoformat(planDate)
    dt = datetime.combine(newPlanDate, datetime.min.time())
    now = datetime.now()
    dt = dt.replace(hour= now.hour, minute= random.randint(now.minute + 2, 59))
    # print(dt)
    # if days <= 1:
    #     endDate = '+10h'
    # else:
    #     endDate = f"+{10*days}h"

    result = fake.date_time_between(start_date= dt, end_date= dt)
    print(result)
    return result



class GoogleFormViewSet(viewsets.ViewSet):

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='auto-submit',
    )
    @csrf_exempt
    def auto_submit(self, request):
        csv_file = request.FILES.get('file')
        planDate = request.data['plan_date']
        if request.data.get("during_date"):
            days = request.data['during_date']
        else :
            days = 1

        cName = request.data['campaign']
        duplicates = Campaign.objects.filter(name=cName).exists()
        if duplicates:
            return JsonResponse({"error": f"{cName} đã tồn tại. Hãy chọn tên campaign khác" }, status=400, json_dumps_params={'ensure_ascii':False})

        content = StringIO(csv_file.read().decode('utf-8-sig'))
        csv_reader = csv.reader(content, delimiter=',', quoting=csv.QUOTE_NONE)




        csv_rows = [[x.strip() for x in row] for row in csv_reader]
        field_names = csv_rows[0]  # Get the header row
        del csv_rows[0]
        camp = Campaign.objects.create(
                        name=cName,
                        file_name=csv_file.name,
                        total= len(csv_rows),
                        sent= 0
                    )
        # print(camp.id)
        # submitForm(690)
        # return
        scheduler = BackgroundScheduler()
        scheduler.start()

        for index, row in enumerate(csv_rows):
            data_dict = dict(zip(field_names, row))
            # print(data_dict)
            planDt = rotate_time(planDate, days)
            trigger = CronTrigger(
                year=planDt.year, month=planDt.month, day=planDt.day, hour=planDt.hour, minute=planDt.minute, second=planDt.second
            )
            obj, created = UserFormInfo.objects.update_or_create(phone=row[1],
                defaults = data_dict,
                age = 'Tùy chọn 1',
                gender = 'Tùy chọn 1',
                lucky_number = f'{random.randint(0, 9999)}',
                campaign_id = camp.id,
                target_date = planDt.strftime('%Y-%m-%d %H:%M:%S')
            )
            # print(created, obj.auto_increment_id)
            # scheduler.add_job(
            #     submitForm,
            #     trigger=trigger,
            #     args=[obj.auto_increment_id],
            #     name="Submit Form",
            # )

        updateForms.apply_async(kwargs={}, eta=now() + timedelta(seconds=1*30))
        # filename = secure_filename(data.filename)
        # data.save("/temp/" + filename)
        return JsonResponse({"success": True, "campaign_id" : camp.id }, status=200)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='campaign-detail',
    )
    @csrf_exempt
    def campaignDetail(self, request):
        try:
            id = request.query_params.get('id', '')
        except:
            return JsonResponse({"error_message": "id parameter is required" }, status=400)
        data = UserFormInfo.objects.filter(campaign_id= id).order_by('target_date').select_related("campaign")
        # print(data)
        campaign = serializers.serialize('json', data)
        # print(campaign)
        return HttpResponse(campaign, content_type="application/json")


def submitForm(id):
    # print(id)
    res = googleSubmitForm.apply(kwargs={ "id":id})
    # print(res)

