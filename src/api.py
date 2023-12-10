import requests
import os
from requests.auth import HTTPBasicAuth
from pprint import pprint
import json

from cli import NoData
# from base64 import b64encode

# TODO: make this not hardcoded
workspace_id = 5992965

toggl_url = "https://api.track.toggl.com/api/v9/me"

api_token: str | None = os.environ.get("TOGGL")
if not api_token:
    raise Exception("No toggle API token found")


# curl -u <token>:api_token
def get_user_info(api_token: str = api_token):
    """
    returns details for the user with the given api_token as JSON.
    """
    response = requests.get(toggl_url, auth=HTTPBasicAuth(api_token, "api_token"))
    if response.status_code == 200:
        return response.json()
    else:
        raise Unauthorized


def get_user_projects(api_token: str = api_token):
    """
    returns the projects of the user with the given api_token as JSON.
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


def get_user_tags(api_token: str = api_token):
    """
    Gets project names and ids
    the format is a list of dicts like this
            {'at': '2022-08-26T20:33:32.262363Z',
              'id': 10950283,
              'name': 'Tour of Go',
              'workspace_id': 5992965}
    """
    response = requests.get(
        f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags",
        headers={"content-type": "application/json"},
        auth=HTTPBasicAuth(api_token, "api_token"),
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Unauthorized


def get_running_timer(api_token: str = api_token) -> dict[str, str]:
    url = toggl_url + "/time_entries/current"
    response = requests.get(
        url,
        headers={"content-type": "application/json"},
        auth=HTTPBasicAuth(api_token, "api_token"),
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Unauthorized


def stop_timer(time_entry_id: str, workspace_id: str):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/time_entries/{time_entry_id}/stop"
    response = requests.patch(
        url,
        headers={
            "content-type": "application/json",
        },
        auth=HTTPBasicAuth(api_token, "api_token"),
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Unauthorized


def start_timer(project_name: str, project_id: int, start_time: str, tag_id: int):
    print("start_time:", start_time)
    if not project_id or not start_time or not workspace_id:
        raise NoData
    payload = {
        "created_with": "sesh",
        "duration": -1,
        "project_id": project_id,
        "start": start_time,
        "tag_action": "add",
        "tag_ids": [tag_id],
        "tags": [project_name],
        "workspace_id": workspace_id,
    }
    response = requests.post(
        f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/time_entries",
        json=payload,
        headers={"content-type": "application/json"},
        auth=HTTPBasicAuth(api_token, "api_token"),
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(response.reason)
        print(response.text)
        print(response.request.url)
        print(response.request.headers)
        print(response.request.body.decode("utf-8"))
        # for c in response.request.body:
        #     print(str(c))


class Unauthorized(Exception):
    pass


if __name__ == "__main__":
    try:
        # pprint(get_user_info(api_token))
        # pprint(get_user_projects(api_token))
        # pprint(get_running_timer(api_token))
        pprint(get_user_tags())
    except Unauthorized:
        print("Unauthorized")
