import os
from dotenv import load_dotenv
import pytz
import threading

from pypresence import Presence

import toggl

def _update_presence(session, RPC, is_connected):
    # Update the rich prescence in here

    if not is_connected:
        try:
            RPC.connect()
            print("Connected to discord")
            is_connected = True

        except:
            print("Error connecting to discord, trying again in a minute")
            
            timer = threading.Timer(60.0, _update_presence, [session, RPC, False])
            timer.start()
            return

    # Get current time entry
    #entry = toggl.get_current_time_entry_and_daily_hours(session)
    entry = toggl.get_running_time_entry(session)
    #print(entry)

    if entry:
        epoch_start_time = entry["start_time"].astimezone(pytz.timezone("Europe/Zurich")).strftime('%s')
        
        image_name = "toggl"
        if entry["project_name"] in toggl.eth_projects:
            image_name = "eth"

        details = "No Details"
        state = ""
        if entry["project_name"] and entry["description"]:
            details = f'{entry["project_name"]} - {entry["description"]}'
        elif entry["project_name"]:
            details = f'{entry["project_name"]}'
        elif entry["description"]:
            details = f'{entry["description"]}'

        # Get hours today to add to status

        # Update discord Rich Presence
        try:
            RPC.update(
                details=details,
                #state=state, 
                start=epoch_start_time,
                large_image=image_name
            )
        except:
            print("Lost connection to discord")
            is_connected = False
    else:
        try:
            RPC.clear()
        except:
            print("Lost connection to discord")
            is_connected = False

    # Can only update rich presence every 15 seconds
    timer = threading.Timer(30.0, _update_presence, [session, RPC, is_connected])
    timer.start()


def start_presence(session):
    client_id = os.getenv("DISCORD_CLIENT_ID", "")
    if client_id:
        RPC = Presence(client_id)
        _update_presence(session, RPC, False)
        
    else:
        print("client_id invalid")


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOGGL_TOKEN", "")

    if token:
        session, _, _ = toggl.authenticate(token)

        start_presence(session)

    else:
        print("Discord Status: Token invalid")