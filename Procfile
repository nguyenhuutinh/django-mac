web: gunicorn gform.wsgi --chdir backend --limit-request-line 8188 --log-file -
worker: REMAP_SIGTERM=SIGQUIT celery --workdir backend --app=gform worker --loglevel=info
beat: REMAP_SIGTERM=SIGQUIT celery --workdir backend --app=gform beat -S redbeat.RedBeatScheduler --loglevel=info
