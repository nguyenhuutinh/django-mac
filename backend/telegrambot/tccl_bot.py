from soupsieve import iselect
from telegrambot.models import Message, TelegramUser, MessageCounter
import uuid

from datetime import datetime, timedelta
import os
import cv2
import re
from re import M
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from types import SimpleNamespace
from langdetect import detect
import hashlib
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
from django.utils import timezone

import pytesseract
from PIL import Image
import cloudmersive_image_api_client
from cloudmersive_image_api_client.rest import ApiException

configuration = cloudmersive_image_api_client.Configuration()
configuration.api_key['Apikey'] = '9f957878-68e3-4b7b-ba1b-5c960f445002'
api_instance = cloudmersive_image_api_client.NsfwApi(cloudmersive_image_api_client.ApiClient(configuration))

photoUrl = ""
MSG_COUNTER = 0
MSG_MAX = 50

report_sent = False


last_message_time = {}


# Maintain a set to store hashes of recently deleted messages
recently_deleted_messages = set()

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

@shared_task
def clear_last_message_time():
    # Clear last_message_time
    last_message_time.clear()
@shared_task(bind=True)
def clear_periodic(self):
    # Sleep for 1 hour
    time.sleep(3600)
    # Call the clear_last_message_time task
    clear_last_message_time.delay()

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

# Define a constant for admin status check
ADMIN_STATUSES = ['administrator', 'creator']

@bot.message_handler(content_types=['photo'])
def photo(message):
    global photoUrl
    result = bot.get_chat_member(message.chat.id, message.from_user.id).status in ADMIN_STATUSES or \
             message.from_user.username == "GroupAnonymousBot" or \
             message.from_user.first_name == "Telegram"
    
    if result:
        print("admin")
        return

    convert_to_send_task(message)

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ''
    full_name = f"{first_name}{last_name}"

    res = checkingPhoto(message=message)
    caption_text = f" with caption: {message.caption}" if message.caption else ""
    print(f"\n{bcolors.UNDERLINE}{bcolors.OKCYAN}{first_name} sent photo URL {photoUrl}{caption_text}{bcolors.ENDC}\n")

    if res == 1:
        print("stop")
    elif res == 3:
        process_image_scan_result(message, full_name, "SCAM / LỪA ĐẢO")
    elif res == 2:
        process_image_scan_result(message, full_name, "18+")
    else:
        print("check photo and it is valid")


