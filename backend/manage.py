#!/usr/bin/env python

import os
import sys
import telebot
from decouple import config

BOT_TOKEN = "5495185707:AAHfM3MiF5nC-z_dCX-1YWv0oz-ZWL1boJs"
APP_URL = "https://api.tradecoinchienluoc.com/api/tccl-bot/webhook/"
# APP_URL = "https://8b67-2402-800-63b6-817c-e451-5128-d771-ecc5.ngrok.io/api/tccl-bot/webhook/"

bot = telebot.TeleBot(BOT_TOKEN)

# class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
#     # Class will check whether the user is admin or creator in group or not
#     key='is_admin'
#     @staticmethod
#     def check(message: telebot.types.Message):
#         result = bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator']
#         print("check" + result)
#         return result



if __name__ == "__main__":
    settings_module = config("DJANGO_SETTINGS_MODULE", default=None)
    # bot.add_custom_filter(IsAdmin())
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    if sys.argv[1] == "test":
        if settings_module:
            print(
                "Ignoring config('DJANGO_SETTINGS_MODULE') because it's test. "
                "Using 'telegrambot.settings.test'"
            )
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telegrambot.settings.test")
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
