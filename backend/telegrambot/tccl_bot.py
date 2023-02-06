from soupsieve import iselect
from telegrambot.models import Message, TelegramUser

from datetime import datetime, timedelta
import os
from re import M
import telebot
# from config import *
import logging
from manage import bot
from telebot import types,util
from django.http import HttpResponse, JsonResponse
import json
import requests
from os.path import exists
from pathlib import Path
from diffimg import diff
from celery import shared_task


# from PIL import ImageChops, ImageStat,Image

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# BOT_TOKEN = "5495185707:AAFOwex3SfYxz2xhz-KA3GdyLpMVLnicUaI"

logger = telebot.logger

logger.setLevel(logging.ERROR)

ban_reason = ""
warning_max = 30
warning_count = 0
def process_request(request):
    # print(request.data)
    json_string = request.data
    # print("received message: ", json_string)
    if json_string == None or json_string == '':
        return "empty body", 400
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return JsonResponse({"result": "ok" }, status=200)


@bot.chat_member_handler()
def chat_m(message: types.ChatMemberUpdated):
    print("chat_mem_change", message)
    old = message.old_chat_member
    new = message.new_chat_member
    print(old)
    print(new)
#     if new.status == "member":
#         bot.send_message(message.chat.id,"Hello {name}!".format(name=new.user.first_name)) # Welcome message


# When comment has been written, we save data into our db and send user to starting state 1 - START
# @bot.message_handler(func=lambda message: message)
# def _add_comment(message):
#     print("add_comment")


#     user_id = message.from_user.id
#     comment = message.text
#     db_object.execute("INSERT INTO places(address, comment, user_id) VALUES (%s, %s, %s)",
#                       (user_states.ADDRESS, comment, user_id))
#     db_connection.commit()
#     bot.send_message(message.chat.id, "Successfully added!")
#     user_states.update_state(message, user_states.START)

@bot.message_handler(content_types=['photo'])
def photo(message):
    result = bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator'] or message.from_user.username == "GroupAnonymousBot" or message.from_user.first_name == "Telegram"
    if result == True:
        print("admin")
        return
    print(f"\n{bcolors.UNDERLINE}{bcolors.OKCYAN}{message.from_user.first_name} sent photo with caption:  {str( message.caption)} {bcolors.ENDC}\n")
    moderate(message=message)


