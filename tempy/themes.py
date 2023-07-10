#!/usr/bin/env python3
from rich.theme import Theme


DEFAULT = Theme(
    {
        "panel_border": "blue",
        "labels": "bright_blue",
        "table_divider": "yellow",
        "table_header": "italic yellow",
        "report_header": "yellow",
    }
)


@dataclass
class Default:
    panel_border_style: str = "blue"
    labels: str = "bright_blue"
    table_divider: str = "yellow"
    table_header: str = "italic yellow"
    report_header: str = "yellow"
