import datetime
from .widget_files import WeatherClient, FacialRecognitionHandler

class Widgets:

    def __init__(self, smart_mirror):
        """Class to handle Widget interaction with pygame

        Args:
            smart_mirror (SmartMirror): SmartMirror object
        """
        self.smart_mirror = smart_mirror
        self.weather_client = WeatherClient()
        self.facial_rec_handler = FacialRecognitionHandler()
        self.facial_rec_handler.start_in_frame_thread()

    def date_and_time(self):
        """Current Date and Time
        """
        datetime_now = datetime.datetime.now()
        current_date_str = datetime_now.strftime('%A, %B %-d')
        current_date = self.smart_mirror.sans_font.render(current_date_str, True, (255,255,255))
        current_date_rect = current_date.get_rect()

        current_time_str = datetime_now.strftime('%-I:%M %p').lower()
        current_time = self.smart_mirror.sans_font.render(current_time_str, True, (255,255,255))
        current_time_rect = current_time.get_rect()

        current_date_rect.topleft = self.smart_mirror.screen_rect.topleft
        current_time_rect.center = current_date_rect.center
        current_time_rect.top = current_date_rect.bottom + 20
        
        self.smart_mirror._to_draw.append((current_date, current_date_rect))
        self.smart_mirror._to_draw.append((current_time, current_time_rect))
    
    def face_rec_name(self):
        """Current Recognized Face
        """
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

        names = self.smart_mirror.sans_font.render(name_str, True, (255,255,255))
        names_rect = names.get_rect()
        names_rect.center = self.smart_mirror.screen_rect.center
        self.smart_mirror._to_draw.append((names, names_rect))
    
    def weather_and_location(self):
        """Current Weather and Location
        """
        self.weather_client.check_for_temp_update()

        location_str = self.weather_client.get_location()
        location = self.smart_mirror.sans_font.render(location_str, True, (255,255,255))
        location_rect = location.get_rect()

        temp_str, icon_path = self.weather_client.get_current_temp_f()
        temp = self.smart_mirror.sans_font.render(temp_str+' F', True, (255,255,255))
        temp_rect = temp.get_rect()

        current_icon = self.smart_mirror.import_image(icon_path)
        current_icon_rect = current_icon.get_rect()

        location_rect.topright = self.smart_mirror.screen_rect.topright
        temp_rect.midtop = location_rect.midbottom
        temp_rect.top += 20
        current_icon_rect.midright = temp_rect.midleft
        temp_rect.left += 20

        self.smart_mirror._to_draw.append((location, location_rect))
        self.smart_mirror._to_draw.append((current_icon, current_icon_rect))
        self.smart_mirror._to_draw.append((temp, temp_rect))