import sys
from datetime import datetime, timedelta
from typing import Optional

import requests

from .console import console


class Data(dict):
    """Stores the raw weather report data for specified location and units

    Attributes:
        1. _proxy_domain (str): The domain name of the proxy server to forward requests to
        2. _proxy_port (int): The port of the proxy server to forward requests to
        3. _proxy_endpoint (str): The full URL of the proxy server to forward requests to
        4. _api_endpoint (str): The full url of the api endpoint to use if an api key is provided
        5. _location (str): The location to target for the weather report

    """

    _proxy_domain = "noprobelm.dev"
    _proxy_port = 80
    _api_endpoint = "https://api.weatherapi.com/v1"

    def __init__(self, location: str, api_key: Optional[str] = ""):
        """Initializes an instance of the Data class

        Reaches out to either the proxy server or weatherapi (depending on if API key is present). The resulting json
        is then formatted/parsed/simplified for rendering.

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

        self._proxy_endpoint = f"http://{Data._proxy_domain}:{Data._proxy_port}"
        self._location = location

        data = self._request_api(api_key) if api_key else self._request_proxy()

        localdata = self._parse_localdata(data)
        weather = self._parse_weather(data)
        forecast = self._parse_forecast(data)

        super().__init__(
            {"localdata": localdata, "weather": weather, "forecast": forecast}
        )

    def _request_proxy(self) -> dict:
        """Send weather report request to the proxy server

        This method is used if no API key is provided.

        Returns:
            data (dict): The unparsed weather report data

        """
        response = requests.get(
            f"{self._proxy_endpoint}", headers={"location": self._location}
        )

        data = response.json()
        self._validate_data(data)

        return data

    def _request_api(self, api_key: str) -> dict:
        """Send weather report request to the API endpoint

        This method is used if an API key is provided.

        Args:
            api_key (str): The alphanumeric API key to use

        Returns:
            data (dict): The unparsed weather report data

        """
        response = requests.get(
            f"{self._api_endpoint}/forecast.json?key={api_key}&q={self._location}&days=3&aqi=yes&alerts=yes"
        )

        data = response.json()
        self._validate_data(data)

        return data

    def _validate_data(self, data: dict) -> None:
        """Validates the http json response

        Checks to see if the http json response contains an 'error' key. If so, something went wrong.

        TODO:
            - Explore and account for additional errors. Currently we're only accounting for invalid location
              (which is the most probable outcome since we've received a 200 response at this point).

        """
        if "error" in data.keys():
            console.print(
                f"tempy: '{self._location}': {data['error']['message']} Please try again"
            )
            sys.exit()

    def _parse_localdata(self, data: dict):
        """Parses the localdata of the http json response

        Args:
            1. data (dict): The http json response

        Returns:
            - localdata (dict): The localdata associated with the weather report
        """

        localtime = datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M")
        localdata = {
            "location": f"{data['location']['name']}, {data['location']['region']}",
            "localtime": f"{localtime.strftime('%A, %B')} {localtime.strftime('%e').strip()}{localtime.strftime(' | %H:%M')}",
        }

        return localdata

    def _parse_weather(self, data: dict):
        """Parses the current weather data of the http json response

        Args:
            1. data (dict): The http json response

        Returns:
            - weather (dict): The current weather information
        """

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
        """Parses the forecast data from http json response

        Args:
            1. data (dict): The http json response

        Returns:
            - forecast (list[dict]): A list of dicts containing forecast information for each day
        """
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
