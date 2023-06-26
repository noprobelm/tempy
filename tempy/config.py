import argparse
import os
import sys
from pathlib import Path
from typing import Union

VALID_OPTIONS = "location", "units", "api_key"


class TempyRC(dict):
    """Stores configuration information for tempy from the tempyrc file in the user's config path

    Attributes:
        1. path (Path): The path of tempyrc

    """

    def __init__(self, path: Union[Path, str]) -> None:
        """Creates instance of TempyRC with specified config file path

        1. If the tempyrc provided is found:
            a. Parse the contents, ignoring lines that start with '#'
        2. If no tempyrc is found:
            a. If the tempyrc parent path does not exist, create it
            b. If tempyrc does not exist, create one from the skel
        3. Init dict superclass with tempyrc contents

        Args:
            path (str): The path of tempyrc (usually ~/.tempyrc/config)
        """

        self.path = Path(path)

        try:
            with open(self.path, "r") as f:
                tempyrc = f.readlines()

        except FileNotFoundError:
            tempyrc_parent_path = self.path.parent
            if not os.path.isdir(tempyrc_parent_path) and os.name == "posix":
                try:
                    os.mkdir(tempyrc_parent_path)
                except FileNotFoundError:
                    print(f"Invalid config path '{tempyrc_parent_path}'")
                    sys.exit()

            skel_path = os.path.join(Path(__file__).parent, "tempyrc")

            with open(skel_path, "r") as f:
                skel = f.read()
            with open(self.path, "w") as f:
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
    """Stores configuration information for tempy from the tempyrc file in the user's config path

    Attributes:
        1. usage (str): Holds the ArgumentParser instance's usage str
    """

    def __init__(self, unparsed: list[str]) -> None:
        """Creates instance of TempyRC with specified config file path

        Args:
            1. unparsed (list[str]): A list of the arguments to parse (e.g. sys.argv[1:])

        """

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
        parser.add_argument(
            "-u",
            "--units",
            dest="units",
            choices=["imperial", "metric"],
            default="imperial",
        )
        parser.add_argument("-k", "--key", dest="api_key", default="")

        parsed = parser.parse_args(args=unparsed)
        parsed.location = " ".join(parsed.location)
        super().__init__(
            {
                "location": parsed.location,
                "units": parsed.units,
                "api_key": parsed.api_key,
            }
        )


class Config(dict):
    """Stores the final configuration information to be used by weather.Report"""

    def __init__(self) -> None:
        """Creates instance of TempyRC with specified config file path

        This is a convenience class used to select config data between command line args and the tempyrc

        Priority order:
            1. Args config
            2. TempyRC config

        Config keys:
            1. location (str): The location to fetch weather data for
            2. units (str): The measurement system to use (imperial or metric)
            3. api_key (str): The API key to use. If no API key is passed, use http://noprobelm.dev


        TODO:
            - Add robust testing for Windows configurations. I don't have the infrastructure to adequately test this at
              the moment
        """

        if os.name == "nt":
            config_dir = f"{os.path.expanduser('~')}\\AppData\\Roaming\\tempyrc"
        else:
            config_dir = f"{os.path.expanduser('~')}/.config/tempyrc"

        self.tempyrc = TempyRC(config_dir)
        self.args = Args(sys.argv[1:])
        config = {}

        for option in VALID_OPTIONS:
            config[option] = self.args[option] or self.tempyrc[option]

        if not config["location"]:
            print(
                f"Error: 'location' not provided in tempyrc or as command line arg. Usage: {args.usage}"
            )
            sys.exit()

        if not config["units"]:
            config["units"] = "imperial"

        super().__init__(config)
