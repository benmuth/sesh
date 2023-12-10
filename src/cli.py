import argparse
import data_layer
import api
from datetime import datetime, timezone
# from . import core


class NoData(Exception):
    pass


def timer(args: argparse.Namespace):
    if args.project in args.projects:
        print(args.project)
    else:
        print(
            f"timer {args.project} not found in list of projects. Please choose from {args.projects}"
        )


def stop(args: list[str]):
    running_timer = api.get_running_timer()
    time_entry_id = running_timer["id"]
    workspace_id = running_timer["workspace_id"]
    timer_name = running_timer["tags"][0]
    # print(running_timer)
    print(time_entry_id, workspace_id, timer_name)
    response = api.stop_timer(time_entry_id=time_entry_id, workspace_id=workspace_id)
    print("stop response: %s" % response)
    print("stopped %s" % timer_name)
    # print("STOP")


def start(args: argparse.Namespace):
    if args.project in args.projects and args.project in args.tags:
        project_id = None
        print(args.project)
        for project in args.user_data.projects:
            if project["name"] == args.project:
                project_id = project["id"]

        tag_id = None
        for tag in args.user_data.tags:
            if tag["name"] == args.project:
                tag_id = tag["id"]

        now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if project_id is None:
            raise NoData
        if tag_id is None:
            raise NoData
        print("start", args.project)
        api.start_timer(
            project_name=args.project,
            project_id=project_id,
            start_time=now,
            tag_id=tag_id,
        )
    else:
        print(f"timer {args.project} not found in list of projects")
        print("projects:", args.projects)
        print("tags:", args.tags)
        return


def sync(args: list[str]):
    data_layer.sync_projects_with_toggl()


def main():
    stored_projects: list[dict[str, str]] | None = data_layer.read_data("projects.json")
    if not stored_projects:
        raise NoData
    projects: list[str] = [x["name"] for x in stored_projects]

    stored_tags: list[dict[str, str]] | None = data_layer.read_data("tags.json")
    if not stored_tags:
        raise NoData
    tags: list[str] = [x["name"] for x in stored_tags]

    user_data = data_layer.UserData()

    parser = argparse.ArgumentParser(
        description="Control Toggl Track timers from the command line"
    )
    # parser.add_argument("-e", "--example", help="Example argument", required=False)
    subparsers = parser.add_subparsers(
        title="subcommands", help="sub-command help", dest="subcommands"
    )

    # TIMER
    parser_timer = subparsers.add_parser("timer", help="Start a timer")
    parser_timer.add_argument("project", help="The project name", choices=projects)
    parser_timer.set_defaults(func=timer, projects=projects)

    # STOP
    parser_stop = subparsers.add_parser("stop", help="Stops the current timer")
    parser_stop.set_defaults(func=stop)

    # START
    parser_start = subparsers.add_parser("start", help="Start a timer")
    parser_start.add_argument(
        "project", help="the name of the project to start", choices=projects
    )
    parser_start.set_defaults(
        func=start, user_data=user_data, projects=projects, tags=tags
    )
    # SYNC
    parser_sync = subparsers.add_parser("sync", help="Syncs user data with Toggl")
    parser_sync.set_defaults(func=sync)

    # stop_parser.add_argument(
    #     "stop", help="Stop the currently running timer, if any", nargs=1
    # )
    # stop_parser.set_defaults(func=)

    args = parser.parse_args()
    # print("args: ", args)
    # Check if a subcommand was provided
    if args.subcommands is None:
        parser.print_help()
    else:
        args.func(args)

    # if args.example:
    #     # core.do_something(args.example)
    #     print("this is an example")
    #     pass
    # else:
    #     args.func(args)
    # elif args.timer:
    #     # print("timer")
    #     if args.timer[1] in projects:
    #         print(args.timer[1])
    #     else:
    #         print(f"timer {args.timer[1]} not found in list of projects")
    # elif args.stop:
    #     print("stopping!")
    # else:
    #     parser.print_help()


if __name__ == "__main__":
    main()
