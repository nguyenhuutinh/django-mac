# https://docs.djangoproject.com/en/1.10/ref/settings/

from datetime import timedelta
import os

from decouple import config  # noqa
from dj_database_url import parse as db_url  # noqa
from rest_framework.settings import api_settings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def base_dir_join(*args):
    return os.path.join(BASE_DIR, *args)

SITE_ID = 1

DEBUG = True

ADMINS = (("Admin", "huutinh.baoloc@gmail.com"),)

AUTH_USER_MODEL = "users.User"

ALLOWED_HOSTS = ["139.180.185.245", "tele-check.xyz", 'localhost', '0.0.0.0', '8b67-2402-800-63b6-817c-e451-5128-d771-ecc5.ngrok.io']
TELEGRAM_BOT_TOKEN = "5697634365:AAEUgF96qD1wcXtxF5x1tXJSH5CjU18KAYM"

DATABASES = {
    "default": config("DATABASE_URL", cast=db_url),
}

# REST_CAPTCHA = {
#     'CAPTCHA_CACHE': 'default',
#     'CAPTCHA_TIMEOUT': 60,  # 5 minutes
#     'CAPTCHA_LENGTH': 4,
#     'CAPTCHA_FONT_SIZE': 30,
#     'CAPTCHA_IMAGE_SIZE': (200, 60),
#     'CAPTCHA_LETTER_ROTATION': (-1, 1),
#     'CAPTCHA_FOREGROUND_COLOR': '#cd1417',
#     'CAPTCHA_BACKGROUND_COLOR': '#ffffff',
# #     # 'CAPTCHA_FONT_PATH': FONT_PATH,
#     'CAPTCHA_CACHE_KEY': 'rest_captcha_{key}.{version}',
#     'FILTER_FUNCTION': 'rest_captcha.captcha.filter_default',
#     'NOISE_FUNCTION': 'rest_captcha.captcha.noise_default'
# }

def get_cache():
  import os
  try:
    servers = os.environ['MEMCACHIER_SERVERS']
    username = os.environ['MEMCACHIER_USERNAME']
    password = os.environ['MEMCACHIER_PASSWORD']
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        # TIMEOUT is not the connection timeout! It's the default expiration
        # timeout that should be applied to keys! Setting it to `None`
        # disables expiration.
        'TIMEOUT': None,
        'LOCATION': servers,
        'OPTIONS': {
          'binary': True,
          'username': username,
          'password': password,
          'behaviors': {
            # Enable faster IO
            'no_block': True,
            'tcp_nodelay': True,
            # Keep connection alive
            'tcp_keepalive': True,
            # Timeout settings
            'connect_timeout': 2000, # ms
            'send_timeout': 750 * 1000, # us
            'receive_timeout': 750 * 1000, # us
            '_poll_timeout': 2000, # ms
            # Better failover
            'ketama': True,
            'remove_failed': 1,
            'retry_timeout': 2,
            'dead_timeout': 30,
          }
        }
      }
    }
  except:
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
    }

CACHES = get_cache()
CORS_ALLOWED_ORIGINS = (
# 'http://localhost:3000',  # for localhost (REACT Default)
'https://ezyfshare.com', # for network
'https://fsharevip.com',
)
CORS_ALLOW_ALL_ORIGINS = True
INSTALLED_APPS = [
    # 'rest_captcha',
    # "django.contrib.admin",   
    'rest_framework_simplejwt',
    'django_celery_beat',

    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django_js_reverse",
    # "webpack_loader",
    # 'knox',

    "import_export",
    "rest_framework",
    "common",
    "users",
    'corsheaders',
    'telegrambot'

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    "debreach.middleware.RandomCommentMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "telegrambot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [base_dir_join("templates")],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                # "django.contrib.messages.context_processors.messages",
                # "common.context_processors.sentry_dsn",
                # "common.context_processors.commit_sha",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
        },
    },
]

WSGI_APPLICATION = "telegrambot.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Jakarta"

USE_I18N = True

USE_L10N = True

USE_TZ = False

# STATICFILES_DIRS = (base_dir_join("../frontend"),)

# Webpack
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": False,  # on DEBUG should be False
        "STATS_FILE": base_dir_join("../webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [".+\.hot-update.js", ".+\.map"],
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# CELERYBEAT_SCHEDULE_FILENAME = os.path.join(BASE_DIR, 'celerybeat-schedule.db')

# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Celery
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACKS_LATE = True
CELERY_TIMEZONE = TIME_ZONE

# Celery configuration
CELERY_LOG_LEVEL = 'DEBUG'
CELERY_WORKER_LOG_LEVEL = 'DEBUG'
CELERY_BEAT_LOG_LEVEL = 'DEBUG'


# Celery
CELERY_IMPORTS = ("telegrambot")
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_SEND_TASK_ERROR_EMAILS = True

# Sentry
# SENTRY_DSN = config("SENTRY_DSN", default="")
# COMMIT_SHA = config("HEROKU_SLUG_COMMIT", default="")

# Fix for Safari 12 compatibility issues, please check:
# https://github.com/vintasoftware/safari-samesite-cookie-issue
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SAMESITE = None

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
