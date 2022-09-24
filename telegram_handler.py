import os

from telegram.ext import Updater, CommandHandler
from main import generate_image

def start_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    if token:
        print("Starting Telegram bot")
        updater = Updater(token)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('stats', _send_image))
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


def _send_image(update, context):
    print("Sending stats")
    chat_id = update.message.chat_id

    print(f"Chat ID: {chat_id}")
    path = generate_image()
    img_bytes = _get_image_bytes_from_file_path(path)

    context.bot.send_photo(chat_id=chat_id, photo=img_bytes)
    

def send_image_in_telegram_message(image_path, chat_id, token, caption):
    updater = Updater(token)

    with open("bars.png", 'rb') as image:
        updater.bot.send_photo(chat_id=chat_id, photo=image, caption=caption)

