import sys
import os

from .config import Config
from .console import console
from .weather import Report


def main():
    if os.name == "nt":
        tempyrc_path = f"{os.path.expanduser('~')}\\AppData\\Roaming\\tempyrc"
    else:
        tempyrc_path = f"{os.path.expanduser('~')}/.config/tempyrc"

    config = Config.from_cli(tempyrc_path=tempyrc_path, unparsed=sys.argv[1:])
    report = Report(config["location"], config["units"], config["api_key"])
    console.print(report)


if __name__ == "__main__":
    main()
