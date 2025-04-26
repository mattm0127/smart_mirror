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
        self.facial_recognition = FacialRecognition(
                                    self.picam2, 
                                    self.face_detect_model, 
                                    self.face_recog_model
                                    )
        self.in_frame = []
        self.in_frame_datalock = threading.Lock()
        self.scan_for_faces = True


    def _run_recognition(self):
        """Run facial detection and recognition on a frame

        Returns:
            [str, ]: List of names detected
        """
        if not os.path.exists(self.facial_recognition._JSON_PATH):
            self.facial_recognition.learn_new_faces_hailo()
        try:
            face_names = self.facial_recognition.process_new_image_hailo()
        except Exception:
            return None
        face_names[:] = [x for x in face_names if x != 'unknown']

        if not face_names:
            return None
        return face_names
    
    def _process_face_names(self, face_names):
        """Processes a list of names from recognition to update faces in frame
        and remove unknown entries

        Args:
            face_names ([str,]): List of detected names from facial recognition

        Returns:
            [str, ]: List of names within frame
        """
        with self.in_frame_datalock:
            in_frame_copy = self.in_frame[:]
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
        return in_frame_copy

    def _update_in_frame(self):
        """Update names of recognized faces in frame
        """
        while self.scan_for_faces:
            face_names = self._run_recognition()
            in_frame_copy = self._process_face_names(face_names)
            with self.in_frame_datalock:
                self.in_frame = in_frame_copy[:]
            time.sleep(1)

    def start_in_frame_thread(self):
        """Starts the thread that handles updated faces in frame
        """
        in_frame_thread = threading.Thread(target=self._update_in_frame, daemon=True)
        in_frame_thread.start()

    def add_new_face(self):
        self.facial_recognition.capture_new_face('matt')
        self.facial_recognition.learn_new_faces_hailo()


if __name__ == "__main__":
    fr = FacialRecognitionHandler()
    fr.add_new_face()
