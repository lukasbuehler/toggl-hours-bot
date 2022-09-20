import os
import requests
from dotenv import load_dotenv
import base64
import datetime
import json

session = requests.Session()


def _authenticate():
    load_dotenv()

    token = os.getenv("TOGGL_API_TOKEN", "")

    if token:
        #print("Token successfully loaded")
        api_url = "https://api.track.toggl.com/api/v9/me/sessions" # curl -u 1971800d4d82861d8f2c1651fea4d212:api_token
        
        auth_base64_string = base64.b64encode(f"{token}:api_token".encode('ascii')).decode('ascii')
        
        response = session.post(api_url, headers={'Authorization': f'Basic {auth_base64_string}'})
        
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
    else:
        print("'TOGGL_API_TOKEN' not specified in .env file")


def _get_project_name_by_project_id():
    pass


def _get_time_entries_of_today():
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

def _get_hours_today(time_entries=None):
    if not time_entries:
        time_entries = _get_time_entries_of_today()

    for time_entry in time_entries:
        print(str(time_entry["description"])+": "+str(time_entry["duration"]))
    

if __name__ == "__main__":
    _authenticate()
    _get_hours_today()