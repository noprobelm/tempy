import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from .data import WeatherAPI

from rich import box
from rich.align import Align
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Column, Table
from rich.text import Text

from .console import console


class Report:
    """A terminal-renderable weather report.

    The purpose of this class is to provide a object that can be rendered to the terminal by the rich.console.Console
    class.

    NOTE: If this class is being instantiated any way other than using the data generated from the WeatherAPI.parse
          method, take care to ensure the 'condition' arg matches at least one of the asset filenames in the assets
          directory of this project. The 'condition' arg is directly referenced when loading ASCII art assets

    TODO: Low priority: Add option to exclude ASCII art from terminal render. This will loosen the requirements for the
          'condition' arg to match the ASCII art assets, making it easier to generate weather reports using data from
          non-weatherapi.com sources. Highly doubtful this will ever be used since, in all likelihood, all userse of
          tempy are interfacing with the __main__ module and NOT adapting this class to their own use.

    Attributes:
        1. localtime (datetime): The localtime of the location of the weather report. This is used to generate the report
        header and forecast headers
        2. is_day (bool): Boolean indicating day or night. Used in conjunction with 'condition' to select the ASCII art
        3. location (str): The location to display in the report header
        4. condition (str): The current weather condition. Used in conjunction with 'is_day' to select the ASCII art
        5. weather_table (dict): The data to display in the table for current weather conditions. The key/value pairs
           should contain the deisred text for rendering.
        6. forecast_tables (list[dict]): A list of the tables to use for forecast conditions. The key/value pairs should
           contain the desired text for rendering

    """

    def __init__(
        self,
        localtime: datetime,
        is_day: bool,
        location: str,
        condition: str,
        weather_table: dict,
        forecast_tables: list[dict],
    ) -> None:
        """Initializes an instance of the Report class

        A data.Data object is instantiated based on the 'location', and 'api_key' args. The _imperial bool is used to
        influence the unit system of measurement to use when rendering the report.
        """
        self.localtime = localtime
        self.is_day = is_day
        self.location = location
        self.condition = condition
        self.weather_table = weather_table
        self.forecast_tables = forecast_tables

    def _get_localtime_header(self, localtime: datetime) -> str:
        """Parses the localtime of the report for rendering

        Args:
            1. localtime (datetime): The datetime to parse

        Returns:
            str: The parsed string to be used in the weather report render
        """
        return f"{localtime.strftime('%A, %B')} {localtime.strftime('%e').strip()}{localtime.strftime(' | %H:%M')}"

    def _get_localtime_timedelta(self, days: int) -> str:
        """Parses the localtime and adds a specified timedelta

        This is used to generate table headers for the forecast tables.

        Args:
            days (int): The number of days to add to the localtime instance variable

        Returns:
            str: A formatted string of the datetime (e.g. 'Tuesday, July 11')
        """
        date = self.localtime + timedelta(days=days)
        title = f"{date.strftime('%A, %B')} {date.strftime('%e').strip()}"
        return title

    def _get_ascii_art(self, condition: str, is_day: bool):
        """Gets the ASCII art corresponding to current weather conditions and time of day

        Each asset follows the naming scheme: '<condition>_<day or night>.txt'. The 'condition' portion of the text file simply
        follows the condition as returned by the API request, all lowercase with spaces replaced with underscores.

        Each asset is plain text formatted using ANSII escape sequences. We use the rich.text.Text.from_ansii
        classmethod to manage interpretation of the ANSII escape sequences.

        The label is representative of the current conditions, formatted to be title text.

        Args:
            condition (str): The current weather conditions as returned by the API request
            is_day (bool): Boolean representing whether it's currently daytime or nighttime.

        Returns:
            art (Text): The ASCII art to render to the terminal
        """
        assets_path = os.path.join(Path(__file__).parent, "assets")
        filename = condition.replace(" ", "_").lower()
        if is_day is True:
            filename = f"{filename}_day.txt"
        else:
            filename = f"{filename}_night.txt"

        asset_path = os.path.join(assets_path, filename)

        with open(asset_path, "r") as f:
            asset = f.read()

        art = Text.from_ansi(asset)
        width = console.measure(art).maximum

        label = Text(
            condition.title().center(width),
            style="labels",
        )

        art.append("\n\n")
        art.append(label)

        return art

    def _get_weather_table(self, table_data: dict, title: str) -> Table:
        """Builds a table of weather conditions for rendering to the terminal

        In the terminal, this is the 'current conditions', 'today's forecast', and each forecast in the lower region of
        the weather report renderable.

        Args:
            table_data (dict): A dict of the table data to use for the weather report
            title (str): The title to place above the table

        Returns:
            table (Table): The weather table to render to the terminal
        """
        labels = Column(
            "labels",
            width=max([len(label) for label in table_data.keys()]),
            no_wrap=True,
            style="labels",
        )
        values = Column(
            "values",
            width=max([len(str(value)) for value in table_data.values()]),
            no_wrap=True,
            style="labels",
        )
        table = Table(
            labels,
            values,
            show_edge=False,
            expand=False,
            show_header=False,
            title_style="table_header",
            border_style="table_divider",
        )

        table.title = f"{title}\n"
        for label in table_data:
            table.add_row(label, table_data[label])

        return table

    @classmethod
    def from_weatherapi(cls, location: str, units: str, api_key: Optional[str] = ""):
        """Convenience method used to create a Report object using data sourced from weatherapi.com

        Args:
            location (str): The location to use for the API request
            units (str): The unit of measurement to parse the weather data into ('imperial' or 'metric')
            api_key (Optional[str]): API key to use if the user has one. Fallback is to use noprobelm.dev as the
                                     proxy domain

        Returns:
            Report: An instance of the Report class
        """
        data = WeatherAPI(location, api_key)
        data = data.parse(units)

        return cls(
            data["localtime"],
            data["is_day"],
            data["location"],
            data["condition"],
            data["weather_table"],
            data["forecast_tables"],
        )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """The rich console special method.

        This method is called when the Report object is printed using the rich.console.Console.print method

        Each element of the weather report renderable is generated separately, then assigned to upper and lower regions

        - Upper report region
            - Headers
                - location (Text): The location to render (e.g. New York City, New York)
                - localtime (Text): The localtime to render (e.g. Saturday, July 8 | 17:00)
            - Report (left to right)
                - ASCII art
                - Current conditions
                - Today's forecast

        - Lower report region (left to right)
            - Today + 1 day forecast table
            - Today + 2 days forecast table

        After each region of the report has been rendered, we yield the upper, then the lower.
        """
        location = Text(self.location, style="report_header")
        localtime = Text(
            self._get_localtime_header(self.localtime), style="report_header"
        )
        art = self._get_ascii_art(self.condition, self.is_day)

        weather_table = self._get_weather_table(
            self.weather_table, "Current Condiitons"
        )

        forecast_tables = [
            self._get_weather_table(self.forecast_tables[0], "Today's Forecast")
        ]
        for num, day in enumerate(self.forecast_tables[1:]):
            date_header = self._get_localtime_timedelta(num + 1)
            forecast_tables.append(self._get_weather_table(day, date_header))

        report_upper = Table(
            Column("Art"),
            Column("Current Conditions"),
            Column("Today's Forecast"),
            padding=(1, 2, 1, 2),
            box=None,
            show_header=False,
        )
        report_upper.add_row(
            Align(art, vertical="middle"), weather_table, forecast_tables[0]
        )
        # BUG: There might be a bug in the way Panel.fit() calculates the size it needs to be for grids that have padding, hence the explicit definition below. Reminder to look into it.
        report_upper.width = (console.measure(report_upper).maximum) + sum(
            [report_upper.padding[1], report_upper.padding[3]]
        )
        report_upper = Panel.fit(
            Group(
                Align(location, "center"),
                Align(localtime, "center"),
                Rule(style="panel_border"),
                report_upper,
            ),
            box=box.HEAVY,
            border_style="panel_border",
        )

        report_lower = Table(
            Column("1", justify="left"),
            Column("2", justify="right"),
            show_edge=False,
            show_lines=False,
            box=None,
            show_header=False,
            padding=0,
        )

        report_lower.width = console.measure(report_upper).maximum
        report_lower.add_row(
            Panel(
                Align(forecast_tables[1], "center"),
                box=box.HEAVY,
                style="panel_border",
                width=(report_lower.width // 2 - 1),
            ),
            Panel(
                Align(forecast_tables[2], "center"),
                box=box.HEAVY,
                style="panel_border",
                width=(report_lower.width // 2 + 1)
                if report_lower.width % 2 == 1
                else report_lower.width // 2,
            ),
        )
        yield report_upper
        yield report_lower
