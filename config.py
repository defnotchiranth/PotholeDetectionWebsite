import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

OUTPUT_FOLDER = os.path.join(BASE_DIR, "static", "outputs")