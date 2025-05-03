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
        self.update_lock = threading.Lock()
        self.forecast = self._load_weather_json()
        self._is_updated = True
        self._last_update_clock = None
        self._degree_symbol = chr(0xB0)

    # -- Weather API calling and JSON updating -- #
    def _ensure_weather_json_exists(self):
        if not os.path.exists(self._FORECAST_JSON):
            self._start_request_weather_thread(self._get_forecast_url)

    def _load_weather_json(self):  
        self._ensure_weather_json_exists()
        while not os.path.exists(self._FORECAST_JSON):
            None
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
            return data
        except Exception as e:
            print(f'Error retreiving API response: {e}\n Attempting again in 30 minutes')

    def _save_weather(self, data):
        try:
            with self.forecast_datalock:
                    with open(self._FORECAST_JSON, "w") as json_file:
                        json.dump(data, json_file, indent=4)
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
        # 31 minutes to allow for weather server to update at 30
        return current_min % 16 == 1 and current_min != self._last_update_clock

    def _check_for_temp_update(self):
        if self._is_updated is False:
            self.forecast = self._load_weather_json()
            with self.update_lock:
                self._is_updated = True
        current_min = int(datetime.datetime.now().strftime('%M'))
        if self._needs_weather_update(current_min):
            self._last_update_clock = current_min
            self._start_request_weather_thread(self._get_forecast_url)

    # -- Get data for current weather widget -- #
    def _get_location(self):
        location = self.forecast["location"]["name"]
        region = self.forecast["location"]["region"]
        location_str = f"{location}, {region}"
        return location_str

    def _get_current_icon_path(self):
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
        temp_f = int(self.forecast["current"]["temp_f"])
        temp_f_str = f"{temp_f}{self._degree_symbol}F"
        return temp_f_str

    def _get_daily_temp_f(self):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        for day in self.forecast['forecast']['forecastday']:
            if day['date'] == current_date:
                day_high = int(day['day']['maxtemp_f'])
                day_low = int(day['day']['mintemp_f'])
        day_high_str = f"High {day_high}{self._degree_symbol}F"
        day_low_str = f"Low {day_low}{self._degree_symbol}F"
        return day_high_str, day_low_str
    
    def get_current_location_weather(self):
        self._check_for_temp_update()
        location_str = self._get_location()
        current_temp_str = self._get_current_temp_f()
        current_icon_path = self._get_current_icon_path()
        daily_temp_strs = self._get_daily_temp_f()

        return location_str, current_temp_str, current_icon_path, daily_temp_strs

    # -- Get data for forecast widget
    def _get_forcast_icon(self, icon_code):
        icon_path = os.path.join(self._ICON_DIR, f'{icon_code}.png')
        cloudy_icon = os.path.join(self._ICON_DIR, '1009.png')
        if os.path.exists(icon_path):
            return icon_path
        else:
            return cloudy_icon
        
    def get_forecast_5day(self):
        forecast_5day = []
        for day in self.forecast['forecast']['forecastday'][1:]:
            day_dict = {}
            day_datetime = datetime.datetime.strptime(day['date'], "%Y-%m-%d")
            day_dict['weekday_str'] = day_datetime.strftime("%A")
            day_dict['date_str'] = day_datetime.strftime("%B %-d")
            avg = int(day['day']['avgtemp_f'])
            day_dict['avg_str'] = f"{avg}{self._degree_symbol}F"
            high = int(day['day']['maxtemp_f'])
            day_dict['high_str'] = f"{high}{self._degree_symbol}F"
            low = int(day['day']['mintemp_f'])
            day_dict['low_str'] = f"{low}{self._degree_symbol}F"
            icon_code = day['day']['condition']['code']
            day_dict['icon_path'] = self._get_forcast_icon(icon_code)
            forecast_5day.append(day_dict)
        return forecast_5day
            



