# ============================================================================
# FILE: app/repositories/equipment_repo.py
# MỤC ĐÍCH: Tầng REPOSITORY cho Equipment — đọc/ghi dữ liệu thiết bị vào database.
#
# CRUD: Create, Read (get_by_id, get_all, get_by_status, get_by_category), Update, Delete
# ============================================================================

from app.core.database import get_db
from app.models.equipment import Equipment
from datetime import datetime


def _row_to_equipment(row) -> Equipment:
    """Chuyển 1 dòng database → đối tượng Equipment.

    Giống _row_to_member ở member_repo.py:
    - Dùng __new__() để tạo object rỗng (không gọi __init__)
    - Gán từng thuộc tính từ database row vào object
    """
    e = Equipment.__new__(Equipment)
    e.id = row["id"]
    e.name = row["name"]               # Tên thiết bị
    e.category = row["category"]       # Loại thiết bị
    e.quantity = row["quantity"]        # Số lượng
    e.status = row["status"]           # Trạng thái: working/broken/maintenance
    e.purchase_date = row["purchase_date"]  # Ngày mua (chuỗi hoặc None)
    e.location = row["location"]       # Vị trí đặt
    e.notes = row["notes"]             # Ghi chú
    e.created_at = datetime.fromisoformat(row["created_at"])
    e.updated_at = datetime.fromisoformat(row["updated_at"])
    e.is_active = bool(row["is_active"])
    return e


def create(equipment: Equipment) -> Equipment:
    """Thêm thiết bị mới vào database (INSERT)."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO equipment (id, name, category, quantity, status, purchase_date,
               location, notes, created_at, updated_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (equipment.id, equipment.name, equipment.category, equipment.quantity,
             equipment.status, equipment.purchase_date,
             equipment.location, equipment.notes,
             equipment.created_at.isoformat(), equipment.updated_at.isoformat(),
             int(equipment.is_active))
        )
    return equipment


def get_by_id(id: str) -> Equipment | None:
    """Tìm thiết bị theo ID. Trả về Equipment hoặc None."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM equipment WHERE id = ?", (id,)).fetchone()
    return _row_to_equipment(row) if row else None


def get_all(active_only: bool = True) -> list[Equipment]:
    """Lấy danh sách tất cả thiết bị, sắp xếp theo tên A→Z.

    active_only=True: chỉ lấy thiết bị đang hoạt động (chưa bị xóa mềm)
    """
    with get_db() as conn:
        if active_only:
            rows = conn.execute("SELECT * FROM equipment WHERE is_active = 1 ORDER BY name").fetchall()
        else:
            rows = conn.execute("SELECT * FROM equipment ORDER BY name").fetchall()
    return [_row_to_equipment(r) for r in rows]


def get_by_status(status: str) -> list[Equipment]:
    """Lấy thiết bị theo trạng thái (working/broken/maintenance).

    VD: get_by_status("broken") → lấy tất cả thiết bị đang hỏng
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM equipment WHERE is_active = 1 AND status = ? ORDER BY name", (status,)
        ).fetchall()
    return [_row_to_equipment(r) for r in rows]


def get_by_category(category: str) -> list[Equipment]:
    """Lấy thiết bị theo loại (VD: "Cardio", "Tạ tự do").

    VD: get_by_category("Cardio") → lấy tất cả máy Cardio
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM equipment WHERE is_active = 1 AND category = ? ORDER BY name", (category,)
        ).fetchall()
    return [_row_to_equipment(r) for r in rows]


def update(equipment: Equipment) -> Equipment:
    """Cập nhật thông tin thiết bị trong database (UPDATE)."""
    equipment.update()  # Cập nhật updated_at
    with get_db() as conn:
        conn.execute(
            """UPDATE equipment SET name=?, category=?, quantity=?, status=?,
               purchase_date=?, location=?, notes=?, updated_at=?, is_active=? WHERE id=?""",
            (equipment.name, equipment.category, equipment.quantity, equipment.status,
             equipment.purchase_date, equipment.location, equipment.notes,
             equipment.updated_at.isoformat(), int(equipment.is_active), equipment.id)
        )
    return equipment


def delete(id: str):
    """Xóa mềm thiết bị (soft delete): is_active = 0."""
    with get_db() as conn:
        conn.execute(
            "UPDATE equipment SET is_active = 0, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), id)
        )
