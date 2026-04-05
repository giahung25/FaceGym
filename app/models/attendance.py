from app.models.base import BaseModel


class Attendance(BaseModel):
    """Đại diện cho một bản ghi điểm danh (check-in/check-out)."""

    METHOD_FACE_ID = "face_id"
    METHOD_MANUAL = "manual"
    METHOD_QR_CODE = "qr_code"

    def __init__(self, member_id, check_in_time, method="face_id",
                 confidence=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_id = member_id
        self.check_in = check_in_time
        self.check_out = None
        self.method = method
        self.confidence = confidence

    def __str__(self):
        return f"Attendance(id={self.id}, member={self.member_id}, method={self.method})"
