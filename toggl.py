import os
import requests
import base64
import datetime
import json


eth_projects = [
    # Lukas and Menzi
    "Phys. Sim. in CG", 
    "HPCSE I", 
    "DP and Opt. Control", 
    "Computer Graphics", 
    "Case Studies",

    "Network Analysis",
    "Quantenmechanik 1",
    "Bachelor Arbeit",
    "Introduction to Computational Physics", "Intriduction to Computational Physics",
    
    # Deli
    "Lectures/Sessions",
]

def authenticate(token):
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


def _get_time_entries(session, start_date, end_date=None):
    if not end_date:
        end_date = datetime.date.today() + datetime.timedelta(days=1) # date of tomorrow

    start_date_string = start_date.strftime('%Y-%m-%d')
    end_date_string = end_date.strftime('%Y-%m-%d')

    response = session.get("https://api.track.toggl.com/api/v9/me/"
        + f"time_entries?start_date={start_date_string}&end_date={end_date_string}")

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()
        return


def _group_hours_by_project_from_entries(session, time_entries):
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

        multiplier = 1
        project_name = hours_by_projects[project_id]["name"]
        if project_name not in eth_projects:
            multiplier = -1

        if time_entry["stop"]:
            hours_by_projects[project_id]["hours"] += multiplier * time_entry["duration"] / 3600
        else:
            start_datetime_string = time_entry["start"]
            start_datetime = datetime.datetime.fromisoformat(start_datetime_string)
            currently_running_duration = (datetime.datetime.now(datetime.timezone.utc) - start_datetime).total_seconds() / 3600
            hours_by_projects[project_id]["hours"] += currently_running_duration

    return hours_by_projects


def get_hours_today(session):
    today = datetime.date.today()
    time_entries = _get_time_entries(session, today)

    return _group_hours_by_project_from_entries(session, time_entries)


def get_hours_this_week(session):
    monday = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    time_entries = _get_time_entries(session, monday)

    return _group_hours_by_project_from_entries(session, time_entries)