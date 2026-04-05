"""
Service layer cho Face ID — điều phối nhận diện khuôn mặt.

GUI gọi face_svc, KHÔNG gọi face_id module trực tiếp.
"""

import os
import logging
from app.core.config import DATASET_PATH, ENCODINGS_FILE, FACE_MODEL_TYPE
from app.face_id.face_encoder import FaceEncoder
from app.face_id.face_recognizer import FaceRecognitionSystem
from app.face_id.face_register import FaceRegistration
from app.repositories import member_repo

logger = logging.getLogger("FaceService")

# Singleton instances (khởi tạo khi cần)
_recognition_system = None
_registration_system = None


def _get_recognition_system():
    """Lấy hoặc khởi tạo FaceRecognitionSystem (singleton)."""
    global _recognition_system
    if _recognition_system is None:
        _recognition_system = FaceRecognitionSystem()
    return _recognition_system


def _get_registration_system():
    """Lấy hoặc khởi tạo FaceRegistration (singleton)."""
    global _registration_system
    if _registration_system is None:
        _registration_system = FaceRegistration()
    return _registration_system


def register_face(member_id, num_photos=5, camera_id=None):
    """Đăng ký khuôn mặt cho hội viên qua camera.

    Flow:
        1. Chụp ảnh qua camera
        2. Encode ảnh → embeddings
        3. Cập nhật file encodings
        4. Cập nhật trạng thái face_registered trong DB

    Returns: dict {"success": bool, "photos": int, "encodings": int}
    """
    reg = _get_registration_system()
    result = reg.register_member(member_id, num_photos, camera_id)

    if result["success"]:
        # Cập nhật face_registered = True trong database
        member = member_repo.get_by_id(member_id)
        if member:
            member.face_registered = True
            member.photo_path = os.path.join(DATASET_PATH, str(member_id))
            member_repo.update(member)
            logger.info(f"Đã cập nhật face_registered cho member {member_id}")

        # Reload encodings trong recognition system
        global _recognition_system
        if _recognition_system is not None:
            _recognition_system.reload_encodings()

    return result


def register_face_from_images(member_id, image_paths):
    """Đăng ký khuôn mặt từ ảnh có sẵn (không cần camera).

    Returns: dict {"success": bool, "photos": int, "encodings": int}
    """
    reg = _get_registration_system()
    result = reg.register_from_images(member_id, image_paths)

    if result["success"]:
        member = member_repo.get_by_id(member_id)
        if member:
            member.face_registered = True
            member.photo_path = os.path.join(DATASET_PATH, str(member_id))
            member_repo.update(member)

        global _recognition_system
        if _recognition_system is not None:
            _recognition_system.reload_encodings()

    return result


def recognize_frame(frame):
    """Nhận diện khuôn mặt trong 1 frame BGR.

    Returns: list[dict] — [{"name": str, "confidence": float, "bbox": tuple}, ...]
    """
    system = _get_recognition_system()
    return system.recognize_frame(frame)


def reload_encodings():
    """Tải lại encodings (sau khi đăng ký hội viên mới)."""
    global _recognition_system
    if _recognition_system is not None:
        _recognition_system.reload_encodings()


def remove_face(member_id):
    """Xóa encodings khuôn mặt của hội viên.

    Returns: bool — True nếu xóa thành công
    """
    reg = _get_registration_system()
    success = reg.remove_member(member_id)

    if success:
        member = member_repo.get_by_id(member_id)
        if member:
            member.face_registered = False
            member_repo.update(member)

        global _recognition_system
        if _recognition_system is not None:
            _recognition_system.reload_encodings()

    return success


def encode_all():
    """Encode lại toàn bộ dataset (rebuild encodings file).

    Dùng khi file encodings bị hỏng hoặc cần rebuild.
    """
    encoder = FaceEncoder(model_type=FACE_MODEL_TYPE)
    data = encoder.encode_all_members(DATASET_PATH)
    encoder.save_encodings(data, ENCODINGS_FILE)

    global _recognition_system
    if _recognition_system is not None:
        _recognition_system.reload_encodings()

    logger.info(f"Rebuild encodings: {len(data['encodings'])} từ {len(set(data['names']))} hội viên")
    return data


def get_registration_status(member_id):
    """Kiểm tra hội viên đã đăng ký khuôn mặt chưa.

    Returns: bool
    """
    member = member_repo.get_by_id(member_id)
    if member:
        return member.face_registered
    return False


def get_registered_count():
    """Đếm số hội viên đã đăng ký khuôn mặt.

    Returns: int
    """
    data = FaceEncoder.load_encodings(ENCODINGS_FILE)
    return len(set(data.get("names", [])))
