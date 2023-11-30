import argparse
# from . import core


def main():
    parser = argparse.ArgumentParser(
        description="Control Toggl Track timers from the command line"
    )
    parser.add_argument("-e", "--example", help="Example argument", required=False)
    parser.add_argument(
        "timer",
    )
    args = parser.parse_args()
    if args.example:
        # core.do_something(args.example)
        print("example")
        pass
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
