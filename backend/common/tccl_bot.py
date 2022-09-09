from datetime import datetime, timedelta
from re import M
import telebot
# from config import *
import logging
from telebot import types,util
from django.http import HttpResponse, JsonResponse
import json
from PIL import ImageChops, ImageStat,Image



BOT_TOKEN = "5495185707:AAFOwex3SfYxz2xhz-KA3GdyLpMVLnicUaI"

bot = telebot.TeleBot(BOT_TOKEN)
logger = telebot.logger

logger.setLevel(logging.DEBUG)

class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key='is_admin'
    @staticmethod
    def check(message: telebot.types.Message):
        return bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator']
bot.add_custom_filter(IsAdmin())


def process_request(request):
    print(request.data)
    json_string = request.data
    print("received message: ", json_string)
    if json_string == None or json_string == '':
        return "empty body", 400
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return JsonResponse({"result": "ok" }, status=200)



# @bot.message_handler(commands=['start', 'help'])
# def _start(message):
    # print(message)
    # user_name = message.from_user.username
    # start_message = f'Hello, {user_name}! You can add your places with /add command.\n' \
    #                 f'Type /list to show 10 last places you added' \
    #                 f'You can delete all your places with /reset command.' \
    #                 f'Try typing /add <wanted address> to add your first place'
#     bot.reply_to(message, start_message)


# When user types /add we send him to state 2 - ADD_ADDRESS and ask him to write address
# @bot.message_handler(commands=['add'])
# def _add_start(message):
#     print( "add_start")
    # clear address global variable
#     user_states.ADDRESS = ''
#     bot.send_message(message.chat.id, "Write address that you want to save")
#     user_states.update_state(message, user_states.ADD_ADDRESS)

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

@bot.message_handler(commands=['report'])
def report(message):
    # print ('reported', message)
    if message.reply_to_message:
        firstname = message.reply_to_message.from_user.first_name
        last_name = message.reply_to_message.from_user.last_name
        uid = message.reply_to_message.from_user.id
        mess = message.reply_to_message.text
        messId = message.reply_to_message.id
        name =  f" {firstname} {last_name}"
        reportName = message.from_user.first_name
        bot.send_message("-643525876", f"{reportName} reported {uid} - {name}:  mess :{messId} {mess}" )

@bot.message_handler(content_types=['photo'])
def photo(message):
    print("photo", message.caption)
    moderate(message=message)


@bot.message_handler(is_admin=False)
def _all(message):
    print("other", message.text)
    # moderate(message=message)
@bot.message_handler(is_admin=True)
def _all(message):
    # print("admin message", message.text)
    data = bot.get_user_profile_photos(message.from_user.id)
    # print(data)
    # njson = json.loads(data)
    # print(data['result'])
    user_photos = data.photos
    if len(user_photos) > 0:

        # photos_ids = []
        fileId = user_photos[0][0].file_id
        print()
        fileUrl = bot.get_file_url(fileId)
        print(fileUrl)
        result = compare_images(Image.open('/mario-circle-cs.png'), Image.open('/mario-circle-node.png'))
        print(result)


    # moderate(message=message)

def compare_images(img1, img2):
    """Calculate the difference between two images of the same size
    by comparing channel values at the pixel level.
    `delete_diff_file`: removes the diff image after ratio found
    `diff_img_file`: filename to store diff image

    Adapted from Nicolas Hahn:
    https://github.com/nicolashahn/diffimg/blob/master/diffimg/__init__.py
    """

    # Don't compare if images are of different modes or different sizes.
    if (img1.mode != img2.mode) \
            or (img1.size != img2.size) \
            or (img1.getbands() != img2.getbands()):
        return None

    # Generate diff image in memory.
    diff_img = ImageChops.difference(img1, img2)
    # Calculate difference as a ratio.
    stat = ImageStat.Stat(diff_img)
    diff_ratio = sum(stat.mean) / (len(stat.mean) * 255)

    return diff_ratio * 100
def moderate(message):
    if processCheckAndBan(message):
        banUser(message)
    if checkAndDeleteMessage(message):
        deleteMessage(message)

def checkAndDeleteMessage(message):
    if "land of conquest"  in f"{message.text} {message.caption}".lower():
        return True
    if "follow us" in f"{message.text} {message.caption}".lower():
        return True
    if "rewards distribution" in f"{message.text} {message.caption}".lower():
        return True
    if "fut" in f"{message.text} {message.caption}".lower() and "spot" in f"{message.text} {message.caption}".lower():
        return True

