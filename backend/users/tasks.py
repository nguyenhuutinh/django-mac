from datetime import datetime, timedelta
import random
from django.core import management
# from common.models import Campaign
# from common.google_form_submit import googleSubmitForm
# from common.models import UserFormInfo

from telegrambot import celery_app


# @celery_app.task
# def clearsessions():
#     management.call_command('clearsessions')


@celery_app.task
def updateForms():
    print("scheduled_posts")

