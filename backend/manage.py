#!/usr/bin/env python

import os
import sys
from common.tccl_bot import bot
from decouple import config

APP_URL = "https://tele-check.xyz/api/tccl-bot/webhook/"
# APP_URL = "https://8b67-2402-800-63b6-817c-e451-5128-d771-ecc5.ngrok.io/api/tccl-bot/webhook/"


if __name__ == "__main__":
    settings_module = config("DJANGO_SETTINGS_MODULE", default=None)
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    if sys.argv[1] == "test":
        if settings_module:
            print(
                "Ignoring config('DJANGO_SETTINGS_MODULE') because it's test. "
                "Using 'macos.settings.test'"
            )
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "macos.settings.test")
    else:
        if settings_module is None:
            print(
                "Error: no DJANGO_SETTINGS_MODULE found. Will NOT start devserver. "
                "Remember to create .env file at project root. "
                "Check README for more info."
            )
            sys.exit(1)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
