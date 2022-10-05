import os
import sys

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
        title = "Hours Today"
        get_hours_func = toggl.get_hours_today
        
    elif type == "week":
        path = "charts/week_bars.png"
        title = "Hours this Week"
        get_hours_func = toggl.get_hours_week

    elif type == "month":
        path = "charts/month_bars.png"
        title = "Hours this Month"
        get_hours_func = toggl.get_hours_month

    elif type == "semester":
        path = "charts/semester_bars.png"
        title = "Hours this Semester"
        get_hours_func = toggl.get_hours_semester
        

    # Dataframe that is created
    """
        user_id  user_name   project_name   hours
    0   AAAAA    Lukas       HPCSE I        3.8
    1   BBBBB    Adel        Exercise       2.1
    """
    #d = {"user_id": [], "user_name": [], "project_name": [], "hours": []}
    obj_list = []
    color_list = []

    for token in tokens:
        session, user_id, user_name = toggl.authenticate(token)
        #print(user_name)
        users.append(user_name)

        if session:
            hours_by_projects = get_hours_func(session)
            #print(hours_by_projects)

            for project_id in hours_by_projects:
                multiplier = 1
                if not hours_by_projects[project_id]["is_eth"]:
                    multiplier = -1

                obj = {
                    "user_id": user_id, 
                    "user_name": user_name, 
                    "project_name": hours_by_projects[project_id]["name"], 
                    "hours": multiplier * hours_by_projects[project_id]["hours"]
                }
                obj_list.append(obj)

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

        telegram_handler.send_image_in_telegram_message(path, chat_id, token, caption="Daily hours")
    else: 
        print("No entries to plot and report!")


if __name__ == "__main__":
    load_dotenv()
    
    if len(sys.argv) > 1 and str(sys.argv[1]) == "telegram":
        telegram_handler.start_bot()
    if len(sys.argv) > 1 and str(sys.argv[1]) == "week":
        generate_and_send_hours("week")
    else:
        generate_and_send_hours("today")
