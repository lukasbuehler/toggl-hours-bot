import os
import sys
import datetime

import pandas as pd
from dotenv import load_dotenv

import toggl
import charts
import telegram_handler


def generate_hours_chart(type="today"):
    tokens = os.getenv("TOGGL_API_TOKENS", "").split(",")
    users = []
    
    if type == "today":
        path = "charts/today_bars.png"
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=1)
        title = f"Hours Today ({start_date.strftime('%d.%m.%Y')})"

    elif type == "yesterday":
        path = "charts/yesterday_bars.png"
        start_date = datetime.date.today() - datetime.timedelta(days = 1)
        end_date = start_date + datetime.timedelta(days=1)
        title = f"Hours Yesterday ({start_date.strftime('%d.%m.%Y')})"
        
    elif type == "week":
        path = "charts/week_bars.png"
        start_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
        end_date = datetime.date.today() + datetime.timedelta(days=1)
        title = f"Hours this Week ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    elif type == "lastweek":
        path = "charts/lastweek_bars.png"
        end_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
        start_date = end_date - datetime.timedelta(days=7)
        title = f"Hours Last Week ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    elif type == "month":
        path = "charts/month_bars.png"
        start_date = datetime.date.today().replace(day=1)
        end_date = datetime.date.today() + datetime.timedelta(days=1)
        title = f"Hours this Month ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    elif type == "lastmonth":
        path = "charts/lastmonth_bars.png"
        end_date = datetime.date.today().replace(day=1)
        prev_last_dom = end_date - datetime.timedelta(days=1)
        start_date = prev_last_dom.replace(day=1)
        title = f"Hours Last Month ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"

    elif type == "semester":
        path = "charts/semester_bars.png"
        start_date = datetime.date.fromisoformat("2022-09-19")
        end_date = datetime.date.today() + datetime.timedelta(days=1)
        title = f"Hours this Semester ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"
        

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

    for token in tokens:
        session, user_id, user_name = toggl.authenticate(token)
        #print(user_name)
        users.append(user_name)

        if session:
            hours_by_projects = toggl.get_hours(session, start_date, end_date)

            for project_id in hours_by_projects:
                multiplier = 1
                if not hours_by_projects[project_id]["is_eth"]:
                    multiplier = -1

                project_name = hours_by_projects[project_id]["name"]
                obj = {
                    "user_id": user_id, 
                    "user_name": user_name, 
                    "project_name": project_name, 
                    "hours": multiplier * hours_by_projects[project_id]["hours"]
                }
                obj_list.append(obj)

                if project_name not in added_projects:
                    added_projects.append(project_name)
                    project_color = hours_by_projects[project_id]["color"]
                    color_list.append(project_color)
            
    if len(obj_list) > 0:
        df = pd.DataFrame.from_records(obj_list)
        return charts.generate_stacked_bar_chart_png(df, title=title, project_color_sequence=color_list, path=path)


def generate_and_send_hours(type="today"):
    path = generate_hours_chart(type)

    if path:
        chat_id = -736370542
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")

        #telegram_handler.send_image_in_telegram_message(path, chat_id, token, caption="Daily hours")
    else: 
        print("No entries to plot and report!")


if __name__ == "__main__":
    load_dotenv()
    
    if len(sys.argv) > 1 and str(sys.argv[1]) == "telegram":
        telegram_handler.start_bot()
    if len(sys.argv) > 1 and str(sys.argv[1]) == "send_daily_hours":
        generate_and_send_hours("today")
    if len(sys.argv) > 1:
        chart_type = str(sys.argv[1]) 
        generate_hours_chart(chart_type)
    else:
        generate_hours_chart("today")
