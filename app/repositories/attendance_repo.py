from app.core.database import get_db
from app.models.attendance import Attendance
from datetime import datetime


def _row_to_attendance(row) -> Attendance:
    """Chuyển 1 dòng database thành đối tượng Attendance."""
    a = Attendance.__new__(Attendance)
    a.id = row["id"]
    a.member_id = row["member_id"]
    a.check_in = row["check_in"]
    a.check_out = row["check_out"]
    a.method = row["method"]
    a.confidence = row["confidence"]
    a.created_at = datetime.fromisoformat(row["created_at"])
    a.is_active = bool(row["is_active"])
    return a


def create(attendance: Attendance) -> Attendance:
    """Tạo bản ghi điểm danh mới."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO attendance (id, member_id, check_in, check_out,
               method, confidence, created_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (attendance.id, attendance.member_id, attendance.check_in,
             attendance.check_out, attendance.method, attendance.confidence,
             attendance.created_at.isoformat(), int(attendance.is_active))
        )
    return attendance


def get_today(member_id=None) -> list[Attendance]:
    """Lấy danh sách điểm danh hôm nay."""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        if member_id:
            rows = conn.execute(
                """SELECT * FROM attendance
                   WHERE member_id = ? AND DATE(check_in) = ? AND is_active = 1
                   ORDER BY check_in DESC""",
                (member_id, today)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM attendance
                   WHERE DATE(check_in) = ? AND is_active = 1
                   ORDER BY check_in DESC""",
                (today,)
            ).fetchall()
    return [_row_to_attendance(r) for r in rows]


def has_checked_in_today(member_id: str) -> bool:
    """Kiểm tra hội viên đã check-in hôm nay chưa."""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as cnt FROM attendance
               WHERE member_id = ? AND DATE(check_in) = ? AND is_active = 1""",
            (member_id, today)
        ).fetchone()
    return row["cnt"] > 0


def check_out(attendance_id: str):
    """Ghi nhận check-out."""
    now = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE attendance SET check_out = ? WHERE id = ?",
            (now, attendance_id)
        )


def get_history(member_id: str, limit: int = 30) -> list[Attendance]:
    """Lấy lịch sử điểm danh của hội viên."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM attendance
               WHERE member_id = ? AND is_active = 1
               ORDER BY check_in DESC LIMIT ?""",
            (member_id, limit)
        ).fetchall()
    return [_row_to_attendance(r) for r in rows]


def get_by_date_range(from_date: str, to_date: str, member_id=None) -> list[Attendance]:
    """Lấy điểm danh theo khoảng thời gian."""
    with get_db() as conn:
        if member_id:
            rows = conn.execute(
                """SELECT * FROM attendance
                   WHERE member_id = ? AND DATE(check_in) BETWEEN ? AND ? AND is_active = 1
                   ORDER BY check_in DESC""",
                (member_id, from_date, to_date)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM attendance
                   WHERE DATE(check_in) BETWEEN ? AND ? AND is_active = 1
                   ORDER BY check_in DESC""",
                (from_date, to_date)
            ).fetchall()
    return [_row_to_attendance(r) for r in rows]


def count_today() -> int:
    """Đếm số lượt check-in hôm nay."""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as cnt FROM attendance
               WHERE DATE(check_in) = ? AND is_active = 1""",
            (today,)
        ).fetchone()
    return row["cnt"]
