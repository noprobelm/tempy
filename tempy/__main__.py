from .config import Config
from .console import console
from .weather import Report


def main():
    config = Config()
    report = Report(config["location"], config["units"], config["api_key"])
    console.print(report)


if __name__ == "__main__":
    main()