def process_image_scan_result(message, full_name, scan_type):
    userId = message.from_user.id
    chatId = message.chat.id
    deleteMessageTask.apply_async(kwargs={"chat_id": chatId, 'message_id': message.message_id}, countdown=3)

    bot.ban_chat_member(chatId, userId)
    bot.reply_to(message, f"‼️ {full_name} bị ban vì post hình ảnh có nội dung {scan_type}. ‼️\n\n👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG THU khoản phí nào.\n👉 ⚠️Các admin KHÔNG BAO GIỜ NHẮN TIN trước.\n👉 ⚠️ Bất kỳ ai đều có thể đổi tên và avatar giống admin để chat với bạn\n👉 Hãy luôn CẨN THẬN với tài sản của mình.")
    
    bot.send_message("-1001349899890", f"IMAGE SCAN - {scan_type} BẰNG HÌNH")
    try:
        bot.send_photo("-1001349899890", photo=open(photoUrl, 'rb'))
    except Exception as e:
        print("Error sending photo:", e)
        
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
    print("checking photo")

    # Check if the message contains a photo
    if message.photo and message.photo[-1]:
        # Extract file information
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_extension = '.' + file_info.file_path.split('.')[-1]
        fileName = str(uuid.uuid4()) + file_extension
        filePath = '/home/user/app/backend/data/' + fileName
        photoUrl = filePath

        # Download the photo
        response = requests.get(bot.get_file_url(file_id), stream=True)
        with open(filePath, 'wb') as handle:
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)

        # Check if the file exists
        if os.path.exists(filePath):
            # Read the image using OpenCV
            img = cv2.imread(filePath)

            # Convert the image to grayscale
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Use pytesseract to extract text from the image
            text = pytesseract.image_to_string(gray_img, lang="eng")
            print("Converted text:", text)

            # Check for specific text patterns
            if "chưa tham gia" in text.lower() or "Futures ai tham gia" in text.lower() or "cần bán" in text.lower() or "cần ra đi" in text.lower():
                os.remove(filePath)
                return 3

            # Use regular expressions to find percentage values
            pattern = r'\b\d{4,}%'
            match = re.search(pattern, text)
            if match:
                print(f"Percentage value greater than or equal to 1000 found: {match.group(0)}")
                os.remove(filePath)
                return 1

            # Load the pre-trained neural network model for nudity detection
            model = cv2.dnn.readNetFromCaffe('/home/user/app/backend/data/deploy.prototxt', '/home/user/app/backend/data/res10_300x300_ssd_iter_140000.caffemodel')

            # Define the classes for the neural network model
            classes = ['background', 'person']

            # Convert the image to a blob
            input_size = (300, 300)
            blob = cv2.dnn.blobFromImage(img, 1.0, input_size, (104.0, 177.0, 123.0))

            # Set the input for the neural network model and perform forward pass
            model.setInput(blob)
            output = model.forward()

            # Check if any detected objects are classified as a person
            for i in range(output.shape[2]):
                confidence = output[0, 0, i, 2]
                if confidence > 0.8 and classes[int(output[0, 0, i, 1])] == 'person':
                    try:
                        # Classify the image for nudity using an external API
                        api_response = api_instance.nsfw_classify(filePath)
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
                    print('No nudity detected')
                    return -1

        # Remove the temporary file
        os.remove(filePath)

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

    try:
        message_data = json.loads(message)
        message_object = SimpleNamespace(**message_data)
        # Convert nested dictionaries to SimpleNamespace objects
        from_user_ns = SimpleNamespace(**message_data['from_user'])
        chat_ns = SimpleNamespace(**message_data['chat'])

        # Remove nested dictionaries from message_data
        message_data.pop('from_user')
        message_data.pop('chat')

        # Create SimpleNamespace object for message_data
        message_object = SimpleNamespace(chat=chat_ns, from_user=from_user_ns, **message_data)

        # print("message", message_object)
        # print("Received message:", message_object.chat)
        print(f"{bcolors.WARNING} moderateMessageTask... {bcolors.ENDC}")

        moderate(message_object)
    except Exception as exc:
            # Retry the task with a delay of 5 seconds between retries
            raise moderateMessageTask.retry(exc=exc, countdown=5, max_retries=1)

def moderate(message):
    chat_id = message.chat.id
    from_user = message.from_user

    if chat_id != -1001724937734:
        print(f"{bcolors.FAIL}wrong chat group: {str(chat_id)} {bcolors.ENDC}")
        return

    if message.photo:
        caption_info = f" with caption: {message.caption}" if message.caption else " without caption"
        print(f"{bcolors.WARNING}Received Photo{caption_info}{bcolors.ENDC}")
    else:
        print(f"{bcolors.WARNING}Received Text: {message.text}{bcolors.ENDC}")

    if checkAndDeleteMessage(message):
        _deleteMessage(message)

    if message.message_id:
        user_exist = TelegramUser.objects.filter(user_id=from_user.id, firstname=from_user.first_name, lastname=from_user.last_name).exists()
        print(f"checking user {from_user.id} existence: {user_exist}")

        is_photo = message.text is None

        if not user_exist or is_photo:
            if not user_exist:
                TelegramUser.objects.create(user_id=from_user.id, firstname=from_user.first_name, lastname=from_user.last_name, username=from_user.username, isBot=from_user.is_bot, status="new", user_avatar_link="")
                print(f"add user {from_user.id} to DB")

            print("step 2")
            processChecUserProfile.apply_async(kwargs={"userId": from_user.id, "chatId": chat_id, "messageId": message.message_id}, countdown=1)

            if checkingUserProfilePhoto(from_user.id, "function"):
                banUser(message, 'message bi cam')
                return

            if processCheckAndBan(message):
                banUser(message, 'message bi cam')
                return


