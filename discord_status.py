import os
from dotenv import load_dotenv
import pytz
import time

from pypresence import Presence

import toggl

def _update_presence(session, RPC, is_connected):
    # Update the rich prescence in here

    while True:
        if is_connected:
            # Get current time entry
            entry = None
            try:
                entry = toggl.get_current_time_entry_and_daily_hours(session)
                #entry = toggl.get_running_time_entry(session) # (less intensive) alternative
            except Exception as e:
                print(f"Error getting entry: {e}")
                return

            if entry:
                epoch_start_time = entry["start_time"].strftime('%s')
                epoch_end_time = None
                if entry["end_time"]:
                    epoch_end_time = entry["end_time"].strftime('%s')
                
                image_name = "toggl"

                
                
                if entry["tag"]:
                    if entry["tag"] in toggl.eth_tags:
                        image_name = "eth"

                        # Set info
                        current_info = "No Details"
                        if entry["project_name"] and entry["description"]:
                            current_info = f'{entry["project_name"]} - {entry["description"]}'
                        elif entry["project_name"]:
                            current_info = f'{entry["project_name"]}'
                        elif entry["description"]:
                            current_info = f'{entry["description"]}'

                    elif entry["tag"].lower() == "work":
                        image_name = "work"
                        current_info = "Work"

                    elif entry["tag"].lower() == "private":
                        image_name = "private"
                        current_info = "Private"


                daily_hour_info = None
                eth_hours = round(entry["eth_hours"] * 10) / 10
                total_hours = round(entry["total_hours"] * 10) / 10
                if eth_hours > 0:
                    daily_hour_info = f"Total: {eth_hours}h for ETH today"
                    if total_hours > eth_hours:
                        daily_hour_info += f" of {total_hours}h tracked"
                elif total_hours > 0:
                    daily_hour_info = f"Total: {total_hours}h tracked today"

                # Get hours today to add to status

                # Update discord Rich Presence
                try:
                    RPC.update(
                    details=daily_hour_info,
                    state="Current: "+current_info, 
                    start=epoch_start_time,
                    large_image=image_name,
                    end=epoch_end_time
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

            time.sleep(30)

        else: # not connected
            try:
                print("Trying to connect to discord")
                RPC.connect()
                print("Connected to discord")
                is_connected = True

            except Exception as e:
                print(f"Error connecting to discord: {e}")
                interval = 60 # seconds
                
                # sleep for interval seconds
                time.sleep(interval)
        



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

        print("Starting discord status")
        start_presence(session)

    else:
        print("Discord Status: Token invalid")