# ============================================================================
# FILE: app/repositories/training_session_repo.py
# MỤC ĐÍCH: CRUD cho bảng training_sessions — buổi tập HLV-học viên.
# ============================================================================

from app.core.database import get_db
from app.models.training_session import TrainingSession
from datetime import datetime


def _row_to_session(row) -> TrainingSession:
    s = TrainingSession.__new__(TrainingSession)
    s.id = row["id"]
    s.trainer_id = row["trainer_id"]
    s.member_id = row["member_id"]
    s.assignment_id = row["assignment_id"]
    s.session_date = row["session_date"]
    s.start_time = row["start_time"]
    s.end_time = row["end_time"]
    s.content = row["content"]
    s.status = row["status"]
    s.notes = row["notes"]
    s.created_at = datetime.fromisoformat(row["created_at"])
    s.updated_at = datetime.fromisoformat(row["updated_at"])
    s.is_active = bool(row["is_active"])
    return s


def create(session: TrainingSession) -> TrainingSession:
    with get_db() as conn:
        conn.execute(
            """INSERT INTO training_sessions
               (id, trainer_id, member_id, assignment_id, session_date, start_time,
                end_time, content, status, notes, created_at, updated_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session.id, session.trainer_id, session.member_id,
             session.assignment_id, session.session_date, session.start_time,
             session.end_time, session.content, session.status, session.notes,
             session.created_at.isoformat(), session.updated_at.isoformat(),
             int(session.is_active))
        )
    return session


def get_by_id(id: str) -> TrainingSession | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM training_sessions WHERE id = ?", (id,)
        ).fetchone()
    return _row_to_session(row) if row else None


def get_by_trainer_and_week(trainer_id: str, week_start: str, week_end: str) -> list[TrainingSession]:
    """Lấy buổi tập của HLV trong khoảng ngày [week_start, week_end]."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM training_sessions
               WHERE trainer_id = ? AND session_date >= ? AND session_date <= ?
               AND is_active = 1
               ORDER BY session_date, start_time""",
            (trainer_id, week_start, week_end)
        ).fetchall()
    return [_row_to_session(r) for r in rows]


def count_by_trainer_month(trainer_id: str, year: int, month: int) -> int:
    """Đếm số buổi tập của HLV trong tháng."""
    month_str = f"{year}-{month:02d}"
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as cnt FROM training_sessions
               WHERE trainer_id = ? AND session_date LIKE ? AND is_active = 1""",
            (trainer_id, f"{month_str}%")
        ).fetchone()
    return row["cnt"] if row else 0


def update(session: TrainingSession) -> TrainingSession:
    session.update()
    with get_db() as conn:
        conn.execute(
            """UPDATE training_sessions
               SET session_date=?, start_time=?, end_time=?, content=?,
                   status=?, notes=?, member_id=?, assignment_id=?,
                   updated_at=?, is_active=?
               WHERE id=?""",
            (session.session_date, session.start_time, session.end_time,
             session.content, session.status, session.notes,
             session.member_id, session.assignment_id,
             session.updated_at.isoformat(), int(session.is_active), session.id)
        )
    return session


def get_by_member_and_week(member_id: str, week_start: str, week_end: str) -> list[TrainingSession]:
    """Lấy buổi tập của hội viên trong khoảng ngày [week_start, week_end]."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM training_sessions
               WHERE member_id = ? AND session_date >= ? AND session_date <= ?
               AND is_active = 1
               ORDER BY session_date, start_time""",
            (member_id, week_start, week_end)
        ).fetchall()
    return [_row_to_session(r) for r in rows]


def delete(id: str):
    """Xóa mềm buổi tập."""
    with get_db() as conn:
        conn.execute(
            "UPDATE training_sessions SET is_active = 0, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), id)
        )
