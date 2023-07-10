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
                - is_day (int): bool representing day or night for current weathe report
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

        super().__init__(data)

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
