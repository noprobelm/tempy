import sys
from typing import Optional
from datetime import datetime

import requests

from .console import console


class WeatherAPI:
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

        Reaches out to either the proxy server or weatherapi (depending on if API key is present).

        Args:
            1. location (str): The location to request weather information for (can be city, state/province, zip code)
            2. api_key (Optional[str]): Optional API key to bypass proxy server

        """

        self._proxy_endpoint = (
            f"http://{WeatherAPI._proxy_domain}:{WeatherAPI._proxy_port}"
        )
        self._location = location

        self.data = self._request_api(api_key) if api_key else self._request_proxy()

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

    def parse(self, units: str) -> dict:
        """Parse the weatherapi response into something the report.Report class can use

        Args:
            units (str): The unit of measurement to use when parsing the data

        Returns:
            dict: A dictionary of the args needed for report.Report
        """

        if units == "imperial":
            imperial = True
        else:
            imperial = False

        localtime = datetime.strptime(
            self.data["location"]["localtime"], "%Y-%m-%d %H:%M"
        )
        is_day = bool(self.data["current"]["is_day"])
        location = self._parse_location(
            self.data["location"]["name"], self.data["location"]["region"]
        )

        condition = self.data["current"]["condition"]["text"]
        weather = self._parse_weather(self.data["current"], imperial)
        forecasts = []
        for day in self.data["forecast"]["forecastday"]:
            forecast = self._parse_forecast(day["day"], imperial)
            forecasts.append(forecast)

        return {
            "localtime": localtime,
            "is_day": is_day,
            "location": location,
            "condition": condition,
            "weather_table": weather,
            "forecast_tables": forecasts,
        }
