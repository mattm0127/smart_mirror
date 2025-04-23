import pygame
from facial_recognition import FacialRecognitionHandler
import threading
import time

pygame.init()

class SmartMirror:

    def __init__(self):
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.screen_rect = self.screen.get_rect()
        self.font = pygame.font.SysFont(None, size=48)
        self.facial_recogntion = FacialRecognitionHandler()
        self.in_frame = []
        self.in_frame_datalock = threading.Lock()
        self.scan_for_faces = True
        self._to_draw = []

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
                print(self.in_frame)
            time.sleep(1)

    def _in_frame_thread_handler(self):
        in_frame_thread = threading.Thread(
            target=self._update_in_frame,
            daemon=True
        )
        in_frame_thread.start()

    def _create_name_rect(self):
        with self.in_frame_datalock:
            in_frame_copy = self.in_frame[:]
        
        if not in_frame_copy:
            return None
        name_str = ''
        if len(in_frame_copy) == 1:
            name_str += in_frame_copy[0]
        else:
            for x in range(len(in_frame_copy)):
                if x == len(in_frame_copy) - 1:
                    name_str += in_frame_copy[x]
                else:
                    name_str += in_frame_copy[x] + ', '

        names = self.font.render(name_str, True, (255,255,255))
        names_rect = names.get_rect()
        names_rect.center = self.screen_rect.center
        self._to_draw.append((names, names_rect))

    def draw_screen(self):
        self.screen.fill((0,0,0))
        self._create_name_rect()
        self.screen.blits(blit_sequence=self._to_draw)
        pygame.display.flip()
        self._to_draw=[]

    def run_program(self):
        self._in_frame_thread_handler()
        while True:
            self.draw_screen()



if __name__ == '__main__':
    smart_mirror = SmartMirror()
    smart_mirror.run_program()