def checkAndDeleteMessage(message):
    text_to_check = (message.text or message.caption or "").lower()

    # Check for specific patterns to exclude messages
    exclusion_patterns = [
        "/addstickers",
        "tribc1991",
        ".com", ".gov", ".net", ".org",
        "https://t.me/tcclroom",
        "https://t.me/tcclchat",
        "https://t.me/tradecoinchienluoc"
    ]
    if any(pattern in text_to_check for pattern in exclusion_patterns):
        return False

    # Check for specific language or content patterns to include messages
    if (
        isRussia(text_to_check) or
        (isEnglish(text_to_check) and ("https://" in text_to_check or "@" in text_to_check)) or
        ("cập nhập plan btc mới nhất" in text_to_check and "uptrend" in text_to_check) or
        ("vào avatar" in text_to_check and "plan" in text_to_check) or
        (is_not_english_or_vietnamese(text_to_check) and "https://" in text_to_check) or
        "t.me" in text_to_check or
        ("t.me/" in text_to_check and "tcclroom" not in text_to_check and "tcclchat" not in text_to_check and "https://t.me/tradecoinchienluoc" not in text_to_check) or
        "land of conquest" in text_to_check or
        ("join" in text_to_check and "@" in text_to_check) or
        "@tradinghoiquan" in text_to_check or
        ("ae vào" in text_to_check and "@" in text_to_check) or
        ("crypto" in text_to_check and "@" in text_to_check) or
        "follow us" in text_to_check or
        "gold vip signal" in text_to_check or
        "rewards distribution" in text_to_check or
        "@RyanNguyenVBC" in text_to_check or
        "@tradefutureforexsignals" in text_to_check or
        ("@" in text_to_check and "kèo" in text_to_check and ":" in text_to_check and message.reply_to_message is None) or
        "opensea.io" in text_to_check or
        "vinacoin.live" in text_to_check or
        ("www." in text_to_check and "airdrop" in text_to_check) or
        ("airdrop" in text_to_check and "$" in text_to_check) or
        (text_to_check.count('@') > 2 and text_to_check.count('@@') == 0) or
        ("vào avatar" in text_to_check and "cập nhập" in text_to_check) or
        ("avatar" in text_to_check and "cập nhập" in text_to_check and "link" in text_to_check)
    ):
        return True

    return False

def _deleteMessage(message):

    global recently_deleted_messages

    # Hash the message content
    message_hash = hashlib.md5((message.text or "").encode()).hexdigest()

    # Check if the message hash is in the set of recently deleted messages
    if message_hash in recently_deleted_messages:
        # Update the counter when a message is deleted
        recently_deleted_messages.remove(message_hash)
    
    if message_hash not in recently_deleted_messages:
        print(f"{bcolors.FAIL} _deleteMessage -> reply_to {message} {bcolors.ENDC}")
        bot.reply_to(message, "⚠️ không chia sẻ link hoặc nội dung vi phạm quy định của TCCL. ⚠️")
    else:
        # If the message hash is not found, warn the user or take further action
        print(f"{bcolors.FAIL} _deleteMessage -> ban_user {message} {bcolors.ENDC}")
        banUser(message, 'message bi cam')

    # Asynchronously delete the message
    deleteMessageTask.apply_async(kwargs={"chat_id": message.chat.id, 'message_id': message.message_id}, countdown=1)

    # Extract information about the user
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    user_id = message.from_user.id
    full_name = f"{first_name} {last_name}".strip()

    # Prepare message content for logging
    message_content = f"Tin nhắn đã bị xóa: {message.text or ''} {message.caption or ''} - Người dùng: {user_id} - "
    if full_name:
        message_content += f" ({full_name})"

    # Log the deleted message content
    bot.send_message("-1001349899890", message_content)

    # Add the message hash to the set of recently deleted messages
    recently_deleted_messages.add(message_hash)



