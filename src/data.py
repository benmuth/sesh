import api
import os
import json

api_token: str | None = os.environ.get("TOGGL")
if not api_token:
    raise Exception("No toggle API token found")


def sync_projects_with_toggl(api_token: str):
    project_list = api.get_user_projects(api_token=api_token)
    sorted_project_list = sorted(
        project_list, key=lambda x: x["actual_seconds"], reverse=True
    )
    project_properties = ["name", "color"]
    projects = [{k: d[k] for k in project_properties} for d in sorted_project_list]
    print(json.dumps(projects, indent=2))

    with open("data/projects.json", "wt") as f:
        f.write(json.dumps(projects))


def read_data() -> list[dict[str, str]]:
    data_dir = "/home/ben/code/python/sesh/data/"

    data: list[dict[str, str]] = [{}]
    for data_file in os.listdir(data_dir):
        with open(os.path.join(data_dir + data_file), "rt") as f:
            data: list[dict[str, str]] = json.JSONDecoder().decode(f.read())
    return data


for datum in read_data():
    print(datum["name"])

# sync_projects_with_toggl(api_token=api_token)
