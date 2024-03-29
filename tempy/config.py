import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Union

from .parser import parse_rc

VALID_OPTIONS = "location", "units", "api_key"


class TempyRC(dict):
    """Stores configuration information for tempy from the tempyrc file in the user's config path"""

    def __init__(self, path: Union[Path, str]) -> None:
        """Creates instance of TempyRC with specified config file path

        1. If the tempyrc provided is found:
            a. Parse the contents
            b. Fill in empty key/value pairs; delete erroneous key/value pairs
        2. If no tempyrc is found:
            a. If the tempyrc parent path does not exist, attempt to create it
            b. If tempyrc does not exist, create one from the skel
        3. Init dict superclass with tempyrc contents

        Args:
            path (str): The path of tempyrc (usually ~/.tempyrc/config)
        """

        path = Path(path)

        try:
            with open(path, "r") as fp:
                parsed = parse_rc(fp)

        except FileNotFoundError:
            self._copy_skel(path)
            parsed = {option: "" for option in VALID_OPTIONS}

        else:
            for option in VALID_OPTIONS:
                if option not in parsed.keys():
                    parsed[option] = ""

            for option in parsed:
                if option not in VALID_OPTIONS:
                    del parsed[option]

        super().__init__(parsed)

    def _copy_skel(self, path: Path) -> None:
        """Copy tempyrc skel to user config path

        For posix users:
            - If the specified configuration path (usually ~/.config) does not exist, create it.
            - If the parent of the specified configuration path does not exist, terminate tempy to avoid recursive path
              creation

        For Windows users:
            - If the specified configuration path does not exist, warn the user and terminate.
        """

        tempyrc_parent_path = path.parent
        if not os.path.isdir(tempyrc_parent_path):
            if os.name == "posix":
                try:
                    os.mkdir(tempyrc_parent_path)
                except FileNotFoundError:
                    sys.exit(f"No such path: '{tempyrc_parent_path.parent}'")
            elif os.name == "nt":
                sys.exit(f"No such path: '{tempyrc_parent_path}'")

        skel_path = os.path.join(Path(__file__).parent, "tempyrc")

        with open(skel_path, "r") as f:
            skel = f.read()
        with open(path, "w") as f:
            f.write(skel)


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
    """Stores the final configuration information to be used by weather.Report

    Attributes:
        _tempyrc (TempyRC): TempyRC for priority comparison
        _args (Args): Args sourced from cmdline args for priority comparison
    """

    def __init__(self, tempyrc: TempyRC, args: Args) -> None:
        """Creates instance of TempyRC with specified config file path

        This is a convenience class used to select config data between command line args and the tempyrc

        Priority order:
            1. Args config
            2. TempyRC config

        Config keys:
            1. location (str): The location to fetch weather data for
            2. units (str): The measurement system to use (imperial or metric)
            3. api_key (str): The API key to use. If no API key is passed, use http://noprobelm.dev


        Args:
            1. tempyrc (Union[TempyRC, None]): The TempyRC to compare
            2. unparsed (Union[Args, None]]) : Unparsed command line args to use for Args. Default will
               use sys.argv[1:]

        TODO:
            - Add robust testing for Windows configurations. I don't have the infrastructure to adequately test this at
              the moment
        """

        config = {}

        for option in VALID_OPTIONS:
            config[option] = args[option] or tempyrc[option]

        if not config["location"]:
            print(
                f"Error: 'location' not provided in tempyrc or as command line arg. Usage: {args.usage}"
            )
            sys.exit()

        if not config["units"]:
            config["units"] = "imperial"

        super().__init__(config)

    @classmethod
    def from_default(cls) -> "Config":
        """Constructor method to instantiate a Config object from a tempyrc path and sys.argv

        Args:
            1. tempyrc_path (Optional[Union[Path, str, None]]): Path to use for TempyRC. Default will use user config
               path (~/.config for Linux)
            2. unparsed (Optional[Union[list[str], None]]) : Unparsed command line args to use for Args. Default will
               use sys.argv[1:]

        Returns:
            Config: An instance of self based on a tempyrc path and sys.argv[1:]
        """

        if os.name == "nt":
            tempyrc_path = f"{os.path.expanduser('~')}\\AppData\\Roaming\\tempyrc"
        else:
            tempyrc_path = f"{os.path.expanduser('~')}/.config/tempyrc"

        tempyrc = TempyRC(tempyrc_path)
        args = Args(sys.argv[1:])

        return cls(tempyrc, args)
