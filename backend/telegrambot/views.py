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
from celery.result import AsyncResult
# from common.models import GoogleFormField
# from common.models import GoogleFormInfoSerializer
# from common.models import GoogleFormInfo
# from common.google_form import getFormResponse
# from common.google_form_submit import googleSubmitForm
# from common.models import CampaignSerializer, Schedule
from dateutil import parser, tz
from faker import Faker
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
# from users.tasks import updateForms
from werkzeug.utils import secure_filename
from rest_framework import generics, permissions, mixins
# from common.models import Message

# from common.models import TelegramUser


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
# from common.models import Campaign, UserFormInfo
# from common.api_captcha import RestCaptchaSerializer
from telegrambot.settings import base
# from common.file_info_task import checkfileInfoTask
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer


from telegrambot.tccl_bot import process_request
# from common.ads_shorten_task import shorten




# from common.download_direct_task import downloadDirectFshare
# from common.download_zip_task import downloadZipFShare


# from common.file_info_task import checkaccountInfoTask

# cache_template = base.REST_CAPTCHA["CAPTCHA_CACHE_KEY"]

class IndexView(generic.TemplateView):
    template_name = 'common/index.html'

class TCCLBotView(viewsets.ViewSet):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer]  # Ensure appropriate renderers

    @action(
        detail=False,
        methods=['head', 'get'],
        permission_classes=[AllowAny],
        url_path='health',
    )
    @csrf_exempt

    def health_check(self, request):
        try:
            html_content = "<html><body><h1>Health Check OK</h1></body></html>"
            return Response(html_content, content_type='text/html', status=200)
        except Exception as e:
            logger.error(f"Error in health check endpoint: {e}")
            return Response(status=500)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='webhook',
    )
    @csrf_exempt
    def check_bot(self, request):
        return process_request(request)


# class UsersApi(generics.GenericAPIView):
#     permission_classes = ()
#     authentication_classes = ()
#     def get(self, request, *args,  **kwargs):
#         # print("haha")


#         users = TelegramUser.objects.all()
#         # print(data)
#         usersData = serializers.serialize('json', users)
#         # print(usersData)
#         return HttpResponse(usersData, content_type="application/json")

# class MessageApi(generics.GenericAPIView):
#     permission_classes = ()
#     authentication_classes = ()
#     def get(self, request, *args,  **kwargs):
#         # print("haha")


#         messages = Message.objects.all()
#         # print(data)
#         messagesData = serializers.serialize('json', messages)
#         # print(messagesData)
#         return HttpResponse(messagesData, content_type="application/json")




