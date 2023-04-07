import os
import sys

from dotenv import load_dotenv

import telegram_handler
import motivation
from main import generate_hours_chart, get_hours_object_list

def generate_and_send_hours(_type="today"):
    path, _ = generate_hours_chart(_type)

    if path:
        chat_id = os.getenv("CHAT_ID", 0)
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")

        if chat_id and token:
            telegram_handler.send_image_in_telegram_message(path, chat_id, token, caption=f"Hours for {_type}")

    else: 
        print("No entries to plot and report!")

def recap_day():
    path, today_data = generate_hours_chart("today")

    if not path or not today_data:
        print("Day Recap: path invalid")
        return

    chat_id = os.getenv("CHAT_ID", 0)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    if not chat_id or not token:
        print("Day Recap: chat_id or token invalid")
        return

    # get weeekly data to check week status
    week_obj_list, week_data, _, _, _ = get_hours_object_list("week")

    text = motivation.make_day_recap_caption(today_data, week_data)

    telegram_handler.send_image_in_telegram_message(path, chat_id, token, caption=text)

def recap_week():
    path, week_data = generate_hours_chart("week")

    if not path or not week_data:
        print("Day Recap: path invalid")
        return

    chat_id = os.getenv("CHAT_ID", 0)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    if not chat_id or not token:
        print("Day Recap: chat_id or token invalid")
        return

    text = motivation.make_week_recap_caption(week_data)

    message_id = telegram_handler.send_image_in_telegram_message(path, chat_id, token, caption=text)

    if message_id:
        telegram_handler.pin_message(token, chat_id, message_id)


def recap_month():
    type_str = "month"
    if datetime.date.today().day <= 1:
        type_str = "lastmonth"

    path, data = generate_hours_chart(type_str)

    if path:
        chat_id = os.getenv("CHAT_ID", 0)
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")

        if chat_id and token:
            telegram_handler.send_image_in_telegram_message(path, chat_id, token, caption=f"Hours for this month")
        else:
            print("Month recap: Chat ID or token invalid")

    else: 
        print("Month Recap: No entries to plot and report!")


if __name__ == "__main__":
    load_dotenv()

    # Recaps
    if len(sys.argv) > 1 and str(sys.argv[1]) == "day-recap":
        recap_day()
        
    elif len(sys.argv) > 1 and str(sys.argv[1]) == "week-recap":
        recap_week()

    elif len(sys.argv) > 1 and str(sys.argv[1]) == "month-recap":
        recap_month()

