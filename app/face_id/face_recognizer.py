"""
Module nhận diện khuôn mặt real-time.

Chức năng:
    - FaceDetector: Phát hiện vị trí khuôn mặt trong frame.
    - FaceRecognitionSystem: Nhận diện khuôn mặt từ camera/frame.
"""

import logging
import numpy as np
import face_recognition

from app.core.config import (
    FACE_TOLERANCE, FACE_MODEL_TYPE, FRAME_RESIZE_SCALE, ENCODINGS_FILE
)
from app.face_id.face_encoder import FaceEncoder
from app.face_id.image_processing import resize_frame, convert_bgr_to_rgb

logger = logging.getLogger("FaceRecognizer")


class FaceDetector:
    """Phát hiện vị trí khuôn mặt trong ảnh/frame."""

    def __init__(self, model_type=None):
        self.model_type = model_type or FACE_MODEL_TYPE
        logger.info(f"FaceDetector khởi tạo với model: {self.model_type}")

    def detect(self, frame):
        """Tìm vị trí các khuôn mặt trong frame RGB.

        Returns: list[tuple] — (top, right, bottom, left)
        """
        return face_recognition.face_locations(frame, model=self.model_type)

    def detect_and_encode(self, frame):
        """Phát hiện + trích xuất encoding khuôn mặt.

        Returns: (face_locations, face_encodings)
        """
        face_locations = face_recognition.face_locations(frame, model=self.model_type)
        face_encodings = face_recognition.face_encodings(frame, known_face_locations=face_locations)
        return face_locations, face_encodings


class FaceRecognitionSystem:
    """Hệ thống nhận diện khuôn mặt.

    Có thể dùng để:
    - Nhận diện khuôn mặt trong 1 frame (recognize_frame)
    - Chạy vòng lặp camera real-time (run_camera_loop) — dùng cho CLI/debug
    """

    def __init__(self, encodings_file=None, tolerance=None, model_type=None):
        self.encodings_file = encodings_file or ENCODINGS_FILE
        self.tolerance = tolerance or FACE_TOLERANCE
        self.model_type = model_type or FACE_MODEL_TYPE

        self.detector = FaceDetector(model_type=self.model_type)

        self.known_names = []
        self.known_encodings = []
        self._load_known_encodings()

        logger.info(
            f"FaceRecognitionSystem sẵn sàng | "
            f"Tolerance: {self.tolerance} | "
            f"Hội viên đã đăng ký: {len(set(self.known_names))}"
        )

    def _load_known_encodings(self):
        """Load encodings từ file pickle."""
        data = FaceEncoder.load_encodings(self.encodings_file)
        self.known_names = data.get("names", [])
        self.known_encodings = data.get("encodings", [])

        if not self.known_encodings:
            logger.warning("Chưa có encoding nào được load! Hãy chạy encode dataset trước.")

    def reload_encodings(self):
        """Tải lại encodings (khi có hội viên mới đăng ký)."""
        self._load_known_encodings()
        logger.info("Đã reload encodings thành công.")

    def recognize_frame(self, frame):
        """Nhận diện tất cả khuôn mặt trong 1 frame BGR.

        Returns: list[dict] — mỗi dict gồm:
            {"name": str, "confidence": float, "bbox": tuple(top,right,bottom,left)}
        """
        results = []

        small_frame = resize_frame(frame, scale=FRAME_RESIZE_SCALE)
        rgb_frame = convert_bgr_to_rgb(small_frame)

        face_locations, face_encodings = self.detector.detect_and_encode(rgb_frame)

        for (face_loc, face_enc) in zip(face_locations, face_encodings):
            name = "Unknown"
            confidence = 0.0

            if self.known_encodings:
                distances = face_recognition.face_distance(self.known_encodings, face_enc)
                best_idx = np.argmin(distances)
                best_distance = distances[best_idx]

                if best_distance <= self.tolerance:
                    name = self.known_names[best_idx]
                    confidence = 1.0 - best_distance

            # Scale bbox về kích thước gốc
            scale = 1.0 / FRAME_RESIZE_SCALE
            top, right, bottom, left = face_loc
            bbox = (
                int(top * scale),
                int(right * scale),
                int(bottom * scale),
                int(left * scale)
            )

            results.append({
                "name": name,
                "confidence": confidence,
                "bbox": bbox
            })

        return results
