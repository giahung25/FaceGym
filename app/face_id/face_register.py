"""
Module đăng ký khuôn mặt hội viên.

Quy trình:
    1. Mở camera → chụp nhiều ảnh khuôn mặt
    2. Lưu ảnh vào data/dataset/{member_id}/
    3. Encode ảnh → embedding 128D
    4. Cập nhật file encodings pickle
"""

import os
import cv2
import time
import logging
import face_recognition

from app.core.config import (
    CAMERA_ID, FRAME_WIDTH, FRAME_HEIGHT,
    DATASET_PATH, ENCODINGS_FILE, FACE_MODEL_TYPE
)
from app.face_id.face_encoder import FaceEncoder
from app.face_id.image_processing import convert_bgr_to_rgb

logger = logging.getLogger("FaceRegister")


class FaceRegistration:
    """Hệ thống đăng ký khuôn mặt hội viên."""

    def __init__(self, model_type=None):
        self.model_type = model_type or FACE_MODEL_TYPE
        self.encoder = FaceEncoder(model_type=self.model_type)
        logger.info("FaceRegistration đã khởi tạo.")

    def capture_faces(self, member_id, num_photos=5, camera_id=None):
        """Mở camera và chụp ảnh khuôn mặt hội viên.

        Điều khiển: SPACE=Chụp | A=Auto | Q=Xong

        Args:
            member_id: ID hoặc tên hội viên (dùng làm tên folder)
            num_photos: Số ảnh tối thiểu cần chụp
            camera_id: ID camera

        Returns: list[str] — danh sách đường dẫn ảnh đã chụp
        """
        cam_id = camera_id if camera_id is not None else CAMERA_ID

        save_dir = os.path.join(DATASET_PATH, str(member_id))
        os.makedirs(save_dir, exist_ok=True)

        logger.info(f"Bắt đầu đăng ký khuôn mặt cho: {member_id}")

        cap = cv2.VideoCapture(cam_id)
        if not cap.isOpened():
            logger.error(f"Không thể mở camera {cam_id}!")
            return []

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        saved_paths = []
        photo_count = 0
        auto_capture = False
        auto_capture_interval = 1.5
        last_auto_capture_time = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                rgb_frame = convert_bgr_to_rgb(frame)
                face_locations = face_recognition.face_locations(rgb_frame, model=self.model_type)

                display_frame = frame.copy()

                # Vẽ bbox
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # HUD
                overlay = display_frame.copy()
                cv2.rectangle(overlay, (0, 0), (FRAME_WIDTH, 90), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, display_frame, 0.4, 0, display_frame)

                cv2.putText(display_frame, f"Dang ky: {member_id}",
                            (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(display_frame, f"Anh: {photo_count}/{num_photos}",
                            (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                status_color = (0, 255, 0) if face_locations else (0, 0, 255)
                cv2.putText(display_frame, f"Khuon mat: {len(face_locations)}",
                            (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)

                mode_text = "AUTO" if auto_capture else "MANUAL"
                mode_color = (0, 200, 0) if auto_capture else (200, 200, 200)
                cv2.putText(display_frame, f"Mode: {mode_text}",
                            (FRAME_WIDTH - 180, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)

                cv2.putText(display_frame, "SPACE=Chup | A=Auto | Q=Xong",
                            (10, FRAME_HEIGHT - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

                # Progress bar
                if num_photos > 0:
                    progress = min(photo_count / num_photos, 1.0)
                    bar_width = int((FRAME_WIDTH - 20) * progress)
                    bar_color = (0, 255, 0) if progress >= 1.0 else (0, 200, 255)
                    cv2.rectangle(display_frame, (10, FRAME_HEIGHT - 35),
                                  (10 + bar_width, FRAME_HEIGHT - 25), bar_color, -1)
                    cv2.rectangle(display_frame, (10, FRAME_HEIGHT - 35),
                                  (FRAME_WIDTH - 10, FRAME_HEIGHT - 25), (100, 100, 100), 1)

                # Auto-capture
                current_time = time.time()
                if (auto_capture and len(face_locations) == 1
                        and (current_time - last_auto_capture_time) >= auto_capture_interval):
                    path = self._save_face_photo(frame, face_locations[0], member_id, photo_count, save_dir)
                    if path:
                        saved_paths.append(path)
                        photo_count += 1
                        last_auto_capture_time = current_time

                cv2.imshow("Dang Ky Khuon Mat - Face Registration", display_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord(' '):
                    if face_locations:
                        path = self._save_face_photo(frame, face_locations[0], member_id, photo_count, save_dir)
                        if path:
                            saved_paths.append(path)
                            photo_count += 1
                elif key == ord('a'):
                    auto_capture = not auto_capture

        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()

        logger.info(f"Đã chụp tổng cộng {len(saved_paths)} ảnh cho {member_id}")
        return saved_paths

    def _save_face_photo(self, frame, face_location, member_id, photo_idx, save_dir):
        """Lưu ảnh khuôn mặt (crop với padding)."""
        top, right, bottom, left = face_location

        h, w = frame.shape[:2]
        pad_y = int((bottom - top) * 0.3)
        pad_x = int((right - left) * 0.3)
        crop_top = max(0, top - pad_y)
        crop_bottom = min(h, bottom + pad_y)
        crop_left = max(0, left - pad_x)
        crop_right = min(w, right + pad_x)

        face_crop = frame[crop_top:crop_bottom, crop_left:crop_right]
        if face_crop.size == 0:
            return None

        timestamp = int(time.time() * 1000)
        crop_filename = f"{member_id}_{photo_idx:03d}_{timestamp}.jpg"
        crop_path = os.path.join(save_dir, crop_filename)

        cv2.imwrite(crop_path, face_crop)
        logger.info(f"  Đã lưu: {crop_filename}")
        return crop_path

    def register_member(self, member_id, num_photos=5, camera_id=None):
        """Quy trình đăng ký hoàn chỉnh: chụp ảnh → encode → cập nhật encodings.

        Returns: dict {"success": bool, "photos": int, "encodings": int}
        """
        saved_photos = self.capture_faces(member_id, num_photos, camera_id)

        if not saved_photos:
            return {"success": False, "photos": 0, "encodings": 0}

        new_names = []
        new_encodings = []
        for photo_path in saved_photos:
            embedding = self.encoder.encode_face(photo_path)
            if embedding is not None:
                new_names.append(str(member_id))
                new_encodings.append(embedding)

        if not new_encodings:
            return {"success": False, "photos": len(saved_photos), "encodings": 0}

        existing = FaceEncoder.load_encodings(ENCODINGS_FILE)
        existing["names"].extend(new_names)
        existing["encodings"].extend(new_encodings)
        self.encoder.save_encodings(existing, ENCODINGS_FILE)

        return {
            "success": True,
            "photos": len(saved_photos),
            "encodings": len(new_encodings)
        }

    def register_from_images(self, member_id, image_paths):
        """Đăng ký từ ảnh có sẵn (không cần camera).

        Returns: dict {"success": bool, "photos": int, "encodings": int}
        """
        import shutil

        save_dir = os.path.join(DATASET_PATH, str(member_id))
        os.makedirs(save_dir, exist_ok=True)

        valid_paths = []
        for img_path in image_paths:
            if os.path.isfile(img_path):
                dest = os.path.join(save_dir, os.path.basename(img_path))
                if img_path != dest:
                    shutil.copy2(img_path, dest)
                valid_paths.append(dest)

        if not valid_paths:
            return {"success": False, "photos": 0, "encodings": 0}

        new_names = []
        new_encodings = []
        for photo_path in valid_paths:
            embedding = self.encoder.encode_face(photo_path)
            if embedding is not None:
                new_names.append(str(member_id))
                new_encodings.append(embedding)

        if not new_encodings:
            return {"success": False, "photos": len(valid_paths), "encodings": 0}

        existing = FaceEncoder.load_encodings(ENCODINGS_FILE)
        existing["names"].extend(new_names)
        existing["encodings"].extend(new_encodings)
        self.encoder.save_encodings(existing, ENCODINGS_FILE)

        return {
            "success": True,
            "photos": len(valid_paths),
            "encodings": len(new_encodings)
        }

    def remove_member(self, member_id):
        """Xóa encodings của hội viên (giữ ảnh)."""
        member_id_str = str(member_id)
        data = FaceEncoder.load_encodings(ENCODINGS_FILE)

        if member_id_str not in data.get("names", []):
            return False

        filtered_names = []
        filtered_encodings = []
        for name, enc in zip(data["names"], data["encodings"]):
            if name != member_id_str:
                filtered_names.append(name)
                filtered_encodings.append(enc)

        data["names"] = filtered_names
        data["encodings"] = filtered_encodings
        self.encoder.save_encodings(data, ENCODINGS_FILE)
        return True
