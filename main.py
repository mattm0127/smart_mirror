import pygame
from facial_recognition import FacialRecognitionHandler
from widgets import Widgets
import threading
import time
import sys
import os
import requests
from io import BytesIO


class SmartMirror:
    pygame.init()
    pygame.mouse.set_visible(False)

    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.sys_font = pygame.font.SysFont(None, size=48)
        self.font_size = 50
        self.title_font_size = 20

        if "win" in sys.platform:
            self.ms_light_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "fonts\ModernSans-Light.otf"
            )
            self.m_deco_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "fonts\Modern-Deco.ttf"
            )
        else:
            self.ms_light_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "fonts/ModernSans-Light.otf"
            )
            self.m_deco_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "fonts/Modern-Deco.ttf"
            )
        self.deco_font = pygame.font.Font(self.m_deco_path, self.font_size)
        self.sans_font = pygame.font.Font(self.ms_light_path, self.font_size)
        self.facial_recogntion = FacialRecognitionHandler()
        self.widgets = Widgets(self)
        self.in_frame = []
        self.in_frame_datalock = threading.Lock()
        self.scan_for_faces = True
        self._to_draw = []

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.facial_recogntion.add_new_face()

    def _update_in_frame(self):
        while self.scan_for_faces:
            with self.in_frame_datalock:
                in_frame_copy = self.in_frame[:]
            face_names = self.facial_recogntion.run_recognition()
            if face_names is None:
                in_frame_copy = []
            elif len(in_frame_copy) == 0:
                in_frame_copy = face_names
            else:
                names_to_remove = []
                for face in in_frame_copy:
                    if face not in face_names:
                        names_to_remove.append(face)
                for remove_name in names_to_remove:
                    in_frame_copy.remove(remove_name)
            with self.in_frame_datalock:
                self.in_frame = in_frame_copy[:]
            time.sleep(1)

    def _start_in_frame_thread(self):
        in_frame_thread = threading.Thread(target=self._update_in_frame, daemon=True)
        in_frame_thread.start()

    def _draw_screen(self):
        self.screen.fill((0, 0, 0))
        self.widgets.face_rec_name()
        self.widgets.date_and_time()
        self.widgets.weather_and_location()
        self.screen.blits(blit_sequence=self._to_draw)
        pygame.display.flip()
        self._to_draw = []

    def import_image(self, img_url):
        img_url = "https:" + img_url
        response = requests.get(img_url)
        img_file = BytesIO(response.content)
        img = pygame.image.load(img_file)
        img = pygame.transform.scale(img, (80, 80))
        return img

    def run_program(self):
        self._start_in_frame_thread()
        while True:
            self._check_events()
            self._draw_screen()
            self.clock.tick(10)


if __name__ == "__main__":
    smart_mirror = SmartMirror()
    smart_mirror.run_program()
