import os
import requests
from dotenv import load_dotenv
import base64
import datetime
import json

import pandas as pd
import charts


def _authenticate(token):
    session = requests.Session()
    #print("Token successfully loaded")
    api_url = "https://api.track.toggl.com/api/v9/me/sessions" # curl -u 1971800d4d82861d8f2c1651fea4d212:api_token
    
    auth_base64_string = base64.b64encode(f"{token}:api_token".encode('ascii')).decode('ascii')
    
    response = session.post(api_url, headers={'Authorization': f'Basic {auth_base64_string}'})
    
    if response.status_code != requests.codes.ok:
        response.raise_for_status()
        return None

    response_json = response.json()
    user_id = response_json['id']
    user_name = response_json['fullname']

    return session, user_id, user_name


def _get_project_name_by_project_id(session, workspace_id, project_id):
    response = session.get(f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects/{project_id}")
    
    if response.status_code == requests.codes.ok:
        return response.json()["name"]


def _get_time_entries_of_today(session):
    today = datetime.date.today()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    today_string = today.strftime('%Y-%m-%d') # Example that works 2022-09-20
    tomorrow_string = tomorrow.strftime('%Y-%m-%d')

    response = session.get("https://api.track.toggl.com/api/v9/me/"
        + f"time_entries?start_date={today_string}&end_date={tomorrow_string}")

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()
        return


def _get_hours_today(session, time_entries=None):
    if not time_entries:
        time_entries = _get_time_entries_of_today(session)

    hours_by_projects = {}

    for time_entry in time_entries:
        # Duration of time entries is in 
        
        #print(time_entry)

        project_id = time_entry["project_id"]

        if not project_id:
            project_id = 0

        project_id = str(project_id)
        if project_id not in hours_by_projects:
            workspace_id = time_entry["workspace_id"]
            project_name = _get_project_name_by_project_id(session, workspace_id, project_id)
            hours_by_projects[project_id] = { "name": project_name,"workspace_id": workspace_id, "hours": 0 }

        if time_entry["stop"]:
            hours_by_projects[project_id]["hours"] += time_entry["duration"] / 3600
        else:
            start_datetime_string = time_entry["start"]
            start_datetime = datetime.datetime.fromisoformat(start_datetime_string)
            currently_running_duration = (datetime.datetime.now(datetime.timezone.utc) - start_datetime).total_seconds() / 3600
            hours_by_projects[project_id]["hours"] += currently_running_duration

    return hours_by_projects
        
        

if __name__ == "__main__":
    load_dotenv()

    tokens = os.getenv("TOGGL_API_TOKENS", "").split(",")
    users = []

    # Dataframe that is created
    """
        user_id  user_name   project_name   hours
    0   AAAAA    Lukas       HPCSE I        3.8
    1   BBBBB    Adel        Exercise       2.1
    """
    d = {"user_id": [], "user_name": [], "project_name": [], "hours": []}
    df = pd.DataFrame(data=d)

    for token in tokens:
        session, user_id, user_name = _authenticate(token)
        users.append(user_name)

        if session:
            hours_by_projects = _get_hours_today(session)

            for project_id in hours_by_projects:
                df2 = {
                    "user_id": user_id, 
                    "user_name": user_name, 
                    "project_name": hours_by_projects[project_id]["name"] or "No Project", 
                    "hours": hours_by_projects[project_id]["hours"]
                }

                df = df.append(df2, ignore_index = True)
            

    
    
    charts.generate_stacked_bar_chart_png(df)