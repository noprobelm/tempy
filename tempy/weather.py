import os
from datetime import datetime, timedelta
from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Column, Table
from rich.text import Text

from .console import console
from .data import Data


class Report:
    """A terminal-renderable weather report.

    The purpose of this class is to provide a object that can be rendered to the terminal by the rich.console.Console
    class.

    This class uses the data.Data class to manage fetching the weather report data.

    Attributes:
        1. _unparsed (Data): The data.Data object containing weather report information retrieved from weatherapi.com or the proxy
                             server
        2. _imperial (bool): Indicator for whether the weather report should display imperial (True) or metric (False)
        3. condition (str): The current weather conditions (e.g. 'Overcast')
        4. is_day (bool): Represents day or night for the weather report
        5. location (str): The city and region of the weather report
        6. localtime (str): The localtime formatted for the weather report
        7. weather (dict): The current weather report
        8. forecasts (list[dict]): A list of forecast reports, the first index being the current day
    """

    def __init__(self, location: str, units: str, api_key: str) -> None:
        """Initializes an instance of the Report class

        A data.Data object is instantiated based on the 'location', and 'api_key' args. The _imperial bool is used to
        influence the unit system of measurement to use when rendering the report.
        """
        self._unparsed = Data(location, api_key)

        if units == "imperial":
            imperial = True
        else:
            imperial = False

        self.condition = self._unparsed["current"]["condition"]["text"]
        self.is_day = bool(self._unparsed["current"]["is_day"])

        self.location = self._parse_location(
            self._unparsed["location"]["name"], self._unparsed["location"]["region"]
        )

        localtime = datetime.strptime(
            self._unparsed["location"]["localtime"], "%Y-%m-%d %H:%M"
        )
        self.localtime = self._parse_localtime(localtime)

        self.weather = self._parse_weather(self._unparsed["current"], imperial)

        self.forecasts = []
        for day in self._unparsed["forecast"]["forecastday"]:
            forecast = self._parse_forecast(day["day"], imperial)
            self.forecasts.append(forecast)

    def _parse_location(self, city: str, region: str) -> str:
        """Parses the weather report location for rendering

        Args:
            1. city (str): The city of the report
            2. region (str): The region of the report

        Returns:
            str: The parsed string to be used in the weather report render
        """
        return f"{city}, {region}"

    def _parse_localtime(self, localtime: datetime) -> str:
        """Parses the localtime of the report for rendering

        Args:
            1. localtime (datetime): The datetime to parse

        Returns:
            str: The parsed string to be used in the weather report render
        """
        return f"{localtime.strftime('%A, %B')} {localtime.strftime('%e').strip()}{localtime.strftime(' | %H:%M')}"

    def _parse_weather(self, weather: dict, imperial: bool) -> dict:
        """Parses the weather data of the report for rendering. This is later passed to the _get_weather_table method

        Args:
            1. weather (dict): A dict of the weather report
            2. imperial (bool): Flag indicating whether the data should be parsed for imperial or metric

        Returns:
            dict: The weather report formatted for rendering
        """

        def _parse_weather_imperial(weather: dict) -> dict:
            parsed = {
                "temperature": f"{weather['temp_f']}°F",
                "wind": f"{weather['wind_mph']} mph {weather['wind_dir']}",
                "gusts": f"{weather['gust_mph']} mph",
                "pressure": f"{weather['pressure_in']} inHg",
                "precipitation": f"{weather['precip_in']} in",
                "visibility": f"{weather['vis_miles']} mi",
                "humidity": f"{weather['humidity']}%",
                "cloud cover": f"{weather['cloud']}%",
                "UV index": f"{weather['uv']}",
            }

            return parsed

        def _parse_weather_metric(weather: dict) -> dict:
            parsed = {
                "temperature": f"{weather['temp_c']}°C",
                "wind": f"{weather['wind_kph']} kph {weather['wind_dir']}",
                "gusts": f"{weather['gust_kph']} kph",
                "pressure": f"{int(weather['pressure_mb'])} mb",
                "precipitation": f"{weather['precip_mm']} mm",
                "visibility": f"{weather['vis_km']} km",
                "humidity": f"{weather['humidity']}%",
                "cloud cover": f"{weather['cloud']}%",
                "UV index": f"{weather['uv']}",
            }

            return parsed

        if imperial == True:
            parsed = _parse_weather_imperial(weather)
        else:
            parsed = _parse_weather_metric(weather)

        return parsed

    def _parse_forecast(self, forecast: dict, imperial: bool) -> dict:
        """Parses the forecast data of a given day for rendering. This is later passed to the _get_weather_table method

        Args:
            1. weather (dict): A dict of the weather report
            2. imperial (bool): Flag indicating whether the data should be parsed for imperial or metric

        Returns:
            dict: The weather report formatted for rendering
        """

        def _parse_forecast_imperial(forecast: dict) -> dict:
            parsed = {
                "average": f"{forecast['avgtemp_f']}°F",
                "low": f"{forecast['mintemp_f']}°F",
                "high": f"{forecast['maxtemp_f']}°F",
                "gusts": f"{forecast['maxwind_mph']} mph",
                "total precipitation": f"{forecast['totalprecip_in']} in",
                "average visibility": f"{forecast['avgvis_miles']} mi",
                "chance of rain": f"{forecast['daily_chance_of_rain']}%",
                "chance of snow": f"{forecast['daily_chance_of_snow']}%",
                "uv index": f"{forecast['uv']}",
            }

            return parsed

        def _parse_forecast_metric(forecast: dict) -> dict:
            parsed = {
                "average": f"{forecast['avgtemp_c']}°C",
                "low": f"{forecast['mintemp_c']}°C",
                "high": f"{forecast['maxtemp_c']}°C",
                "gusts": f"{forecast['maxwind_kph']} kph",
                "total precipitation": f"{forecast['totalprecip_mm']} mm",
                "average visibility": f"{forecast['avgvis_km']} km",
                "chance of rain": f"{forecast['daily_chance_of_rain']}%",
                "chance of snow": f"{forecast['daily_chance_of_snow']}%",
                "uv index": f"{forecast['uv']}",
            }

            return parsed

        if imperial == True:
            parsed = _parse_forecast_imperial(forecast)
        else:
            parsed = _parse_forecast_metric(forecast)

        return parsed

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
            table.add_row(label.title(), table_data[label])

        return table

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
        localtime = Text(self.localtime, style="report_header")
        art = self._get_ascii_art(self.condition, self.is_day)

        weather_table = self._get_weather_table(self.weather, "Current Condiitons")

        forecast_tables = [
            self._get_weather_table(self.forecasts[0], "Today's Forecast")
        ]
        for num, day in enumerate(self.forecasts[1:]):
            date = datetime.strptime(
                self._unparsed["location"]["localtime"], "%Y-%m-%d %H:%M"
            ) + timedelta(days=num + 1)
            title = f"{date.strftime('%A, %B')} {date.strftime('%e').strip()}"
            forecast_tables.append(self._get_weather_table(day, title))

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