@shared_task
def deleteMessageTask(chat_id, message_id):
    print("delete Message Task")
    print(f"{bcolors.OKGREEN}deleted message: {chat_id} {message_id}{bcolors.ENDC}")
    track_deleted_message()
    bot.delete_message(chat_id,message_id=message_id)
@shared_task
def clearDBRecord(user_id):
    TelegramUser.objects.filter(user_id=user_id).delete()
def processCheckAndBan(message):
    firstName = message.from_user.first_name or ""
    lastName = message.from_user.last_name or ""
    username = message.from_user.username or ""
    print(f"{bcolors.WARNING}processCheckAndBan {firstName} - {lastName} - {username} {bcolors.ENDC}")

    text = message.text.lower() if message.text else ""
    caption = message.caption.lower() if message.caption else ""
    if "dịch vụ kubet"  in text:
        return True
    if "@cccd" in text:
        return True
    if "giveaway" in firstName.lower() or "giveaway" in lastName.lower():
        return True
    if "tradingview" in firstName.lower() or "tradingview" in lastName.lower():
        return True
    if "tai khoan tradingview" in text:
        return True
    if "puffer.farm" in text:
        return True
    if "tín hiệu" in text and "của tôi" in text:
        return True
    if "cập nhập plan btc mới nhất" in text and "uptrend" in text:
        return True
    if "vào avatar" in text and "link" in text:
        return True
    if "https://t.me/+" in text:
        return True
    if "kèo" in text and "👉" in text:
        return True
    if "link" in text and "👉" in text:
        return True
    if "nhómvip" in text or "ai chưa tham gia" in text:
        print(f"{bcolors.WARNING}case 1  {bcolors.ENDC}")
        return True
    if "thông báo" in text and "anh em" in text:
        print(f"{bcolors.WARNING}case 33  {bcolors.ENDC}")
        return True
    if len(message.text or "") < 60:
        if "whaless" in text:
            print(f"{bcolors.WARNING}case 2  {bcolors.ENDC}")
            return True
        if "thông báo nhóm" in text:
            print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
            return True
        if "anh em" in text and "vào nhóm" in text and "vip" in text:
            print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
            return True
        if "ai" in text and "vào nhóm" in text and "liên hệ" in text:
            print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
            return True
        if "anh em" in text and "vào nhóm" in text and "liên hệ" in text:
            print(f"{bcolors.WARNING}case 3  {bcolors.ENDC}")
            return True
        if "vào" in text and "nhóm" in text and "vip" in text and "inbox" in text:
            print(f"{bcolors.WARNING}case 20  {bcolors.ENDC}")
            return True
        if any(word in text for word in ["vào nhóm vip", "vào nhóm vlp", "vào nhóm v1p", "vào nhóm vip ib"]):
            print(f"{bcolors.WARNING}case 220  {bcolors.ENDC}")
            return True
        if any(word in text for word in ["ai tham gia ib", "ai tham gia liên hệ"]):
            print(f"{bcolors.WARNING}case 214-215  {bcolors.ENDC}")
            return True
        if any(word in text for word in ["futt + spot", "thông báo anh em", "liên hệ admin"]):
            print(f"{bcolors.WARNING}case 6-7-8  {bcolors.ENDC}")
            return True
    if any(word in (firstName + " " + lastName).lower() for word in ["tccl community", "tccl"]):
        print(f"{bcolors.WARNING}case 4-5  {bcolors.ENDC}")
        return True
    if "tccl" in (username or "").lower():
        print(f"{bcolors.WARNING}case 9  {bcolors.ENDC}")
        return True
    if any(word in (firstName + " " + lastName).lower() for word in ["trung kim son", "trade coin chiến lược", "admln"]):
        print(f"{bcolors.WARNING}case 10-11-12-13-14-15-16-17-18  {bcolors.ENDC}")
        return True
    if "glcapital1" in text:
        print(f"{bcolors.WARNING}case 19  {bcolors.ENDC}")
        return True
    if "aecryptodhchat" in text:
        print(f"{bcolors.WARNING}case 29  {bcolors.ENDC}")
        return True
    if "qua đây trao đổi với mình" in text and "@" in text:
        print(f"{bcolors.WARNING}case 30  {bcolors.ENDC}")
        return True
    if "chưa vào" in text and "nhắn ad" in text:
        print(f"{bcolors.WARNING}case 31  {bcolors.ENDC}")
        return True
    if "chưa tham" in text and "nhóm" in text:
        if "ad" in text:
            print(f"{bcolors.WARNING}case 10112  {bcolors.ENDC}")
            return True
        else:
            print(f"{bcolors.WARNING}case 10111  {bcolors.ENDC}")
            return True
    if "buy and wait" in text and "@" in text:
        print(f"{bcolors.WARNING}case 10113  {bcolors.ENDC}")
        return True
    if "@xauusd_goldsignals1" in text:
        return True

    print("no case")
    return False

