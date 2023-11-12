import requests
import os
from requests.auth import HTTPBasicAuth
from pprint import pprint

api_token = os.environ.get("TOGGL")
toggl_url = "https://api.track.toggl.com/api/v9/me"


# curl -u <token>:api_token
def get_user_info(api_token):
    """
    returns details for the user with the given api_token as JSON.
    """
    response = requests.get(toggl_url, auth=HTTPBasicAuth(api_token, "api_token"))
    if response.status_code == 200:
        return response.json()
    else:
        raise Unauthorized


def get_user_projects(api_token):
    """
    returns details for the user with the given api_token as JSON.
    """
    response = requests.get(
        toggl_url + "/projects",
        headers={"content-type": "application/json"},
        auth=HTTPBasicAuth(api_token, "api_token"),
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Unauthorized


class Unauthorized(Exception):
    pass


if __name__ == "__main__":
    try:
        pprint(get_user_info(api_token))
        pprint(get_user_projects(api_token))
    except Unauthorized:
        print("Unauthorized")
