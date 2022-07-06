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
        # target_date__gt= current_task.sent_date_time, #with the 'sent' flag, you may or may not want this
        target_date__lte= datetime.now()
    )
    print("scheduled_posts")
    for form in scheduled_posts:
        googleSubmitForm(form.auto_increment_id)