def banUser(message, error_text):
    print("start ban user")
    chat_id = message.chat.id
    user = message.from_user

    # Extract user information
    first_name = user.first_name
    last_name = user.last_name or ''
    full_name = f"{first_name}{last_name}"
    user_id = user.id

    # Delete the message after 3 seconds
    deleteMessageTask.apply_async(kwargs={"chat_id": chat_id, 'message_id': message.message_id}, countdown=3)

    # Ban the user
    bot.ban_chat_member(chat_id, user_id)

    # Check if the user is already banned
    is_exist = TelegramUser.objects.filter(user_id=user.id, status='banned').exists()
    print(f"banned ?: {is_exist}")

    if not is_exist:
        print(f"{bcolors.FAIL} banUser -> reply_to {message} {bcolors.ENDC}")
        bot.reply_to(message, f"‼️ TÀI KHOẢN {full_name} ĐÃ BỊ KHÓA DO VI PHẠM CHÍNH SÁCH VỀ SPAM / LỪA ĐẢO ‼️")

        # URL of the warning image
        image_url = "https://s3-hn-2.cloud.cmctelecom.vn/vnba.org.vn/vnba-media/bancanbiet/Agribank_khuyen_cao_khach_hang_1.jpg"
        link_text = 'https://t.me/dobao_tccl'

        # Caption for the image with highlighted title
        caption = f"""*CẢNH BÁO GIẢ MẠO ADMIN INBOX LỪA ĐẢO*\n\nTẤT CẢ CÁC TÀI KHOẢN TELEGRAM MANG TÊN *ĐỖ BẢO* HOẶC *ĐỖ BẢO.TCCL* INBOX TRƯỚC CHO CÁC BẠN ĐỀU LÀ LỪA ĐẢO. \n\n  💢🆘 ‼️\n\n👉 ⚠️CÁC ADMIN TCCL KHÔNG BAO GIỜ NHẮN TIN TRƯỚC.\n👉 ⚠️TCCL KHÔNG CÓ GROUP VIP.\n👉 ⚠️TCCL KHÔNG THU KHOẢN PHÍ NÀO.\n👉 ⚠️ BẤT KỲ AI ĐỀU CÓ THỂ TẠO TÀI KHOẢN GIẢ MẠO ĐỖ BẢO ĐỂ CHAT VỚI BẠN\n👉 HÃY LUÔN CẨN THẬN VỚI TÀI SẢN CỦA MÌNH. \n--------------\n\n*Dobao.TCCL ( Không Tích Xanh, Không Inb trước, Không tạo nhóm riêng )*\n*Check Account Chính Chủ: {link_text}*"""
        
        # Send the photo with the caption
        sent_message = bot.send_photo("-1001724937734", image_url, caption=caption, parse_mode="Markdown")
        
        # Delete the warning message after 60 seconds
        deleteMessageTask.apply_async(kwargs={"chat_id": sent_message.chat.id, 'message_id': sent_message.message_id}, countdown=60)

    # Send a message to notify about the banned user
    bot.send_message("-1001349899890", f"Đã ban user id: {user_id} - Tên: {full_name} - Nội Dung Tin Nhắn: {message.id} {message.text}" + (f" - Caption: {message.caption}" if message.caption else ""))
    
    # Update the status of the user to 'banned' in the database
    TelegramUser.objects.filter(user_id=user_id).update(status='banned', ban_reason=error_text)
    print(f"{bcolors.OKGREEN} banned {user_id} {full_name} {bcolors.ENDC}")



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

    

