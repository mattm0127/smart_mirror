import pygame
from widgets import Widgets
import gc

class SmartMirror:

    pygame.init()
    pygame.font.init()

    def __init__(self):
        """Class to run main Smart Mirror logic
        """
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.widgets = Widgets(self)


    def _check_events(self):
        None

    def _draw_screen(self):
        """Takes widgets from _to_draw and blits them screen
        """
        self.screen.fill((0, 0, 0))
        self.widgets.create_and_place()
        self.screen.blits(blit_sequence=self.widgets.screen_obejcts())
        pygame.display.flip()

    def import_font(self, font_path, font_size):
        return pygame.font.Font(font_path, font_size)

    def import_image(self, icon_path, size=80):
        """Takes image path from Widgets and imports into pygame

        Args:
            icon_path (Path): Path() to the current icon.png file

        Returns:
            Surface: Pygame surface of the icon
        """
        icon = pygame.image.load(icon_path)
        scaled_icon = pygame.transform.scale(icon, (size, size))
        return scaled_icon

    def run_program(self):
        """Runs the main loop of the Smart Mirror application
        """
        try:
            while True:
                self._check_events()
                self._draw_screen()
                self.clock.tick(30)
        finally:
            print('Closing Pygame')
            pygame.quit()
            print('Clearing resources')
            self.widgets.facial_rec_handler.picam2.close()
            gc.collect()

if __name__ == "__main__":
    smart_mirror = SmartMirror()
    smart_mirror.run_program()
