import requests
from datetime import datetime, timedelta
from typing import Union
from .console import console


class Data(dict):
    # Backup in case the user doesn't want to get their own API key.
    proxy_server = "http://noprobelm.dev:80"
    # Request the actual endpoint if an API key is detected
    api_endpoint = "https://api.weatherapi.com/v1/forecast.json"

    def __init__(self, location: str, api_key: Union[str, None]):
        if api_key:
            data = requests.get(
                f"{self.api_endpoint}?key={api_key}&q={location}&days=3&awi=yes"
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

        localdata = {
            "location": f"{data['location']['name']}, {data['location']['region']}",
            "localtime": datetime.fromtimestamp(
                data["location"]["localtime_epoch"]
            ).strftime("%A, %B %-d | %H:%M"),
        }
        weather = {
            "condition": data["current"]["condition"]["text"],
            "is_day": data["current"]["is_day"],
            "imperial": {
                "temperature": f"{data['current']['temp_f']}°F",
                "wind": f"{data['current']['wind_mph']} mph {data['current']['wind_dir']}",
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
                "pressure": f"{int(data['current']['pressure_mb'])} mbar",
                "precipitation": f"{data['current']['precip_mm']} mm",
                "visibility": f"{data['current']['vis_km']} km",
                "humidity": f"{data['current']['humidity']}%",
                "cloud cover": f"{data['current']['cloud']}%",
                "UV index": f"{data['current']['uv']}",
            },
        }

        forecast = []
        for num, day in enumerate(data["forecast"]["forecastday"]):
            selected = day["day"]
            forecast.append(
                {
                    "date": (
                        datetime.fromtimestamp(data["location"]["localtime_epoch"])
                        + timedelta(days=num)
                    ).strftime("%A, %B %-d"),
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

        super().__init__(
            {"localdata": localdata, "weather": weather, "forecast": forecast}
        )
