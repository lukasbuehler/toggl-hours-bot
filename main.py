import os
import sys
import datetime

import pandas as pd
from dotenv import load_dotenv

import toggl
import charts
import telegram_handler
import motivation 

def _get_start_and_end_date_from_type_string(type_string="today") -> (datetime.date, datetime.date, str, str): 
    """
    A simple helper function that translates the command strings to python 
    datetime dates and other necessairy variables.

    Returns: start_date (datetime.date), end_date ...
    """

    if type_string == "today":
        path = "charts/today_bars.png"
        start_date = datetime.date.today()
        end_date = start_date
        title = f"Hours Today ({start_date.strftime('%d.%m.%Y')})"

    elif type_string == "yesterday":
        path = "charts/yesterday_bars.png"
        start_date = datetime.date.today() - datetime.timedelta(days = 1)
        end_date = start_date
        title = f"Hours Yesterday ({start_date.strftime('%d.%m.%Y')})"
        
    elif type_string == "week":
        path = "charts/week_bars.png"
        start_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
        end_date = datetime.date.today()
        title = f"Hours this Week ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    elif type_string == "lastweek":
        path = "charts/lastweek_bars.png"
        end_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
        start_date = end_date - datetime.timedelta(days=7)
        title = f"Hours Last Week ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    elif type_string == "month":
        path = "charts/month_bars.png"
        start_date = datetime.date.today().replace(day=1)
        end_date = datetime.date.today()
        title = f"Hours this Month ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    elif type_string == "lastmonth":
        path = "charts/lastmonth_bars.png"
        end_date = datetime.date.today().replace(day=1)
        prev_last_dom = end_date - datetime.timedelta(days=1)
        start_date = prev_last_dom.replace(day=1)
        title = f"Hours Last Month ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    elif type_string == "semester":
        path = "charts/semester_bars.png"
        start_date = datetime.date.fromisoformat("2022-09-19")
        end_date = datetime.date.today()
        title = f"Hours this Semester ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    return start_date, end_date, title, path


def get_hours_object_list(type_string="today"):
    tokens = os.getenv("TOGGL_API_TOKENS", "").split(",")
    users = []
    
    start_date, end_date, title, path = _get_start_and_end_date_from_type_string(type_string)
        

    # Dataframe that is created
    """
        user_id  user_name   project_name   hours
    0   AAAAA    Lukas       HPCSE I        3.8
    1   BBBBB    Adel        Exercise       2.1
    """

    #d = {"user_id": [], "user_name": [], "project_name": [], "hours": []}
    obj_list = []
    color_list = []
    added_projects = []
    users_hours = []

    for token in tokens:
        session, user_id, user_name = toggl.authenticate(token)
        #print(user_name)
        users.append(user_name)
        
        user_hours = {
            "name": user_name, 
            "eth_hours": 0,
            "other_hours": 0,
            "day_target_hours": 6,
            "week_target_hours": 36,
            "motivation_strategy": "roast"
        }
        hours = 0

        if not session:
            print("get_hours_object_list(): The session is invalid")

        hours_by_projects = toggl.get_hours(session, start_date, end_date)

        for project_id in hours_by_projects:
            hours = hours_by_projects[project_id]["hours"]
            multiplier = 1

            if not hours_by_projects[project_id]["is_eth"]:
                multiplier = -1
                user_hours["other_hours"] += hours
            else:
                user_hours["eth_hours"] += hours
            

            project_name = hours_by_projects[project_id]["name"]
            obj = {
                "user_id": user_id, 
                "user_name": user_name, 
                "project_name": project_name, 
                "hours": multiplier * hours
            }
            obj_list.append(obj)

            if project_name not in added_projects:
                # Only add the color to the array if there is no other project with the same name
                added_projects.append(project_name)
                project_color = hours_by_projects[project_id]["color"]
                color_list.append(project_color)

        users_hours.append(user_hours)
        data = {
            "user_hours": users_hours,
            "objects": obj_list
        }

    return obj_list, data, color_list, title, path


def generate_hours_chart(type_string="today"):
    obj_list, data, color_list, title, path = get_hours_object_list(type_string)
            
    if len(obj_list) > 0:
        df = pd.DataFrame.from_records(obj_list)
        path = charts.generate_stacked_bar_chart_png(df, title=title, project_color_sequence=color_list, path=path)

        return path, data


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
    
    # start telegram bot
    if len(sys.argv) > 1 and str(sys.argv[1]) == "telegram":
        telegram_handler.start_bot()

    # Recaps
    elif len(sys.argv) > 1 and str(sys.argv[1]) == "day-recap":
        recap_day()
        
    elif len(sys.argv) > 1 and str(sys.argv[1]) == "week-recap":
        recap_week()

    elif len(sys.argv) > 1 and str(sys.argv[1]) == "month-recap":
        recap_month()

    # Unrecognized command
    elif len(sys.argv) > 1:
        chart_type = str(sys.argv[1])
        generate_hours_chart(chart_type)
        
    # No command
    else:
        generate_hours_chart("today")
