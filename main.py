import pygame
from facial_recognition import FacialRecognitionHandler
import threading
import time

class SmartMirror:

    def __init__(self):
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.facial_recogntion = FacialRecognitionHandler()
        self.in_frame = []
        self.in_frame_datalock = threading.Lock()
        self.scan_for_faces = True
    
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

    def in_frame_thread_handler(self):
        in_frame_thread = threading.Thread(
            target=self._update_in_frame,
            daemon=True
        )
        in_frame_thread.start()

    def run_program(self):
        while True:
            print(self.in_frame)
            time.sleep(1)

if __name__ == '__main__':
    smart_mirror = SmartMirror()
    smart_mirror.in_frame_thread_handler()
    smart_mirror.run_program()