def deleteMessage(message):
    print(message)
    # bot.delete_message(message.chat.id,message_id=message.id)
    # bot.send_message("-643525876", f"deleted message {message.text}" )

def processCheckAndBan(message):
    userId = message.from_user.id
    chatId = message.chat.id
    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    print(f"{message.text} {message.caption} - {firstName} {lastName} {userId} {chatId} ".lower())
    if "NhómVIP".lower() in f"{message.text} {message.caption}".lower() or "ai chưa tham gia" in f"{message.text} {message.caption}".lower():
        # bot.delete_message(chatId,message_id=(message.id + 1))
        return True
    if "futt + spot" in f"{message.text} {message.caption}".lower():
        return True

    if "anh em" in f"{message.text} {message.caption}".lower() and  "vào nhóm" in f"{message.text} {message.caption}".lower() :
        return True
    if "TCCL Community".lower() in f"{firstName} {lastName}".lower() :
        return True
    if "TCCL".lower() in f"{firstName} {lastName}".lower() :
        return True
    if ".".lower() == f"{firstName}".lower() :
        return True
    if "tccl" in f"{username}":
        return True
    if "Đỗ Bảo".lower() in f"{firstName} {lastName}".lower() :
        return True
    if "Bảo Đỗ".lower() in f"{firstName} {lastName}".lower() :
        return True
    if "Trung Kim Son".lower() in f"{firstName} {lastName}".lower() :
        return True
    if "Trade Coin Chiến Lược".lower() in f"{firstName} {lastName}".lower() :
        return True
    if "Trade".lower() in f"{firstName} {lastName}".lower() and  "Chiến Lược".lower() in f"{firstName} {lastName}".lower():
        return True
    if "Trade".lower() in f"{firstName} {lastName}".lower() and  "Lược".lower() in f"{firstName} {lastName}".lower():
        return True
    if "Trade".lower() in f"{firstName} {lastName}".lower() and  "Iược".lower() in f"{firstName} {lastName}".lower():
        return True
    if "Bảo".lower() in f"{firstName}".lower() and lastName == None :
        return True
    return False

def banUser(message):
    print("banUser")
    # userId = message.from_user.id
    # chatId = message.chat.id
    # firstName = message.from_user.first_name
    # lastName = message.from_user.last_name

    # bot.reply_to(message, "🧞‍♂️ ‼️ User: " + firstName + " sử dụng message bị cấm. Mời ra đảo du lịch không hẹn ngày về ‼️ 🧞‍♂️")
    # bot.delete_message(chatId,message_id=message.id)
    # bot.ban_chat_member(chatId, userId)
    # bot.send_message("-643525876", "Reported user id: " + str(userId) + " - firstName: "+ f"{firstName}" + " - lastname: "+ f"{lastName}" + f" - message: {message.id} {message.text} " + f" - caption: {message.caption}")

# @bot.message_handler(commands=['list'])
# def _list(message):
#     print("_list")
@bot.message_handler(commands=['ban_user'])
def manualbanUser(message):
    print(message)
    # userId = message.text.replace("/ban_user ", "")
    # bot.ban_chat_member(-1001724937734, userId)
    # bot.kick_chat_member(chat_id =-1001724937734,user_id=userId)

    bot.send_message("-643525876", "Đã ban user id: " + f" {userId}")
@bot.message_handler(commands=['delete_message'])
def deleteMessage(message):
    print(message)
    # message_id = message.text.replace("/delete_message ", "")
    # bot.delete_message(-1001724937734, message_id)
    # bot.send_message("-643525876", "Đã Delete Message id: " + f" {message_id}")

@bot.message_handler( content_types=[
    "new_chat_members"
])
def new_chat_members(message):
    print("WELCOME", message)


@bot.message_handler(commands=['unban_user'])
def unban_user(message):
    userId = message.text.replace("/unban_user ", "")
    bot.unban_chat_member(-1001724937734, userId)
    bot.send_message("-643525876", "Đã Mở " + f" {userId}")



@bot.message_handler(content_types=[
    "left_chat_member"
])
def foo(message):
    userId = message.from_user.id
    chatId = message.chat.id

    firstName = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    bot.send_message("-643525876", "User left : " + f" id {userId}  firstName {firstName} userName {username}")

@bot.message_handler(commands=['reset'])
def _reset(message):
    print("_reset")
#     user_id = message.from_user.id
#     db_object.execute("DELETE FROM places WHERE user_id = {}".format(user_id))
#     db_connection.commit()
#     bot.send_message(message.chat.id, "All your saved addresses have been deleted")