# Function to check the queue length based on task name
def check_queue_length_for_task(task_name):
    with celery_app.connection_or_acquire() as conn:
        with conn.channel() as channel:
            queue = celery_app.amqp.queues[task_name](channel)
            queue.declare()
            return queue.qos().messages

@bot.message_handler()
def allMessage(message):
    global MSG_COUNTER, MSG_MAX
    # clear_periodic.delay()

    result = bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator'] or message.from_user.username == "GroupAnonymousBot" or message.from_user.first_name == "Telegram" or message.from_user.first_name == "Channel"
    if result == True:
        # print("admin")
        return

    print(f"\n{bcolors.UNDERLINE}{bcolors.OKCYAN}{message.from_user.first_name} sent message:  {str( message.text)} {bcolors.ENDC} {MSG_COUNTER} {MSG_MAX}")
    if message.reply_to_message is None and message.photo == None:
        MSG_COUNTER = MSG_COUNTER + 1

    if MSG_COUNTER >= MSG_MAX:
        MSG_COUNTER = 0
        # URL of the image
        image_url = "https://s3-hn-2.cloud.cmctelecom.vn/vnba.org.vn/vnba-media/bancanbiet/Agribank_khuyen_cao_khach_hang_1.jpg"
        
        link_text = 'https://t.me/dobao_tccl'

        # Caption for the image with highlighted title
        caption = f"""*CẢNH BÁO GIẢ MẠO ADMIN NHẮN TIN LỪA ĐẢO*\n\nTẤT CẢ CÁC TÀI KHOẢN TELEGRAM MANG TÊN *ĐỖ BẢO* HOẶC *ĐỖ BẢO.TCCL* INBOX TRƯỚC CHO CÁC BẠN ĐỀU LÀ LỪA ĐẢO. \n\n  💢🆘 ‼️\n\n👉 ⚠️CÁC ADMIN TCCL KHÔNG BAO GIỜ NHẮN TIN TRƯỚC.\n👉 ⚠️TCCL KHÔNG CÓ GROUP VIP.\n👉 ⚠️TCCL KHÔNG THU KHOẢN PHÍ NÀO.\n👉 ⚠️ BẤT KỲ AI ĐỀU CÓ THỂ TẠO TÀI KHOẢN GIẢ MẠO ĐỖ BẢO ĐỂ CHAT VỚI BẠN\n👉 HÃY LUÔN CẨN THẬN VỚI TÀI SẢN CỦA MÌNH. \n--------------\n\n*Dobao.TCCL ( Không Tích Xanh, Không Inb trước, Không tạo nhóm riêng )*\n*Check Account Chính Chủ: {link_text}*"""
        
        # Send the photo with the caption
        sentmessage = bot.send_photo("-1001724937734", image_url, caption=caption, parse_mode="Markdown")
        # sentmessage = bot.send_message("-1001724937734", "[CẢNH BÁO SCAM/LỪA ĐẢO]\n\nTất cả tài khoản Telegram mang tên Đỗ Bảo hoặc Đỗ Bảo - TCCL inbox cho các bạn trước đều là LỪA ĐẢO / SCAM. \n\n 💢🆘 ‼️\n\n👉 ⚠️Các ADMIN TCCL KHÔNG BAO GIỜ NHẮN TIN trước.\n👉 ⚠️TCCL KHÔNG có group VIP.\n👉 ⚠️TCCL KHÔNG THU khoản phí nào.\n👉 ⚠️ Bất kỳ ai đều có thể đổi tên và avatar giống Đỗ Bảo để chat với bạn\n👉 Hãy luôn CẨN THẬN với tài sản của mình.")
        # print(sentmessage)
        chatId = sentmessage.chat.id
        print("sent warning ... ", chatId, sentmessage.message_id)
        deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': sentmessage.message_id}, countdown=180)
    
    convert_to_send_task(message)

    # Get the user ID
    # user_id = message.from_user.id
    
    # Check if the user ID is already in the dictionary
    # if user_id in last_message_time:
    #     # Calculate the time difference between the current message and the last message
    #     time_diff = time.time() - last_message_time[user_id]
        
    #     # If the time difference is less than 15 seconds and the user has sent 3 or more messages
    #     if time_diff < 15 and last_message_time['message_count'] >= 3:
    #         chatId = message.chat.id
    #         deleteMessageTask.apply_async(kwargs={ "chat_id": chatId,'message_id': message.message_id}, countdown=1)
    #         return
    


