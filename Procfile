web: gunicorn telegrambot.wsgi --chdir backend --limit-request-line 8188 --log-file -
worker: REMAP_SIGTERM=SIGQUIT celery --workdir backend --app=telegrambot worker --loglevel=info
beat: REMAP_SIGTERM=SIGQUIT celery --workdir backend --app=telegrambot beat -S redbeat.RedBeatScheduler --loglevel=info
