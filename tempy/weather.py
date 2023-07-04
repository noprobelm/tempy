from pathlib import Path
from typing import List, Optional, Union

from rich import box
from rich.align import Align
from rich.console import Console, ConsoleOptions, Group, Measurement, RenderResult
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Column, Table
from rich.text import Text

from .console import console
from .data import Data
from .themes import Default

from dataclasses import dataclass


@dataclass
class Weather:
    title: str
    weather: dict

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        labels = Column(
            "labels",
            width=max([len(label) for label in self.weather.keys()]),
            no_wrap=True,
            style=Default.information,
        )
        values = Column(
            "values",
            width=max([len(str(value)) for value in self.weather.values()]),
            no_wrap=True,
            style=Default.information,
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

        table.title = f"{self.title}\n"
        for label in self.weather:
            table.add_row(label.title(), self.weather[label])

        yield table


class Report:
    def __init__(self, location: str, units: str, api_key: str) -> None:
        self.data = Data(location, api_key)
        self.units = units

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
    def weather_table(self) -> Weather:
        if self.units == "imperial":
            weather_table = Weather(
                "Current Conditions\n", self.data["weather"]["imperial"]
            )
        else:
            weather_table = Weather(
                "Current Conditions\n", self.data["weather"]["metric"]
            )

        return weather_table

    @property
    def forecast_tables(self) -> List[Weather]:
        forecast = self.data["forecast"]
        if self.units == "imperial":
            forecast_tables = [Weather("Today's Forecast\n", forecast[0]["imperial"])]
            for data in forecast[1:]:
                forecast_tables.append(Weather(f"{data['date']}\n", data["imperial"]))
        else:
            forecast_tables = [Weather("Today's Forecast\n", forecast[0]["metric"])]
            for data in forecast[1:]:
                forecast_tables.append(Weather(f"{data['date']}\n", data["metric"]))

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
            Column("1", justify="left"),
            Column("2", justify="right"),
            show_edge=False,
            show_lines=False,
            box=None,
            show_header=False,
            padding=0,
        )
        future.width = console.measure(today).maximum
        future.add_row(
            Panel(
                Align(forecast_tables[1], "center"),
                box=box.HEAVY,
                style=Default.panel_border_style,
                width=(future.width // 2 - 1),
            ),
            Panel(
                Align(forecast_tables[2], "center"),
                box=box.HEAVY,
                style=Default.panel_border_style,
                width=(future.width // 2 + 1)
                if future.width % 2 == 1
                else future.width // 2,
            ),
        )
        yield today
        yield future
