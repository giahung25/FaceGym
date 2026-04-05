# ============================================================================
# FILE: app/services/trainer_svc.py
# MỤC ĐÍCH: Tầng SERVICE cho HLV — chứa logic nghiệp vụ.
#
# KIẾN TRÚC: GUI → Service → Repository → Database
# ============================================================================

import re
from app.models.trainer import Trainer
from app.repositories import trainer_repo


def _validate(name: str, phone: str, email: str = None):
    """Kiểm tra dữ liệu HLV trước khi lưu."""
    if not name or not name.strip():
        raise ValueError("Tên HLV không được để trống")

    if not phone or not phone.strip():
        raise ValueError("Số điện thoại không được để trống")

    if not re.fullmatch(r"[0-9+\-\s]{7,15}", phone.strip()):
        raise ValueError("Số điện thoại không hợp lệ")

    if email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email.strip()):
        raise ValueError("Email không hợp lệ")


def register_trainer(name: str, phone: str, email: str = None,
                     specialization: str = None) -> Trainer:
    """Đăng ký HLV mới.

    Tham số:
        name: Họ tên HLV
        phone: SĐT (dùng để đăng nhập user app)
        email: Email
        specialization: Chuyên môn (VD: "Yoga", "Gym", "Boxing")

    Trả về:
        Trainer đã được tạo và lưu vào DB
    """
    _validate(name, phone, email)

    # Kiểm tra trùng SĐT — mỗi HLV phải có SĐT duy nhất (dùng để đăng nhập)
    existing = trainer_repo.get_by_phone(phone.strip())
    if existing:
        raise ValueError("Số điện thoại đã được đăng ký bởi HLV khác")

    trainer = Trainer(
        name=name.strip(),
        phone=phone.strip(),
        email=email.strip() if email else None,
        specialization=specialization.strip() if specialization else None,
    )

    return trainer_repo.create(trainer)


def update_trainer(trainer: Trainer) -> Trainer:
    """Cập nhật thông tin HLV."""
    _validate(trainer.name, trainer.phone, trainer.email)
    # Kiểm tra trùng SĐT với HLV khác (trừ chính mình)
    existing = trainer_repo.get_by_phone(trainer.phone.strip())
    if existing and existing.id != trainer.id:
        raise ValueError("Số điện thoại đã được đăng ký bởi HLV khác")
    return trainer_repo.update(trainer)


def get_trainer_by_id(trainer_id: str) -> Trainer | None:
    """Lấy thông tin HLV theo ID."""
    return trainer_repo.get_by_id(trainer_id)


def get_all_trainers(active_only: bool = True) -> list[Trainer]:
    """Lấy danh sách tất cả HLV."""
    return trainer_repo.get_all(active_only)


def reset_pin(trainer_id: str, new_pin: str) -> Trainer:
    """Reset PIN HLV. PIN phải là 6 chữ số."""
    if not re.fullmatch(r"\d{6}", new_pin):
        raise ValueError("PIN phải gồm đúng 6 chữ số")
    trainer = trainer_repo.get_by_id(trainer_id)
    if not trainer:
        raise ValueError("Không tìm thấy HLV")
    trainer.pin = new_pin
    return trainer_repo.update(trainer)


def get_trainer_members(trainer_id: str) -> list:
    """Lấy danh sách học viên CỦA HLV NÀY (chỉ học viên được gán, không phải tất cả)."""
    from app.services import assignment_svc
    return assignment_svc.get_trainer_students(trainer_id)
