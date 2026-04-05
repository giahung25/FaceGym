# ============================================================================
# FILE: app/repositories/trainer_repo.py
# MỤC ĐÍCH: Tầng REPOSITORY cho Trainer — ĐỌC/GHI dữ liệu HLV vào database.
#
# KIẾN TRÚC: GUI → Service → Repository → Database
# ============================================================================

from app.core.database import get_db
from app.models.trainer import Trainer
from datetime import datetime


def _row_to_trainer(row) -> Trainer:
    """Chuyển 1 dòng database thành đối tượng Trainer.

    Dùng __new__() để tạo object mà KHÔNG gọi __init__()
    → giữ nguyên id, created_at từ database.
    """
    t = Trainer.__new__(Trainer)
    t.id = row["id"]
    t.name = row["name"]
    t.phone = row["phone"]
    t.email = row["email"]
    t.specialization = row["specialization"]
    t.pin = row["pin"]
    t.created_at = datetime.fromisoformat(row["created_at"])
    t.updated_at = datetime.fromisoformat(row["updated_at"])
    t.is_active = bool(row["is_active"])
    return t


def create(trainer: Trainer) -> Trainer:
    """Thêm HLV mới vào database."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO trainers (id, name, phone, email, specialization, pin,
               created_at, updated_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (trainer.id, trainer.name, trainer.phone, trainer.email,
             trainer.specialization, trainer.pin,
             trainer.created_at.isoformat(), trainer.updated_at.isoformat(),
             int(trainer.is_active))
        )
    return trainer


def get_by_id(id: str) -> Trainer | None:
    """Tìm HLV theo ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM trainers WHERE id = ?", (id,)).fetchone()
    return _row_to_trainer(row) if row else None


def get_by_phone(phone: str) -> Trainer | None:
    """Tìm HLV theo số điện thoại (dùng cho đăng nhập user app)."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM trainers WHERE phone = ? AND is_active = 1", (phone,)
        ).fetchone()
    return _row_to_trainer(row) if row else None


def get_all(active_only: bool = True) -> list[Trainer]:
    """Lấy danh sách tất cả HLV."""
    with get_db() as conn:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM trainers WHERE is_active = 1 ORDER BY name"
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM trainers ORDER BY name").fetchall()
    return [_row_to_trainer(r) for r in rows]


def update(trainer: Trainer) -> Trainer:
    """Cập nhật thông tin HLV."""
    trainer.update()  # BaseModel.update() → cập nhật updated_at
    with get_db() as conn:
        conn.execute(
            """UPDATE trainers SET name=?, phone=?, email=?, specialization=?,
               pin=?, updated_at=?, is_active=? WHERE id=?""",
            (trainer.name, trainer.phone, trainer.email, trainer.specialization,
             trainer.pin, trainer.updated_at.isoformat(),
             int(trainer.is_active), trainer.id)
        )
    return trainer


def delete(id: str):
    """Xóa mềm HLV và cascade tới các bảng liên quan.

    Cascade: kết thúc assignments, hủy sessions chưa hoàn thành, xóa notifications.
    """
    now = datetime.now().isoformat()
    with get_db() as conn:
        # 1. Soft delete HLV
        conn.execute(
            "UPDATE trainers SET is_active = 0, updated_at = ? WHERE id = ?",
            (now, id)
        )
        # 2. Cascade: kết thúc trainer_assignments
        conn.execute(
            "UPDATE trainer_assignments SET is_active = 0, status = 'ended', end_date = ?, updated_at = ? WHERE trainer_id = ? AND status = 'active'",
            (now, now, id)
        )
        # 3. Cascade: hủy training_sessions chưa hoàn thành
        conn.execute(
            "UPDATE training_sessions SET is_active = 0, status = 'cancelled', updated_at = ? WHERE trainer_id = ? AND status = 'scheduled'",
            (now, id)
        )
        # 4. Xóa thông báo
        conn.execute(
            "DELETE FROM notifications WHERE user_id = ? AND user_type = 'trainer'",
            (id,)
        )
