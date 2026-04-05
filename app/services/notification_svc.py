# ============================================================================
# FILE: app/services/notification_svc.py
# MỤC ĐÍCH: Logic nghiệp vụ cho thông báo — tạo, đọc, và tự động kiểm tra
#            gói tập sắp hết hạn để gửi thông báo cho hội viên.
#
# KIẾN TRÚC: GUI → notification_svc → notification_repo
# ============================================================================

from datetime import datetime, timedelta
from app.models.notification import Notification
from app.repositories import notification_repo, membership_repo, trainer_assignment_repo


def create_notification(user_id: str, user_type: str,
                        title: str, message: str) -> Notification:
    """Tạo và lưu một thông báo mới.

    Tham số:
        user_id:   ID người nhận
        user_type: 'member' hoặc 'trainer'
        title:     Tiêu đề
        message:   Nội dung

    Trả về:
        Notification đã lưu vào DB
    """
    notif = Notification(
        user_id=user_id,
        user_type=user_type,
        title=title,
        message=message,
    )
    return notification_repo.create(notif)


def get_notifications(user_id: str, user_type: str) -> list[Notification]:
    """Lấy tất cả thông báo của user, mới nhất trước."""
    return notification_repo.get_by_user(user_id, user_type)


def get_unread_count(user_id: str, user_type: str) -> int:
    """Đếm số thông báo chưa đọc."""
    return notification_repo.get_unread_count(user_id, user_type)


def mark_read(notification_id: str):
    """Đánh dấu 1 thông báo đã đọc."""
    notification_repo.mark_read(notification_id)


def mark_all_read(user_id: str, user_type: str):
    """Đánh dấu tất cả thông báo đã đọc."""
    notification_repo.mark_all_read(user_id, user_type)


def check_expiring_subscriptions(member_id: str):
    """Kiểm tra gói tập của hội viên và tạo thông báo nếu cần.

    Được gọi MỖI LẦN hội viên đăng nhập vào user app.
    Tạo thông báo khi:
      - Gói tập active còn <= 7 ngày (sắp hết hạn)
      - Gói tập đã hết hạn (expired)

    Mỗi loại thông báo chỉ tạo 1 lần/ngày (tránh trùng lặp).
    """
    subs = membership_repo.get_subscriptions_by_member(member_id)
    today = datetime.now().date()

    for sub in subs:
        if sub.status != "active":
            continue

        # Tính số ngày còn lại
        try:
            if isinstance(sub.end_date, str):
                end_date = datetime.strptime(sub.end_date, "%Y-%m-%d").date()
            elif hasattr(sub.end_date, "date"):
                end_date = sub.end_date.date()
            else:
                end_date = sub.end_date
        except (ValueError, TypeError):
            continue

        days_left = (end_date - today).days

        if days_left < 0:
            # Gói đã hết hạn
            title = "Gói tập đã hết hạn!"
            if not notification_repo.has_notification_today(member_id, title):
                create_notification(
                    user_id=member_id,
                    user_type="member",
                    title=title,
                    message=f"Gói tập của bạn đã hết hạn. Hãy gia hạn để tiếp tục tập luyện.",
                )

        elif days_left <= 7:
            # Gói sắp hết hạn
            title = "Gói tập sắp hết hạn!"
            if not notification_repo.has_notification_today(member_id, title):
                create_notification(
                    user_id=member_id,
                    user_type="member",
                    title=title,
                    message=f"Gói tập của bạn còn {days_left} ngày nữa sẽ hết hạn. Hãy gia hạn sớm.",
                )


def check_trainer_notifications(trainer_id: str):
    """Kiểm tra và tạo thông báo cho HLV khi đăng nhập.

    Thông báo:
    - Học viên sắp hết gói (<=7 ngày)
    """
    assignments = trainer_assignment_repo.get_by_trainer(trainer_id, active_only=True)
    today = datetime.now().date()

    for a in assignments:
        if not a.subscription_id:
            continue

        sub = membership_repo.get_subscription_by_id(a.subscription_id)
        if not sub or sub.status != "active":
            continue

        try:
            if hasattr(sub.end_date, "date"):
                end_date = sub.end_date.date()
            else:
                end_date = datetime.strptime(str(sub.end_date), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        days_left = (end_date - today).days

        if 0 <= days_left <= 7:
            from app.repositories import member_repo
            member = member_repo.get_by_id(a.member_id)
            member_name = member.name if member else "Học viên"

            title = f"Gói tập sắp hết hạn — {member_name}"
            if not notification_repo.has_notification_today(trainer_id, title):
                create_notification(
                    user_id=trainer_id,
                    user_type="trainer",
                    title=title,
                    message=f"Học viên {member_name} còn {days_left} ngày sẽ hết gói tập. Hãy nhắc gia hạn.",
                )
