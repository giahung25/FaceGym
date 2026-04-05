# ============================================================================
# FILE: app/models/trainer_assignment.py
# MỤC ĐÍCH: Model liên kết HLV ↔ Hội viên (trainer_assignments).
# ============================================================================

from datetime import datetime
from app.models.base import BaseModel


class TrainerAssignment(BaseModel):
    """Liên kết giữa HLV và hội viên.

    Ghi lại việc HLV X được gán kèm hội viên Y, có thể qua gói tập hoặc thủ công.
    """

    STATUS_ACTIVE = "active"
    STATUS_ENDED = "ended"

    def __init__(self, member_id, trainer_id, subscription_id=None,
                 start_date=None, end_date=None, notes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_id = member_id
        self.trainer_id = trainer_id
        self.subscription_id = subscription_id  # None = gan thu cong
        self.start_date = start_date or datetime.now()
        self.end_date = end_date                # None = dang kem
        self.status = self.STATUS_ACTIVE
        self.notes = notes

    def __str__(self):
        return (f"TrainerAssignment(member={self.member_id}, "
                f"trainer={self.trainer_id}, status={self.status})")
