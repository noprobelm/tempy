import os
from pathlib import Path
import argparse

VALID_OPTIONS = "location", "units", "api_key"

if os.name == "nt":
    TEMPYRC = f"{os.path.expanduser('~')}\\AppData\\Roaming\\tempyrc"
else:
    TEMPYRC = f"{os.path.expanduser('~')}/.config/tempyrc"


class TempyRC(dict):
    def __init__(self):
        try:
            with open(TEMPYRC, "r") as f:
                tempyrc = f.readlines()

        except FileNotFoundError:
            parent = Path(__file__).parent
            CONFIGDIR = os.path.join(Path(os.path.expanduser("~")), ".config")
            if not os.path.isdir(CONFIGDIR) and os.name == "posix":
                os.mkdir(CONFIGDIR)
            skel = f"{parent}/tempyrc"
            with open(skel, "r") as f:
                skel = f.read()
            with open(TEMPYRC, "w") as f:
                f.write(skel)

            config = {option: "" for option in VALID_OPTIONS}

        else:
            config = {}
            for line in tempyrc:
                line = line.strip()
                if len(line) > 0 and line.startswith("#"):
                    continue

                line = [val.strip().lower() for val in line.split("=")]
                if line[0] in VALID_OPTIONS:
                    config[line[0]] = line[1]

            for option in VALID_OPTIONS:
                if option not in config.keys():
                    config[option] = ""

        super().__init__(config)


class Args(dict):
    parser = argparse.ArgumentParser(
        prog="tempy",
        usage="tempy <location> <optional args>",
        description="Render current and near future weather data as rich text to your terminal",
    )

    def __init__(self):
        self.parser.add_argument(
            "location",
            nargs="*",
            help="Input a city name or US/UK/Canadian postal code",
        )
        self.parser.add_argument("-u", "--units", dest="units", default="")
        self.parser.add_argument("-k", "--key", dest="api_key", default="")

        args = self.parser.parse_args()
        args.location = " ".join(args.location)
        super().__init__(
            {
                "location": args.location,
                "units": args.units,
                "api_key": args.api_key,
            }
        )


class Config(dict):
    def __init__(self):
        tempyrc = TempyRC()
        args = Args()
        config = {}

        for option in VALID_OPTIONS:
            config[option] = args[option] or tempyrc[option]
        if not config["location"]:
            print(
                f"Error: 'location' not provided in tempyrc or as command line arg. Usage: {Args.parser.usage}"
            )
            quit()
        if not config["units"]:
            config["units"] = "imperial"

        super().__init__(config)
