import copy
import csv
import json
import pprint
import random
import sys
from datetime import date, datetime, time, timedelta
from io import StringIO
from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views import generic
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from celery.result import AsyncResult
from gform.models import UserFormInfoSerializer
from gform.models import Owner
from users.serializer import UserSerializer
from gform.models import GoogleFormField
from gform.models import GoogleFormInfoSerializer
from gform.models import GoogleFormInfo
from gform.google_form import getFormResponse
from gform.google_form_submit import googleSubmitForm
from gform.models import CampaignSerializer, Schedule
from dateutil import parser, tz
from faker import Faker
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from users.tasks import updateForms
from werkzeug.utils import secure_filename
from rest_framework.generics import RetrieveAPIView
from rest_framework import generics
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


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
from gform.models import Campaign, UserFormInfo
# from gform.api_captcha import RestCaptchaSerializer
from gform.settings import base
# from gform.file_info_task import checkfileInfoTask
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class IndexView(generic.TemplateView):
    template_name = 'common/index.html'


def randomTimes(stime, etime, n):
    # frmt = '%d-%m-%Y %H:%M:%S'
    # stime = datetime.strptime(stime, frmt)
    # etime = datetime.strptime(etime, frmt)
    td = etime - stime
    timeRange = [random.random() * td + stime for _ in range(n)]
    timeRange.sort()
    return timeRange



