import os
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
from .themes import Default


class Report:
    def __init__(self, location: str, units: str, api_key: str) -> None:
        self._data = Data(location, api_key)

        if units == "imperial":
            self._imperial = True
        else:
            self._imperial = False

    def _get_ascii_art(self, condition: str, is_day: bool):
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
