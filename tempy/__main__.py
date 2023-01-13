from .config import Config
from .weather import Report
from .console import console


def main():
    config = Config()
    renderable = Report(config)
    console.print(renderable)


if __name__ == "__main__":
    main()
