# ============================================================================
# FILE: app/repositories/notification_repo.py
# MỤC ĐÍCH: Tầng REPOSITORY cho Notification — ĐỌC/GHI thông báo vào database.
#
# Notification khác các model khác:
#   - Không có updated_at, is_active (chỉ tạo + đọc, không sửa nội dung)
#   - Có is_read (đánh dấu đã đọc)
# ============================================================================

from app.core.database import get_db
from app.models.notification import Notification
from datetime import datetime


def _row_to_notification(row) -> Notification:
    """Chuyển 1 dòng database thành đối tượng Notification."""
    n = Notification.__new__(Notification)
    n.id = row["id"]
    n.user_id = row["user_id"]
    n.user_type = row["user_type"]
    n.title = row["title"]
    n.message = row["message"]
    n.is_read = bool(row["is_read"])
    n.created_at = datetime.fromisoformat(row["created_at"])
    return n


def create(notification: Notification) -> Notification:
    """Tạo thông báo mới."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO notifications (id, user_id, user_type, title, message,
               is_read, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (notification.id, notification.user_id, notification.user_type,
             notification.title, notification.message,
             int(notification.is_read), notification.created_at.isoformat())
        )
    return notification


def get_by_user(user_id: str, user_type: str) -> list[Notification]:
    """Lấy tất cả thông báo của một user, sắp xếp mới nhất trước."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM notifications
               WHERE user_id = ? AND user_type = ?
               ORDER BY created_at DESC""",
            (user_id, user_type)
        ).fetchall()
    return [_row_to_notification(r) for r in rows]


def get_unread_count(user_id: str, user_type: str) -> int:
    """Đếm số thông báo chưa đọc của một user."""
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as cnt FROM notifications
               WHERE user_id = ? AND user_type = ? AND is_read = 0""",
            (user_id, user_type)
        ).fetchone()
    return row["cnt"] if row else 0


def mark_read(notification_id: str):
    """Đánh dấu 1 thông báo là đã đọc."""
    with get_db() as conn:
        conn.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ?",
            (notification_id,)
        )


def mark_all_read(user_id: str, user_type: str):
    """Đánh dấu TẤT CẢ thông báo của user là đã đọc."""
    with get_db() as conn:
        conn.execute(
            """UPDATE notifications SET is_read = 1
               WHERE user_id = ? AND user_type = ? AND is_read = 0""",
            (user_id, user_type)
        )


def has_notification_today(user_id: str, title: str) -> bool:
    """Kiểm tra user đã có thông báo với title này trong ngày hôm nay chưa.

    Dùng để tránh tạo trùng thông báo hết hạn mỗi lần đăng nhập.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as cnt FROM notifications
               WHERE user_id = ? AND title = ? AND created_at LIKE ?""",
            (user_id, title, f"{today}%")
        ).fetchone()
    return row["cnt"] > 0 if row else False
