from ultralytics import YOLO
from config import MODEL_PATH

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO loaded successfully.")