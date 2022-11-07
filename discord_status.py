import os
from dotenv import load_dotenv
import pytz
import time


from pypresence import Presence

import toggl

def start_presence(session):
    client_id = os.getenv("DISCORD_CLIENT_ID", "")
    if client_id:
        RPC = Presence(client_id)
        RPC.connect()

        while True:
            # Update the rich prescence in here

            # Get current time entry
            entry = toggl.get_running_time_entry(session)
            if entry:
                epoch_start_time = entry["start_time"].astimezone(pytz.timezone("Europe/Zurich")).strftime('%s')

                details = ""
                if entry["project_name"] and entry["description"]:
                    details = f'{entry["project_name"]} - {entry["description"]}'
                elif entry["project_name"]:
                    details = f'{entry["project_name"]}'
                elif entry["description"]:
                    details = f'{entry["description"]}'
                else:
                    details = "No Project"

                

                # Update discord Rich Presence
                RPC.update(
                    #state=description, 
                    details=details,
                    start=epoch_start_time,
                    large_image="toggl"
                )
            else:
                RPC.clear()

            time.sleep(15) # Can only update rich presence every 15 seconds
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