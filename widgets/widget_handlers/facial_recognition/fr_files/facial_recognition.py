import face_recognition
import numpy as np
import os
import time
import concurrent.futures
import cv2
import json
from .fr_functions import logger


class FacialRecognition:

    _FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    _JSON_PATH = _FILE_DIR + "/known_faces.json"
    _FACE_PIC_DIR = _FILE_DIR + "/known_faces"

    def __init__(self, picam2):
        """Class to handle all Facial Recognition logic

        Args:
            picam2 (Picam2): Picam2 object for image capture
            facial_detect_model (degirum.Model): Facial detection model for Hailo 8l
            facial_recog_model (degirum.Model): Facial recognition model for Hailo 8l
        """
        self.picam2 = picam2

    def _safe_infer(self, model, *args, timeout=3):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(model, *args)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                print("[Facial_Recognition] Timed Out")
            except Exception as e:
                print(f"[FacialRecognition] Inference Failed: {e}")

    # -- Capture an Save new face to json -- #
    def _capture_and_save(self, person_name, img_num, person_folder):
        """Capture and save new images of face for model training

        Args:
            person_name (str): Name of person to add to known_faces
            img_num (int): Number of images to be taken and saved
            person_folder (Path): Path to new face image folder
        """
        img_name = f"{person_name}_scan{img_num}.jpg"
        img_path = os.path.join(person_folder, img_name)
        write_success = self.picam2.capture_file(img_path)
        if write_success:
            logger.info(f"Image {img_num + 1} successfully saved to {person_name}")
        else:
            logger.error(f"Error saving image {img_num + 1}")

    def capture_new_face(self, person_name, num_imgs=5):
        """Main function for capturing new face.

        Args:
            person_name (str): Name of person to add to known_faces
            num_imgs (int, optional): Number of images to take. Defaults to 5.
        """
        new_person_folder = os.path.join(self._FACE_PIC_DIR, person_name)

        try:
            os.makedirs(new_person_folder, exist_ok=True)
            logger.info(f"{new_person_folder} Created/Exists")
        except OSError as e:
            logger.error(f"{new_person_folder} Failed to Create: {e}")
        print("Move your face for each picture..")
        for x in range(num_imgs):
            print(f"Taking Picutre {x + 1} in...")
            print("3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            time.sleep(1)
            self._capture_and_save(
                person_name=person_name, img_num=x, person_folder=new_person_folder
            )

    # -- Facial Recognition Process Functions-- #
    def _cropped_faces(self, detected_faces):
        try:
            cropped_faces = []
            for detected_face in detected_faces.results:
                x1, y1, x2, y2 = map(int, detected_face["bbox"])
                cropped_face = detected_faces.image[y1:y2, x1:x2]
                cropped_face_scaled = cv2.resize(cropped_face, (112, 112))
                cropped_faces.append(cropped_face_scaled)
            return cropped_faces
        except Exception as e:
            logger.error(f"Failed cropping faces: {e}")
            return

    def _encode_faces(self, cropped_faces, recog_model):
        try:
            face_encodings = []
            for face in cropped_faces:
                encoding = self._safe_infer(recog_model, face)
                if encoding:
                    encoding_array = np.array(encoding.results[0]['data'][0])
                    face_encodings.append(encoding_array)
            return face_encodings
        except Exception as e:
            logger.error(f"Failed to encode faces: {e}")
            return 

    def _convert_faces_to_names(self, face_encodings, known_encodings, known_names):

        def _euclidean_distance(encoding1, encoding2):
            """Calculates the Euclidean distance between two encodings."""
            return np.sqrt(np.sum((np.array(encoding1) - np.array(encoding2)) ** 2))
        
        try:
            named_faces = []
            for encoding in face_encodings:
                distances = [
                    _euclidean_distance(known_encoding, encoding) for known_encoding in known_encodings
                    ]
                best_dist_id = np.argmin(distances)
                if distances[best_dist_id] < 6.0:
                    named_faces.append(known_names[best_dist_id])
                else:
                    named_faces.append('unknown')
            return named_faces
        except Exception as e:
            logger.error(f"Failed to convert faces to names: {e}")

    def _convert_and_save_json(self, known_encodings, known_names): # Needs Error Correction
        file_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info("Converting encodings to json")
        json_encodings = []
        for encoding in known_encodings:
            json_encodings.append(list(encoding))
        json_dict = {"known_encodings": json_encodings, "known_names": known_names}
        json_file = os.path.join(file_dir, "known_faces.json")
        with open(json_file, "w") as enc_file:
            json.dump(json_dict, enc_file, indent=4)

        logger.info("New entry saved.")
    
    def _get_json_file(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(file_dir, "known_faces.json")
        with open(json_path, "r") as json_data:
            known_data = json.load(json_data)
        known_encodings = [np.array(encoding) for encoding in known_data["known_encodings"]]
        known_names = known_data["known_names"]
        return known_encodings, known_names

    # -- Facial Recognition End-Points -- #
    def learn_new_faces_hailo(self, detect_model, recog_model):
        """Train model to learn new faces using custom model on Hailo 8l
        """
        known_encodings = []
        known_names = []
        logger.info("Creating known face encodings")
        try:
            os.makedirs(self._FILE_DIR, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to Create: {e}")
            
        if not os.listdir(self._FACE_PIC_DIR):
            print("No faces saved, your first.")
            name = input("What is your name: ")
            self.capture_new_face(name)
        try:
            for person_name in os.listdir(self._FACE_PIC_DIR):
                person_dir = os.path.join(self._FACE_PIC_DIR, person_name)
                for filename in os.listdir(person_dir):
                    if filename.endswith(".jpg"):
                        img_path = os.path.join(person_dir, filename)
                        try:
                            detected_faces = self._safe_infer(detect_model, img_path)
                            cropped_faces = self._cropped_faces(detected_faces)
                            encoding_results = self._encode_faces(cropped_faces, recog_model)
                            known_encodings.append(
                                encoding_results[0]
                            )  # Assuming only one face in learning image
                            known_names.append(person_name)
                        except Exception as e:
                            logger.error(f"Failed to encode {person_name}, {img_path}: {e}")
            self._convert_and_save_json(known_encodings, known_names)
        except Exception as e:
            print(f"{e}")

    def process_new_image_hailo(self, detect_model, recog_model):
        """Perform Facial Detection and Recognition on new frame using
        custom model on Hailo 8l

        Returns:
            [str,]: List of names associated with faces from frame
        """
        known_encodings, known_names = self._get_json_file()
        frame = self.picam2.capture_array()
        try:
            detected_faces = self._safe_infer(detect_model, frame)
            cropped_faces = self._cropped_faces(detected_faces)
            face_encodings = self._encode_faces(cropped_faces, recog_model)
            named_faces = self._convert_faces_to_names(
                face_encodings, known_encodings, known_names)
            return named_faces
        except Exception as e:
            print(f"Failed to process new image: {e}")


    # -- Functions for Non-Hailo Based Facial Recognition -- #
    def learn_new_faces_cpu(self):
        """Train model to learn new faces using FaceRecognition module on CPU
        """
        known_encodings = []
        known_names = []
        logger.info("Creating known face encodings")

        if not os.listdir(self._FACE_PIC_DIR):
            print("No faces saved, your first.")
            name = input("What is your name: ")
            self.capture_new_face(name)

        for person_name in os.listdir(self._FACE_PIC_DIR):
            person_dir = os.path.join(self._FACE_PIC_DIR, person_name)
            for filename in os.listdir(person_dir):
                if filename.endswith(".jpg"):
                    img_path = os.path.join(person_dir, filename)
                    try:
                        image = face_recognition.load_image_file(img_path)
                        encodings = face_recognition.face_encodings(image)
                        if encodings:
                            known_encodings.append(
                                encodings[0]
                            )  # Assuming only one face in learning image
                            known_names.append(person_name)
                    except Exception as e:
                        logger.error(f"Failed to encode {person_name}, {img_path}: {e}")

        self._convert_and_save_json(known_encodings, known_names)

    def process_new_image_cpu(self):
        """Perform Facial Detection and Recognition on new frame using
        FaceRecognition model on CPU

        Returns:
            [str,]: List of names associated with faces from frame
        """
        known_encodings, known_names = self._get_json_file()
        frame = self.picam2.capture_array()
        face_encoding = face_recognition.face_encodings(frame)
        face_names = []
        for face in face_encoding:
            matches = face_recognition.compare_faces(
                known_encodings, face, tolerance=0.6
            )
            name = "unknown"
            face_distances = face_recognition.face_distance(known_encodings, face)
            best_dist_id = np.argmin(face_distances)
            if matches[best_dist_id]:
                name = known_names[best_dist_id]
            face_names.append(name)
        return face_names

if __name__ == "__main__":
    None