def checkingUserProfilePhoto(message):
    print(f"checking user photo {message.from_user.id}")

    data = bot.get_user_profile_photos(message.from_user.id)
    # print(data)
    # njson = json.loads(data)
    # print(data['result'])
    user_photos = data.photos
    if len(user_photos) > 0:

        # photos_ids = []
        fileName = user_photos[0][0].file_unique_id
        fileId = user_photos[0][0].file_id

        pic_url = bot.get_file_url(fileId)
        # print(pic_url)
        # Path("/home/user/app/backend/data/directory").mkdir(parents=True, exist_ok=True)

        filePath = '/home/user/app/backend/data/' + fileName + '.jpg'
        if not os.path.exists(filePath):
            with open(filePath, 'w'): pass
        with open(filePath, 'wb') as handle:
            response = requests.get(pic_url, stream=True)

            if not response.ok:
                print(f"{bcolors.FAIL}open file error: {response} {bcolors.ENDC}")

            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
        file_exists = exists(filePath)
        if file_exists:
            result = diff('/home/user/app/backend/data/logo1.jpg', filePath, diff_img_file='/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)
            TelegramUser.objects.filter(user_id=message.from_user.id).update(user_avatar_link= pic_url, profile_score= result)

            if result is not None and result < 0.07:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            else:
                print(f"{bcolors.OKGREEN}diff: {str(result)} {bcolors.ENDC}")
            #compare Bao's Photo
            result = diff('/home/user/app/backend/data/logo3.jpeg', filePath, diff_img_file = '/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)

            TelegramUser.objects.filter(user_id=message.from_user.id).update(user_avatar_link = pic_url, profile_score = result)

            if result is not None and result < 0.07:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            else:
                print(f"{bcolors.OKGREEN}diff: {str(result)} {bcolors.ENDC}")


            result = diff('/home/user/app/backend/data/logo4.jpg', filePath, diff_img_file = '/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)

            TelegramUser.objects.filter(user_id=message.from_user.id).update(user_avatar_link = pic_url, profile_score = result)

            if result is not None and result < 0.07:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            else:
                print(f"{bcolors.OKGREEN}diff: {str(result)} {bcolors.ENDC}")

            os.remove(filePath)

    return False

# def compare_images(img1, img2):
#     """Calculate the difference between two images of the same size
#     by comparing channel values at the pixel level.
#     `delete_diff_file`: removes the diff image after ratio found
#     `diff_img_file`: filename to store diff image

#     Adapted from Nicolas Hahn:
#     https://github.com/nicolashahn/diffimg/blob/master/diffimg/__init__.py
#     """

#     # Don't compare if images are of different modes or different sizes.
#     # if (img1.mode != img2.mode) \
#     #         or (img1.size != img2.size) \
#     #         or (img1.getbands() != img2.getbands()):
#     #     return None

#     # Generate diff image in memory.
#     diff_img = ImageChops.difference(img1, img2)
#     # Calculate difference as a ratio.
#     stat = ImageStat.Stat(diff_img)
#     diff_ratio = sum(stat.mean) / (len(stat.mean) * 255)

#     return diff_ratio

def moderate(message):
    if message.chat.id != -1001724937734:
        print(f"{bcolors.FAIL}wrong chat group: {str(message.chat.id)} {bcolors.ENDC}")
        return
    if checkAndDeleteMessage(message):
        _deleteMessage(message)

    if message.message_id:
        isExist = TelegramUser.objects.filter(user_id=message.from_user.id).exists()
        print(f"checking user {message.from_user.id} exist : {isExist}")
        if isExist is not True:
            TelegramUser.objects.create(user_id=message.from_user.id, firstname=message.from_user.first_name, lastname=message.from_user.last_name, username=message.from_user.username, isBot=message.from_user.is_bot, status = "new", user_avatar_link = "")
            print(f"create user to db")
        else :
            user = TelegramUser.objects.get(user_id=message.from_user.id)
            print(f"checking user status : {message.from_user.id} - {user.status}")
            if user.status == 'banned':
                _deleteMessage(message)

    if processCheckAndBan(message):
        banUser(message, 'message bi cam')
    elif checkingUserProfilePhoto(message):
        banUser(message, 'photo tccl')

def checkAndDeleteMessage(message):
    print(f"{bcolors.WARNING}checkAndDeleteMessage - text: {message.text} - caption: {message.caption}  {bcolors.ENDC}")
    if ("https://t.me/" in f"{message.text} {message.caption}".lower()) and ("https://t.me/tcclchat" not in message.text) and ("https://t.me/tradecoinchienluoc" not in message.text):
        print(f"{bcolors.WARNING}case 1  {bcolors.ENDC}")
        return True
    if "land of conquest"  in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 2  {bcolors.ENDC}")
        return True
    if "follow us" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
        return True
    if "rewards distribution" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 4  {bcolors.ENDC}")
        return True
    if "mẹ" in f"{message.text} {message.caption}".lower() and "mày" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 5  {bcolors.ENDC}")
        return True
    if "lồn" in f"{message.text} {message.caption}".lower() and "mày" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 5  {bcolors.ENDC}")
        return True
    if "địt" in f"{message.text} {message.caption}".lower() and "mày" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 6  {bcolors.ENDC}")
        return True
    isExist = TelegramUser.objects.filter(user_id=message.from_user.id, status='banned' ).exists()
    if isExist:
        print(f"{bcolors.WARNING}case 7  {bcolors.ENDC}")
        return True

def _deleteMessage(message):
    print(f"{bcolors.FAIL}deleted message: {message.text}{bcolors.ENDC}")
    isExist = TelegramUser.objects.filter(user_id=message.from_user.id, status='banned').exists()
    if not isExist:
        print(f"{bcolors.FAIL} _deleteMessage -> reply_to {message} {bcolors.ENDC}")
        bot.reply_to(message, "‼️ Tin nhắn " + message.from_user.first_name + " sử dụng từ ngữ bị cấm. ‼️")

    deleteMessageTask.apply_async(kwargs={ "chat_id": message.chat.id,'message_id': message.message_id}, countdown=5)
    bot.send_message("-1001349899890", f"deleted message: {message.text} - {message.from_user.id} {message.from_user.first_name}" )

@shared_task
def deleteMessageTask(chat_id, message_id):
    print("deleteMessageTask")
    print(f"{bcolors.OKGREEN}deleted message: {chat_id} {message_id}{bcolors.ENDC}")
    bot.delete_message(chat_id,message_id=message_id)

def processCheckAndBan(message):
    userId = message.from_user.id
    chatId = message.chat.id
    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    print(f"{bcolors.WARNING}processCheckAndBan - text: {message.text} - caption: {message.caption}  {bcolors.ENDC} \nUser info: {firstName} {lastName} -userId: {userId} -chatId: {chatId}".lower())
    if "NhómVIP".lower() in f"{message.text} {message.caption}".lower() or "ai chưa tham gia" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 1  {bcolors.ENDC}")
        return True
    # # if "futt + spot" in f"{message.text} {message.caption}".lower():
    #     return True
    if "whaless" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 2  {bcolors.ENDC}")
        return True

    if "anh em" in f"{message.text} {message.caption}".lower() and  "vào nhóm" in f"{message.text} {message.caption}".lower() and  "vip" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
        return True
    if "vào" in f"{message.text} {message.caption}".lower() and  "nhóm" in f"{message.text} {message.caption}".lower() and  "vip" in f"{message.text} {message.caption}".lower() and  "inbox" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 20  {bcolors.ENDC}")
        return True
    if "vào" in f"{message.text} {message.caption}".lower() and  "nhóm" in f"{message.text} {message.caption}".lower() and  "vlp" in f"{message.text} {message.caption}".lower() and  "inbox" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 220  {bcolors.ENDC}")
        return True
    if "vào" in f"{message.text} {message.caption}".lower() and  "nhóm" in f"{message.text} {message.caption}".lower() and  "v1p" in f"{message.text} {message.caption}".lower() and  "inbox" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 220  {bcolors.ENDC}")
        return True
    if  "vào" in f"{message.text} {message.caption}".lower() and "nhóm" in f"{message.text} {message.caption}".lower() and  "vip" in f"{message.text} {message.caption}".lower() and  "ib" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 21  {bcolors.ENDC}")
        return True

    if "TCCL Community".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 4  {bcolors.ENDC}")
        return True
    if "TCCL".lower() in f"{firstName} {lastName}".lower():
        print(f"{bcolors.WARNING}case 5  {bcolors.ENDC}")
        return True
    if ".".lower() == f"{firstName}".lower() and None == lastName:
        print(f"{bcolors.WARNING}case 6  {bcolors.ENDC}")
        return True
    if "..".lower() == f"{firstName}".lower() and None == lastName:
        print(f"{bcolors.WARNING}case 7  {bcolors.ENDC}")
        return True
    if "...".lower() == f"{firstName}".lower() and None == lastName:
        print(f"{bcolors.WARNING}case 8  {bcolors.ENDC}")
        return True
    if "tccl" in f"{username}":
        print(f"{bcolors.WARNING}case 9  {bcolors.ENDC}")
        return True
    if "Đỗ Bảo".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 10  {bcolors.ENDC}")
        return True
    if "Đỗ Bảo".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 10  {bcolors.ENDC}")
        return True
    if "Bảo Đỗ".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 11  {bcolors.ENDC}")
        return True
    if "Bảo".lower() in f"{firstName}".lower() and  "Đỗ".lower() in f"{firstName}".lower():
        print(f"{bcolors.WARNING}case 20  {bcolors.ENDC}")
        return True
    if "Bả0".lower() in f"{firstName}".lower() and  "Đỗ".lower() in f"{firstName}".lower():
        print(f"{bcolors.WARNING}case 202  {bcolors.ENDC}")
        return True
    if "Bả0".lower() in f"{firstName.replace('.','')}".lower() and  "Đỗ".lower() in f"{firstName.replace('.','')}".lower():
        print(f"{bcolors.WARNING}case 201  {bcolors.ENDC}")
        return True
    if "Trung Kim Son".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 12  {bcolors.ENDC}")
        return True
    if "Trade Coin Chiến Lược".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 13  {bcolors.ENDC}")
        return True
    if "Trade".lower() in f"{firstName} {lastName}".lower() and  "Chiến Lược".lower() in f"{firstName} {lastName}".lower():
        print(f"{bcolors.WARNING}case 14  {bcolors.ENDC}")
        return True
    if "Trade".lower() in f"{firstName} {lastName}".lower() and  "Lược".lower() in f"{firstName} {lastName}".lower():
        print(f"{bcolors.WARNING}case 15  {bcolors.ENDC}")
        return True
    if "Trade".lower() in f"{firstName} {lastName}".lower() and  "Iược".lower() in f"{firstName} {lastName}".lower():
        print(f"{bcolors.WARNING}case 16  {bcolors.ENDC}")
        return True
    if "admin none" == f"{firstName} {lastName}".lower() or "none admin" == f"{firstName} {lastName}".lower():
        print(f"{bcolors.WARNING}case 17  {bcolors.ENDC}")
        return True
    if "admln" in f"{firstName} {lastName}".lower():
        print(f"{bcolors.WARNING}case 18  {bcolors.ENDC}")
        return True
    if "glcapital1" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 19  {bcolors.ENDC}")
        return True

    return False

def banUser(message, error_text):
    print("start ban user")
    chatId = message.chat.id
    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    userId = message.from_user.id

    deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': message.message_id}, countdown=3)

    bot.ban_chat_member(chatId, userId)

    isExist = TelegramUser.objects.filter(user_id=message.from_user.id, status='banned').exists()
    print(f"banned ?: {isExist}")
    if not isExist:
        print(f"{bcolors.FAIL} banUser -> reply_to {message} {bcolors.ENDC}")
        bot.reply_to(message, "‼️" + firstName + " bị ban vì hành vi spam / lừa đảo‼️\n\n👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG thu khoản phí nào.\n👉 ⚠️Các admin KHÔNG bao giờ DM trước.\n👉 Hãy luôn cẩn thận với tài sản 💰 của mình.")

    bot.send_message("-1001349899890", "Đã ban user id: " + str(userId) + " - firstName: "+ f"{firstName}" + " - lastname: "+ f"{lastName}" + f" - message: {message.id} {message.text} " + f" - caption: {message.caption}")
    print(TelegramUser.objects.filter(user_id=userId))
    TelegramUser.objects.filter(user_id=userId).update(status='banned', ban_reason=error_text)
    print(f"{bcolors.OKGREEN} banned {userId} {firstName} {bcolors.ENDC}")



@bot.message_handler(commands=['report'])
def report(message):

    if message.reply_to_message:

        firstname = message.reply_to_message.from_user.first_name
        last_name = message.reply_to_message.from_user.last_name
        uid = message.reply_to_message.from_user.id
        mess = message.reply_to_message.text
        messId = message.reply_to_message.id
        name =  f" {firstname} {last_name}"
        reportName = message.from_user.first_name
        print (f"{bcolors.BOLD}reported  {mess} {bcolors.ENDC}")
        bot.send_message("-1001349899890", f"{reportName} reported {uid} - {name}:  mess :{messId} {mess}" )



@bot.message_handler(commands=['ban_user'])
def manualbanUser(message):
    if message.chat.id != -1001349899890:
        print(f"{bcolors.FAIL}wrong chat group: {str(message.chat.id)} {bcolors.ENDC}")
        return
    print(f"manualbanUser {message}")
    userId = message.text.replace("/ban_user ", "")
    bot.ban_chat_member(-1001724937734, userId)
    bot.kick_chat_member(chat_id =-1001724937734,user_id=userId)

    bot.send_message("-1001349899890", "Đã ban user id: " + f" {userId}")

@bot.message_handler(commands=['delete_message'])
def manualDeleteMessage(message):
    if message.chat.id != -1001349899890:
        print(f"{bcolors.FAIL}wrong chat group: {str(message.chat.id)} {bcolors.ENDC}")
        return
    print(f"deleteMessage {message.text}")
    message_id = message.text.replace("/delete_message ", "")
    # bot.delete_message(-1001724937734, message_id)
    deleteMessageTask.apply_async(kwargs={ "chat_id": -1001724937734,'message_id': message_id}, countdown=3)
    print(f"{bcolors.FAIL}deleted message  : {str(message_id)} {bcolors.ENDC}")

    bot.send_message("-1001349899890", "Đã Delete Message id: " + f" {message_id}")

@bot.message_handler(commands=['unban_user'])
def unban_user(message):
    if message.chat.id != -1001349899890:
        print(f"{bcolors.FAIL}wrong chat group: {str(message.chat.id)} {bcolors.ENDC}")
        return
    userId = message.text.replace("/unban_user ", "")
    bot.unban_chat_member(-1001724937734, userId)
    bot.send_message("-1001349899890", "Đã Mở UserId:  " + f" {userId}")


@bot.message_handler()
def allMessage(message):
    result = bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator'] or message.from_user.username == "GroupAnonymousBot" or message.from_user.first_name == "Telegram" or message.from_user.first_name == "Channel"
    if result == True:
        print("admin")
        return
    print(f"\n{bcolors.UNDERLINE}{bcolors.OKCYAN}{message.from_user.first_name} sent message:  {str( message.text)} {bcolors.ENDC} {warning_count}\n")
    warning_count += 1
    if warning_count >= warning_max:
        warning_count = 0
        bot.reply_to(message, "‼️ 🆘💢 Cảnh báo lừa đảo 💢🆘 ‼️\n\n👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG thu khoản phí nào.\n👉 ⚠️Các admin KHÔNG bao giờ DM trước.\n👉 Hãy luôn cẩn thận với tài sản của mình.🦮🦮🦮")

    moderate(message=message)

@bot.message_handler( content_types=[
    "new_chat_members"
])
def new_chat_members(message):
    print("WELCOME", message)



@bot.message_handler(content_types=[
    "left_chat_member"
])
def left_chat_member(message):
    userId = message.from_user.id
    chatId = message.chat.id

    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    bot.send_message("-1001349899890", "User left : " + f" id {userId}  firstName {firstName} userName {username}")

@bot.message_handler(commands=['reset'])
def _reset(message):
    print("_reset")
#     user_id = message.from_user.id
#     db_object.execute("DELETE FROM places WHERE user_id = {}".format(user_id))
#     db_connection.commit()
#     bot.send_message(message.chat.id, "All your saved addresses have been deleted")






