import datetime
from .widget_files import WeatherClient, FacialRecognitionHandler


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
        self.facial_rec_handler.start_in_frame_thread()
        self._alpha_full_value = self._MAX_ALPHA
        self._alpha_partial_value = self._MAX_ALPHA
    
    def update_alpha_values(self, time=3, framerate=30): 
        """Updates the alpha value for widget fade.

        Args:
            time (int, optional): How long to go from opaque to transparent. Defaults to 3.
            framerate (int, optional): Framerate of the application. Defaults to 30.
        """
        zero_value_factor = self._MAX_ALPHA / (framerate * time)
        partial_value_factor = self._PARTIAL_ALPHA / (framerate * (time/2))
        if self.facial_rec_handler.in_frame:
            self._alpha_full_value = self._MAX_ALPHA
            self._alpha_partial_value = self._MAX_ALPHA
            return
        if self._alpha_full_value > 0:
            self._alpha_full_value -= zero_value_factor
        if self._alpha_partial_value > self._PARTIAL_ALPHA:
            self._alpha_partial_value -= partial_value_factor

    def face_rec_name(self):
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

        names = self.smart_mirror.sans_font.render(name_str, True, (255, 255, 255))
        names_rect = names.get_rect()
        names_rect.midtop = self.smart_mirror.screen_rect.midtop
        self.smart_mirror._to_draw.append((names, names_rect))

    def date_and_time(self):
        """Current Date and Time"""
        datetime_now = datetime.datetime.now()
        current_date_str = datetime_now.strftime("%A, %B %-d")
        current_date = self.smart_mirror.sans_font.render(
            current_date_str, True, (255, 255, 255)
        )
        current_time_str = datetime_now.strftime("%-I:%M%p").lower()
        current_time = self.smart_mirror.sans_font.render(
            current_time_str, True, (255, 255, 255)
        )

        current_date_rect = current_date.get_rect()
        current_time_rect = current_time.get_rect()

        # Set Alpha Values for partial or full fade.
        current_date.set_alpha(self._alpha_full_value)
        current_time.set_alpha(self._alpha_partial_value)

        current_date_rect.topleft = self.smart_mirror.screen_rect.topleft
        current_time_rect.midtop = current_date_rect.midbottom
        current_time_rect.top += self._MARGIN_VALUE

        self.smart_mirror._to_draw.append((current_date, current_date_rect))
        self.smart_mirror._to_draw.append((current_time, current_time_rect))

    def weather_and_location(self):
        """Current Weather and Location"""
        degree_symbol = chr(0xB0)

        location_str, temp_str, icon_path = self.weather_client.get_current_location_weather()

        location = self.smart_mirror.sans_font.render(
        location_str, True, (255, 255, 255)
        )
        temp = self.smart_mirror.raleway_font.render(
            temp_str + f"{degree_symbol}F", True, (255, 255, 255)
        )
        current_icon = self.smart_mirror.import_image(icon_path)

        location_rect = location.get_rect()
        temp_rect = temp.get_rect()
        current_icon_rect = current_icon.get_rect()

        # Set Alpha Values for partial or full fade.
        location.set_alpha(self._alpha_full_value)
        temp.set_alpha(self._alpha_full_value)
        current_icon.set_alpha(self._alpha_full_value)

        location_rect.topright = self.smart_mirror.screen_rect.topright
        temp_rect.midtop = location_rect.midbottom
        temp_rect.top += self._MARGIN_VALUE
        current_icon_rect.midright = temp_rect.midleft
        temp_rect.left += self._MARGIN_VALUE

        self.smart_mirror._to_draw.append((location, location_rect))
        self.smart_mirror._to_draw.append((current_icon, current_icon_rect))
        self.smart_mirror._to_draw.append((temp, temp_rect))

    