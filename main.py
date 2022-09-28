import os
import pandas as pd
from dotenv import load_dotenv

import toggl
import charts
import telegram_handler


def generate_image(is_week=False):
    tokens = os.getenv("TOGGL_API_TOKENS", "").split(",")
    users = []
    
    if is_week:
        path = "charts/week_bars.png"
        title = "Hours this Week"
    else:
        path = "charts/today_bars.png"
        title = "Hours Today"

    # Dataframe that is created
    """
        user_id  user_name   project_name   hours
    0   AAAAA    Lukas       HPCSE I        3.8
    1   BBBBB    Adel        Exercise       2.1
    """
    d = {"user_id": [], "user_name": [], "project_name": [], "hours": []}
    obj_list = []

    for token in tokens:
        session, user_id, user_name = toggl.authenticate(token)
        #print(user_name)
        users.append(user_name)

        if session:
            if is_week:
                hours_by_projects = toggl.get_hours_this_week(session)
            else:
                hours_by_projects = toggl.get_hours_today(session)
            #print(hours_by_projects)

            for project_id in hours_by_projects:
                obj = {
                    "user_id": user_id, 
                    "user_name": user_name, 
                    "project_name": hours_by_projects[project_id]["name"] or "No Project", 
                    "hours": hours_by_projects[project_id]["hours"]
                }

                obj_list.append(obj)
            
    if len(obj_list) > 0:
        df = pd.DataFrame.from_records(obj_list)
        return charts.generate_stacked_bar_chart_png(df, title=title, path=path)


def generate_image_and_send_message():
    path = generate_image()

    if path:
        chat_id = -736370542
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")

        telegram_handler.send_image_in_telegram_message(path, chat_id, token, caption="Daily hours")
    else: 
        print("No entries to plot and report!")


if __name__ == "__main__":
    load_dotenv()
    
    #generate_image_and_send_message()
    generate_image(True)

