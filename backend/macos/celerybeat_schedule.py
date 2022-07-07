from datetime import timedelta
from celery.schedules import crontab  # pylint:disable=import-error,no-name-in-module


CELERY_BEAT_SCHEDULE = {
    # Internal tasks
    "form-every-180-seconds": {"schedule": 5*60.0, "task": "tasks.post_scheduled_updates"},
}
