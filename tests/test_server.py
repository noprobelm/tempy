from ward import test
import socket
import os
from tempy import config
from tempy import data


@test("Proxy server domain name resolves to 173.255.235.176")
def _():
    assert "173.255.235.176" == socket.gethostbyname(data.Data._proxy_domain)


@test("Request weatherapi returns valid data")
def _():
    tempyrc = config.TempyRC(
        os.path.join(os.path.expanduser("~"), ".config/tempyrc_test")
    )
    weather_data = data.Data(location=tempyrc["location"], api_key=tempyrc["api_key"])

    for key in ["localdata", "weather", "forecast"]:
        assert key in weather_data.keys()
