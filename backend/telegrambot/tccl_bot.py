from soupsieve import iselect
from telegrambot.models import Message, TelegramUser
import uuid

from datetime import datetime, timedelta
import os
import cv2
import re
from re import M
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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

import pytesseract
from PIL import Image
import cloudmersive_image_api_client
from cloudmersive_image_api_client.rest import ApiException

configuration = cloudmersive_image_api_client.Configuration()
configuration.api_key['Apikey'] = '9f957878-68e3-4b7b-ba1b-5c960f445002'
api_instance = cloudmersive_image_api_client.NsfwApi(cloudmersive_image_api_client.ApiClient(configuration))

photoUrl = ""
MSG_COUNTER = 0
MSG_MAX = 20

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
warning_max = 20
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
    print("chat_mem_change_old",old)
    print("chat_mem_change_new", new)

@bot.message_handler(content_types=['photo'])
def photo(message):
    global photoUrl
    result = bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator'] or message.from_user.username == "GroupAnonymousBot" or message.from_user.first_name == "Telegram"
    if result == True:
        print("admin")
        return
    print(f"\n{bcolors.UNDERLINE}{bcolors.OKCYAN}{message.from_user.first_name} sent photo with caption:  {str( message.caption)} {bcolors.ENDC}\n")
    moderate(message=message)


    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
    full_name = f"{first_name}{last_name}"

    res = checkingPhoto(message=message)
    if res == 1:
        # userId = message.from_user.id
        # chatId = message.chat.id
        # # deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': message.message_id}, countdown=3)
        # keyboard = InlineKeyboardMarkup()

        # delete_button = InlineKeyboardButton('🔴 Xóa', callback_data=f'delete {message.from_user.id} {message.message_id}', color= 'red')
        # ban_button = InlineKeyboardButton('🚫 Ban ' + full_name, callback_data=f'ban {message.from_user.id}', color= 'red')

        # clear_button = InlineKeyboardButton('Sai', callback_data=f'invalid {message.from_user.id}', color= 'grey')

        # keyboard.add(delete_button, ban_button, clear_button)
        # bot.reply_to(message, "‼️ Hệ thống nhận diện hình ảnh này có nội dung SCAM / LỪA ĐẢO.‼️ Chờ admin xác nhận" , reply_markup=keyboard)

        # bot.send_message("-1001349899890", "IMAGE SCAN - SCAM BẰNG HÌNH")
        # try:
        #     bot.send_photo("-1001349899890", photo=open(photoUrl, 'rb'))
        # except Exception as e:
        #     print("Error sending photo:", e)
        print("stop")
    elif res == 3:
        userId = message.from_user.id
        chatId = message.chat.id
        deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': message.message_id}, countdown=3)
        # print("photoUrl")
        # print(photoUrl)
        try:
            bot.ban_chat_member(chatId, userId)
        except Exception as e:
            print("Error :", e)

        bot.reply_to(message, "‼️ "+ full_name + " bị ban vì post hình ảnh có nội dung SCAM / LỪA ĐẢO. ‼️" + "\n\n👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG THU khoản phí nào.\n👉 ⚠️Các admin KHÔNG BAO GIỜ NHẮN TIN trước.\n👉 ⚠️ Bất kỳ ai đều có thể đổi tên và avatar giống admin để chat với bạn\n👉 Hãy luôn CẨN THẬN với tài sản của mình.")
        bot.send_message("-1001349899890", "IMAGE SCAN - SCAM BẰNG HÌNH")
        try:
            bot.send_photo("-1001349899890", photo=open(photoUrl, 'rb'))
        except Exception as e:
            print("Error sending photo:", e)

    elif res == 2:
        userId = message.from_user.id
        chatId = message.chat.id
        # deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': message.message_id}, countdown=3)
        # bot.reply_to(message, "‼️ Tin nhắn bị xóa / vì sử dụng hình ảnh nhạy cảm. ‼️")
        keyboard = InlineKeyboardMarkup()
        delete_button = InlineKeyboardButton('🔴 Xóa', callback_data=f'delete {message.from_user.id} {message.message_id}', color= 'red')
        ban_button = InlineKeyboardButton('🚫 Ban ' + full_name, callback_data=f'ban {message.from_user.id}', color= 'red')
        clear_button = InlineKeyboardButton('Sai', callback_data=f'invalid {message.from_user.id}', color= 'grey')
        keyboard.add(delete_button, ban_button, clear_button)
        bot.reply_to(message, "‼️ Hệ thống nhận diện hình ảnh có nội dung 18+.‼️ Chờ admin xác nhận" , reply_markup=keyboard)
        bot.send_message("-1001349899890", "IMAGE SCAN - Nudity detected")
        try:
            bot.send_photo("-1001349899890", photo=open(photoUrl, 'rb'))
        except Exception as e:
            print("Error sending photo:", e)
    else:
        print("check photo and it is valid")

