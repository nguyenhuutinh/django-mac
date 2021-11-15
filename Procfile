web: gunicorn macos.wsgi --chdir backend --limit-request-line 8188 --log-file -
worker: REMAP_SIGTERM=SIGQUIT celery --workdir backend --app=macos worker --loglevel=info
beat: REMAP_SIGTERM=SIGQUIT celery --workdir backend --app=macos beat -S redbeat.RedBeatScheduler --loglevel=info
