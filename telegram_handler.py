import os
import sys
import asyncio

import logging
import traceback
import json
import html

from dotenv import load_dotenv

from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.constants import ParseMode

from main import generate_toggl_chart

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def start_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    if token:
        print("Starting Telegram bot")
        app = ApplicationBuilder().token(token).build()

        app.add_handler(CommandHandler("today", _send_hours_chart_today))
        app.add_handler(CommandHandler("day", _send_hours_chart_today))
        app.add_handler(CommandHandler("yesterday", _send_hours_chart_yesterday))
        app.add_handler(CommandHandler("week", _send_hours_chart_week))
        app.add_handler(CommandHandler("lastweek", _send_hours_chart_lastweek))
        app.add_handler(CommandHandler("month", _send_hours_chart_month))
        app.add_handler(CommandHandler("lastmonth", _send_hours_chart_lastmonth))
        app.add_handler(CommandHandler("semester", _send_hours_chart_semester))

        app.add_handler(
            CommandHandler("schedule", _send_schedule_chart_handler, has_args=1)
        )

        # app.add_error_handler(error_handler) # dsabled for now

        app.run_polling()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = os.getenv("CHAT_ID", "")

    if chat_id:
        """Log the error and send a telegram message to notify the developer"""

        logger.error("Exception while handling an update:", exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        tb_string = "".join(tb_list)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        # Finally, send the message
        await context.bot.send_message(
            chat_id=chat_id, text=message, parse_mode=ParseMode.HTML
        )


def _get_image_bytes_from_file_path(path):
    if not path:
        print("image path is empty!")
        return

    with open(path, "rb") as image:
        f = image.read()
        # b = bytearray(f)
        return f


async def _send_hours_chart(hours_type, update, context) -> str:
    chat_id = update.message.chat_id

    # print(f"Chat ID: {chat_id}")
    path, _ = generate_toggl_chart("hours", hours_type)
    img_bytes = _get_image_bytes_from_file_path(path)

    message = await context.bot.send_photo(
        chat_id=chat_id, photo=img_bytes, reply_to_message_id=update.message.message_id
    )

    return message.message_id


async def _send_schedule_chart(update, context) -> str:
    chat_id = update.message.chat_id

    schedule_type = "today"
    if len(context.args) > 0:
        schedule_type = context.args[0]

    print("hi")

    # print(f"Chat ID: {chat_id}")
    path, _ = generate_toggl_chart(
        chart_type_string="schedule", time_type_string=schedule_type
    )
    img_bytes = _get_image_bytes_from_file_path(path)

    message = await context.bot.send_photo(
        chat_id=chat_id, photo=img_bytes, reply_to_message_id=update.message.message_id
    )

    return message.message_id


async def _send_hours_chart_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_hours_chart("today", update, context)


async def _send_hours_chart_yesterday(update, context):
    await _send_hours_chart("yesterday", update, context)


async def _send_hours_chart_week(update, context):
    await _send_hours_chart("week", update, context)


async def _send_hours_chart_lastweek(update, context):
    await _send_hours_chart("lastweek", update, context)


async def _send_hours_chart_month(update, context):
    await _send_hours_chart("month", update, context)


async def _send_hours_chart_lastmonth(update, context):
    await _send_hours_chart("lastmonth", update, context)


async def _send_hours_chart_semester(update, context):
    await _send_hours_chart("semester", update, context)


async def _send_schedule_chart_handler(update, context):
    await _send_schedule_chart(update, context)


def send_image_in_telegram_message(image_path, chat_id, token, caption) -> None:
    """
    Send an image with a caption from a local path to a specified chat.

    Returns the message id of the message that was sent.
    """
    bot = Bot(token)
    loop = asyncio.get_event_loop()

    with open(image_path, "rb") as image:
        loop.run_until_complete(
            bot.send_photo(chat_id=chat_id, photo=image, caption=caption)
        )

    loop.run_until_complete(bot.shutdown())

    loop.close()


async def pin_message(token, chat_id, message_id):
    updater = Updater(token)

    await updater.bot.pin_chat_message(
        chat_id=chat_id, message_id=message_id, disable_notification=True
    )


if __name__ == "__main__":
    load_dotenv()

    # start telegram bot
    if len(sys.argv) > 1 and str(sys.argv[1]) == "start":
        start_bot()
