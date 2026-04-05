# ============================================================================
# FILE: app/models/training_session.py
# MỤC ĐÍCH: Model buổi tập — HLV lên lịch dạy học viên.
# ============================================================================

from datetime import datetime
from app.models.base import BaseModel


class TrainingSession(BaseModel):
    """Một buổi tập giữa HLV và học viên."""

    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, trainer_id, member_id, session_date, start_time,
                 end_time=None, content=None, assignment_id=None,
                 notes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trainer_id = trainer_id
        self.member_id = member_id
        self.assignment_id = assignment_id
        self.session_date = session_date      # "YYYY-MM-DD"
        self.start_time = start_time          # "HH:MM"
        self.end_time = end_time              # "HH:MM" or None
        self.content = content                # Nội dung buổi tập
        self.status = self.STATUS_SCHEDULED
        self.notes = notes

    def __str__(self):
        return f"TrainingSession({self.session_date} {self.start_time}, trainer={self.trainer_id})"
