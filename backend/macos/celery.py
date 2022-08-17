import os
import sys

from django.apps import apps

from celery import Celery
from decouple import config

from .celerybeat_schedule import CELERY_BEAT_SCHEDULE

settings_module = config("DJANGO_SETTINGS_MODULE", default=None)
if settings_module is None:
    print(
        "Error: no DJANGO_SETTINGS_MODULE found. Will NOT start devserver. "
        "Remember to create .env file at project root. "
        "Check README for more info."
    )
    sys.exit(1)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

app = Celery("macos")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
app.conf.beat_schedule = {
    "form-every-60-seconds": {"schedule": 60.0, "task": "users.tasks.updateForms"},
}
# print("hell")
