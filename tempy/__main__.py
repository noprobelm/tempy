from .config import Config
from .weather import Report
from .console import console


def main():
    config = Config()
    report = Report(config["location"], config["units"], config["api_key"])
    console.print(report)


if __name__ == "__main__":
    main()
