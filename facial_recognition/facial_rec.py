from .fr_files import initialize_models, picam2_init, FacialRecognition
import os


class FacialRecognitionHandler:

    def __init__(self):
        self.picam2 = picam2_init()
        self.face_detect_model, self.face_recog_model = initialize_models()
        self.facial_recognition = FacialRecognition(
                                    self.picam2, 
                                    self.face_detect_model, 
                                    self.face_recog_model
                                    )

    def run_recognition(self,):
        if not os.path.exists(self.facial_recognition.JSON_PATH):
            self.facial_recognition.learn_new_faces_hailo()
        try:
            face_names = self.facial_recognition.process_new_image_hailo()
        except Exception:
            return None
        face_names[:] = [x for x in face_names if x != 'unknown']

        if not face_names:
            return None
        return face_names

    def add_new_face(self):
        self.facial_recognition.capture_new_face('matt')
        self.facial_recognition.learn_new_faces_hailo()

if __name__ == "__main__":
    fr = FacialRecognitionHandler()
    fr.add_new_face()
