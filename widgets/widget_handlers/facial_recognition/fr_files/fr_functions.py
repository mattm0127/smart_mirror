import logging
import degirum as dg
from decouple import config
import numpy as np
from picamera2 import Picamera2
import time
import os

# --- Set Up Logging (Cleaner Way) --- Move this to its own file, import around facial recognition files
file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(file_dir)
logfile = os.path.join(parent_dir, "facial_rec.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File Handler
file_handler = logging.FileHandler(logfile, mode="a")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Log INFO and above to console
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# --- End Logging Setup ---


def _setup_model(type: str):
    face_det_model_name = "scrfd_2.5g--640x640_quant_hailort_hailo8l_1"
    face_rec_model_name = "arcface_mobilefacenet--112x112_quant_hailort_hailo8l_1"
    inference_host_addr = "@local"
    zoo_url = "degirum/models_hailort"
    token = config("DEGIRUM_API_KEY")

    if type == "detect":
        face_det_model = dg.load_model(
            model_name=face_det_model_name,
            inference_host_address=inference_host_addr,
            zoo_url=zoo_url,
            token=token,
        )
        return face_det_model

    if type == "recog":
        face_rec_model = dg.load_model(
            model_name=face_rec_model_name,
            inference_host_address=inference_host_addr,
            zoo_url=zoo_url,
            token=token,
        )
        return face_rec_model


def initialize_models():
    print("Initializing Detection Model")
    dummy_frame_detect = np.zeros((640, 640, 3), dtype=np.uint8)
    facial_detect_model = _setup_model("detect")
    try:
        _ = facial_detect_model(dummy_frame_detect)
        logger.info("Face Detection Model Initialized")
    except Exception as e:
        logger.warning(f"Face Detection model failure: {e}")

    print("Initializing Recognition Model")
    dummy_face_recog = np.zeros((112, 112, 3), dtype=np.uint8)
    facial_recog_model = _setup_model("recog")
    try:
        _ = facial_recog_model(dummy_face_recog)
        logger.info("Face Recognition Model Initialized")
    except Exception as e:
        logger.warning(f"Face Recognition model failure: {e}")
    return facial_detect_model, facial_recog_model


def picam2_init(width: int = 640, height: int = 640) -> Picamera2:
    picam2 = Picamera2()
    cap_config = picam2.create_still_configuration(main={"size": (width, height)})
    picam2.configure(cap_config)
    picam2.start()
    time.sleep(0.5)
    return picam2
