import os
import time
import uuid
import cv2

from ultralytics import YOLO

import config


class YOLOService:

    def __init__(self):

        print("=" * 60)
        print("Loading YOLO model...")
        print("=" * 60)

        self.model = YOLO(config.MODEL_PATH)

        print("Model loaded successfully.")
        print("=" * 60)

    # =====================================================
    # Helper Functions
    # =====================================================

    @staticmethod
    def _unique_filename(extension):

        return f"{uuid.uuid4().hex}.{extension}"

    @staticmethod
    def _confidence_stats(detections):

        if len(detections) == 0:

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

        start = time.time()

        results = self.model.predict(

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

            x1, y1, x2, y2 = (

                box.xyxy[0].tolist()

            )

            detections.append({

                "class": self.model.names[cls],

                "confidence": confidence,

                "bbox": [

                    int(x1),

                    int(y1),

                    int(x2),

                    int(y2)

                ]

            })

        stats = self._confidence_stats(

            detections

        )

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

    def detect_video(self, video_path):

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():

            return {

                "success": False,

                "message": "Unable to open video."

            }

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fps = cap.get(cv2.CAP_PROP_FPS)

        if fps <= 0:

            fps = 30

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        output_name = self._unique_filename("mp4")

        output_path = os.path.join(

            config.OUTPUT_FOLDER,

            output_name

        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        writer = cv2.VideoWriter(

            output_path,

            fourcc,

            fps,

            (width, height)

        )

        start = time.time()

        total_detections = 0

        processed_frames = 0

        highest_confidence = 0

        confidence_sum = 0

        confidence_count = 0

        while True:

            success, frame = cap.read()

            if not success:

                break

            results = self.model.predict(

                source=frame,

                conf=config.CONFIDENCE,

                verbose=False

            )

            result = results[0]

            annotated = result.plot()

            writer.write(annotated)

            processed_frames += 1

            for box in result.boxes:

                confidence = round(

                    float(box.conf[0]) * 100,

                    2

                )

                total_detections += 1

                confidence_sum += confidence

                confidence_count += 1

                if confidence > highest_confidence:

                    highest_confidence = confidence

        cap.release()

        writer.release()

        processing_time = round(

            time.time() - start,

            2

        )

        average_confidence = 0

        if confidence_count > 0:

            average_confidence = round(

                confidence_sum / confidence_count,

                2

            )

        return {
    "success": True,
    "original": os.path.basename(video_path),
    "output_video": output_name,
    "frames": processed_frames,
    "detections": total_detections,
    "processing_time": processing_time
}

        
    # =====================================================
    # LIVE CAMERA STREAM
    # =====================================================

    def stream_camera(self):

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            raise RuntimeError("Unable to access webcam.")

        try:

            while True:

                success, frame = camera.read()

                if not success:
                    break

                results = self.model.predict(

                    source=frame,

                    conf=config.CONFIDENCE,

                    verbose=False

                )

                annotated = results[0].plot()

                _, buffer = cv2.imencode(".jpg", annotated)

                frame_bytes = buffer.tobytes()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes +
                    b"\r\n"
                )

        finally:

            camera.release()

            cv2.destroyAllWindows()


# =====================================================
# Singleton Service Instance
# =====================================================

yolo_service = YOLOService()