import pygame
from widgets import Widgets
import gc
import flask_app
from decouple import config
import requests
import sys
import signal


running = True

class SmartMirror:

    pygame.init()
    pygame.font.init()

    def __init__(self):
        """Class to run main Smart Mirror logic
        """
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        flask_app.start_flask_thread()
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.widgets = Widgets(self)
        self._shutdown_called = False

    def _check_events(self):
        None

    def _draw_screen(self):
        """Takes widgets from _to_draw and blits them screen
        """
        self.screen.fill((0, 0, 0))
        self.widgets.create_and_place()
        self.screen.blits(blit_sequence=self.widgets.screen_objects())
        pygame.display.flip()

    def _shutdown(self):
        if self._shutdown_called:
            print("Shutdown already initiated, skipping...")
            return
        self._shutdown_called = True
        print("Initiating shutdown sequence...")

        print("Shutting down Flask server...")
        try:
            requests.get(f"http://{config('FLASK_IP')}:{config('FLASK_PORT')}/shutdown", timeout=5)
            print("Flask server shutdown initiated.")
        except requests.exceptions.RequestException as e:
            print(f"Error shutting down Flask server: {e}")
            # Potentially try a more forceful shutdown if necessary

        self.widgets.facial_rec_handler.stop_event.set()
        if hasattr(self.widgets, 'facial_rec_thread') and self.widgets.facial_rec_thread.is_alive():
            print("Waiting for facial recognition thread to finish...")
            self.widgets.facial_rec_thread.join()  # Add a timeout to prevent indefinite blocking
        print("Facial Recognition Thread Terminated.")

        print("Releasing camera resources...")
        try:
            self.widgets.facial_rec_handler.picam2.close()
            print("Camera resources released.")
        except Exception as e:
            print(f"Error closing Picamera2: {e}")

        print('Closing Pygame')
        pygame.quit()
        print('Clearing resources')
        gc.collect()
        print("Shutdown complete.")
        sys.exit(0)

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
        if size:
            icon = pygame.transform.scale(icon, (size, size))
        return icon

    def run_program(self):
        """Runs the main loop of the Smart Mirror application
        """
        while running:
            self._check_events()
            self._draw_screen()
            self.clock.tick(30)  



def signal_handler(sig, frame):
    global running
    print("Caught CTRL+C, shutting down")
    running = False

    
if __name__ == "__main__":
    #signal.signal(signal.SIGINT, signal_handler)
    smart_mirror = SmartMirror()
    smart_mirror.run_program()