@bot.callback_query_handler(func=lambda call: True)
def handle_button_callback(call):
    result = bot.get_chat_member(call.message.chat.id, call.message.from_user.id).status in ['administrator','creator'] or call.message.from_user.username == "GroupAnonymousBot" or call.message.from_user.first_name == "Telegram" or call.message.from_user.first_name == "Channel"
    if result == False:
        bot.answer_callback_query(call.id, text='Chức năng chỉ dành cho admin', show_alert=True)
        return
    # Check which button was clicked and take appropriate action
    if call.data.startswith('delete'):
        _, user_id, message_id = call.data.split(' ')
        bot.delete_message(call.message.chat.id, message_id)
        bot.answer_callback_query(call.id, text='Message deleted.')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.reply_to(call.message, "  🗣️ 🗣️ 👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG THU khoản phí nào.\n👉 ⚠️Các admin KHÔNG BAO GIỜ NHẮN TIN trước.\n👉 ⚠️ Bất kỳ ai đều có thể đổi tên và avatar giống admin để chat với bạn\n👉 Hãy luôn CẨN THẬN với tài sản của mình.")

    elif call.data.startswith('ban'):
        _, user_id = call.data.split(' ')
        bot.ban_chat_member(call.message.chat.id, user_id)
        bot.answer_callback_query(call.id, text='User banned.')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.reply_to(call.message, "  🗣️ 🗣️ \n\n👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG THU khoản phí nào.\n👉 ⚠️Các admin KHÔNG BAO GIỜ NHẮN TIN trước.\n👉 ⚠️ Bất kỳ ai đều có thể đổi tên và avatar giống admin để chat với bạn\n👉 Hãy luôn CẨN THẬN với tài sản của mình.")


    elif call.data.startswith('invalid'):
        if call.message.message_id:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        else:
            bot.answer_callback_query(call.id, text='There is no message to delete.')

@bot.message_handler(func=lambda message: message.new_chat_members and bot.get_me().username in [user.username for user in message.new_chat_members])
def handle_new_member(message):
    new_name = message.new_chat_member.first_name
    print(f"Bot name has been updated to {new_name}")
    bot.send_message("-1001349899890", "TEST - Detect Change Name  - user id: " + f"{new_name}")

@shared_task
def processChecUserProfile (userId, chatId, messageId):
    if checkingUserProfilePhoto(userId, "task"):
        deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': messageId}, countdown=3)
        bot.ban_chat_member(chatId, userId)
        bot.send_message("-1001349899890", "Đã ban user id: " + str(userId))

