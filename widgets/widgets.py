import datetime
from .widget_handlers import WeatherClient, FacialRecognitionHandler
from .fonts import FontHandler


class Widgets:
    _MAX_ALPHA = 255
    _PARTIAL_ALPHA = 125
    _MARGIN_VALUE = 20

    def __init__(self, smart_mirror):
        """Class to handle Widget interaction with pygame

        Args:
            smart_mirror (SmartMirror): SmartMirror object
        """
        self.smart_mirror = smart_mirror
        self.weather_client = WeatherClient()
        self.facial_rec_handler = FacialRecognitionHandler()
        self.fonts = FontHandler(self.smart_mirror)
        self.facial_rec_handler.start_in_frame_thread()
        self._alpha_full_value = self._MAX_ALPHA
        self._alpha_partial_value = self._MAX_ALPHA
        self._to_draw = []

    def _update_alpha_values(self, time=3, framerate=30):
        """Updates the alpha value for widget fade.

        Args:
            time (int, optional): How long to go from opaque to transparent. Defaults to 3.
            framerate (int, optional): Framerate of the application. Defaults to 30.
        """
        zero_value_factor = self._MAX_ALPHA / (framerate * time)
        partial_value_factor = self._PARTIAL_ALPHA / (framerate * (time / 2))
        if self.facial_rec_handler.in_frame:
            self._alpha_full_value = self._MAX_ALPHA
            self._alpha_partial_value = self._MAX_ALPHA
            return
        if self._alpha_full_value > 0:
            self._alpha_full_value -= zero_value_factor
        if self._alpha_partial_value > self._PARTIAL_ALPHA:
            self._alpha_partial_value -= partial_value_factor

    def _face_rec_name(self):
        """Current Recognized Face"""
        with self.facial_rec_handler.in_frame_datalock:
            in_frame_copy = self.facial_rec_handler.in_frame[:]

        if not in_frame_copy:
            return None
        name_str = "Hello, "
        if len(in_frame_copy) == 1:
            name_str += in_frame_copy[0].title()
        else:
            for x in range(len(in_frame_copy)):
                if x == len(in_frame_copy) - 1:
                    name_str += in_frame_copy[x].title()
                else:
                    name_str += in_frame_copy[x].title() + ", "

        names = self.fonts.render_string(
            name_str, self.fonts.modern_sans_light["large"]
        )
        names_rect = names.get_rect()
        names_rect.midtop = self.smart_mirror.screen_rect.midtop
        self._to_draw.append((names, names_rect))

    def _date_and_time(self):
        """Current Date and Time"""
        datetime_now = datetime.datetime.now()
        current_date_str = datetime_now.strftime("%A, %B %-d")
        current_date = self.fonts.render_string(
            current_date_str, self.fonts.modern_sans_light["large"]
        )
        current_time_str = datetime_now.strftime("%-I:%M%p").lower()
        current_time = self.fonts.render_string(
            current_time_str, self.fonts.modern_sans_light["large"]
        )

        current_date_rect = current_date.get_rect()
        current_time_rect = current_time.get_rect()

        # Set Alpha Values for partial or full fade.
        current_date.set_alpha(self._alpha_full_value)
        current_time.set_alpha(self._alpha_partial_value)

        current_date_rect.topleft = self.smart_mirror.screen_rect.topleft
        current_time_rect.midtop = current_date_rect.midbottom
        current_time_rect.top += self._MARGIN_VALUE

        self._to_draw.append((current_date, current_date_rect))
        self._to_draw.append((current_time, current_time_rect))

    def _current_weather_and_location(self):
        """Current Weather and Location"""

        location_str, current_temp_str, current_icon_path, daily_temp_strs = (
            self.weather_client.get_current_location_weather()
        )
        daily_high_str, daily_low_str = daily_temp_strs
        forecast_5day = self.weather_client.get_forecast_5day()

        location = self.fonts.render_string(
            location_str, self.fonts.modern_sans_light["large"]
        )
        current_temp = self.fonts.render_string(
            current_temp_str, self.fonts.raleway_light["large"]
        )
        current_icon = self.smart_mirror.import_image(current_icon_path)
        daily_high = self.fonts.render_string(
            daily_high_str, self.fonts.raleway_light["small"]
        )
        daily_low = self.fonts.render_string(
            daily_low_str, self.fonts.raleway_light["small"]
        )

        location_rect = location.get_rect()
        current_temp_rect = current_temp.get_rect()
        current_icon_rect = current_icon.get_rect()
        daily_high_rect = daily_high.get_rect()
        daily_low_rect = daily_low.get_rect()

        # Set Alpha Values for partial or full fade.
        location.set_alpha(self._alpha_full_value)
        current_temp.set_alpha(self._alpha_partial_value)
        current_icon.set_alpha(self._alpha_partial_value)
        daily_high.set_alpha(self._alpha_full_value)
        daily_low.set_alpha(self._alpha_full_value)

        # Place Rects on screen in relation to eachother
        location_rect.topright = self.smart_mirror.screen_rect.topright
        current_temp_rect.midtop = location_rect.midbottom
        current_temp_rect.top += self._MARGIN_VALUE
        current_icon_rect.midright = current_temp_rect.midleft
        current_temp_rect.left += self._MARGIN_VALUE
        daily_high_rect.topleft = current_temp_rect.topright
        daily_low_rect.bottomleft = current_temp_rect.bottomright
        daily_high_rect.right = self.smart_mirror.screen_rect.right
        daily_low_rect.right = self.smart_mirror.screen_rect.right
        daily_low_rect.top += 5

        for x in range(len(forecast_5day)):
            day = self.fonts.render_string(
                forecast_5day[x]['weekday_str'], self.fonts.modern_sans_light['medium'])
            date = self.fonts.render_string(
                forecast_5day[x]['date_str'], self.fonts.modern_sans_light['small']
            )
            high_temp = self.fonts.render_string(
                forecast_5day[x]['high_str'], self.fonts.raleway_light['medium']
            )
            icon = self.smart_mirror.import_image(forecast_5day[x]['icon_path'], size=50)

            day_rect = day.get_rect()
            date_rect = date.get_rect()
            high_temp_rect = high_temp.get_rect()
            icon_rect = icon.get_rect()

            day.set_alpha(self._alpha_full_value)
            date.set_alpha(self._alpha_full_value)
            high_temp.set_alpha(self._alpha_full_value)
            icon.set_alpha(self._alpha_full_value)

            full_height = day_rect.height + date_rect.height
            day_rect.topleft = location_rect.bottomleft
            day_rect.top = (
                current_icon_rect.bottom + (x * full_height) + self._MARGIN_VALUE
                )
            date_rect.topleft = day_rect.bottomleft
            icon_rect.center = date_rect.topright
            high_temp_rect.center = icon_rect.center
            high_temp_rect.right = self.smart_mirror.screen_rect.right - self._MARGIN_VALUE
            icon_rect.right = high_temp_rect.left - self._MARGIN_VALUE

            self._to_draw.append((day, day_rect))
            self._to_draw.append((date, date_rect))
            self._to_draw.append((high_temp, high_temp_rect))
            self._to_draw.append((icon, icon_rect))

        # Add rects and images to _to_draw to blit to screen in main loop
        self._to_draw.append((location, location_rect))
        self._to_draw.append((current_icon, current_icon_rect))
        self._to_draw.append((current_temp, current_temp_rect))
        self._to_draw.append((daily_high, daily_high_rect))
        self._to_draw.append((daily_low, daily_low_rect))

    def create_and_place(self):
        self._to_draw = []
        self._update_alpha_values()
        self._face_rec_name()
        self._date_and_time()
        self._current_weather_and_location()
    
    def screen_obejcts(self):
        return self._to_draw
    