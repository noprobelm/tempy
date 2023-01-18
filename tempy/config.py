import os
import argparse
import re

VALID_OPTIONS = "location", "measurement_system", "api_key"
TEMPYRC = f"{os.path.expanduser('~')}/.config/tempyrc"


class TempyRC(dict):
    def __init__(self):
        try:
            with open(TEMPYRC, "r") as f:
                tempyrc = [option.split("=") for option in f.readlines()]
                for idx in range(len(tempyrc)):
                    tempyrc[idx][0] = tempyrc[idx][0].strip()
                    tempyrc[idx][1] = tempyrc[idx][1].strip()

        except FileNotFoundError:
            with open(TEMPYRC, "w") as f:
                f.write("location=\nunits=\napi_key=\n")
            super().__init__({option: "" for option in VALID_OPTIONS})
            return

        options = {}
        for option in tempyrc:
            if option[0] == "location":
                options.update({option[0]: " ".join(option[1:])})
            elif option[0] == "units":
                options.update({"measurement_system": option[1]})
            elif option[0] == "api_key":
                options.update({"api_key": option[1]})

        for option in VALID_OPTIONS:
            if option not in options.keys():
                options.update({option: ""})

        super().__init__(options)


class Args(dict):
    parser = argparse.ArgumentParser(
        prog="tempy",
        usage="tempy <location> <optional args>",
        description="Beautifully render current and near future weather data to your terminal",
    )

    def save_config(self):
        with open(TEMPYRC, "r") as f:
            tempyrc = f.read()
        for option in self:
            if self[option] and option in VALID_OPTIONS:
                new = f"{option}={self[option]}"
                tempyrc = re.sub(f"{option}\S*", new, tempyrc)
        with open(TEMPYRC, "w") as f:
            f.write(tempyrc)

    def __init__(self):
        self.parser.add_argument(
            "location",
            nargs="*",
            help="Input a city name or US/UK/Canadian postal code",
        )
        self.parser.add_argument("-u", "--units", dest="measurement_system", default="")
        self.parser.add_argument("-k", "--key", dest="api_key", default="")
        self.parser.add_argument(
            "-s", "--save", dest="save", action="store_true", default=False
        )

        args = self.parser.parse_args()
        args.location = " ".join(args.location)
        super().__init__(
            {
                "location": args.location,
                "measurement_system": args.measurement_system,
                "api_key": args.api_key,
            }
        )

        if args.save is True:
            self.save_config()


class Config(dict):
    def __init__(self):
        tempyrc = TempyRC()
        args = Args()
        super().__init__(self.set_config(tempyrc, args))

    def set_config(self, tempyrc, args):
        config = {}
        for option in VALID_OPTIONS:
            config[option] = args[option] or tempyrc[option]
        if not config["location"]:
            print(
                f"Error: 'location' not provided in tempyrc or as command line arg. Usage: {Args.parser.usage}"
            )
            quit()
        if not config["measurement_system"]:
            config["measurement_system"] = "imperial"

        return config
