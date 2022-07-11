import csv
import json
import pprint
import random
import sys
from datetime import date, datetime, time, timedelta
from io import StringIO

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views import generic

from celery.result import AsyncResult
from common.models import GoogleFormInfoSerializer
from common.models import GoogleFormInfo
from common.google_form import getFormResponse
from common.google_form_submit import googleSubmitForm
from common.models import CampaignSerializer, Schedule
from dateutil import parser, tz
from faker import Faker
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from users.tasks import updateForms
from werkzeug.utils import secure_filename


fake = Faker()
import os
import re
from datetime import timedelta
from time import sleep

from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from celery.result import AsyncResult
from common.models import Campaign, UserFormInfo
# from common.api_captcha import RestCaptchaSerializer
from macos.settings import base
# from common.file_info_task import checkfileInfoTask
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# from common.google_drive_task import downloadGoogleDrive
# from common.ads_shorten_task import shorten




# from common.download_direct_task import downloadDirectFshare
# from common.download_zip_task import downloadZipFShare


# from common.file_info_task import checkaccountInfoTask

# cache_template = base.REST_CAPTCHA["CAPTCHA_CACHE_KEY"]

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


# def rotate_time(startDate, endDate):
#     # newPlanDate = date.fromisoformat(startDate)
#     # dt = datetime.combine(newPlanDate, datetime.min.time())




#     print(startDate)
#     print(endDate)
#     # if days <= 1:
#     #     endDate = '+10h'
#     # else:
#     #     endDate = f"+{10*days}h"

#     result = fake.date_time_between(start_date= startDate, end_date= endDate)
#     sameDate = result.date() == datetime.today().date()
#     now = datetime.now()

#     minMinute = now.minute + 2
#     minHour = now.hour

#     maxHour = 23

#     if now.minute >= 57:
#         minHour = now.hour + 1
#         minMinute =  1

#     if sameDate == False:
#         minHour = 7
#         minMinute = 1
#     result = result.replace(hour= random.randint(minHour, maxHour), minute= random.randint(minMinute + 2, 59))
#     print(result)
#     return result
def randomTimes(stime, etime, n):
    # frmt = '%d-%m-%Y %H:%M:%S'
    # stime = datetime.strptime(stime, frmt)
    # etime = datetime.strptime(etime, frmt)
    td = etime - stime
    timeRange = [random.random() * td + stime for _ in range(n)]
    timeRange.sort()
    return timeRange


