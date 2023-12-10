import api
import os
import json

# TODO: hook up to SQLite

# TODO: create a class that holds all user data (including a dict mapping project names to IDs)


def sync_projects_with_toggl():
    """
    Writes a list of the user's projects to 'data/projects.json'.
    The list is sorted by user time recorded.
    """
    project_list = api.get_user_projects()
    sorted_project_list = sorted(
        project_list, key=lambda x: x["actual_seconds"], reverse=True
    )
    # print(sorted_project_list)
    project_properties = ["name", "color", "id"]
    projects = [{k: d[k] for k in project_properties} for d in sorted_project_list]
    print("PROJECT DATA RECEIVED FROM TOGGL")
    print(json.dumps(projects, indent=2))

    with open("data/projects.json", "wt") as f:
        f.write(json.dumps(projects))


def sync_tags_with_toggl():
    """
    Writes a list of the user's tags to 'data/tags.json'.
    """
    tag_list = api.get_user_tags()
    tag_properties = ["name", "id"]
    tags = [{k: d[k] for k in tag_properties} for d in tag_list]
    print("TAG DATA RECEIVED FROM TOGGL")
    print(json.dumps(tags, indent=2))

    with open("data/tags.json", "wt") as f:
        f.write(json.dumps(tags))


class UserData:
    def __init__(
        self
    ):  # TODO: handle case where tags and projects files are empty (sync with toggl)
        self.tags = read_data("tags.json")
        self.projects = read_data("projects.json")


# TODO: separate stored data by user
def read_data(
    data_file: str, data_dir: str = "/home/ben/code/python/sesh/data/"
) -> list[dict[str, str]] | None:
    """Reads the given data file if it exists and returns it as a dictionary"""
    valid_data_files = ("projects.json", "tags.json")
    if data_file in valid_data_files:
        with open(os.path.join(data_dir + data_file), "rt") as f:
            data: list[dict[str, str]] = json.JSONDecoder().decode(f.read())
            return data
    else:
        print(f"given data file {data_file} not found")
        return None


data_dir = "/home/ben/code/python/sesh/data/"

# for datum in read_data(data_dir=data_dir):
# print(datum["name"])

# sync_projects_with_toggl(api_token=api_token)
