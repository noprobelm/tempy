from tempy import report
from tempy import themes
from rich.console import Console
from datetime import datetime
from io import StringIO
from ward import test

console = Console(file=StringIO(), theme=themes.DEFAULT)
location = "New York, New York"
localtime = datetime.now()
weather_table = {
    "Temperature": "15°F",
    "Wind": "15 mph SW",
    "Gusts": "15 mph",
    "Pressure": "10 inHg",
    "Precipitation": "1.0 in",
    "Visibility": "1.0 mi",
    "Humidity": "10%",
    "Cloud Cover": "10%",
    "UV index": "10.0",
}

forecast_tables = [
    {
        "Average": "15°F",
        "Low": "10°F",
        "High": "20°F",
        "Gusts": "10 mph",
        "Total Precipitation": "1.0 in",
        "Average Visibility": "1.0 mi",
        "Chance Of Rain": "10%",
        "Chance Of Snow": "10%",
        "UV Index": "1.0",
    },
    {
        "Average": "20°F",
        "Low": "15°F",
        "High": "25°F",
        "Gusts": "15 mph",
        "Total Precipitation": "2.0 in",
        "Average Visibility": "2.0 mi",
        "Chance Of Rain": "15%",
        "Chance Of Snow": "15%",
        "UV Index": "2.0",
    },
    {
        "Average": "30°F",
        "Low": "25°F",
        "High": "35°F",
        "Gusts": "20 mph",
        "Total Precipitation": "3.0 in",
        "Average Visibility": "3.0 mi",
        "Chance Of Rain": "20%",
        "Chance Of Snow": "20%",
        "UV Index": "3.0",
    },
]

conditions = [
    "Torrential rain shower",
    "Light rain shower",
    "Cloudy",
    "Moderate or heavy showers of ice pellets",
    "Fog",
    "Moderate or heavy rain with thunder",
    "Overcast",
    "Patchy heavy snow",
    "Light drizzle",
    "Heavy snow",
    "Moderate or heavy snow showers",
    "Light snow showers",
    "Ice pellets",
    "Patchy light drizzle",
    "Moderate or heavy sleet showers",
    "Sunny",
    "Patchy light rain",
    "Freezing drizzle",
    "Moderate rain at times",
    "Patchy light snow with thunder",
    "Patchy freezing drizzle possible",
    "Light showers of ice pellets",
    "Thundery outbreaks possible",
    "Patchy light rain with thunder",
    "Blowing snow",
    "Light rain",
    "Patchy moderate snow",
    "Blizzard",
    "Moderate or heavy freezing rain",
    "Moderate snow",
    "Partly cloudy",
    "Heavy freezing drizzle",
    "Patchy snow possible",
    "Patchy light snow",
    "Patchy rain possible",
    "Light snow",
    "Freezing fog",
    "Heavy rain at times",
    "Mist",
    "Light freezing rain",
    "Clear",
    "Moderate or heavy snow with thunder",
    "Patchy sleet possible",
    "Heavy rain",
    "Light sleet",
    "Moderate or heavy rain shower",
    "Moderate or heavy sleet",
    "Moderate rain",
    "Light sleet showers",
]

reports = []
str_outputs = []

for condition in conditions:
    for is_day in [True, False]:
        time_of_day = "day" if is_day is True else "night"

        if condition == "Sunny":
            renderable = report.Report(
                localtime, True, location, condition, weather_table, forecast_tables
            )
            continue
        elif condition == "Clear":
            renderable = report.Report(
                localtime, False, location, condition, weather_table, forecast_tables
            )
            continue
        else:
            renderable = report.Report(
                localtime, is_day, location, condition, weather_table, forecast_tables
            )

        reports.append(renderable)

for report in reports:

    @test(
        f"A report with condition '{report.condition}' with 'is_day' set to '{report.is_day}' will render"
    )
    def _():
        console.print(report)
        str_outputs.append(console.file.getvalue())
