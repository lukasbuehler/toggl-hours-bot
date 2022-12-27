import os
import requests
import base64
import json
import datetime

import pytz


eth_projects = [
    # Lukas and Menzi
    "Phys. Sim. in CG", 
    "HPCSE I", 
    "DP and Opt. Control", 
    "Computer Graphics", 
    "Case Studies",

    # Anna
    "Network Analysis",
    "Quantenmechanik 1",
    "Bachelorarbeit",
    "Introduction to Computational Physics",
    
    # Deli
    "Lectures/Sessions",
    "Study",
    "Practice",
    "Preparation",
    "Exams"
]

LOCAL_TIMEZONE_STR = datetime.datetime.now().astimezone().tzname()

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


def _get_project_info_by_project_id(session, workspace_id, project_id):
    response = session.get(f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects/{project_id}")
    
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status
        return None


def _get_time_entries(session, start_date, end_date=None):
    if not end_date:
        end_date = datetime.date.today()

    # The Toggl API uses the end date as the last date it checks for entries
    # threfore add a day to make it till midnight the next day
    end_date = end_date + datetime.timedelta(days=1)
    start_date = start_date - datetime.timedelta(days=1)

    start_date_string = start_date.strftime('%Y-%m-%d')
    end_date_string = end_date.strftime('%Y-%m-%d')

    response = session.get("https://api.track.toggl.com/api/v9/me/"
        + f"time_entries?start_date={start_date_string}&end_date={end_date_string}")

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()


def _get_current_time_entry(session):
    response = session.get("https://api.track.toggl.com/api/v9/me/time_entries/current")

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()


def _get_duration_in_hours_from_entry(time_entry, start_date):
    """
    - time_entry: Toggl time_entry object 
    - start_date: python date object of the date we want to start counting hours from
        note: time entries can start earlier and can go into the start date.
    """

    hours_duration = 0
    is_current = False # Wether this entry is the one currently active, (either it's running or we are inside it)

    start_datetime = datetime.datetime.fromisoformat(time_entry["start"]).astimezone()
    start_entries_time = pytz.timezone(LOCAL_TIMEZONE_STR).localize(datetime.datetime.fromordinal(start_date.toordinal()))

    if start_datetime < start_entries_time:
        if time_entry["stop"]:
            stop_datetime = datetime.datetime.strptime(time_entry["stop"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC).astimezone()
            if stop_datetime < start_entries_time:
                return 0, start_datetime, stop_datetime, False
            else:
                # This time entry ran through midnight, handle it correctly
                # Calculate the duration from midnight to stop time
                hours_duration = (stop_datetime - start_entries_time).total_seconds() / 3600

            now = datetime.datetime.now().astimezone()
            if now > start_datetime and now < stop_datetime:
                is_current = True

            return hours_duration, start_entries_time, stop_datetime, is_current

        else:
            # This time entry also is still running
            hours_duration = (datetime.datetime.now(tz=pytz.timezone("Europe/Zurich")) - start_entries_time).total_seconds() / 3600
            is_current = True

            return hours_duration, start_entries_time, None, is_current

    else:
        # The entry started after the start time, so count its duration
        if time_entry["stop"]:
            hours_duration = time_entry["duration"] / 3600

            now = datetime.datetime.now().astimezone()
            stop_datetime = datetime.datetime.strptime(time_entry["stop"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC).astimezone()
            if now > start_datetime and now < stop_datetime:
                is_current = True

            return hours_duration, start_datetime, stop_datetime, is_current

        else:
            if time_entry["duration"] != 0:
                # This time entry is still running, calculate the duration yourself
                hours_duration = (datetime.datetime.now(tz=pytz.timezone("Europe/Zurich")) - start_datetime).total_seconds() / 3600
                is_current = True
                return hours_duration, start_datetime, None, is_current
            else:
                return 0, None, None, False


    


def _group_hours_by_project_from_entries(session, time_entries, start_date):
    hours_by_projects = {}

    for time_entry in time_entries:
        
        hours_duration, _, _, _ = _get_duration_in_hours_from_entry(time_entry, start_date)
        if hours_duration <= 0:
            continue


        project_id = time_entry["project_id"]

        if not project_id:
            project_id = 0

        project_id = str(project_id)
        if project_id not in hours_by_projects:
            workspace_id = time_entry["workspace_id"]

            # default values
            project_name = "No Project"
            project_color = "grey"
            project_is_eth = False

            if project_id != str(0):
                project_info = _get_project_info_by_project_id(session, workspace_id, project_id)
                if project_info:
                    project_name = project_info["name"]
                    project_color = project_info["color"]
                    project_is_eth = project_name in eth_projects

            hours_by_projects[project_id] = { 
                "name": project_name,
                "workspace_id": workspace_id, 
                "hours": 0, 
                "color": project_color, 
                "is_eth": project_is_eth
            }

        hours_by_projects[project_id]["hours"] += hours_duration

    #print(hours_by_projects)
    return hours_by_projects



def get_hours(session, start_date, end_date):
    time_entries = _get_time_entries(session, start_date, end_date)
    #print(time_entries)
    return _group_hours_by_project_from_entries(session, time_entries, start_date)


def get_running_time_entry(session):
    time_entry = _get_current_time_entry(session)

    if time_entry:
        project_id = time_entry["project_id"] or 0
        entry_description = time_entry["description"]

        project_id = str(project_id)
        workspace_id = time_entry["workspace_id"]

        # default value

        project_name = ""
        if project_id != str(0):
            project_info = _get_project_info_by_project_id(session, workspace_id, project_id)
            if project_info:
                project_name = project_info["name"]


        if time_entry["start"]:
            start_datetime_string = time_entry["start"]
            start_datetime = datetime.datetime.fromisoformat(start_datetime_string)

        return {
            "project_name": project_name,
            "description": entry_description,
            "start_time": start_datetime
        }


def get_current_time_entry_and_daily_hours(session):
    today_date = datetime.date.today()
    time_entries = _get_time_entries(session, today_date)

    has_current_project = False
    total_eth_hours = 0
    total_hours = 0
    current_project_name = ""
    current_entry_description = ""
    current_start_datetime = None
    current_end_datetime = None

    for time_entry in time_entries:
        hours_duration, entry_start_datetime, entry_end_datetime, is_current = _get_duration_in_hours_from_entry(time_entry, today_date)
        if hours_duration <= 0:
            continue # this entry does not contribute to today, skip the rest of this loop iteration

        total_hours += hours_duration

        project_id = time_entry["project_id"] or 0
        workspace_id = time_entry["workspace_id"]

        if project_id != 0:
            project_info = _get_project_info_by_project_id(session, workspace_id, project_id)
            if project_info:
                if project_info["name"] in eth_projects:
                    total_eth_hours += hours_duration
                
                if is_current:
                    current_project_name = project_info["name"]

        if is_current:
            has_current_project = True
            current_entry_description = time_entry["description"]
            current_start_datetime = entry_start_datetime
            current_end_datetime = entry_end_datetime

    if has_current_project:
        return {
            "project_name": current_project_name,
            "description": current_entry_description,
            "start_time": current_start_datetime,
            "end_time": current_end_datetime,
            "eth_hours": total_eth_hours,
            "total_hours": total_hours,
        }

    return