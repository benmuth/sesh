#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
from json.decoder import JSONDecodeError
from typing import Dict, List, Tuple

# from . import core
import requests
import os
from requests.auth import HTTPBasicAuth
from pathlib import Path

import json

# from base64 import b64encode
from datetime import timedelta
from io import StringIO
import csv


class NoData(Exception):
    pass


data_dir = Path.home() / ".cache" / "sesh" / "data"

# ------------------------------------
# API
# ------------------------------------

# TODO: make this not hardcoded
workspace_id = 5992965

toggl_url = "https://api.track.toggl.com/api/v9/me"

api_token: str | None = os.environ.get("TOGGL")
if not api_token:
    raise Exception("No toggle API token found")


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


def start_timer(project_name: str, project_id: int, start_time: str):
    print("start_time:", start_time)
    if not project_id or not start_time or not workspace_id:
        raise NoData
    payload = {
        "created_with": "sesh",
        "duration": -1,
        "project_id": project_id,
        "start": start_time,
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
        # print(response.request.body.decode("utf-8"))
        # for c in response.request.body:
        #     print(str(c))


def get_report(start_date: str, end_date: str):
    payload = {
        # "billable": "boolean",
        "calculate": "time",
        # "client_ids": ["integer"],
        # "description": "string",
        "date_format": "MM/DD/YYYY",
        "end_date": end_date,
        "group_by_task": False,
        # "group_ids": ["integer"],
        # "grouping": "string",
        # "max_duration_seconds": "integer",
        # "min_duration_seconds": "integer",
        # "postedFields": ["string"],
        # "project_ids": ["integer"], TODO: get these
        # "rounding": "integer",
        # "rounding_minutes": "integer",
        # "startTime": "string",
        "start_date": start_date,
        # "tag_ids": ["integer"],
        # "task_ids": ["integer"],
        # "time_entry_ids": ["integer"],
        # "user_ids": ["integer"],
    }
    data = requests.post(
        f"https://api.track.toggl.com/reports/api/v3/workspace/{workspace_id}/weekly/time_entries.csv",
        json=payload,
        headers={
            "content-type": "application/json",
            # "Authorization": "Basic %s"
            # % b64encode(b"<email>:<password>").decode("ascii"),
        },
        auth=HTTPBasicAuth(api_token, "api_token"),
    )
    return data


class Unauthorized(Exception):
    pass


# ------------------------------------
# HELPERS
# ------------------------------------


def print_elapsed_duration(start_time: str):
    time_format = "%Y-%m-%dT%H:%M:%S%z"

    try:
        given_datetime = datetime.strptime(start_time, time_format)
    except ValueError as e:
        print(f"Error parsing time: {e}")
        return

    current_time = datetime.now().astimezone(given_datetime.tzinfo)
    elapsed_duration = current_time - given_datetime

    seconds = elapsed_duration.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    print(f"{hours:02}:{minutes:02}:{seconds:02}")


def last_period_dates(period: str) -> Tuple[str, str]:
    if period == "week":
        # today = datetime.now()
        today = datetime.today()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_of_previous_week = last_monday.strftime("%Y-%m-%d")
        end_of_previous_week = last_sunday.strftime("%Y-%m-%d")
        return (
            start_of_previous_week,
            end_of_previous_week,
        )
    # NOTE: API for this isn't working?
    # TODO: see if you still get "something went terribly wrong" error from Toggl
    elif period == "month":
        today = datetime.today()
        first_day_of_this_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_this_month - timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
        return (
            first_day_of_previous_month.strftime("%Y-%m-%d"),
            last_day_of_previous_month.strftime("%Y-%m-%d"),
        )
    else:
        raise ValueError("Invalid period for report given")


def parse_project_times_from_csv(csv_content):
    result = []
    s = StringIO(csv_content)
    reader = csv.reader(s)
    next(reader)
    for row in reader:
        if row:
            result.append({row[1]: row[-1]})
    return result


def sum_durations(durations):
    total_duration = timedelta()
    for duration in durations:
        hours, minutes, seconds = map(int, duration.split(":"))
        total_duration += timedelta(hours=hours, minutes=minutes, seconds=seconds)

    total_seconds = int(total_duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"


# def sort_dicts(dicts: List[dict], *groups: List[str]):
#     sorted_lists = [[] for _ in groups]

#     for d in dicts:
#         for index, string_list in enumerate(groups):
#             if any(key in d for key in string_list):
#                 sorted_lists[index].append(d)
#                 break

#     return sorted_lists


def group_projects(dicts: List[Dict], groups: Dict[str, List]):
    result = {}

    for d in dicts:
        for label, group in groups.items():
            if any(key in d for key in group):
                try:
                    result[label].append(d)
                except KeyError:
                    result[label] = [d]
                break

    return result


# ------------------------------------
# DATA
# ------------------------------------

# TODO: hook up to SQLite

# TODO: create a class that holds all user data (including a dict mapping project names to IDs)


def create_file_if_not_exists(path: Path):
    # Split the path into head (directories) and tail (file)
    dirs, _ = os.path.split(path)

    # Create directories if they don't exist
    if dirs and not os.path.exists(dirs):
        os.makedirs(dirs)

    # Attempt to create the file
    try:
        f = open(path, "x")
        f.close()
    except FileExistsError:
        pass


def sync_projects_with_toggl():
    """
    Writes a list of the user's projects to 'data/projects.json'.
    The list is sorted by user time recorded.
    """
    project_list = get_user_projects()
    sorted_project_list = sorted(
        project_list, key=lambda x: x["actual_seconds"], reverse=True
    )
    # print(sorted_project_list)
    project_properties = ["name", "color", "id"]
    projects = [{k: d[k] for k in project_properties} for d in sorted_project_list]
    print("PROJECT DATA RECEIVED FROM TOGGL")
    # print(json.dumps(projects, indent=2))

    with open(data_dir / "projects.json", "wt") as f:
        f.write(json.dumps(projects))

    print("data stored at ")


# TODO: separate stored data by user
def read_data(data_file: str, data_dir: Path = data_dir) -> list[dict[str, str]] | None:
    """Reads the given data file if it exists and returns it as a dictionary"""
    create_file_if_not_exists(data_dir / data_file)

    valid_data_files = ("projects.json", "tags.json")
    if data_file in valid_data_files:
        with open(data_dir / data_file, "rt") as f:
            try:
                data: list[dict[str, str]] = json.JSONDecoder().decode(f.read())
                return data
            except JSONDecodeError:
                sync_projects_with_toggl()
                read_data(data_file=data_file)

    else:
        print(f"given data file {data_file} not found")
        return None


# ------------------------------------
# CLI
# ------------------------------------


def timer(args: argparse.Namespace):
    if args.project in args.projects:
        print(args.project)
    else:
        print(
            f"timer {args.project} not found in list of projects. Please choose from {args.projects}"
        )


def stop(args: argparse.Namespace):
    running_timer = get_running_timer()
    if not running_timer:
        print("No timer running")
        return
    time_entry_id = running_timer["id"]
    workspace_id = running_timer["workspace_id"]
    project_id = running_timer["project_id"]
    response = stop_timer(time_entry_id=time_entry_id, workspace_id=workspace_id)
    start = response["start"]
    for project in args.stored_projects:
        if project["id"] == project_id:
            print("stopping", project["name"])
            print_elapsed_duration(start)
            return


def start(args: argparse.Namespace):
    if args.project in args.project_names:
        project_id = None
        print("starting", args.project)
        for project in args.stored_projects:
            if project["name"] == args.project:
                project_id = project["id"]
                break

        now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if project_id is None:
            raise NoData
        print("start", args.project)
        start_timer(
            project_name=args.project,
            project_id=project_id,
            start_time=now,
        )
    else:
        print(f"timer {args.project} not found in list of projects")
        print("projects:", args.projects)
        return


def sync(args: argparse.Namespace):
    sync_projects_with_toggl()


def show_running_timer(args: argparse.Namespace):
    response = get_running_timer()
    if response:
        project_id = response["project_id"]
        start = response["start"]
        for project in args.stored_projects:
            if project["id"] == project_id:
                print(project["name"])
                print_elapsed_duration(start)
                return
    else:
        print("No timer running")


def report(args: argparse.Namespace):
    start_date, end_date = last_period_dates(args.period)
    print(f"report from {start_date} to {end_date}:")
    data = get_report(start_date, end_date)

    csv = data.content.decode("utf8")
    project_times = parse_project_times_from_csv(csv)

    # total = sum_durations([list(project.values())[0] for project in times])
    grouped_projects = group_projects(project_times, args.project_groups)

    # print(total)
    # print(result)
    # print(sorted_dicts)

    def print_dictionary(sorted_dict):
        for key, dict_list in sorted_dict.items():
            total_time = sum_durations([list(d.values())[0] for d in dict_list])
            print(f"### {key}: {total_time}")
            sorted_list = sorted(
                dict_list, key=lambda x: list(x.values()), reverse=True
            )
            for i, d in enumerate(sorted_list, 1):
                for sub_key, sub_value in d.items():
                    print(f"{i}. {sub_key} {sub_value}")

    print_dictionary(grouped_projects)


def main():
    stored_projects: list[dict[str, str]] | None = read_data("projects.json")
    if not stored_projects:
        raise NoData
    project_names: list[str] = [x["name"] for x in stored_projects]

    parser = argparse.ArgumentParser(
        description="Control Toggl Track timers from the command line"
    )
    parser.set_defaults(stored_projects=stored_projects)
    parser.add_argument(
        "-r",
        "--running",
        help="display the currently running timer",
        action="store_true",
        required=False,
    )

    parser.add_argument(
        "-l",
        "--list",
        help="display all projects",
        action="store_true",
        required=False,
    )

    subparsers = parser.add_subparsers(
        title="subcommands", help="sub-command help", dest="subcommands"
    )

    # STOP
    parser_stop = subparsers.add_parser("stop", help="Stops the current timer")
    parser_stop.set_defaults(func=stop)

    # START
    parser_start = subparsers.add_parser("start", help="Start a timer")
    parser_start.add_argument(
        "project", help="the name of the project to start", choices=project_names
    )
    parser_start.set_defaults(
        func=start, project_names=project_names, stored_projects=stored_projects
    )
    # SYNC
    parser_sync = subparsers.add_parser("sync", help="Syncs user data with Toggl")
    parser_sync.set_defaults(func=sync)

    # REPORT
    parser_report = subparsers.add_parser(
        "report", help="See your report for last week or month"
    )
    parser_report.add_argument(
        "period", help="the period for the report", choices=["week", "month"]
    )
    # TODO: make this configurable instead of hard coded
    project_groups = {
        "work": [
            "Programming",
            "Reading/Watching Programming",
            "ProductScope",
            "Puzzles and algorithms",
            "ArchiveBox",
            "Blogging/Writing",
            "bert email project",
            "Linux admin",
            "exercise",
            "Programming study",
            "Jobs",
            "RC",
            "MIT OCW",
            "Spanish",
            "Writing",
            "math",
        ],
        "unproductive": ["browsing"],
        "other": ["loft", "Drawing", "Malayalam", "tools", "meta", "Finance"],
    }

    parser_report.set_defaults(func=report, project_groups=project_groups)

    args = parser.parse_args()
    if args.running:
        show_running_timer(args)
    elif args.list:
        for project in project_names:
            print(project)
    elif args.subcommands is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
