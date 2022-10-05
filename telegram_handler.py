import os

from telegram.ext import Updater, CommandHandler
from main import generate_hours_chart

def start_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    if token:
        print("Starting Telegram bot")
        updater = Updater(token)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('today', _send_hours_chart_today))
        dp.add_handler(CommandHandler('week', _send_hours_chart_week))
        dp.add_handler(CommandHandler('month', _send_hours_chart_month))
        dp.add_handler(CommandHandler('semester', _send_hours_chart_semester))
        updater.start_polling()
        updater.idle()


def _get_image_bytes_from_file_path(path):
    if not path:
        print("image path is empty!")
        return 

    with open(path, 'rb') as image:
        f = image.read()
        #b = bytearray(f)
        return f


def _send_hours_chart(hours_type, update, context):
    chat_id = update.message.chat_id

    #print(f"Chat ID: {chat_id}")
    path = generate_hours_chart(hours_type)
    img_bytes = _get_image_bytes_from_file_path(path)

    context.bot.send_photo(chat_id=chat_id, photo=img_bytes)


def _send_hours_chart_today(update, context):
    _send_hours_chart("today", update, context)

def _send_hours_chart_week(update, context):
    _send_hours_chart("week", update, context)

def _send_hours_chart_month(update, context):
    _send_hours_chart("month", update, context)

def _send_hours_chart_semester(update, context):
    _send_hours_chart("semester", update, context)
    

def send_image_in_telegram_message(image_path, chat_id, token, caption):
    updater = Updater(token)

    with open(image_path, 'rb') as image:
        updater.bot.send_photo(chat_id=chat_id, photo=image, caption=caption)
