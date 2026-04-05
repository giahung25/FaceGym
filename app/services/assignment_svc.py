# ============================================================================
# FILE: app/services/assignment_svc.py
# MỤC ĐÍCH: Logic nghiệp vụ gán/kết thúc HLV ↔ Hội viên.
# ============================================================================

from datetime import datetime
from app.models.trainer_assignment import TrainerAssignment
from app.repositories import trainer_assignment_repo


def assign_trainer(member_id: str, trainer_id: str,
                   subscription_id: str = None, notes: str = None) -> TrainerAssignment:
    """Gán HLV cho hội viên.

    - Validate: member tồn tại, trainer tồn tại
    - Kiểm tra trùng: member đã có assignment active với trainer này chưa?
    - Tạo TrainerAssignment → lưu DB
    """
    from app.repositories import member_repo, trainer_repo

    member = member_repo.get_by_id(member_id)
    if not member:
        raise ValueError("Không tìm thấy hội viên")

    trainer = trainer_repo.get_by_id(trainer_id)
    if not trainer:
        raise ValueError("Không tìm thấy HLV")

    if trainer_assignment_repo.check_duplicate(member_id, trainer_id):
        raise ValueError("Hội viên đã được gán cho HLV này rồi")

    assignment = TrainerAssignment(
        member_id=member_id,
        trainer_id=trainer_id,
        subscription_id=subscription_id,
        notes=notes,
    )

    return trainer_assignment_repo.create(assignment)


def end_assignment(assignment_id: str) -> TrainerAssignment:
    """Kết thúc kèm cặp — set status='ended', end_date=now."""
    result = trainer_assignment_repo.end_assignment(assignment_id)
    if not result:
        raise ValueError("Không tìm thấy assignment")
    return result


def get_trainer_students(trainer_id: str) -> list[dict]:
    """Lấy danh sách học viên ĐANG ACTIVE của 1 HLV.

    Trả về: [{"member": Member, "assignment": TrainerAssignment, "subscription": sub_or_None}]
    """
    from app.repositories import member_repo, membership_repo

    assignments = trainer_assignment_repo.get_by_trainer(trainer_id, active_only=True)
    result = []

    for a in assignments:
        member = member_repo.get_by_id(a.member_id)
        if not member:
            continue

        sub = None
        if a.subscription_id:
            sub = membership_repo.get_subscription_by_id(a.subscription_id)

        result.append({
            "member": member,
            "assignment": a,
            "subscription": sub,
        })

    return result


def get_member_trainers(member_id: str) -> list[dict]:
    """Lấy danh sách HLV đang kèm 1 hội viên."""
    from app.repositories import trainer_repo

    assignments = trainer_assignment_repo.get_by_member(member_id, active_only=True)
    result = []

    for a in assignments:
        trainer = trainer_repo.get_by_id(a.trainer_id)
        if not trainer:
            continue

        result.append({
            "trainer": trainer,
            "assignment": a,
        })

    return result


def get_trainer_history(trainer_id: str) -> list[dict]:
    """Lấy danh sách học viên ĐÃ KẾT THÚC của 1 HLV (status='ended')."""
    from app.repositories import member_repo

    assignments = trainer_assignment_repo.get_by_trainer(trainer_id, active_only=False)
    ended = [a for a in assignments if a.status == "ended"]
    result = []

    for a in ended:
        member = member_repo.get_by_id(a.member_id)
        if not member:
            continue
        result.append({
            "member": member,
            "assignment": a,
        })

    return result


def update_assignment_notes(assignment_id: str, notes: str) -> None:
    """Cập nhật ghi chú cho assignment."""
    a = trainer_assignment_repo.get_by_id(assignment_id)
    if not a:
        raise ValueError("Không tìm thấy assignment")
    a.notes = notes
    trainer_assignment_repo.update(a)


def auto_end_expired_assignments():
    """Tự động kết thúc assignment khi subscription liên kết đã hết hạn/hủy."""
    from app.repositories import membership_repo

    # Lấy tất cả assignment active có subscription_id
    from app.core.database import get_db
    with get_db() as conn:
        rows = conn.execute(
            """SELECT ta.id as ta_id, s.status as sub_status
               FROM trainer_assignments ta
               JOIN subscriptions s ON ta.subscription_id = s.id
               WHERE ta.status = 'active' AND ta.is_active = 1
               AND ta.subscription_id IS NOT NULL
               AND s.status != 'active'"""
        ).fetchall()

    for row in rows:
        trainer_assignment_repo.end_assignment(row["ta_id"])
