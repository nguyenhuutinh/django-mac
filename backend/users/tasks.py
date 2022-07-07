from datetime import datetime, timedelta
from django.core import management
from common.google_form_submit import googleSubmitForm
from common.models import UserFormInfo

from macos import celery_app


@celery_app.task
def clearsessions():
    management.call_command('clearsessions')


@celery_app.task
def updateForms():
    print("scheduled_posts")
    scheduled_posts = UserFormInfo.objects.filter(
        sent=False,
        target_date__lte= datetime.now()
    )
    # print(scheduled_posts , datetime.now() + timedelta(seconds=1*10))
    if scheduled_posts != None and len(scheduled_posts) > 0 :
        formList = scheduled_posts
        if len(scheduled_posts) > 10 :
            formList = scheduled_posts[:10]
            print(len(formList))
        for form in formList:
            googleSubmitForm.apply_async(kwargs={ "id":form.auto_increment_id}, countdown = 10)
