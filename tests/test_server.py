from ward import test
import socket
from tempy import data

weather_data = data.WeatherAPI(location="nyc")
KEYS = ["location", "current", "forecast", "alerts"]
CURRENT_KEYS = [
    "last_updated_epoch",
    "last_updated",
    "temp_c",
    "temp_f",
    "is_day",
    "condition",
    "wind_mph",
    "wind_kph",
    "wind_degree",
    "wind_dir",
    "pressure_mb",
    "pressure_in",
    "precip_mm",
    "precip_in",
    "humidity",
    "cloud",
    "feelslike_c",
    "feelslike_f",
    "vis_km",
    "vis_miles",
    "uv",
    "gust_mph",
    "gust_kph",
    "air_quality",
]
FORECAST_KEYS = ["date", "date_epoch", "day", "astro", "hour"]


@test("Proxy server domain name resolves to 173.255.235.176")
def _():
    assert "173.255.235.176" == socket.gethostbyname(data.WeatherAPI._proxy_domain)


@test("All expected values from the v1 weatherapi are present")
def _():
    for key in KEYS:
        assert key in weather_data.data.keys()


@test("All expected keys for current weather data are present")
def _():
    for key in CURRENT_KEYS:
        assert key in weather_data.data["current"]


@test("Three days of forecast data are contained in the API response")
def _():
    assert len(weather_data.data["forecast"]["forecastday"]) == 3


@test("All expected keys for forecast data are present")
def _():
    for key in FORECAST_KEYS:
        assert key in weather_data.data["forecast"]["forecastday"][0].keys()
