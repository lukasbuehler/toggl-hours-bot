import os
import requests
from dotenv import load_dotenv
import base64

session = requests.Session()

def _authenticate():
    load_dotenv()

    token = os.getenv("TOGGL_API_TOKEN", "")
    print(token)

    if token:
        print("Token successfully loaded")
        api_url = "https://api.track.toggl.com/api/v9/me/sessions" # curl -u 1971800d4d82861d8f2c1651fea4d212:api_token
        auth_base64_string = base64.b64encode(f"{token}:api_token".encode('ascii')).decode('ascii')
        print(auth_base64_string)
        response = session.post(api_url, headers={'Authorization': f'Basic {auth_base64_string}'})
        
        if response.status_code == requests.codes.ok:
            print("success")
            print(f"Cookie: {session.cookies}")
        else:
            response.raise_for_status()
    else:
        print("'TOGGL_API_TOKEN' not specified in .env file")

def _get_daily_hours():
    pass

if __name__ == "__main__":
    _authenticate()