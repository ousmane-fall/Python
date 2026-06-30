import argparse
import sys

def greet(name):
    message = f"Hello, {name}!"
    print(message)
    return message

def goodbye(name):
    message = f"Goodbye, {name}!"
    print(message)
    return message


def greet_interactive():
    name = input("Enter your name: ")
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Shortcut mode used in tests: `python cli_tool.py Alice`
    if len(sys.argv) == 2 and sys.argv[1] not in {"greet", "goodbye"}:
        greet(sys.argv[1])
        raise SystemExit(0)

    parser = argparse.ArgumentParser(description="A CLI tool with subcommands")
    subparsers = parser.add_subparsers(dest="command")  # Add subcommands

    # Subcommand: greet
    greet_parser = subparsers.add_parser("greet", help="Greet someone")
    greet_parser.add_argument("name", help="Person's name")

    # Subcommand: goodbye
    goodbye_parser = subparsers.add_parser("goodbye", help="Say goodbye to someone")
    goodbye_parser.add_argument("name", help="Person's name")

    args = parser.parse_args()

    if args.command == "greet":
        greet(args.name)
    elif args.command == "goodbye":
        goodbye(args.name)