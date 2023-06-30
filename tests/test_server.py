from ward import test
import socket
import os
from tempy import config
from tempy import data

KEYS = ["localdata", "weather", "forecast"]


@test("Proxy server domain name resolves to 173.255.235.176")
def _():
    assert "173.255.235.176" == socket.gethostbyname(data.Data._proxy_domain)


@test("Request to proxy server returns valid data")
def _():
    args = config.Args(["nyc"])
    weather_data = data.Data(args["location"])

    for key in KEYS:
        assert key in weather_data.keys()


@test("Request to weatherapi returns valid data")
def _():
    tempyrc = config.TempyRC(
        os.path.join(os.path.expanduser("~"), ".config/tempyrc_test")
    )
    weather_data = data.Data(location=tempyrc["location"], api_key=tempyrc["api_key"])

    for key in KEYS:
        assert key in weather_data.keys()
