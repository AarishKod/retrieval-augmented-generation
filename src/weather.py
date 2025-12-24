"""
By Aarish Kodnaney
"""

from typing import Dict, Optional, Any
from dotenv import load_dotenv
import requests
import os
import json

# for testing only
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

class WeatherInfo:
    """Object for info returned by weather api"""
    def __init__(self, location: str, text_description: str, temp_fahrenheit: float, wind_speed_mph: float):
        self.location = location
        self.text_description = text_description
        self.temp_fahrenheit = temp_fahrenheit
        self.wind_speed_mph = wind_speed_mph

    def __json__(self) -> Dict[str, Any]:
        return {
            "location": self.location,
            "text_description": self.text_description,
            "temp_f": self.temp_fahrenheit,
            "wind_speed": self.wind_speed_mph
        }

class Weather:
    """handles the weather"""
    def __init__(self, api_key: str | None, url: str) -> None:
        self.api_key = api_key
        self.url = url
        self.timeout = 20

    def get_data_from_endpoint(self, location: str) -> Any:
        parameters = {
            "key": self.api_key,
            "q": location
        }
        try:
            response = requests.get(self.url + "/current.json", params=parameters, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as issue:
            print(f"Error: {issue}")
            return None

    def get_desired_info(self, json_data: Any) -> Dict[str, Any]:
        to_return = {
            "name": json_data["location"]["name"],
            "text": json_data["current"]["condition"]["text"],
            "wind_mph": json_data["current"]["wind_mph"],
            "temp_f": json_data["current"]["temp_f"]
        }

        return to_return

    def build_weather_info_obect(self, info: Dict[str, Any]) -> WeatherInfo:
        return WeatherInfo(info["name"], info["text"], info["temp_f"], info["wind_mph"])
