from datetime import datetime, timedelta
import random
from django.core import management
from common.models import Campaign
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
        target_date__lt = datetime.now()
    ).exclude(campaign__status = 'canceled').order_by('auto_increment_id').select_related("campaign")
    # print(scheduled_posts , datetime.now() + timedelta(seconds=1*10))
    if scheduled_posts != None and len(scheduled_posts) > 0 :
        if scheduled_posts[0].campaign.status == "ready":
            print("update status")
            Campaign.objects.filter(id=scheduled_posts[0].campaign.id).update(status='running')
        formList = scheduled_posts
        if len(scheduled_posts) > 5 :
            formList = scheduled_posts[:5]
        print(f"available list {len(formList)}")
        for form in formList:
            # print(form)
            # print(form.campaign)
            googleSubmitForm.apply_async(kwargs={ "id":form.auto_increment_id}, countdown = random.randint(3, 30))
