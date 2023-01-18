from pathlib import Path
from typing import Optional, Union, List
from rich.align import Align
from rich.rule import Rule
from rich.console import Console, ConsoleOptions, Measurement, Group, RenderResult
from rich.text import Text
from rich.panel import Panel
from rich.table import Table, Column
from rich import box
from .console import console
from .themes import Default
from .data import Data
from .config import Config


class WeatherTable:
    def __init__(self, title: Optional[Union[Text, str]] = None, **table_data):
        self.title = title
        for label in table_data:
            table_data[label] = str(table_data[label])
            setattr(self, label, table_data[label])
        self.renderable = table_data

    @property
    def renderable(self) -> Table:
        return self._renderable

    @renderable.setter
    def renderable(self, table_data: dict) -> None:
        labels = Column(
            "labels",
            width=max([len(label) for label in table_data.keys()]),
            no_wrap=True,
            style=Default.information,
        )
        values = Column(
            "values",
            width=max([len(str(value)) for value in table_data.values()]),
            no_wrap=True,
            style=Default.information,
        )
        self._renderable = Table(
            labels,
            values,
            show_edge=False,
            expand=False,
            show_header=False,
            title_style=Default.table_header,
            border_style=Default.table_divider,
        )
        if self.title:
            self._renderable.title = f"{self.title}\n"
        for label in table_data:
            self._renderable.add_row(label.title(), table_data[label])

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield self.renderable

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        return console.measure(self.renderable)


class Report:
    def __init__(self, config: Config) -> None:
        self.data = Data(config["location"], config["api_key"])
        self.units = config["units"]

    @property
    def location(self) -> Text:
        return Text(self.data["localdata"]["location"], style=Default.report_header)

    @property
    def localtime(self) -> Text:
        return Text(self.data["localdata"]["localtime"], style=Default.report_header)

    @property
    def art(self) -> Text:
        if self.data["weather"]["is_day"]:
            file_suffix = "day"
        else:
            file_suffix = "night"
        parent = Path(__file__).parent.parent
        filename = f"{parent}/tempy/assets/{self.data['weather']['condition'].replace(' ', '_')}_{file_suffix}.txt".lower()
        with open(filename, "r") as f:
            art = Text.from_ansi(f.read())

        width = console.measure(art).maximum
        # TODO Consider replacing label with a table/grid footer that has a single empty line above it.
        label = Text(
            self.data["weather"]["condition"].title().center(width),
            style=Default.information,
        )
        art = art.append("\n\n")
        art.append(label)
        return art

    @property
    def weather_table(self) -> WeatherTable:
        if self.units == "imperial":
            weather_table = WeatherTable(
                title="Current Conditions", **self.data["weather"]["imperial"]
            )
        else:
            weather_table = WeatherTable(
                title="Current Conditions", **self.data["weather"]["metric"]
            )

        return weather_table

    @property
    def forecast_tables(self) -> List[WeatherTable]:
        forecast = self.data["forecast"]
        if self.units == "imperial":
            forecast_tables = [
                WeatherTable(title="Today's Forecast", **forecast[0]["imperial"])
            ]
            for data in forecast[1:]:
                forecast_tables.append(
                    WeatherTable(title=data["date"], **data["imperial"])
                )
        else:
            forecast_tables = [
                WeatherTable(title="Today's Forecast", **forecast[0]["metric"])
            ]
            for data in forecast[1:]:
                forecast_tables.append(
                    WeatherTable(title=data["date"], **data["metric"])
                )

        return forecast_tables

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        location = self.location
        localtime = self.localtime
        art = self.art
        weather_table = self.weather_table
        forecast_tables = self.forecast_tables

        today = Table(
            Column("Art"),
            Column("Current Conditions"),
            Column("Today's Forecast"),
            padding=(1, 2, 1, 2),
            box=None,
            show_header=False,
        )
        today.add_row(Align(art, vertical="middle"), weather_table, forecast_tables[0])
        # BUG: There might be a bug in the way Panel.fit() calculates the size it needs to be for grids that have padding, hence the explicit definition below. Reminder to look into it.
        today.width = (console.measure(today).maximum) + sum(
            [today.padding[1], today.padding[3]]
        )
        today = Panel.fit(
            Group(
                Align(location, "center"),
                Align(localtime, "center"),
                Rule(style=Default.panel_border_style),
                today,
            ),
            box=box.HEAVY,
            border_style=Default.panel_border_style,
        )

        future = Table(
            Column("1"),
            Column("2"),
            box=None,
            show_header=False,
            width=console.measure(today).maximum,
        )
        future.add_row(
            Align(
                Panel.fit(
                    forecast_tables[1],
                    padding=(0, 1, 0, 1),
                    box=box.HEAVY,
                    style=Default.panel_border_style,
                ),
                "center",
            ),
            Align(
                Panel.fit(
                    forecast_tables[2],
                    padding=(0, 1, 0, 1),
                    box=box.HEAVY,
                    style=Default.panel_border_style,
                ),
                "center",
            ),
        )
        yield today
        yield future
