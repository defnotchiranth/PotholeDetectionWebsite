import os

# ==========================================================
# Base Directory
# ==========================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ==========================================================
# Flask
# ==========================================================

SECRET_KEY = "replace_this_with_a_long_random_secret_key"

MAX_CONTENT_LENGTH = 300 * 1024 * 1024      # 300 MB

# ==========================================================
# Folder Paths
# ==========================================================

STATIC_FOLDER = os.path.join(BASE_DIR, "static")

UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, "uploads")

OUTPUT_FOLDER = os.path.join(STATIC_FOLDER, "outputs")

IMAGE_FOLDER = os.path.join(STATIC_FOLDER, "images")

MODEL_FOLDER = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODEL_FOLDER, "best.pt")

# ==========================================================
# Allowed Extensions
# ==========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "bmp",
    "webp"
}

ALLOWED_VIDEO_EXTENSIONS = {
    "mp4",
    "avi",
    "mov",
    "mkv"
}

# ==========================================================
# YOLO Settings
# ==========================================================

CONFIDENCE = 0.35

LINE_WIDTH = 2

# ==========================================================
# Create Required Folders
# ==========================================================

REQUIRED_FOLDERS = [

    STATIC_FOLDER,

    IMAGE_FOLDER,

    UPLOAD_FOLDER,

    OUTPUT_FOLDER,

    MODEL_FOLDER

]

for folder in REQUIRED_FOLDERS:

    os.makedirs(folder, exist_ok=True)