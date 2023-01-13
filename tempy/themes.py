#!/usr/bin/env python3
from dataclasses import dataclass


@dataclass
class Default:
    panel_border_style: str = "blue"
    information: str = "bright_blue"
    table_divider: str = "yellow"
    table_header: str = "italic yellow"
    report_header: str = "yellow"
