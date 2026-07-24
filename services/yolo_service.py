import os
import time
import uuid
import gc
import cv2
import torch

from ultralytics import YOLO

import config


class YOLOService:

    def __init__(self):
        self.model = None

    # =====================================================
    # Lazy Model Loader
    # =====================================================

    def get_model(self):

        if self.model is None:

            print("=" * 60)
            print("Loading YOLO model...")
            print("=" * 60)

            self.model = YOLO(config.MODEL_PATH)

            print("Model loaded successfully.")
            print("=" * 60)

        return self.model

    # =====================================================
    # Helper Functions
    # =====================================================

    @staticmethod
    def _unique_filename(extension):
        return f"{uuid.uuid4().hex}.{extension}"

    @staticmethod
    def _confidence_stats(detections):

        if not detections:
            return {
                "highest": 0,
                "lowest": 0,
                "average": 0
            }

        values = [d["confidence"] for d in detections]

        return {
            "highest": round(max(values), 2),
            "lowest": round(min(values), 2),
            "average": round(sum(values) / len(values), 2)
        }

    # =====================================================
    # IMAGE DETECTION
    # =====================================================

    def detect_image(self, image_path):

        model = self.get_model()

        start = time.time()

        results = model.predict(
            source=image_path,
            conf=config.CONFIDENCE,
            verbose=False
        )

        inference = round(
            (time.time() - start) * 1000,
            2
        )

        result = results[0]

        annotated = result.plot()

        output_name = self._unique_filename("jpg")

        output_path = os.path.join(
            config.OUTPUT_FOLDER,
            output_name
        )

        cv2.imwrite(output_path, annotated)

        detections = []

        for box in result.boxes:

            cls = int(box.cls[0])

            confidence = round(
                float(box.conf[0]) * 100,
                2
            )

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({

                "class": model.names[cls],

                "confidence": confidence,

                "bbox": [
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2)
                ]

            })

        stats = self._confidence_stats(detections)

        image = cv2.imread(image_path)

        height, width = image.shape[:2]

        return {

            "success": True,

            "original": os.path.basename(image_path),

            "output_image": output_name,

            "detections": detections,

            "total": len(detections),

            "highest": stats["highest"],

            "lowest": stats["lowest"],

            "avg_conf": stats["average"],

            "width": width,

            "height": height,

            "inference": inference

        }
        # =====================================================
    # VIDEO DETECTION
    # =====================================================

    # =====================================================
    # VIDEO DETECTION
    # =====================================================

    def detect_video(self, video_path):

        model = self.get_model()

        output_name = self._unique_filename("mp4")

        output_path = os.path.join(
            config.OUTPUT_FOLDER,
            output_name
        )

        start = time.time()

        highest_confidence = 0
        confidence_sum = 0
        confidence_count = 0
        total_detections = 0
        processed_frames = 0

        with torch.inference_mode():

            results = model.predict(
                source=video_path,
                conf=config.CONFIDENCE,
                stream=True,
                save=True,
                project=config.OUTPUT_FOLDER,
                name=os.path.splitext(output_name)[0],
                exist_ok=True,
                verbose=False,
                imgsz=640
            )

            for result in results:

                processed_frames += 1

                for box in result.boxes:

                    conf = round(float(box.conf[0]) * 100, 2)

                    total_detections += 1
                    confidence_sum += conf
                    confidence_count += 1

                    if conf > highest_confidence:
                        highest_confidence = conf

                del result

                if processed_frames % 10 == 0:
                    gc.collect()

        processing_time = round(
            time.time() - start,
            2
        )

        average_confidence = 0

        if confidence_count:
            average_confidence = round(
                confidence_sum / confidence_count,
                2
            )

        generated_folder = os.path.join(
            config.OUTPUT_FOLDER,
            os.path.splitext(output_name)[0]
        )

        generated_video = None

        for file in os.listdir(generated_folder):
            if file.endswith(".mp4"):
                generated_video = file
                os.rename(
                    os.path.join(generated_folder, file),
                    output_path
                )
                break

        return {

            "success": True,

            "original": os.path.basename(video_path),

            "output_video": output_name,

            "frames": processed_frames,

            "detections": total_detections,

            "highest_confidence": highest_confidence,

            "average_confidence": average_confidence,

            "processing_time": processing_time

        }
        # =====================================================
    # LIVE CAMERA STREAM
    # =====================================================

    def stream_camera(self):

        model = self.get_model()

        camera = cv2.VideoCapture(0, cv2.CAP_ANY)

        if not camera.isOpened():
            raise RuntimeError("Unable to access webcam.")

        try:

            while True:

                success, frame = camera.read()

                if not success:
                    break

                results = model.predict(
                    source=frame,
                    conf=config.CONFIDENCE,
                    verbose=False
                )

                annotated = results[0].plot()

                success, buffer = cv2.imencode(".jpg", annotated)

                if not success:
                    continue

                frame_bytes = buffer.tobytes()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes
                    + b"\r\n"
                )

        finally:

            camera.release()
            cv2.destroyAllWindows()


# =====================================================
# Singleton Service Instance
# =====================================================

yolo_service = YOLOService()