class CampaignListViewSet(viewsets.ModelViewSet):


    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, )
    ordering_fields = '__all__'
    ordering = ('created')
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated,],
        serializer_class = CampaignSerializer,
        url_path='campaign-list',
    )
    @csrf_exempt
    def lst(self, request):
        uid = self.request.user.id
        queryset = Campaign.objects.filter(owner__user_id = uid).select_related("owner")
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        # print(serializer.data)
        return Response(serializer.data)
        # return JsonResponse({"success": True, "campaign_id" : 1 }, status=200)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated,],
        serializer_class = UserFormInfoSerializer,

        url_path='form-list',
    )
    @csrf_exempt
    def formList(self, request):
        try:
            id = request.query_params.get('campaign_id')
        except:
            return JsonResponse({"error_message": "campaign_id parameter is required" }, status=400)
        uid = self.request.user.id
        queryset = Campaign.objects.filter(owner__user_id = uid).select_related("owner")
        if queryset == None:
           return JsonResponse({"error_message": "unauthorized campaign" }, status=401)

        queryset = UserFormInfo.objects.filter(campaign_id= id).select_related("campaign")




        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        # print(serializer.data)
        return Response(serializer.data)
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated,],

        url_path='add-campaign',
    )
    @csrf_exempt
    def post(self, request):
        uid = self.request.user.id
        default_date = datetime.combine(datetime.now(),
                                time(0, tzinfo=tz.gettz("Asia/Jakarta")))

        # try:
        name = request.data.get('name')
        if name == None:
            return JsonResponse({"error_message": "name parameter is required" }, status=400)
        # print(name)
        startDate = request.data.get("start_date")
        if startDate == None:
            return JsonResponse({"error_message": "startDate parameter is required" }, status=400)
        # print(startDate)
        convertedSD = parser.parse(startDate, default =default_date)
        if convertedSD == None:
            return JsonResponse({"error_message": "convertedSD parameter is required" }, status=400)

        # print(convertedSD)
        endDate = request.data.get("end_date")
        if endDate == None:
            return JsonResponse({"error_message": "endDate parameter is required" }, status=400)
        # print(endDate)
        convertedED = parser.parse(endDate, default =default_date)
        if convertedED == None:
            return JsonResponse({"error_message": "convertedED parameter is required" }, status=400)

        startTime = request.data.get("start_time")
        if startTime == None:
            return JsonResponse({"error_message": "startTime parameter is required" }, status=400)

        convertedST = parser.parse(startTime, default =default_date)
        if convertedST == None:
            return JsonResponse({"error_message": "convertedST parameter is required" }, status=400)
        # print(startTime)
        endTime = request.data.get("end_time")
        if endTime == None:
            return JsonResponse({"error_message": "endTime parameter is required" }, status=400)
        # print(endTime)
        convertedET = parser.parse(endTime, default =default_date)
        if convertedET == None:
            return JsonResponse({"error_message": "convertedET parameter is required" }, status=400)


        owner = Owner.objects.create(user_id=uid, role= 'owner', status="active")

        record = Campaign.objects.create(name=name, start_date= convertedSD, end_date=convertedED, start_time= convertedST, end_time= convertedET, status = "new", owner = owner)

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


    @action(
        detail=False,
        methods=['post'],
        # authentication_classes = [SessionAuthentication, BasicAuthentication],
        permission_classes=[IsAuthenticated,],
        url_path='auto-submit',
    )
    @csrf_exempt
    def auto_submit(self, request):

        csv_file = request.FILES.get('file')
        if csv_file == None:
            return JsonResponse({"error_message": "csv_file parameter is required" }, status=400)

        campaignId = request.data.get('campaign_id')
        if campaignId == None or campaignId.isdigit() == False :
            return JsonResponse({"error_message": "campaignId parameter is required" }, status=400)
        campaign = Campaign.objects.get(id=campaignId)
        if campaign == None:
            return JsonResponse({"error": f"{campaignId} ko tồn tại. Hãy chọn tên campaign khác" }, status=400, json_dumps_params={'ensure_ascii':False})
        if campaign.status != "new" and campaign.status != "new_init":
            return JsonResponse({"error": f"{campaign.name} đã có dữ liệu. Vui lòng tạo campaign mới" }, status=400, json_dumps_params={'ensure_ascii':False})
        content = StringIO(csv_file.read().decode('utf-8-sig'))
        temp_content = copy.copy(content)
        # print(temp_content)
        isSemiColon = True

        for _dict in csv.DictReader(temp_content):
            # print(_dict)
            isSemiColon = json.dumps(_dict).count(";") > 3
            break
        # print(isSemiColon)

        del(temp_content)


        csv_reader = csv.reader(content, delimiter= ';' if isSemiColon else ',', quoting=csv.QUOTE_NONE)




        csv_rows = [[x.strip() for x in row] for row in csv_reader]
        field_names =["field1", "field2", "field3", "field4", "field5" ,"field6", "field7", "field8", "field9", "field10"]


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
                data_dict = dict(zip(field_names, row))
                # print(data_dict)
                if any(row) == False:
                    print("empty line")
                    continue
                if index >=schedule.items:
                    break
                data_dict = dict(zip(field_names, row))
                planDt = timeRange.pop(0)

                lastItem = UserFormInfo.objects.create(
                    **data_dict,
                    campaign_id = campaign.id,
                    target_date = planDt.strftime('%Y-%m-%d %H:%M:%S')
                )
            del(csv_rows[: schedule.items])
        if len(csv_rows) > 0:
            for index, row in enumerate(csv_rows):
                if any(row) == False:
                    print("empty line")
                    continue
                data_dict = dict(zip(field_names, row))
                # print(data_dict)
                lastItem = UserFormInfo.objects.create(
                    **data_dict,
                    campaign_id = campaign.id
                )



        del(csv_rows)

        campaign.file_name=csv_file.name
        campaign.status = "ready"
        if lastItem:
            campaign.last_item_id = lastItem.auto_increment_id
        campaign.save()

        updateForms.apply_async(kwargs={}, eta=now() + timedelta(seconds=1*30))

        return JsonResponse({"success": True, "campaign_id" : campaign.id }, status=200)



# class GoogleFormViewSet(viewsets.ViewSet):
#     @action(
#         detail=False,
#         methods=['put'],
#         # authentication_classes = [SessionAuthentication, BasicAuthentication],
#         # permission_classes=[IsAuthenticated],
#         permission_classes=[IsAuthenticated,],

#         url_path='regenerate-date',
#     )
#     @csrf_exempt
#     def regenerateDate(self, request):
#         print()
#         # default_date = datetime.combine(datetime.now(),
#         #                         time(0, tzinfo=tz.gettz("Asia/Jakarta")))

#         # campaignId = request.data['campaign_id']

#         # targetDate = request.data.get("target_date")

#         # # print(startDate)
#         # convertedDate = parser.parse(targetDate, default =default_date)

