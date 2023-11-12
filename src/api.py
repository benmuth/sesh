import requests
import os
from requests.auth import HTTPBasicAuth

# curl -u <token>:api_token
# token =
username = os.environ.get("TOGGL")
toggl_url = "https://api.track.toggl.com/api/v9/me"


def make_auth_request():
    if username:
        response = requests.get(toggl_url, auth=HTTPBasicAuth(username, "api_token"))
        print("response: status ", response.status_code)
    else:
        raise Unauthorized


class Unauthorized(Exception):
    pass


if __name__ == "__main__":
    try:
        make_auth_request()
    except Unauthorized:
        print("Unauthorized")
