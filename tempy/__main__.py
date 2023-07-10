from .config import Config
from .console import console
from .report import Report


def main():
    config = Config.from_default()
    report = Report.from_weatherapi(
        config["location"], config["units"], config["api_key"]
    )
    console.print(report)


if __name__ == "__main__":
    main()