def handle_none(value):
    if value is None:
        return None
    elif isinstance(value, dict):
        return {k: handle_none(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [handle_none(item) for item in value]
    else:
        return value


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




def isRussia(text):
    try:
        detected_language = detect(text)
        return detected_language == 'ru'
    except:
        # Handle cases where language detection fails
        return False

def isEnglish(text):
    try:
        detected_language = detect(text)
        return detected_language == 'en'
    except:
        # Handle cases where language detection fails
        return False


def is_not_english_or_vietnamese(text):
    try:
        detected_language = detect(text)
        return detected_language != 'en' and detected_language != 'vi'
    except:
        # Handle cases where language detection fails
        return False


def convert_to_send_task(message):

    message_data = {
        "content_type": message.content_type,
        "id": message.id,
        "message_id": message.message_id,
        "from_user": {
            "id": message.from_user.id,
            "is_bot": message.from_user.is_bot,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "last_name": message.from_user.last_name,
        },
        # "date": message.date,
        "chat": {
            "id": message.chat.id,
            "type": message.chat.type,
            "title": message.chat.title,
            "username": message.chat.username,
            "first_name": message.chat.first_name,
            "last_name": message.chat.last_name,
            # Include other attributes of the 'chat' object as needed
        },
        "sender_chat": message.sender_chat,
        "text": message.text,
        "caption": message.caption,
        "photo": "",
        # Include other attributes of the 'message' object as needed
    }
    try:
        # Serialize the message data into JSON
        message_json = json.dumps(message_data)

        # Print the serialized message data
        print("Serialized Message Data:", message_json)

        # Your task logic goes here
        # ...

        moderateMessageTask.apply_async(kwargs={ "message" : message_json}, countdown=0)

    except Exception as e:
        # Handle any exceptions during serialization
        print("Error occurred during serialization:", e)
        moderate(message=message)

    global report_sent
    current_time_utc = datetime.now(timezone.utc)

    # Check if the current hour is 17 (5 PM) in UTC
    if current_time_utc.hour == 17 and not report_sent:
        # Call the function to generate the daily report
        send_daily_report()
        report_sent = True


    track_checked_message()

def track_checked_message():
    # Get the current datetime in UTC
    current_datetime_utc = datetime.now(timezone.utc)

    # Extract the date part
    today = current_datetime_utc.date()
    counter, created = MessageCounter.objects.get_or_create(date=today)
    counter.checking_messages += 1
    counter.save()

def track_deleted_message():
    # Get the current datetime in UTC
    current_datetime_utc = datetime.now(timezone.utc)

    # Extract the date part
    today = current_datetime_utc.date()
    counter, created = MessageCounter.objects.get_or_create(date=today)
    counter.deleted_messages += 1
    counter.save()

def generate_daily_report():
    # Get the current datetime in UTC
    current_datetime_utc = datetime.now(timezone.utc)

    # Extract the date part
    today = current_datetime_utc.date()
    counter, created = MessageCounter.objects.get_or_create(date=today)
    report_message = f"Daily Report - {today}:\n"
    report_message += f"Total Checking Messages: {counter.checking_messages}\n"
    report_message += f"Total Deleted Messages: {counter.deleted_messages}\n"
    return report_message

def send_daily_report():
    report = generate_daily_report()
    chat_id = '-1001349899890'  # Replace with the actual chat ID to send the report
    bot.sendMessage(chat_id=chat_id, text=report)
