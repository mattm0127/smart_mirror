import os
import requests
import json
import threading
import datetime
from decouple import config


class WeatherClient:
    _API_KEY = config("WEATHER_API_KEY")
    _BASE_URL = "http://api.weatherapi.com/v1/"
    _WEATHER_DIR = os.path.dirname(os.path.abspath(__file__))
    _FORECAST_JSON = os.path.join(_WEATHER_DIR, "forecast.json")
    _ICON_DIR = os.path.join(_WEATHER_DIR, 'weather_icons')

    def __init__(self):
        self.forecast_datalock = threading.Lock()
        self.forecast = self._load_weather_json()
        self._is_updated = True
        self.update_lock = threading.Lock()
        self._last_update_clock = None

    def _ensure_weather_json_exists(self):
        if not os.path.exists(self._FORECAST_JSON):
            self._start_request_weather_thread(self._get_forecast_url)

    def _load_weather_json(self):  
        self._ensure_weather_json_exists()
        with self.forecast_datalock:
            with open(self._FORECAST_JSON) as json_file:
                forecast = json.load(json_file)
        return forecast

    def _get_forecast_url(self):
        _base_url_addon = "forecast.json"
        params = {"key": self._API_KEY, "q": "Haverstraw", "days":5, "aqi": "no", "alerts": 'no'}
        forecast_url = self._BASE_URL + _base_url_addon
        return forecast_url, params

    def _request_weather(self, url_func):
        url, params = url_func()
        try:
            r = requests.get(url, params=params)
            data = r.json()
            print("New Weather Data Received")
            return data
        except Exception as e:
            print(f'Error retreiving API response: {e}\n Attempting again in 30 minutes')

    def _save_weather(self, data):
        try:
            with self.forecast_datalock:
                    with open(self._FORECAST_JSON, "w") as json_file:
                        json.dump(data, json_file, indent=4)
            print("New Weather Data Saved")
        except Exception as e:
            print(f"Failed to save weather data: {e}\n Attempting again in 30 minutes")

    def _request_and_save_weather(self, url_func):
        data = self._request_weather(url_func)
        if data:
            self._save_weather(data)
            with self.update_lock:
                self._is_updated = False
            
    def _start_request_weather_thread(self, url_func):
        weather_thread = threading.Thread(
            target=self._request_and_save_weather, args=[url_func]
        )
        weather_thread.start()

    def _needs_weather_update(self, current_min):
        return current_min % 30 == 0 and current_min != self._last_update_clock

    def _check_for_temp_update(self):
        if self._is_updated is False:
            self.forecast = self._load_weather_json()
            with self.update_lock:
                self._is_updated = True
        current_min = int(datetime.datetime.now().strftime('%M'))
        if self._needs_weather_update(current_min):
            self._last_update_clock = current_min
            self._start_request_weather_thread(self._get_forecast_url)

    def _get_location(self):
        location = self.forecast["location"]["name"]
        region = self.forecast["location"]["region"]
        location_str = f"{location}, {region}"
        return location_str

    def _get_icon_path(self):
        is_day = self.forecast["current"]["is_day"]
        code = self.forecast["current"]['condition']['code']
        icon_day_night_path = os.path.join(self._ICON_DIR, f'{is_day}/{code}.png')
        icon_path = os.path.join(self._ICON_DIR, f'{code}.png')
        cloudy_icon = os.path.join(self._ICON_DIR, '1009.png')
        if os.path.exists(icon_day_night_path):
            return icon_day_night_path
        elif os.path.exists(icon_path):
            return icon_path
        else:
            return cloudy_icon

    def _get_current_temp_f(self):
        temp_f = str(self.forecast["current"]["temp_f"])
        return temp_f

    def get_current_location_weather(self):
        self._check_for_temp_update()
        location_str = self._get_location()
        temp_str = self._get_current_temp_f()
        icon_path = self._get_icon_path()

        return location_str, temp_str, icon_path