def checkingUserProfilePhoto(userId, mode):
    print(f"checking user photo {userId}")

    data = bot.get_user_profile_photos(userId)
    print(data)
    # njson = json.loads(data)
    # print(data['result'])
    user_photos = data.photos
    if len(user_photos) > 0:
        print("len(user_photos) > 0")

        # photos_ids = []
        fileName = user_photos[0][0].file_unique_id
        fileId = user_photos[0][0].file_id

        pic_url = bot.get_file_url(fileId)
        print(f"{bcolors.OKGREEN} {mode} - avatar - {pic_url}{bcolors.ENDC}")
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
            TelegramUser.objects.filter(user_id=userId).update(user_avatar_link= pic_url, profile_score= result)

            if result is not None and result < 0.039:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            else:
                print(f"{bcolors.OKGREEN}{mode} - diff logo1 - {userId}: {str(result)} {bcolors.ENDC}")
            #compare Bao's Photo
            result = diff('/home/user/app/backend/data/logo3.jpeg', filePath, diff_img_file = '/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)

            TelegramUser.objects.filter(user_id=userId).update(user_avatar_link = pic_url, profile_score = result)

            if result is not None and result < 0.039:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            else:
                print(f"{bcolors.OKGREEN}{mode} - diff logo2 - {userId}: {str(result)} {bcolors.ENDC}")


            result = diff('/home/user/app/backend/data/logo4.jpg', filePath, diff_img_file = '/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)

            TelegramUser.objects.filter(user_id=userId).update(user_avatar_link = pic_url, profile_score = result)

            if result is not None and result < 0.047:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            else:
                print(f"{bcolors.OKGREEN}{mode} - diff logo3 - {userId}: {str(result)} {bcolors.ENDC}")

            #tèo

            result = diff('/home/user/app/backend/data/teo1.jpg', filePath, diff_img_file = '/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)

            TelegramUser.objects.filter(user_id=userId).update(user_avatar_link = pic_url, profile_score = result)

            if result is not None and result < 0.039:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            # else:
                # print(f"{bcolors.OKGREEN}diff: {str(result)} {bcolors.ENDC}")

            result = diff('/home/user/app/backend/data/teo2.jpg', filePath, diff_img_file = '/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)

            TelegramUser.objects.filter(user_id=userId).update(user_avatar_link = pic_url, profile_score = result)

            if result is not None and result < 0.039:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            # else:
                # print(f"{bcolors.OKGREEN}diff: {str(result)} {bcolors.ENDC}")

            result = diff('/home/user/app/backend/data/teo3.jpg', filePath, diff_img_file = '/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)

            TelegramUser.objects.filter(user_id=userId).update(user_avatar_link = pic_url, profile_score = result)

            if result is not None and result < 0.039:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            # else:
                # print(f"{bcolors.OKGREEN}diff: {str(result)} {bcolors.ENDC}")


            result = diff('/home/user/app/backend/data/thinh.jpg', filePath, diff_img_file = '/home/user/app/backend/data/' + 'diff_img' + fileName + '.png', delete_diff_file=True)

            TelegramUser.objects.filter(user_id=userId).update(user_avatar_link = pic_url, profile_score = result)

            if result is not None and result < 0.039:
                print(f"{bcolors.FAIL}detected use TCCL logo: {str(result)} {bcolors.ENDC}")
                os.remove(filePath)
                return True
            # else:
                # print(f"{bcolors.OKGREEN}diff: {str(result)} {bcolors.ENDC}")

            os.remove(filePath)

    return False


def checkingPhoto(message):
    global photoUrl
    print(f"checking photo")

    # data = bot.get_user_profile_photos(message.from_user.id)
    # print(data)
    # njson = json.loads(data)
    # print(data['result'])
    file_id = message.photo[-1].file_id
    # print(message.photo)
    if message.photo != None and message.photo[-1] != None:
        # print("photo existed")
        # photos_ids = []
        # fileName = message.photo[-1].file_unique_id
        fileId = message.photo[-1].file_id
        pic_url = bot.get_file_url(fileId)

        file_info = bot.get_file(file_id)
        # print(pic_url)
        # print(file_info)
        # downloaded_file = bot.download_file(file_info.file_path)
        file_extension = '.' + file_info.file_path.split('.')[-1]
        fileName = str(uuid.uuid4()) + file_extension


        # Path("/home/user/app/backend/data/directory").mkdir(parents=True, exist_ok=True)

        filePath = '/home/user/app/backend/data/' + fileName
        photoUrl = filePath
        # print(filePath)
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
        # print(file_exists)
        if file_exists:

            img2 = cv2.imread(filePath, 1)
            # img = Image.open(filePath)


            img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)


            # Use pytesseract to convert the image to text
            text = pytesseract.image_to_string(img, lang="eng")
            print("converted to text: ", text)
            if "chưa tham gia" in f"{message.text} {message.caption}".lower():
                return 3
            elif "Futures ai tham gia" in text or ( "tham gia" in text and "nbox" in text):
                print("The text contains 'Futures ai tham gia'")
                return 3
            elif "cần bán" in text or "cần ra đi" in text:
                print("The text contains 'Futures ai tham gia'")
                return 3
            else:
                print("The text does not contain 'Futures ai tham gia'")

            pattern = r'\b\d{4,}%'
            # Use the regex search function to find any percentage value greater than or equal to 1000 in the text
            match = re.search(pattern, text)

            # If a percentage value greater than or equal to 1000 is found, print it
            if match:
                print(f"Percentage value greater than or equal to 1000 found: {match.group(0)}")
                os.remove(filePath)
                return 1



            # url = 'https://api.deepai.org/api/nsfw-detector'
            # headers = {
            #     'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'
            # }
            # response = requests.post(
            #     url,
            #     files={
            #         'image': open(filePath, 'rb'),
            #     },
            #     headers=headers
            # )
            # print(response.text)
            # result = json.loads(response.text)
            # if result['output']['nsfw_score'] > 0.7:
            #     print('Nudity detected')
            #     os.remove(filePath)
            #     return 2

            img = cv2.imread(filePath)

            # Load the pre-trained neural network model for nudity detection
            model = cv2.dnn.readNetFromCaffe('/home/user/app/backend/data/deploy.prototxt', '/home/user/app/backend/data/res10_300x300_ssd_iter_140000.caffemodel')

            # Define the classes for the neural network model
            classes = ['background', 'person']
            if img is None or img.shape[0] == 0 or img.shape[1] == 0:
                raise ValueError('Invalid input image')
            # Convert the image to a blob
            input_size = (300, 300)

            blob = cv2.dnn.blobFromImage(img, 1.0, input_size, (104.0, 177.0, 123.0))

            # Set the input for the neural network model
            model.setInput(blob)

            # Perform forward pass to get the output from the neural network model
            output = model.forward()
            print('Checking if any of the detected objects are classified as a person')
            # Check if any of the detected objects are classified as a person
            for i in range(output.shape[2]):
                confidence = output[0, 0, i, 2]
                # print(confidence)
                if confidence > 0.8 and classes[int(output[0, 0, i, 1])] == 'person':
                    print('Nudity detected')
                    # os.remove(filePath)
                    # return 2
                    try:
                        # Classify an image for nudity
                        api_response = api_instance.nsfw_classify(filePath)
                        # print(api_response)
                        # njson = json.loads(api_response)
                        # print(njson)
                        nsfw_score = api_response.score
                        classification_outcome = api_response.classification_outcome
                        print(nsfw_score, classification_outcome)
                        if nsfw_score > 0.8 or classification_outcome == "UnsafeContent_HighProbability":
                            print('Nudity detected')
                            os.remove(filePath)
                            return 2
                    except ApiException as e:
                        print("Exception when calling ImageNudityApi->image_nudity_classify: %s\n" % e)
                    os.remove(filePath)
                    print('No Nudity detected')
                    return -1
    # print(-1)
    return -1

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
@shared_task
def moderateMessageTask(message):
    print("message")
    print("Received message:", message.text)
    print("From user:", message.from_user.username)

    # print(f"{bcolors.WARNING}received message - text: {message.text} - caption: {message.caption}  {bcolors.ENDC}")

def moderate(message):
    if message.chat.id != -1001724937734:
        print(f"{bcolors.FAIL}wrong chat group: {str(message.chat.id)} {bcolors.ENDC}")
        return

    print(f"{bcolors.WARNING}received message - text: {message.text} - caption: {message.caption}  {bcolors.ENDC}")
    if checkAndDeleteMessage(message):
        _deleteMessage(message)

    if message.message_id:
        isExist = TelegramUser.objects.filter(user_id=message.from_user.id, firstname=message.from_user.first_name, lastname=message.from_user.last_name ).exists()
        print(f"checking user {message.from_user.id} exist : {isExist}")
        isPhoto = False
        if message.text == None:
            isPhoto = True
        if isExist is not True or isPhoto is True:
            if isExist is not True and isPhoto is not True:
                TelegramUser.objects.create(user_id=message.from_user.id, firstname=message.from_user.first_name, lastname=message.from_user.last_name, username=message.from_user.username, isBot=message.from_user.is_bot, status = "new", user_avatar_link = "")
                print(f"add user {message.from_user.id} to DB")
            print(f"step 2")
            processChecUserProfile.apply_async(kwargs={ "userId": message.from_user.id, "chatId": message.chat.id, "messageId": message.message_id}, countdown=1)

            if checkingUserProfilePhoto(message.from_user.id, "function"):
                banUser(message, 'message bi cam')
                return

            if processCheckAndBan(message):
                banUser(message, 'message bi cam')
                return
        # else :
            # user = TelegramUser.objects.get(user_id=message.from_user.id)
            # print(f"checking user status : {message.from_user.id} - {user.status}")
            # if user.status == 'banned':
            #     _deleteMessage(message)
            #     clearDBRecord.apply_async(kwargs={ "user_id": message.from_user.id}, countdown=10)
            # first_name = message.from_user.first_name
            # last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
            # full_name = f"{first_name}{last_name}"
            # if user.fir


def checkAndDeleteMessage(message):
    print(f"{bcolors.WARNING}checkAndDeleteMessage{bcolors.ENDC}")
    if ("https://t.me/" in f"{message.text} {message.caption}".lower()) and ("https://t.me/tcclroom" not in message.text) and ("https://t.me/tcclchat" not in message.text) and ("https://t.me/tradecoinchienluoc" not in message.text):
        print(f"{bcolors.WARNING}case 1  {bcolors.ENDC}")
        return True
    if ("t.me" in f"{message.text} {message.caption}".lower()) and ("https://t.me/tcclroom" not in message.text) and ("https://t.me/tcclchat" not in message.text) and ("https://t.me/tradecoinchienluoc" not in message.text):
        print(f"{bcolors.WARNING}case 12222  {bcolors.ENDC}")
        return True
    if "land of conquest"  in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 2  {bcolors.ENDC}")
        return True
    if "join" in f"{message.text} {message.caption}".lower() and "@" in f"{message.text} {message.caption}".lower():
        return True
    if "@tradinghoiquan" in f"{message.text} {message.caption}".lower():
        return True
    if "ae vào"  in f"{message.text} {message.caption}".lower() and "@" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 2  {bcolors.ENDC}")
        return True
    if "crypto"  in f"{message.text} {message.caption}".lower() and "@" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 2  {bcolors.ENDC}")
        return True
    if "follow us" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
        return True
    if "rewards distribution" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 4  {bcolors.ENDC}")
        return True
    if "@RyanNguyenVBC" in f"{message.text} {message.caption}":
        return True
    if "opensea.io" in f"{message.text} {message.caption}".lower():
        return True
    if "vinacoin.live" in f"{message.text} {message.caption}":
        return True
    # if "mẹ" in f"{message.text} {message.caption}".lower() and "mày" in f"{message.text} {message.caption}".lower():
    #     print(f"{bcolors.WARNING}case 5  {bcolors.ENDC}")
    #     return True
    # if "lồn" in f"{message.text} {message.caption}".lower() and "mày" in f"{message.text} {message.caption}".lower():
    #     print(f"{bcolors.WARNING}case 5  {bcolors.ENDC}")
    #     return True
    # if "địt" in f"{message.text} {message.caption}".lower() and "mày" in f"{message.text} {message.caption}".lower():
    #     print(f"{bcolors.WARNING}case 6  {bcolors.ENDC}")
    #     return True
    # isExist = TelegramUser.objects.filter(user_id=message.from_user.id, status='banned' ).exists()
    # if isExist:
    #     print(f"{bcolors.WARNING}case 7  {bcolors.ENDC}")
    #     return True
    return False

def _deleteMessage(message):
    print(f"{bcolors.FAIL}deleted message: {message.text}{bcolors.ENDC}")
    isExist = TelegramUser.objects.filter(user_id=message.from_user.id, status='banned').exists()
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
    full_name = f"{first_name}{last_name}"
    if not isExist:
        print(f"{bcolors.FAIL} _deleteMessage -> reply_to {message} {bcolors.ENDC}")
        bot.reply_to(message, "‼️ Tin nhắn " + full_name + " sử dụng từ ngữ bị cấm. ‼️")

    deleteMessageTask.apply_async(kwargs={ "chat_id": message.chat.id,'message_id': message.message_id}, countdown=1)
    bot.send_message("-1001349899890", f"deleted message: {message.text} {message. caption}- {message.from_user.id} {full_name}" )

@shared_task
def deleteMessageTask(chat_id, message_id):
    print("delete Message Task")
    print(f"{bcolors.OKGREEN}deleted message: {chat_id} {message_id}{bcolors.ENDC}")
    bot.delete_message(chat_id,message_id=message_id)
@shared_task
def clearDBRecord(user_id):
    TelegramUser.objects.filter(user_id=user_id).delete()

def processCheckAndBan(message):

    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    print(f"{bcolors.WARNING}processCheckAndBan {firstName} - {lastName} - {username} {bcolors.ENDC}")

    if "NhómVIP".lower() in f"{message.text} {message.caption}".lower() or "ai chưa tham gia" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 1  {bcolors.ENDC}")
        return True
    if "thông báo" in f"{message.text} {message.caption}".lower() and  "anh em" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 33  {bcolors.ENDC}")
        return True
    # # if "futt + spot" in f"{message.text} {message.caption}".lower():
    #     return True
    if len(message.text) < 60:
        if "whaless" in f"{message.text} {message.caption}".lower():
            print(f"{bcolors.WARNING}case 2  {bcolors.ENDC}")
            return True

        if "thông báo nhóm" in f"{message.text} {message.caption}".lower():
            print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
            return True
        if "anh em" in f"{message.text} {message.caption}".lower() and  "vào nhóm" in f"{message.text} {message.caption}".lower() and  "vip" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
            return True
        if "ai" in f"{message.text} {message.caption}".lower() and  "vào nhóm" in f"{message.text} {message.caption}".lower() and  "liên hệ" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
            return True
        if "anh em" in f"{message.text} {message.caption}".lower() and  "vào nhóm" in f"{message.text} {message.caption}".lower() and  "liên hệ" in f"{message.text} {message.caption}".lower() :
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
            print(f"{bcolors.WARNING}case 213  {bcolors.ENDC}")
            return True
        if  "ai" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gia" in f"{message.text} {message.caption}".lower() and  "ib" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 214  {bcolors.ENDC}")
            return True
        if  "ai" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gia" in f"{message.text} {message.caption}".lower() and  "liên hệ" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 215  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gia" in f"{message.text} {message.caption}".lower() and  "ib" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 216  {bcolors.ENDC}")
            return True
        if  "fut" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gia" in f"{message.text} {message.caption}".lower() and  "ib" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 217  {bcolors.ENDC}")
            return True
        if  "fut" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gia" in f"{message.text} {message.caption}".lower() and  "liên hệ" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 218  {bcolors.ENDC}")
            return True
        if  "fut" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gia" in f"{message.text} {message.caption}".lower() and  "admin" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 219  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gia" in f"{message.text} {message.caption}".lower() and  "lb" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 220  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gla" in f"{message.text} {message.caption}".lower() and  "lb" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 221  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gia" in f"{message.text} {message.caption}".lower() and  "ln" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 222  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and  "gla" in f"{message.text} {message.caption}".lower() and  "ln" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 223  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "tham" in f"{message.text} {message.caption}".lower() and "ad" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 224  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "anh em" in f"{message.text} {message.caption}".lower() and "@" in f"{message.text} {message.caption}".lower():
            print(f"{bcolors.WARNING}case 225  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "inbox" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 226  {bcolors.ENDC}")
            return True
        if  "futu" in f"{message.text} {message.caption}".lower() and "lnbox" in f"{message.text} {message.caption}".lower() :
            print(f"{bcolors.WARNING}case 227  {bcolors.ENDC}")
            return True

        if "TCCL Community".lower() in f"{firstName} {lastName}".lower() :
            print(f"{bcolors.WARNING}case 4  {bcolors.ENDC}")
            return True
        if "TCCL".lower() in f"{firstName} {lastName}".lower():
            print(f"{bcolors.WARNING}case 5  {bcolors.ENDC}")
            return True
    # if ".".lower() == f"{firstName}".lower() and None == lastName:
    #     print(f"{bcolors.WARNING}case 6  {bcolors.ENDC}")
    #     return True
    # if "..".lower() == f"{firstName}".lower() and None == lastName:
    #     print(f"{bcolors.WARNING}case 7  {bcolors.ENDC}")
    #     return True
    # if "...".lower() == f"{firstName}".lower() and None == lastName:
    #     print(f"{bcolors.WARNING}case 8  {bcolors.ENDC}")
    #     return True
    if "tccl" in f"{username}":
        print(f"{bcolors.WARNING}case 9  {bcolors.ENDC}")
        return True
    if "Đỗ Bảo".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 10  {bcolors.ENDC}")
        return True
    if "Đỗ Báo".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 10  {bcolors.ENDC}")
        return True
    if "Đỗ Bảo".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 10  {bcolors.ENDC}")
        return True
    if "Đỗ Bả0".lower() in f"{firstName} {lastName}".lower() :
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
    if "Bả0".lower() in f"{lastName}".lower() and  "Đỗ".lower() in f"{firstName}".lower():
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
    if "aecryptodhchat" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 29  {bcolors.ENDC}")
        return True
    if "qua đây trao đổi với mình" in f"{message.text} {message.caption}".lower() and "@" in f"{message.text} {message.caption}".lower():
        print(f"{bcolors.WARNING}case 30  {bcolors.ENDC}")
        return True

    if "chưa vào" in f"{message.text} {message.caption}".lower() and  "nhắn ad" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 31  {bcolors.ENDC}")
        return True

    if "Đỗ Bả".lower() in f"{firstName} {lastName}".lower() :
        print(f"{bcolors.WARNING}case 10  {bcolors.ENDC}")
        return True
    if "chưa tham" in f"{message.text} {message.caption}".lower() and "nhóm" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 10111  {bcolors.ENDC}")
        return True
    if "chưa tham" in f"{message.text} {message.caption}".lower() and "ad" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 10112  {bcolors.ENDC}")
        return True
    if "buy and wait" in f"{message.text}{message.caption}".lower() and "@" in f"{message.text} {message.caption}".lower() :
        print(f"{bcolors.WARNING}case 10113  {bcolors.ENDC}")
        return True
    print("no case")
    return False

def banUser(message, error_text):
    print("start ban user")
    chatId = message.chat.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
    full_name = f"{first_name}{last_name}"
    userId = message.from_user.id

    deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': message.message_id}, countdown=3)

    bot.ban_chat_member(chatId, userId)

    isExist = TelegramUser.objects.filter(user_id=message.from_user.id, status='banned').exists()
    print(f"banned ?: {isExist}")
    if not isExist:
        print(f"{bcolors.FAIL} banUser -> reply_to {message} {bcolors.ENDC}")
        bot.reply_to(message, "‼️ " + full_name + " bị ban vì hành vi SCAM / LỪA ĐẢO ‼️\n\n👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG THU khoản phí nào.\n👉 ⚠️Các admin KHÔNG BAO GIỜ NHẮN TIN trước.\n👉 ⚠️ Bất kỳ ai đều có thể đổi tên và avatar giống admin để chat với bạn\n👉 Hãy luôn CẨN THẬN với tài sản của mình.")

    bot.send_message("-1001349899890", "Đã ban user id: " + str(userId) + " - firstName: "+ f"{full_name}" + f" - message: {message.id} {message.text} " + f" - caption: {message.caption}")
    print(TelegramUser.objects.filter(user_id=userId))
    TelegramUser.objects.filter(user_id=userId).update(status='banned', ban_reason=error_text)
    print(f"{bcolors.OKGREEN} banned {userId} {full_name} {bcolors.ENDC}")



@bot.message_handler(commands=['report'])
def report(message):

    if message.reply_to_message:

        firstname = message.reply_to_message.from_user.first_name
        last_name = message.reply_to_message.from_user.last_name
        last_name = message.reply_to_message.last_name if message.reply_to_message.last_name is not None else ''
        full_name = f"{firstname}{last_name}"
        uid = message.reply_to_message.from_user.id
        mess = message.reply_to_message.text
        messId = message.reply_to_message.id
        reportName = message.from_user.first_name
        print (f"{bcolors.BOLD}reported  {mess} {bcolors.ENDC}")
        bot.send_message("-1001349899890", f"{reportName} reported {uid} - {full_name}:  mess :{messId} {mess}" )



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

@bot.message_handler(commands=['clear_db'])
def clearDB(message):
    TelegramUser.objects.all().delete()
    bot.send_message("-1001349899890", "Đã clear db: ")

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
    global MSG_COUNTER, MSG_MAX

    result = bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator'] or message.from_user.username == "GroupAnonymousBot" or message.from_user.first_name == "Telegram" or message.from_user.first_name == "Channel"
    if result == True:
        # print("admin")
        return

    print(f"\n{bcolors.UNDERLINE}{bcolors.OKCYAN}{message.from_user.first_name} sent message:  {str( message.text)} {bcolors.ENDC} {MSG_COUNTER} {MSG_MAX}")
    MSG_COUNTER = MSG_COUNTER + 1
    if MSG_COUNTER >= MSG_MAX:
        MSG_COUNTER = 0
        sentmessage = bot.send_message("-1001724937734", "[CẢNH BÁO SCAM/LỪA ĐẢO]\n\nTất cả tài khoản Telegram mang tên Đỗ Bảo hoặc Đỗ Bảo - TCCL inbox cho các bạn trước đều là LỪA ĐẢO / SCAM. \n\n 💢🆘 ‼️\n\n👉 ⚠️Các ADMIN TCCL KHÔNG BAO GIỜ NHẮN TIN trước.\n👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG THU khoản phí nào.\n👉 ⚠️ Bất kỳ ai đều có thể đổi tên và avatar giống Đỗ Bảo để chat với bạn\n👉 Hãy luôn CẨN THẬN với tài sản của mình.")
        # print(sentmessage)
        chatId = sentmessage.chat.id
        print("sent warning", chatId, sentmessage.message_id)
        deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': sentmessage.message_id}, countdown=180)
    
    print(message)
    message_json = json.dumps(message)

    moderateMessageTask.apply_async(kwargs={ "message": message_json}, countdown=1)
    # moderateMessageTask.apply_async(args=[message.chat_id, f"You said: {message.text}", message.message_id])

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






