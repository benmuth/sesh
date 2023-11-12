import argparse
# from . import core


def main():
    parser = argparse.ArgumentParser(description="Your app description here.")
    parser.add_argument("-e", "--example", help="Example argument", required=False)
    args = parser.parse_args()
    if args.example:
        # core.do_something(args.example)
        print("example")
        pass
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
