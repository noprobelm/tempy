import os
import argparse


class Config(dict):
    def __init__(self):
        self.config_dir = f"{os.path.expanduser('~')}/.config/tempyrc"
        args = self.parse_args()
        super().__init__(
            {
                "location": args.location,
                "measurement_system": args.measurement_system,
                "api_key": self.api_key,
            }
        )

    @property
    def api_key(self):
        try:
            with open(self.config_dir, "r") as config:
                api_key = config.read()
        except FileNotFoundError:
            return None
        return api_key

    def parse_args(self):
        parser = argparse.ArgumentParser(
            prog="tempy",
            usage="tempy <location> <optional args>",
            description="Beautifully render current and near future weather data to your terminal",
        )
        parser.add_argument(
            "location",
            nargs="*",
            help="Input a city name or US/UK/Canadian postal code",
        )
        parser.add_argument(
            "-u", "--units", dest="measurement_system", default="imperial"
        )
        args = parser.parse_args()

        if not args.location:
            print(f"Error: missing required arg 'location'. Usage: {parser.usage}")
            quit()

        args.location = " ".join(args.location)
        return args
