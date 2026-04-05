# ============================================================================
# FILE: app/models/trainer.py
# MỤC ĐÍCH: Định nghĩa class Trainer — đại diện cho HUẤN LUYỆN VIÊN phòng gym.
#            Kế thừa từ BaseModel → tự động có id, created_at, updated_at, is_active.
# ============================================================================

from app.models.base import BaseModel


class Trainer(BaseModel):
    """Đại diện cho một huấn luyện viên (HLV) phòng gym.

    Thuộc tính (từ BaseModel): id, created_at, updated_at, is_active
    Thuộc tính riêng: name, phone, email, specialization, pin

    VD: trainer = Trainer(name="Trần Văn B", phone="0909123456", specialization="Yoga")
    """

    def __init__(self, name, phone, email=None, specialization=None,
                 pin="000000", *args, **kwargs):
        """Khởi tạo một huấn luyện viên mới.

        Tham số:
            name (str):                    Họ tên HLV — BẮT BUỘC
            phone (str):                   Số điện thoại — BẮT BUỘC (dùng để đăng nhập user app)
            email (str, optional):         Email
            specialization (str, optional): Chuyên môn (VD: "Yoga", "Gym", "Boxing", "Zumba")
            pin (str):                     PIN 6 số đăng nhập user app — mặc định "000000"
        """
        super().__init__(*args, **kwargs)

        self.name = name                        # Họ tên HLV
        self.phone = phone                      # SĐT (dùng để đăng nhập)
        self.email = email                      # Email
        self.specialization = specialization    # Chuyên môn
        self.pin = pin                          # PIN đăng nhập — đổi sau lần đầu

    def __str__(self):
        return f"Trainer(id={self.id}, name={self.name}, phone={self.phone})"
