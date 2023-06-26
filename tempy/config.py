import os
from pathlib import Path
import argparse


class TempyRC(dict):
    VALID_OPTIONS = "location", "units", "api_key"

    def __init__(self, tempyrc_path: str):
        try:
            with open(tempyrc_path, "r") as f:
                tempyrc = f.readlines()

        except FileNotFoundError:
            skel_path = os.path.join(Path(__file__).parent, "tempyrc")
            user_config_path = os.path.join(Path(os.path.expanduser("~")), ".config")
            if not os.path.isdir(user_config_path) and os.name == "posix":
                os.mkdir(user_config_path)
            with open(skel_path, "r") as f:
                skel = f.read()
            with open(tempyrc_path, "w") as f:
                f.write(skel)

            config = {option: "" for option in self.VALID_OPTIONS}

        else:
            config = {}
            for line in tempyrc:
                line = line.strip()
                if len(line) > 0 and line.startswith("#"):
                    continue

                line = [val.strip().lower() for val in line.split("=")]
                if line[0] in self.VALID_OPTIONS:
                    config[line[0]] = line[1]

            for option in self.VALID_OPTIONS:
                if option not in config.keys():
                    config[option] = ""

        super().__init__(config)


class Args(dict):
    def __init__(self):
        parser = argparse.ArgumentParser(
            prog="tempy",
            usage="tempy <location> <optional args>",
            description="Render current and near future weather data as rich text to your terminal",
        )

        self.usage = parser.usage

        parser.add_argument(
            "location",
            nargs="*",
            help="Input a city name or US/UK/Canadian postal code",
        )
        parser.add_argument("-u", "--units", dest="units", default="")
        parser.add_argument("-k", "--key", dest="api_key", default="")

        args = parser.parse_args()
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
        if os.name == "nt":
            config_dir = f"{os.path.expanduser('~')}\\AppData\\Roaming\\tempyrc"
        else:
            config_dir = f"{os.path.expanduser('~')}/.config/tempyrc"

        tempyrc = TempyRC(config_dir)
        args = Args()
        config = {}

        for option in TempyRC.VALID_OPTIONS:
            config[option] = args[option] or tempyrc[option]

        if not config["location"]:
            print(
                f"Error: 'location' not provided in tempyrc or as command line arg. Usage: {args.usage}"
            )
            quit()
        if not config["units"]:
            config["units"] = "imperial"

        super().__init__(config)
