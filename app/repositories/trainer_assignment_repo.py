# ============================================================================
# FILE: app/repositories/trainer_assignment_repo.py
# MỤC ĐÍCH: CRUD cho bảng trainer_assignments — liên kết HLV ↔ Hội viên.
# ============================================================================

from app.core.database import get_db
from app.models.trainer_assignment import TrainerAssignment
from datetime import datetime


def _row_to_assignment(row) -> TrainerAssignment:
    """Chuyển 1 dòng database thành đối tượng TrainerAssignment."""
    a = TrainerAssignment.__new__(TrainerAssignment)
    a.id = row["id"]
    a.member_id = row["member_id"]
    a.trainer_id = row["trainer_id"]
    a.subscription_id = row["subscription_id"]
    a.start_date = datetime.fromisoformat(row["start_date"])
    a.end_date = datetime.fromisoformat(row["end_date"]) if row["end_date"] else None
    a.status = row["status"]
    a.notes = row["notes"]
    a.created_at = datetime.fromisoformat(row["created_at"])
    a.updated_at = datetime.fromisoformat(row["updated_at"])
    a.is_active = bool(row["is_active"])
    return a


def create(assignment: TrainerAssignment) -> TrainerAssignment:
    """Thêm assignment mới vào database."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO trainer_assignments
               (id, member_id, trainer_id, subscription_id, start_date, end_date,
                status, notes, created_at, updated_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (assignment.id, assignment.member_id, assignment.trainer_id,
             assignment.subscription_id,
             assignment.start_date.isoformat(),
             assignment.end_date.isoformat() if assignment.end_date else None,
             assignment.status, assignment.notes,
             assignment.created_at.isoformat(), assignment.updated_at.isoformat(),
             int(assignment.is_active))
        )
    return assignment


def get_by_id(id: str) -> TrainerAssignment | None:
    """Tìm assignment theo ID."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM trainer_assignments WHERE id = ?", (id,)
        ).fetchone()
    return _row_to_assignment(row) if row else None


def get_by_trainer(trainer_id: str, active_only: bool = True) -> list[TrainerAssignment]:
    """Lấy danh sách assignment của 1 HLV."""
    with get_db() as conn:
        if active_only:
            rows = conn.execute(
                """SELECT * FROM trainer_assignments
                   WHERE trainer_id = ? AND status = 'active' AND is_active = 1
                   ORDER BY start_date DESC""",
                (trainer_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM trainer_assignments
                   WHERE trainer_id = ? AND is_active = 1
                   ORDER BY start_date DESC""",
                (trainer_id,)
            ).fetchall()
    return [_row_to_assignment(r) for r in rows]


def get_by_member(member_id: str, active_only: bool = True) -> list[TrainerAssignment]:
    """Lấy danh sách HLV của 1 hội viên."""
    with get_db() as conn:
        if active_only:
            rows = conn.execute(
                """SELECT * FROM trainer_assignments
                   WHERE member_id = ? AND status = 'active' AND is_active = 1
                   ORDER BY start_date DESC""",
                (member_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM trainer_assignments
                   WHERE member_id = ? AND is_active = 1
                   ORDER BY start_date DESC""",
                (member_id,)
            ).fetchall()
    return [_row_to_assignment(r) for r in rows]


def get_by_subscription(subscription_id: str) -> TrainerAssignment | None:
    """Tìm assignment gắn với 1 subscription."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM trainer_assignments WHERE subscription_id = ? AND is_active = 1",
            (subscription_id,)
        ).fetchone()
    return _row_to_assignment(row) if row else None


def update(assignment: TrainerAssignment) -> TrainerAssignment:
    """Cập nhật assignment."""
    assignment.update()
    with get_db() as conn:
        conn.execute(
            """UPDATE trainer_assignments
               SET status=?, end_date=?, notes=?, updated_at=?, is_active=?
               WHERE id=?""",
            (assignment.status,
             assignment.end_date.isoformat() if assignment.end_date else None,
             assignment.notes, assignment.updated_at.isoformat(),
             int(assignment.is_active), assignment.id)
        )
    return assignment


def end_assignment(id: str) -> TrainerAssignment | None:
    """Kết thúc assignment — set status='ended', end_date=now."""
    a = get_by_id(id)
    if not a:
        return None
    a.status = TrainerAssignment.STATUS_ENDED
    a.end_date = datetime.now()
    return update(a)


def check_duplicate(member_id: str, trainer_id: str) -> bool:
    """Kiểm tra member đã có assignment active với trainer này chưa."""
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as cnt FROM trainer_assignments
               WHERE member_id = ? AND trainer_id = ? AND status = 'active' AND is_active = 1""",
            (member_id, trainer_id)
        ).fetchone()
    return row["cnt"] > 0