#         # data = UserFormInfo.objects.filter(~Q(status = 'queued'), sent=False, campaign_id= campaignId, target_date__date = convertedDate ).order_by('auto_increment_id')
#         # # print(data)
#         # if len(data) == 0:
#         #     return JsonResponse({"error": f"{campaignId} không có dữ liệu form" }, status=400, json_dumps_params={'ensure_ascii':False})




#         # startTime = request.data.get("start_time")
#         # convertedST = parser.parse(startTime, default =default_date)
#         # # print(startTime)
#         # endTime = request.data.get("end_time")
#         # # print(endTime)
#         # convertedET = parser.parse(endTime, default =default_date)



#         # startDate = convertedDate.replace(hour=convertedST.hour,minute = convertedST.minute, second = convertedST.second)
#         # endDate = convertedDate.replace(hour=convertedET.hour,minute = convertedET.minute, second = convertedET.second)

#         # timeRange = randomTimes( startDate, endDate, len(data))

#         # for form in data:

#         #     targetDate = timeRange.pop(0)

#         #     form.target_date = targetDate.strftime('%Y-%m-%d %H:%M:%S')

#         #     form.save()

#         return JsonResponse({"success": True, "campaign_id" : 1 }, status=200)


#     @action(
#         detail=False,
#         methods=['get'],
#         # authentication_classes = [SessionAuthentication, BasicAuthentication],
#         # permission_classes=[IsAuthenticated],
#         permission_classes=[AllowAny],

#         url_path='campaign-detail',
#     )
#     @csrf_exempt
#     def campaignDetail(self, request):
#         try:
#             id = request.query_params.get('id', '')
#         except:
#             return JsonResponse({"error_message": "id parameter is required" }, status=400)
#         data = Campaign.objects.get(id= id)
#         # print(data)
#         campaign = CampaignSerializer(instance=data).data

#         # print(campaign)
#         json_object = json.dumps(campaign)

#         return HttpResponse(json_object, content_type="application/json")
#     @action(
#         detail=False,
#         methods=['get'],
#         # authentication_classes = [SessionAuthentication, BasicAuthentication],
#         # permission_classes=[IsAuthenticated],
#         permission_classes=[AllowAny],

#         url_path='schedule-list',
#     )
#     @csrf_exempt
#     def scheduleListDetail(self, request):
#         try:
#             id = request.query_params.get('campaign_id', '')
#         except:
#             return JsonResponse({"error_message": "id parameter is required" }, status=400)
#         data = Schedule.objects.filter(campaign_id= id)
#         # print(data)
#         schedules = serializers.serialize('json', data)

#         # print(campaign)

#         return HttpResponse(schedules, content_type="application/json")



#     @action(
#         detail=False,
#         methods=['put'],
#         # authentication_classes = [SessionAuthentication, BasicAuthentication],
#         # permission_classes=[IsAuthenticated],
#         permission_classes=[AllowAny],

#         url_path='update-campaign',
#     )
#     @csrf_exempt
#     def updateCampaign(self, request):
#         # print(request.data)
#         try:
#             campaignId = request.data.get('id', '')
#             status = request.data.get('status', '')
#         except:
#             return JsonResponse({"error_message": "id parameter is required" }, status=400)

#         campaign = Campaign.objects.get(id=campaignId)
#         if campaign == None:
#             return JsonResponse({"error": f"{campaignId} ko tồn tại. Hãy chọn tên campaign khác" }, status=400, json_dumps_params={'ensure_ascii':False})

#         campaign.status = status
#         campaign.save()
#         # print(converted)
#         return JsonResponse({"success": True, "campaign_id" : campaign.id }, status = 200)


#     @action(
#         detail=False,
#         methods=['get'],
#         # authentication_classes = [SessionAuthentication, BasicAuthentication],
#         # permission_classes=[IsAuthenticated],
#         permission_classes=[AllowAny],

#         url_path='campaign-list',
#     )



#     @action(
#         detail=False,
#         methods=['get'],
#         # authentication_classes = [SessionAuthentication, BasicAuthentication],
#         # permission_classes=[IsAuthenticated],
#         permission_classes=[AllowAny],

