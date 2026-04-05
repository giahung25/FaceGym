# ============================================================================
# FILE: app/models/equipment.py
# MỤC ĐÍCH: Định nghĩa class Equipment — đại diện cho THIẾT BỊ / MÁY MÓC phòng gym.
#            VD: Máy chạy bộ, Máy kéo cáp, Tạ tay 10kg...
# ============================================================================

from datetime import datetime
from app.models.base import BaseModel


class Equipment(BaseModel):
    """Thiết bị / máy móc trong phòng gym.

    VD: Equipment(name="Máy chạy bộ", category="Cardio", quantity=3, status="working")
    """

    # ── Hằng số trạng thái ────────────────────────────────────────────────────
    # Dùng hằng số thay vì string trực tiếp để tránh lỗi typo
    # VD: Equipment.STATUS_WORKING thay vì gõ "working" (có thể gõ nhầm "workng")
    STATUS_WORKING = "working"          # Hoạt động tốt — sẵn sàng sử dụng
    STATUS_BROKEN = "broken"            # Đang hỏng — không thể dùng
    STATUS_MAINTENANCE = "maintenance"  # Đang được bảo trì / sửa chữa

    def __init__(self, name, category, quantity=1,
                 purchase_date=None, location=None, notes=None, *args, **kwargs):
        """Khởi tạo một thiết bị mới.

        Tham số:
            name (str):           Tên thiết bị — BẮT BUỘC (VD: "Máy chạy bộ TechnoGym")
            category (str):       Loại thiết bị — BẮT BUỘC (VD: "Cardio", "Tạ tự do", "Máy lực")
            quantity (int):       Số lượng — mặc định 1
            purchase_date (str):  Ngày mua (VD: "2025-06-15")
            location (str):       Vị trí đặt (VD: "Tầng 1", "Khu Cardio")
            notes (str):          Ghi chú bảo trì

        VD: eq = Equipment(name="Máy chạy bộ", category="Cardio", quantity=2, location="Tầng 1")
        """
        super().__init__(*args, **kwargs)  # Tạo id, created_at, updated_at, is_active
        self.name = name                            # Tên thiết bị
        self.category = category                    # Loại (phân nhóm)
        self.quantity = quantity                    # Số lượng
        self.status = self.STATUS_WORKING           # Trạng thái ban đầu = hoạt động
        self.purchase_date = purchase_date          # Ngày mua
        self.location = location                    # Vị trí trong phòng gym
        self.notes = notes                          # Ghi chú (VD: "Cần thay dây curoa sau 1000h")

    def mark_broken(self, notes=None):
        """Đánh dấu thiết bị bị hỏng.

        Tham số:
            notes (str, optional): Ghi chú lý do hỏng (VD: "Cháy motor")

        VD: treadmill.mark_broken("Dây curoa đứt")
        """
        self.status = self.STATUS_BROKEN  # Đổi trạng thái → "broken"
        if notes:                         # Nếu có ghi chú → cập nhật
            self.notes = notes
        self.update()                     # Cập nhật updated_at

    def mark_maintenance(self, notes=None):
        """Đưa thiết bị vào trạng thái bảo trì.

        VD: treadmill.mark_maintenance("Đang thay nhớt")
        """
        self.status = self.STATUS_MAINTENANCE
        if notes:
            self.notes = notes
        self.update()

    def mark_working(self):
        """Đánh dấu thiết bị đã sửa xong, hoạt động trở lại.

        VD: Kỹ thuật viên sửa xong → treadmill.mark_working()
        """
        self.status = self.STATUS_WORKING
        self.update()

    def is_available(self):
        """Kiểm tra thiết bị có đang hoạt động (sẵn sàng dùng) không.

        Trả về:
            bool: True nếu status == "working", False nếu đang hỏng hoặc bảo trì
        """
        return self.status == self.STATUS_WORKING

    def __str__(self):
        """Hiển thị thông tin thiết bị khi print()."""
        return (f"Equipment(name={self.name}, category={self.category}, "
                f"quantity={self.quantity}, status={self.status})")
