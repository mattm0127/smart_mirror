import pygame
from widgets import Widgets
import sys
import os

class SmartMirror:

    pygame.init()
    pygame.mouse.set_visible(False)

    def __init__(self):
        """Class to run main Smart Mirror logic
        """
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
        self.widgets = Widgets(self)
        self._to_draw = []

    def _check_events(self):
        None

    def _draw_screen(self):
        """Takes widgets from _to_draw and blits them screen
        """
        self.screen.fill((0, 0, 0))
        self.widgets.face_rec_name()
        self.widgets.date_and_time()
        self.widgets.weather_and_location()
        self.screen.blits(blit_sequence=self._to_draw)
        pygame.display.flip()
        self._to_draw = []

    def import_image(self, icon_path):
        """Takes image path from Widgets and imports into pygame

        Args:
            icon_path (Path): Path() to the current icon.png file

        Returns:
            Surface: Pygame surface of the icon
        """
        icon = pygame.image.load(icon_path)
        scaled_icon = pygame.transform.scale(icon, (80, 80))
        return scaled_icon

    def run_program(self):
        """Runs the main loop of the Smart Mirror application
        """
        while True:
            self._check_events()
            self._draw_screen()
            self.clock.tick(30)

if __name__ == "__main__":
    smart_mirror = SmartMirror()
    smart_mirror.run_program()
