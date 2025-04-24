import os
import datetime
import requests
import json
from decouple import config

class WeatherClient:

    API_KEY = config('WEATHER_API_KEY')
    BASE_URL = 'http://api.weatherapi.com/v1/'
    WEATHER_DIR = os.path.dirname(os.path.abspath(__file__))
    CURRENT_WEATHER_JSON = os.path.join(WEATHER_DIR, 'current_weather.json')
    FORECAST_JSON = os.path.join(WEATHER_DIR, 'forecast.json')

    def __init__(self):
        None
    
    def _get_current_weather_url(self):
        base_url_addon = 'current.json'
        params = {
            'key': self.API_KEY,
            'q': 'Haverstraw',
            'aqi': 'no'
        }
        current_weather_url = self.BASE_URL + base_url_addon
        return current_weather_url, params
    
    def _request_save_weather(self, url_func):
        url, params = url_func()
        r = requests.get(url, params=params)
        data = r.json()
        with open(self.CURRENT_WEATHER_JSON, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    
    def check_for_update(self):
        current_hour = datetime.datetime.now().strftime('%H')
        if not os.path.exists(self.CURRENT_WEATHER_JSON):
            self._request_save_weather(self._get_current_weather_url)
        with open(self.CURRENT_WEATHER_JSON) as json_file:
            current_weather = json.load(json_file)
        last_update = current_weather['current']['last_updated']
        last_update_hour = last_update.split(' ')[1].split(':')[0]
        if current_hour != last_update_hour:
            self._request_save_weather(self._get_current_weather_url)

    def get_location(self):
        with open(self.CURRENT_WEATHER_JSON) as json_file:
            current_weather = json.load(json_file)
        location = current_weather['location']['name']
        region = current_weather['location']['region']
        location_str = f"{location}, {region}"
        return location_str

    def get_current_temp_f(self):
        with open(self.CURRENT_WEATHER_JSON) as json_file:
            current_weather = json.load(json_file)
        temp_f = str(current_weather['current']['temp_f'])
        icon = current_weather['current']['condition']['icon']
        return temp_f, icon


