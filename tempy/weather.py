import os
from pathlib import Path
from datetime import datetime

from rich import box
from rich.align import Align
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Column, Table
from rich.text import Text

from .console import console
from .data import Data
from .themes import Default


class Report:
    """A terminal-renderable weather report

    Attributes:
        1. _data (Data): The data.Data object containing weather report information retrieved from weatherapi.com or the proxy
                  server
        2. _imperial (bool): Indicator for whether the weather report should display imperial (True) or metric (False)
    """

    def __init__(self, location: str, units: str, api_key: str) -> None:
        """Initializes an instance of the Report class

        A Data object is instantiated based on the 'location', and 'api_key' args. The _imperial bool is used to
        influence the unit system of measurement to use when rendering the report.

        When this object is printed to the terminal using rich.console.Console, the __rich_console__ special method is
        invoked:
            1. The 'location' and 'localtime' data is pulled from the Data object
            2. An ASCII art representation of the current weather conditions (and time of day) is generated
            3. Tables containing current and forecasted conditions are generated
            4. The weather report renderable is assembled and yielded
        """
        self._data = Data(location, api_key)

        if units == "imperial":
            self._imperial = True
        else:
            self._imperial = False

    def _parse_location(self, city: str, region: str) -> Text:
        return Text(f"{city}, {region}", style=Default.report_header)

    def _parse_localtime(self, localtime: datetime) -> Text:
        return Text(
            f"{localtime.strftime('%A, %B')} {localtime.strftime('%e').strip()}{localtime.strftime(' | %H:%M')}",
            style=Default.report_header,
        )

    def _parse_weather_imperial(self, weather: dict) -> dict:
        parsed = {
            "temperature": f"{weather['current']['temp_f']}°F",
            "wind": f"{weather['current']['wind_mph']} mph {weather['current']['wind_dir']}",
            "gusts": f"{weather['current']['gust_mph']} mph",
            "pressure": f"{weather['current']['pressure_in']} inHg",
            "precipitation": f"{weather['current']['precip_in']} in",
            "visibility": f"{weather['current']['vis_miles']} mi",
            "humidity": f"{weather['current']['humidity']}%",
            "cloud cover": f"{weather['current']['cloud']}%",
            "UV index": f"{weather['current']['uv']}",
        }

        return parsed

    def _parse_weather_metric(self, weather: dict) -> dict:
        parsed = {
            "temperature": f"{weather['current']['temp_c']}°C",
            "wind": f"{weather['current']['wind_kph']} kph {weather['current']['wind_dir']}",
            "gusts": f"{weather['current']['gust_kph']} kph",
            "pressure": f"{int(weather['current']['pressure_mb'])} mb",
            "precipitation": f"{weather['current']['precip_mm']} mm",
            "visibility": f"{weather['current']['vis_km']} km",
            "humidity": f"{weather['current']['humidity']}%",
            "cloud cover": f"{weather['current']['cloud']}%",
            "UV index": f"{weather['current']['uv']}",
        }

        return parsed

    def _parse_forecast_imperial(self, forecast: dict) -> dict:
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

    def _parse_forecast_metric(self, forecast: dict) -> dict:
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
            style=Default.labels,
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
            style=Default.labels,
        )
        values = Column(
            "values",
            width=max([len(str(value)) for value in table_data.values()]),
            no_wrap=True,
            style=Default.labels,
        )
        table = Table(
            labels,
            values,
            show_edge=False,
            expand=False,
            show_header=False,
            title_style=Default.table_header,
            border_style=Default.table_divider,
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
        location = Text(
            self._data["localdata"]["location"], style=Default.report_header
        )
        localtime = Text(
            self._data["localdata"]["localtime"], style=Default.report_header
        )
        art = self._get_ascii_art(
            self._data["weather"]["condition"], self._data["weather"]["is_day"]
        )
        if self._imperial == True:
            weather_table = self._get_weather_table(
                self._data["weather"]["imperial"], "Current Conditions"
            )

            forecast = self._data["forecast"]
            forecast_tables = [
                self._get_weather_table(forecast[0]["imperial"], "Today's Forecast")
            ]
            for day in forecast[1:]:
                forecast_tables.append(
                    self._get_weather_table(day["imperial"], f"{day['date']}")
                )

        else:
            weather_table = self._get_weather_table(
                self._data["weather"]["metric"], "Current Conditions"
            )

            forecast = self._data["forecast"]
            forecast_tables = [
                self._get_weather_table(forecast[0]["metric"], "Today's Forecast")
            ]
            for day in forecast[1:]:
                forecast_tables.append(
                    self._get_weather_table(day["metric"], f"{day['date']}")
                )

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
                Rule(style=Default.panel_border_style),
                report_upper,
            ),
            box=box.HEAVY,
            border_style=Default.panel_border_style,
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
                style=Default.panel_border_style,
                width=(report_lower.width // 2 - 1),
            ),
            Panel(
                Align(forecast_tables[2], "center"),
                box=box.HEAVY,
                style=Default.panel_border_style,
                width=(report_lower.width // 2 + 1)
                if report_lower.width % 2 == 1
                else report_lower.width // 2,
            ),
        )
        yield report_upper
        yield report_lower