#         url_path='form-info',
#     )
#     @csrf_exempt
#     def formInfo(self, request):
#         try:
#             formId = request.query_params.get('id', '')
#         except:
#             return JsonResponse({"error_message": "id parameter is required" }, status=400)
#         print(formId)
#         try:
#             data = GoogleFormInfo.objects.get(id= formId)
#         except GoogleFormInfo.DoesNotExist:
#             return JsonResponse({"error_message": f"GFomr Id: {id} does not exist" }, status=400)
#         formInfo = GoogleFormInfoSerializer(instance=data).data

#         # print(campaign)
#         json_object = json.dumps(formInfo)

#         return HttpResponse(json_object, content_type="application/json")


#     @action(
#         detail=False,
#         methods=['put'],
#         # authentication_classes = [SessionAuthentication, BasicAuthentication],
#         # permission_classes=[IsAuthenticated],
#         permission_classes=[AllowAny],

#         url_path='delete-campaign',
#     )
#     @csrf_exempt
#     def delete_campaign(self, request):
#         try:
#             campaignId = request.data.get('id', '')
#             password = request.data.get('password', '')
#         except:
#             return JsonResponse({"error_message": "id parameter is required" }, status=400)

#         if password != '5933':
#             return JsonResponse({"error_message": "wrong password" }, status=400)
#         #  delete Schedule
#         Schedule.objects.select_related("campaign").filter(campaign_id= campaignId).delete()
#         GoogleFormField.objects.select_related("campaign").filter(campaign_id= campaignId).delete()
#         GoogleFormInfo.objects.select_related("campaign").filter(campaign_id= campaignId).delete()
#         UserFormInfo.objects.select_related("campaign").filter(campaign_id= campaignId).delete()
#         Campaign.objects.filter(id= campaignId).delete()
#         return JsonResponse({"result": "success" }, status=200)
#     @action(
#         detail=False,
#         methods=['post'],
#         # authentication_classes = [SessionAuthentication, BasicAuthentication],
#         # permission_classes=[IsAuthenticated],
#         permission_classes=[AllowAny],

#         url_path='add-campaign',
#     )
#     @csrf_exempt
#     def add_new_campaign(self, request):
#         default_date = datetime.combine(datetime.now(),
#                                 time(0, tzinfo=tz.gettz("Asia/Jakarta")))


#         # try:
#         name = request.data['name']
#         # print(name)
#         startDate = request.data.get("start_date")
#         # print(startDate)
#         convertedSD = parser.parse(startDate, default =default_date)

#         # print(convertedSD)
#         endDate = request.data.get("end_date")
#         # print(endDate)
#         convertedED = parser.parse(endDate, default =default_date)

#         startTime = request.data.get("start_time")
#         convertedST = parser.parse(startTime, default =default_date)
#         # print(startTime)
#         endTime = request.data.get("end_time")
#         # print(endTime)
#         convertedET = parser.parse(endTime, default =default_date)


#         record = Campaign.objects.create(name=name, start_date= convertedSD, end_date=convertedED, start_time= convertedST, end_time= convertedET, status = "new")

#         data = Campaign.objects.get(id=record.id)
#         # print(data)
#         isValid = add_schedule(data, convertedST, convertedET , request)
#         # print(isValid)
#         if(isValid != True):
#             return isValid


#         isValid = add_google_form(data, request)
#         # print(isValid)
#         if(isValid != True):
#             return isValid

#         campaign = CampaignSerializer(instance=data).data

#         # print(campaign)
#         json_object = json.dumps(campaign)



#         # print(converted)
#         return HttpResponse(json_object, content_type="application/json")
#         # except:
#         #     print("Có ngoại lệ ",sys.exc_info()[0]," xảy ra.")
#         #     return JsonResponse({"error_message": "id parameter is required" }, status=400)

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
        campaign.total_forms = totalSchedules
        campaign.save()
    except:
        # print("Có ngoại lệ ",sys.exc_info()[0]," xảy ra.")
        return JsonResponse({"error_message": "id parameter is required" }, status=400)
    return True

def add_google_form(campaign, request):
    url = request.data['google_form_link']
    val = URLValidator()
    try:
        val(url)
    except:
        return JsonResponse({"error_message": "link is not valid" }, status=400)

    # print(url)
    return getFormResponse(campaign, url)


