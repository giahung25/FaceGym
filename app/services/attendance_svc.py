"""
Service layer cho Điểm danh — kết hợp Face ID + Database.

GUI gọi attendance_svc, KHÔNG gọi repo trực tiếp.
"""

import time
import logging
from datetime import datetime

from app.core.config import CHECKIN_COOLDOWN
from app.models.attendance import Attendance
from app.repositories import attendance_repo, member_repo
from app.repositories import membership_repo

logger = logging.getLogger("AttendanceService")

# Tracking chống check-in trùng lặp: {member_id: timestamp}
_recently_checked = {}


def check_in(member_id, method="face_id", confidence=None):
    """Ghi nhận check-in cho hội viên.

    Kiểm tra:
        1. Cooldown (chống spam check-in liên tục)
        2. Đã check-in hôm nay chưa
        3. Gói tập còn hạn không

    Returns: dict {"status": str, "message": str}
        status: "success", "cooldown", "already", "expired", "no_subscription", "error"
    """
    now = time.time()

    # 1. Kiểm tra cooldown
    if member_id in _recently_checked:
        elapsed = now - _recently_checked[member_id]
        if elapsed < CHECKIN_COOLDOWN:
            return {"status": "cooldown", "message": "Đã điểm danh gần đây"}

    # 2. Kiểm tra đã check-in hôm nay chưa
    if attendance_repo.has_checked_in_today(member_id):
        _recently_checked[member_id] = now
        return {"status": "already", "message": "Đã điểm danh hôm nay"}

    # 3. Kiểm tra gói tập còn hạn không
    active_subs = membership_repo.get_active_subscriptions_by_member(member_id)
    is_expired = not active_subs

    # 4. Ghi nhận check-in (vẫn ghi ngay cả khi hết hạn gói tập)
    attendance = Attendance(
        member_id=member_id,
        check_in_time=datetime.now().isoformat(),
        method=method,
        confidence=confidence
    )
    attendance_repo.create(attendance)

    _recently_checked[member_id] = now
    logger.info(f"CHECK-IN: member={member_id}, method={method}, confidence={confidence}")

    if is_expired:
        return {"status": "expired", "message": "Check-in thành công, nhưng gói tập đã hết hạn!"}

    return {"status": "success", "message": "Check-in thành công!"}


def check_in_by_face(name_or_id, confidence):
    """Check-in bằng kết quả nhận diện khuôn mặt.

    Args:
        name_or_id: Tên hoặc member_id từ face recognition
        confidence: Độ tin cậy nhận diện (0.0-1.0)

    Returns: dict {"status": str, "message": str, "member_name": str}
    """
    # Thử tìm member theo ID trước (encoding lưu bằng member_id)
    member = member_repo.get_by_id(name_or_id)

    # Nếu không tìm thấy theo ID, thử tìm theo tên
    if member is None:
        members = member_repo.search(name_or_id)
        if members:
            member = members[0]

    if member is None:
        return {
            "status": "not_found",
            "message": f"Không tìm thấy '{name_or_id}' trong hệ thống",
            "member_name": name_or_id
        }

    result = check_in(member.id, method="face_id", confidence=round(confidence, 4))
    result["member_name"] = member.name
    return result


def check_out(member_id):
    """Ghi nhận check-out cho hội viên (check-out bản ghi gần nhất hôm nay).

    Returns: bool — True nếu check-out thành công
    """
    today_records = attendance_repo.get_today(member_id)
    if not today_records:
        return False

    # Lấy bản ghi gần nhất chưa check-out
    for record in today_records:
        if record.check_out is None:
            attendance_repo.check_out(record.id)
            logger.info(f"CHECK-OUT: member={member_id}")
            return True

    return False


def get_today_attendance():
    """Lấy danh sách điểm danh hôm nay (kèm thông tin hội viên).

    Returns: list[dict] — [{"attendance": Attendance, "member": Member}, ...]
    """
    records = attendance_repo.get_today()
    result = []
    for att in records:
        member = member_repo.get_by_id(att.member_id)
        result.append({
            "attendance": att,
            "member": member
        })
    return result


def get_member_attendance(member_id, limit=30):
    """Lấy lịch sử điểm danh của hội viên.

    Returns: list[Attendance]
    """
    return attendance_repo.get_history(member_id, limit)


def get_attendance_by_range(from_date, to_date, member_id=None):
    """Lấy điểm danh theo khoảng thời gian.

    Returns: list[Attendance]
    """
    return attendance_repo.get_by_date_range(from_date, to_date, member_id)


def count_today():
    """Đếm số lượt check-in hôm nay.

    Returns: int
    """
    return attendance_repo.count_today()


def get_attendance_stats():
    """Thống kê điểm danh cơ bản.

    Returns: dict {"today": int, "checked_in_members": list}
    """
    today_count = attendance_repo.count_today()
    today_records = attendance_repo.get_today()
    member_ids = list(set(att.member_id for att in today_records))

    return {
        "today": today_count,
        "checked_in_members": member_ids
    }