class GoogleFormViewSet(viewsets.ViewSet):

    @action(
        detail=False,
        methods=['post'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        # permission_classes=[IsAuthenticated],
        permission_classes=[AllowAny],

        url_path='auto-submit',
    )
    @csrf_exempt
    def auto_submit(self, request):
        csv_file = request.FILES.get('file')


        campaignId = request.data['campaign_id']
        campaign = Campaign.objects.get(id=campaignId)
        if campaign == None:
            return JsonResponse({"error": f"{campaignId} ko tồn tại. Hãy chọn tên campaign khác" }, status=400, json_dumps_params={'ensure_ascii':False})
        if campaign.status != "new_init":
            return JsonResponse({"error": f"{campaign.name} đã có dữ liệu. Vui lòng tạo campaign mới" }, status=400, json_dumps_params={'ensure_ascii':False})
        content = StringIO(csv_file.read().decode('utf-8-sig'))
        isSemiColon = False
        for _dict in csv.DictReader(content):
            isSemiColon = json.dumps(_dict).count(";") > 3
            break
        # print(isSemiColon)
        csv_reader = csv.reader(content, delimiter= ';' if isSemiColon else ',', quoting=csv.QUOTE_NONE)




        csv_rows = [[x.strip() for x in row] for row in csv_reader]
        field_names =["field1", "field2", "field3", "field4", "field5" ,"field6", "field7", "field8", "field9", "field10"]

        last_row = csv_rows[-1]
        scheduleList = Schedule.objects.filter(campaign_id = campaignId).order_by("target_date")
        for schedule in scheduleList:

            startDate = schedule.target_date
            newStartDate = startDate.replace(hour=campaign.start_time.hour,minute = campaign.start_time.minute, second = campaign.start_time.second)
            # print("startDate")
            # print(newStartDate)
            endDate = schedule.target_date
            newEndDate = endDate.replace(hour=campaign.end_time.hour,minute = campaign.end_time.minute, second = campaign.end_time.second)
            # print(newEndDate)
            length =  len(csv_rows) if schedule.items > len(csv_rows) else schedule.items
            # print(length)
            timeRange = randomTimes( newStartDate, newEndDate, length)
            # print(len(timeRange))
            # print(timeRange[-1])
            for index, row in enumerate(csv_rows):
                if any(row) == False:
                    print("empty line")
                    continue
                # print("hello")
                # print(len(csv_rows))
                # print(f"{index} - {schedule.items}")
                if index >=schedule.items:
                    break
                data_dict = dict(zip(field_names, row))
                # print(data_dict)
                # print(len(timeRange))
                planDt = timeRange.pop(0)
                lastItem = False
                if last_row == row:
                    # print(data_dict)
                    # print("last_row")
                    lastItem = True
                UserFormInfo.objects.create(
                    **data_dict,
                    campaign_id = campaign.id,
                    target_date = planDt.strftime('%Y-%m-%d %H:%M:%S'),
                    last_item = lastItem
                )
            del(csv_rows[: schedule.items])
        if len(csv_rows) > 0:
            # print("out of schedules length")
            # remain_csv_rows = csv_rows[n:]
            # print(n)
            for index, row in enumerate(csv_rows):
                if any(row) == False:
                    print("empty line")
                    continue
                data_dict = dict(zip(field_names, row))
                # print(data_dict)

                lastItem = False
                if last_row == row:
                    # print(data_dict)
                    # print("last_row")
                    lastItem = True
                UserFormInfo.objects.create(
                    **data_dict,
                    campaign_id = campaign.id,
                    last_item = lastItem
                )




        campaign.file_name=csv_file.name
        campaign.status = "ready"
        campaign.save()

        updateForms.apply_async(kwargs={}, eta=now() + timedelta(seconds=1*30))

        return JsonResponse({"success": True, "campaign_id" : campaign.id }, status=200)

    @action(
        detail=False,
        methods=['get'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        # permission_classes=[IsAuthenticated],
        permission_classes=[AllowAny],

        url_path='campaign-detail',
    )
    @csrf_exempt
    def campaignDetail(self, request):
        try:
            id = request.query_params.get('id', '')
        except:
            return JsonResponse({"error_message": "id parameter is required" }, status=400)
        data = Campaign.objects.get(id= id)
        # print(data)
        campaign = CampaignSerializer(instance=data).data

        # print(campaign)
        json_object = json.dumps(campaign)

        return HttpResponse(json_object, content_type="application/json")
    @action(
        detail=False,
        methods=['get'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        # permission_classes=[IsAuthenticated],
        permission_classes=[AllowAny],

        url_path='schedule-list',
    )
    @csrf_exempt
    def scheduleListDetail(self, request):
        try:
            id = request.query_params.get('campaign_id', '')
        except:
            return JsonResponse({"error_message": "id parameter is required" }, status=400)
        data = Schedule.objects.filter(campaign_id= id)
        # print(data)
        schedules = serializers.serialize('json', data)

        # print(campaign)

        return HttpResponse(schedules, content_type="application/json")

    @action(
        detail=False,
        methods=['get'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        # permission_classes=[IsAuthenticated],
        permission_classes=[AllowAny],

        url_path='form-list',
    )
    @csrf_exempt
    def formList(self, request):
        try:
            id = request.query_params.get('campaign-id', '')
        except:
            return JsonResponse({"error_message": "id parameter is required" }, status=400)
        data = UserFormInfo.objects.filter(campaign_id= id).order_by('auto_increment_id').select_related("campaign")
        # print(data)
        campaign = serializers.serialize('json', data)
        # print(campaign)
        return HttpResponse(campaign, content_type="application/json")

    @action(
        detail=False,
        methods=['put'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        # permission_classes=[IsAuthenticated],
        permission_classes=[AllowAny],

        url_path='update-campaign',
    )
    @csrf_exempt
    def updateCampaign(self, request):
        # print(request.data)
        try:
            campaignId = request.data.get('id', '')
            status = request.data.get('status', '')
        except:
            return JsonResponse({"error_message": "id parameter is required" }, status=400)

        campaign = Campaign.objects.get(id=campaignId)
        if campaign == None:
            return JsonResponse({"error": f"{campaignId} ko tồn tại. Hãy chọn tên campaign khác" }, status=400, json_dumps_params={'ensure_ascii':False})

        campaign.status = status
        campaign.save()
        # print(converted)
        return JsonResponse({"success": True, "campaign_id" : campaign.id }, status = 200)


    @action(
        detail=False,
        methods=['get'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        # permission_classes=[IsAuthenticated],
        permission_classes=[AllowAny],

        url_path='campaign-list',
    )
    @csrf_exempt
    def campaignList(self, request):
        data = Campaign.objects.all().order_by('-created')
        # print(data)
        campaign = serializers.serialize('json', data)
        # print(campaign)
        return HttpResponse(campaign, content_type="application/json")


    @action(
        detail=False,
        methods=['get'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        # permission_classes=[IsAuthenticated],
        permission_classes=[AllowAny],

        url_path='form-info',
    )
    @csrf_exempt
    def formInfo(self, request):
        try:
            formId = request.query_params.get('id', '')
        except:
            return JsonResponse({"error_message": "id parameter is required" }, status=400)
        print(formId)
        data = GoogleFormInfo.objects.get(id= formId)
        formInfo = GoogleFormInfoSerializer(instance=data).data

        # print(campaign)
        json_object = json.dumps(formInfo)

        return HttpResponse(json_object, content_type="application/json")


    @action(
        detail=False,
        methods=['post'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        # permission_classes=[IsAuthenticated],
        permission_classes=[AllowAny],

        url_path='add-campaign',
    )
    @csrf_exempt
    def add_new_campaign(self, request):
        default_date = datetime.combine(datetime.now(),
                                time(0, tzinfo=tz.gettz("Asia/Jakarta")))


        # try:
        name = request.data['name']
        # print(name)
        startDate = request.data.get("start_date")
        # print(startDate)
        convertedSD = parser.parse(startDate, default =default_date)

        # print(convertedSD)
        endDate = request.data.get("end_date")
        # print(endDate)
        convertedED = parser.parse(endDate, default =default_date)

        startTime = request.data.get("start_time")
        convertedST = parser.parse(startTime, default =default_date)
        # print(startTime)
        endTime = request.data.get("end_time")
        # print(endTime)
        convertedET = parser.parse(endTime, default =default_date)



        record = Campaign.objects.create(name=name, start_date= convertedSD, end_date=convertedED, start_time= convertedST, end_time= convertedET, status = "new_init")

        data = Campaign.objects.get(id=record.id)
        # print(data)
        isValid = add_schedule(data, convertedST, convertedET , request)
        # print(isValid)
        if(isValid != True):
            return isValid


        isValid = add_google_form(data, request)
        # print(isValid)
        if(isValid != True):
            return isValid

        campaign = CampaignSerializer(instance=data).data

        # print(campaign)
        json_object = json.dumps(campaign)



        # print(converted)
        return HttpResponse(json_object, content_type="application/json")
        # except:
        #     print("Có ngoại lệ ",sys.exc_info()[0]," xảy ra.")
        #     return JsonResponse({"error_message": "id parameter is required" }, status=400)

def add_schedule(campaign, convertedST, convertedET, request):
    try:
        schedules = request.data['schedules']
        default_date = datetime.combine(datetime.now(),
                                time(0, tzinfo=tz.gettz("Asia/Jakarta")))
        totalSchedules = 0
        for sch in schedules:
            # print(sch)
            targetDate = sch["date"]
            items = sch["items"]
            totalSchedules += items
            convertedDate = parser.parse(targetDate, default =default_date)
            Schedule.objects.create(campaign=campaign, target_date = convertedDate, start_time= convertedST, end_time= convertedET, items = items)
        campaign.total_schedules = totalSchedules
        campaign.save()
    except:
        # print("Có ngoại lệ ",sys.exc_info()[0]," xảy ra.")
        return JsonResponse({"error_message": "id parameter is required" }, status=400)
    return True

def add_google_form(campaign, request):
    url = request.data['google_form_link']
    # print(url)
    return getFormResponse(campaign, url)


