import os

from telegram.ext import Updater, CommandHandler
from main import generate_image

def start_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    print(token)
    if token:
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
    print(update)
    chat_id = update.message.chat_id

    path = generate_image()
    img_bytes = _get_image_bytes_from_file_path(path)

    context.bot.send_photo(chat_id=chat_id, photo=img_bytes)
    

def send_image_in_telegram_message(image_path, chat_id, token=None):
    if not bot:
        if token:
            _start_bot(token)

    with open("bars.png", 'rb') as image:
        bot.send_photo(chat_id=chat_id, photo=image)

