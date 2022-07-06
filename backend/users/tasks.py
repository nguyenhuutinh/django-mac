from datetime import datetime
from django.core import management
from common.google_form_submit import googleSubmitForm
from common.models import UserFormInfo

from macos import celery_app


@celery_app.task
def clearsessions():
    management.call_command('clearsessions')


@celery_app.task
def updateForms():
    scheduled_posts = UserFormInfo.objects.filter(
        sent=False,
        target_date__lte= datetime.now()
    )
    for form in scheduled_posts:
        googleSubmitForm.apply_async(kwargs={ "id":form.auto_increment_id}, eta= datetime.now() + datetime.timedelta(seconds=1*60))
