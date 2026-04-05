# ============================================================================
# FILE: app/models/notification.py
# MỤC ĐÍCH: Định nghĩa class Notification — đại diện cho một THÔNG BÁO
#            gửi tới hội viên hoặc huấn luyện viên trong user app.
#
# Notification KHÔNG kế thừa BaseModel vì:
#   - Không cần updated_at (thông báo chỉ tạo rồi đọc, không sửa)
#   - Không cần is_active / soft delete
#   - Chỉ có id, created_at, is_read là đủ
# ============================================================================

import uuid
from datetime import datetime


class Notification:
    """Đại diện cho một thông báo gửi tới hội viên hoặc HLV.

    VD: Notification(user_id="abc", user_type="member",
                     title="Gói tập sắp hết hạn!",
                     message="Gói 3 tháng của bạn còn 7 ngày.")
    """

    # ── Hằng số user_type ─────────────────────────────────────────────────────
    TYPE_MEMBER = "member"      # Thông báo gửi cho hội viên
    TYPE_TRAINER = "trainer"    # Thông báo gửi cho HLV

    def __init__(self, user_id, user_type, title, message,
                 is_read=False, *args, **kwargs):
        """Khởi tạo một thông báo mới.

        Tham số:
            user_id (str):    ID người nhận (hội viên hoặc HLV) — BẮT BUỘC
            user_type (str):  Loại người nhận: 'member' hoặc 'trainer' — BẮT BUỘC
            title (str):      Tiêu đề thông báo — BẮT BUỘC
            message (str):    Nội dung chi tiết — BẮT BUỘC
            is_read (bool):   Trạng thái đọc — mặc định False (chưa đọc)
        """
        self.id = str(uuid.uuid4())
        self.user_id = user_id          # ID người nhận
        self.user_type = user_type      # 'member' hoặc 'trainer'
        self.title = title              # Tiêu đề
        self.message = message          # Nội dung
        self.is_read = is_read          # False = chưa đọc, True = đã đọc
        self.created_at = datetime.now()

    def mark_read(self):
        """Đánh dấu thông báo này là đã đọc."""
        self.is_read = True

    def __str__(self):
        status = "đã đọc" if self.is_read else "chưa đọc"
        return f"Notification(id={self.id}, title={self.title!r}, {status})"
