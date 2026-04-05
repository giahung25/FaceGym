# ============================================================================
# FILE: app/services/schedule_svc.py
# MỤC ĐÍCH: Logic nghiệp vụ cho lịch dạy HLV.
# ============================================================================

import re
from datetime import datetime, timedelta
from app.models.training_session import TrainingSession
from app.repositories import training_session_repo


def _validate_date(date_str: str) -> str:
    """Validate và chuẩn hóa ngày — phải đúng YYYY-MM-DD."""
    if not date_str or not date_str.strip():
        raise ValueError("Ngày không được để trống")
    date_str = date_str.strip()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Ngày '{date_str}' không hợp lệ. Định dạng: YYYY-MM-DD (VD: 2026-04-05)")
    return date_str


def _validate_time(time_str: str, field_name: str = "Giờ") -> str:
    """Validate và chuẩn hóa giờ — phải đúng HH:MM, giờ 00-23, phút 00-59."""
    if not time_str or not time_str.strip():
        raise ValueError(f"{field_name} không được để trống")
    time_str = time_str.strip()
    if not re.fullmatch(r"\d{1,2}:\d{2}", time_str):
        raise ValueError(f"{field_name} '{time_str}' không hợp lệ. Định dạng: HH:MM (VD: 08:30)")
    parts = time_str.split(":")
    hour, minute = int(parts[0]), int(parts[1])
    if hour < 0 or hour > 23:
        raise ValueError(f"{field_name}: giờ phải từ 00 đến 23 (nhận được {hour})")
    if minute < 0 or minute > 59:
        raise ValueError(f"{field_name}: phút phải từ 00 đến 59 (nhận được {minute})")
    return f"{hour:02d}:{minute:02d}"


def _validate_time_range(start_time: str, end_time: str):
    """Validate giờ bắt đầu phải trước giờ kết thúc."""
    s_parts = start_time.split(":")
    e_parts = end_time.split(":")
    start_minutes = int(s_parts[0]) * 60 + int(s_parts[1])
    end_minutes = int(e_parts[0]) * 60 + int(e_parts[1])
    if end_minutes <= start_minutes:
        raise ValueError(
            f"Giờ kết thúc ({end_time}) phải sau giờ bắt đầu ({start_time})"
        )


def create_session(trainer_id: str, member_id: str, session_date: str,
                   start_time: str, end_time: str = None, content: str = None,
                   assignment_id: str = None, notes: str = None) -> TrainingSession:
    """Tạo buổi tập mới."""
    session_date = _validate_date(session_date)
    start_time = _validate_time(start_time, "Giờ bắt đầu")
    if end_time:
        end_time = _validate_time(end_time, "Giờ kết thúc")
        _validate_time_range(start_time, end_time)

    if not member_id:
        raise ValueError("Vui lòng chọn học viên")

    session = TrainingSession(
        trainer_id=trainer_id,
        member_id=member_id,
        session_date=session_date,
        start_time=start_time,
        end_time=end_time,
        content=content,
        assignment_id=assignment_id,
        notes=notes,
    )
    return training_session_repo.create(session)


def update_session(session: TrainingSession) -> TrainingSession:
    """Cập nhật buổi tập."""
    session.session_date = _validate_date(session.session_date)
    session.start_time = _validate_time(session.start_time, "Giờ bắt đầu")
    if session.end_time:
        session.end_time = _validate_time(session.end_time, "Giờ kết thúc")
        _validate_time_range(session.start_time, session.end_time)
    return training_session_repo.update(session)


def delete_session(session_id: str):
    """Xóa buổi tập (soft delete)."""
    training_session_repo.delete(session_id)


def get_week_sessions(trainer_id: str, week_start_date: datetime) -> list[TrainingSession]:
    """Lấy buổi tập của HLV trong 1 tuần, bắt đầu từ week_start_date (Thứ Hai)."""
    week_start = week_start_date.strftime("%Y-%m-%d")
    week_end = (week_start_date + timedelta(days=6)).strftime("%Y-%m-%d")
    return training_session_repo.get_by_trainer_and_week(trainer_id, week_start, week_end)


def get_member_week_sessions(member_id: str, week_start_date: datetime) -> list[TrainingSession]:
    """Lấy buổi tập của hội viên trong 1 tuần."""
    week_start = week_start_date.strftime("%Y-%m-%d")
    week_end = (week_start_date + timedelta(days=6)).strftime("%Y-%m-%d")
    return training_session_repo.get_by_member_and_week(member_id, week_start, week_end)


def count_sessions_this_month(trainer_id: str) -> int:
    """Đếm số buổi tập của HLV trong tháng hiện tại."""
    now = datetime.now()
    return training_session_repo.count_by_trainer_month(trainer_id, now.year, now.month)


def get_week_start(reference_date: datetime = None) -> datetime:
    """Tính ngày Thứ Hai của tuần chứa reference_date."""
    if reference_date is None:
        reference_date = datetime.now()
    # weekday(): Mon=0, Tue=1, ..., Sun=6
    days_since_monday = reference_date.weekday()
    monday = reference_date - timedelta(days=days_since_monday)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)
