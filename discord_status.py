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

                # Update discord Rich Presence
                RPC.update(
                    state=f'{entry["description"]}', 
                    details=f'Project: {entry["project_name"]}',
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