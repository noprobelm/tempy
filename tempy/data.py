import sys
import requests
from datetime import datetime, timedelta
from .console import console
from typing import Optional


class Data(dict):
    """Stores the raw weather report data for specified location and units

    Attributes:
        1. proxy_server (str): The proxy server to forward requests through
        2. api_endpoint (str): The api endpoint to use if an api key is provided

    """

    def __init__(self, location: str, api_key: Optional[str] = ""):
        """Initializes an instance of the Data class

        Reaches out to either the proxy server our weatherapi (depending on if API key is present). The resulting json
        is then parsed to meet the needs of the weather.Report class.

        Args:
            1. location (str): The location to request weather information for (can be city, state/province, zip code)
            2. api_key (Optional[str]): Optional API key to bypass proxy server

        Keys:
            - localdata (dict): A dict of the localdata parsed from the HTTP resonse
                - location (str): The requested location
                - localtime (str): A datetime str parsed to meet the needs of the weather.Report class
            - weather (dict): A dict of the current weather data parsed from the HTTP response
                - condition (str): str of the current weather conditions (e.g. "sunny")
                - is_day (int): 0 or 1 representing daytime (1) or nighttime (0)
                - imperial (dict[str, str]): The full weather report in imperial format
                - metric (dict[str, str]): The full weather report in metric format
            - forecast (list[dict]): A list of dicts containing daily forecast data. Each day:
                - date (str): A datetime str parsed to emet the needs of the weather.Report class.
                - imperial (dict[str, str]): The full forecast report in imperial format
                - metric (dict[str, str]): The full forecast report in metric format

        """
        self.proxy_server = "http://noprobelm.dev:80"
        self.api_endpoint = "https://api.weatherapi.com/v1/forecast.json"

        data = self._request_data(location, api_key)
        localdata = self._parse_localdata(data)
        weather = self._parse_weather(data)
        forecast = self._parse_forecast(data)

        super().__init__(
            {"localdata": localdata, "weather": weather, "forecast": forecast}
        )

    def _request_data(self, location: str, api_key: str):
        if api_key:
            data = requests.get(
                f"{self.api_endpoint}?key={api_key}&q={location}&days=3&aqi=yes&alerts=yes"
            ).json()
        else:
            response = requests.get(
                f"{self.proxy_server}", headers={"location": location}
            )
            if response.status_code == 429:
                console.print(
                    "Rate limit exceeded. Try again in a few minutes.\nIf you feel the rate limit is too strict, create an issue at github.com/noprobelm/tempy"
                )
                quit()
            else:
                data = response.json()

        if "error" in data.keys():
            console.print(
                f"tempy: '{location}': {data['error']['message']} Please try again"
            )
            sys.exit()

        return data

    def _parse_localdata(self, data: dict):
        localtime = datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M")
        localdata = {
            "location": f"{data['location']['name']}, {data['location']['region']}",
            "localtime": f"{localtime.strftime('%A, %B')} {localtime.strftime('%e').strip()}{localtime.strftime(' | %H:%M')}",
        }

        return localdata

    def _parse_weather(self, data: dict):
        weather = {
            "condition": data["current"]["condition"]["text"],
            "is_day": data["current"]["is_day"],
            "imperial": {
                "temperature": f"{data['current']['temp_f']}°F",
                "wind": f"{data['current']['wind_mph']} mph {data['current']['wind_dir']}",
                "gusts": f"{data['current']['gust_mph']} mph",
                "pressure": f"{data['current']['pressure_in']} inHg",
                "precipitation": f"{data['current']['precip_in']} in",
                "visibility": f"{data['current']['vis_miles']} mi",
                "humidity": f"{data['current']['humidity']}%",
                "cloud cover": f"{data['current']['cloud']}%",
                "UV index": f"{data['current']['uv']}",
            },
            "metric": {
                "temperature": f"{data['current']['temp_c']}°C",
                "wind": f"{data['current']['wind_kph']} kph {data['current']['wind_dir']}",
                "gusts": f"{data['current']['gust_kph']} kph",
                "pressure": f"{int(data['current']['pressure_mb'])} mb",
                "precipitation": f"{data['current']['precip_mm']} mm",
                "visibility": f"{data['current']['vis_km']} km",
                "humidity": f"{data['current']['humidity']}%",
                "cloud cover": f"{data['current']['cloud']}%",
                "UV index": f"{data['current']['uv']}",
            },
        }
        return weather

    def _parse_forecast(self, data: dict) -> list[dict]:
        forecast = []
        for num, day in enumerate(data["forecast"]["forecastday"]):
            selected = day["day"]
            localtime = datetime.strptime(
                data["location"]["localtime"], "%Y-%m-%d %H:%M"
            ) + timedelta(days=num)

            forecast.append(
                {
                    "date": f"{localtime.strftime('%A, %B')} {localtime.strftime('%e').strip()}",
                    "imperial": {
                        "average": f"{selected['avgtemp_f']}°F",
                        "low": f"{selected['mintemp_f']}°F",
                        "high": f"{selected['maxtemp_f']}°F",
                        "gusts": f"{selected['maxwind_mph']} mph",
                        "total precipitation": f"{selected['totalprecip_in']} in",
                        "average visibility": f"{selected['avgvis_miles']} mi",
                        "chance of rain": f"{selected['daily_chance_of_rain']}%",
                        "chance of snow": f"{selected['daily_chance_of_snow']}%",
                        "uv index": f"{selected['uv']}",
                    },
                    "metric": {
                        "average": f"{selected['avgtemp_c']}°C",
                        "low": f"{selected['mintemp_c']}°C",
                        "high": f"{selected['maxtemp_c']}°C",
                        "gusts": f"{selected['maxwind_kph']} kph",
                        "total precipitation": f"{selected['totalprecip_mm']} mm",
                        "average visibility": f"{selected['avgvis_km']} km",
                        "chance of rain": f"{selected['daily_chance_of_rain']}%",
                        "chance of snow": f"{selected['daily_chance_of_snow']}%",
                        "uv index": f"{selected['uv']}",
                    },
                }
            )

        return forecast
