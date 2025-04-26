import face_recognition
import numpy as np
import os
import time
from .fr_functions import (
    logger,
    crop_face,
    euclidean_distance,
    get_json_file,
    convert_and_save_json,
)


class FacialRecognition:
    file_dir = os.path.dirname(os.path.abspath(__file__))
    JSON_PATH = file_dir + "/known_faces.json"
    FACE_PIC_DIR = file_dir + "/known_faces"

    def __init__(self, picam2, facial_detect_model, facial_recog_model):
        """Class to handle all Facial Recognition logic

        Args:
            picam2 (Picam2): Picam2 object for image capture
            facial_detect_model (degirum.Model): Facial detection model for Hailo 8l
            facial_recog_model (degirum.Model): Facial recognition model for Hailo 8l
        """
        self.picam2 = picam2
        self.facial_detect_model = facial_detect_model
        self.facial_recog_model = facial_recog_model

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
        new_person_folder = os.path.join(self.FACE_PIC_DIR, person_name)

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

    def learn_new_faces_cpu(self):
        """Train model to learn new faces using FaceRecognition module on CPU
        """
        known_encodings = []
        known_names = []
        logger.info("Creating known face encodings")

        if not os.listdir(self.FACE_PIC_DIR):
            print("No faces saved, your first.")
            name = input("What is your name: ")
            self.capture_new_face(name)

        for person_name in os.listdir(self.FACE_PIC_DIR):
            person_dir = os.path.join(self.FACE_PIC_DIR, person_name)
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

        convert_and_save_json(known_encodings, known_names)

    def learn_new_faces_hailo(self):
        """Train model to learn new faces using custom model on Hailo 8l
        """
        known_encodings = []
        known_names = []
        logger.info("Creating known face encodings")
        try:
            os.listdir(self.FACE_PIC_DIR)
        except Exception:
            os.mkdir(self.FACE_PIC_DIR)

        if not os.listdir(self.FACE_PIC_DIR):
            print("No faces saved, your first.")
            name = input("What is your name: ")
            self.capture_new_face(name)

        for person_name in os.listdir(self.FACE_PIC_DIR):
            person_dir = os.path.join(self.FACE_PIC_DIR, person_name)
            for filename in os.listdir(person_dir):
                if filename.endswith(".jpg"):
                    img_path = os.path.join(person_dir, filename)
                    try:
                        detected_faces = self.facial_detect_model(img_path)
                        for detected_face in detected_faces.results:
                            cropped_face = crop_face(detected_face, detected_faces)
                            encodings = self.facial_recog_model(cropped_face).results[
                                0
                            ]["data"][0]
                        if encodings:
                            known_encodings.append(
                                np.array(encodings)
                            )  # Assuming only one face in learning image
                            known_names.append(person_name)
                    except Exception as e:
                        logger.error(f"Failed to encode {person_name}, {img_path}: {e}")
        convert_and_save_json(known_encodings, known_names)

    def process_new_image_cpu(self):
        """Perform Facial Detection and Recognition on new frame using
        FaceRecognition model on CPU

        Returns:
            [str,]: List of names associated with faces from frame
        """
        known_encodings, known_names = get_json_file()
        logger.info("Taking Image to Process.")
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

    def process_new_image_hailo(self):
        """Perform Facial Detection and Recognition on new frame using
        custom model on Hailo 8l

        Returns:
            [str,]: List of names associated with faces from frame
        """
        known_encodings, known_names = get_json_file()
        logger.info("Taking Image to Process.")
        frame = self.picam2.capture_array()
        try:
            detected_faces = self.facial_detect_model(frame)
        except Exception as e:
            print(e)
        cropped_faces = [
            crop_face(detected_face, detected_faces)
            for detected_face in detected_faces.results
        ]
        face_encoding = []
        for face in cropped_faces:
            face_encoding.append(
                np.array(self.facial_recog_model(face).results[0]["data"][0])
            )
        face_names = []
        for face in face_encoding:
            distances = [
                euclidean_distance(known_face, face) for known_face in known_encodings
            ]
            best_dist_id = np.argmin(distances)
            if distances[best_dist_id] < 6.0:
                name = known_names[best_dist_id]
            else:
                name = "unknown"
            face_names.append(name)
        return face_names


if __name__ == "__main__":
    None
