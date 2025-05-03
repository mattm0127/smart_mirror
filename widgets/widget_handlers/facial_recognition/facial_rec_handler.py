from .fr_files import initialize_models, picam2_init, FacialRecognition
import os
import threading
import time


class FacialRecognitionHandler:

    def __init__(self):
        """Class to handle Facial Recognition Widget
        """
        self.picam2 = picam2_init()
        self.face_detect_model, self.face_recog_model = initialize_models()
        self.facial_recognition = FacialRecognition(self.picam2)
        self.in_frame = []
        self.in_frame_datalock = threading.Lock()
        self.stop_event = threading.Event()

    def _run_recognition(self, detect_model, recog_model):
        """Run facial detection and recognition on a frame

        Returns:
            [str, ]: List of names detected
        """
        if not os.path.exists(self.facial_recognition._JSON_PATH):
            self.facial_recognition.learn_new_faces_hailo(
                detect_model=detect_model, recog_model=recog_model
                )
        try:
            named_faces = self.facial_recognition.process_new_image_hailo(
                detect_model=detect_model, recog_model=recog_model
            )
            named_faces[:] = [x for x in named_faces if x != 'unknown']

            if not named_faces:
                return None
            return named_faces
        except Exception: 
            return None
        
    def _process_named_faces(self, named_faces):
        """Processes a list of names from recognition to update faces in frame
        and remove unknown entries

        Args:
            named_faces ([str,]): List of detected names from facial recognition

        Returns:
            [str, ]: List of names within frame
        """
        with self.in_frame_datalock:
            in_frame_copy = self.in_frame[:]
        if named_faces is None:
            in_frame_copy = []
        elif len(in_frame_copy) == 0:
            in_frame_copy = named_faces
        else:
            names_to_remove = []
            for face in in_frame_copy:
                if face not in named_faces:
                    names_to_remove.append(face)
            for remove_name in names_to_remove:
                in_frame_copy.remove(remove_name)
        return in_frame_copy

    def _update_in_frame(self):
        """Update names of recognized faces in frame
        """
        while not self.stop_event.is_set():
            named_faces = self._run_recognition(
                detect_model=self.face_detect_model, recog_model=self.face_recog_model
            )
            in_frame_copy = self._process_named_faces(named_faces)
            with self.in_frame_datalock:
                self.in_frame = in_frame_copy[:]
            time.sleep(1)

    def start_in_frame_thread(self):
        """Starts the thread that handles updated faces in frame
        """
        in_frame_thread = threading.Thread(target=self._update_in_frame, daemon=True)
        in_frame_thread.start()
        return in_frame_thread

    def add_new_face(self, name):
        self.facial_recognition.capture_new_face(name)
        self.facial_recognition.learn_new_faces_hailo()


if __name__ == "__main__":
    fr = FacialRecognitionHandler()
    fr.add_new_face()
