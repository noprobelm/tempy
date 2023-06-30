from ward import test
import socket
from tempy import data


@test("Proxy server domain name resolves to 173.255.235.176")
def _():
    assert "173.255.235.176" == socket.gethostbyname(data.Data._proxy_domain)
