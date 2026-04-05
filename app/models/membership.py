# ============================================================================
# FILE: app/models/membership.py
# MỤC ĐÍCH: Định nghĩa 2 class liên quan tới GÓI TẬP:
#   1. MembershipPlan — định nghĩa gói tập (VD: "Gói 1 tháng - 500,000đ")
#   2. MembershipSubscription — hội viên ĐĂNG KÝ gói tập (ai đăng ký gì, bao giờ hết hạn)
#
# MỐI QUAN HỆ:
#   Member ←→ MembershipSubscription ←→ MembershipPlan
#   "Hội viên A đăng ký Gói 1 tháng từ ngày 01/03 đến 31/03"
# ============================================================================

from datetime import datetime, timedelta, date  # timedelta = khoảng thời gian (VD: 30 ngày)
from app.models.base import BaseModel


class MembershipPlan(BaseModel):
    """Gói tập — định nghĩa loại gói mà gym cung cấp.

    VD: "Gói 1 tháng" (30 ngày, giá 500,000đ)
        "Gói 1 năm"   (365 ngày, giá 5,000,000đ)
    """

    def __init__(self, name, duration_days, price, description=None, *args, **kwargs):
        """Khởi tạo một gói tập.

        Tham số:
            name (str):          Tên gói — VD: "Gói 1 tháng"
            duration_days (int): Thời hạn tính bằng ngày — VD: 30
            price (float):       Giá gói tính bằng VND — VD: 500000.0
            description (str):   Mô tả thêm (tùy chọn)
        """
        super().__init__(*args, **kwargs)  # Gọi BaseModel.__init__() → tạo id, created_at...
        self.name = name                    # Tên gói (VD: "Gói 1 tháng", "Gói 6 tháng")
        self.duration_days = duration_days  # Số ngày của gói (VD: 30, 180, 365)
        self.price = price                  # Giá gói bằng VND (VD: 500000)
        self.description = description      # Mô tả thêm (tùy chọn, có thể None)

    def __str__(self):
        """Hiển thị thông tin gói tập khi print().
        f-string với :, = thêm dấu phẩy ngăn cách hàng nghìn (VD: 500,000đ)
        """
        return f"MembershipPlan(name={self.name}, duration={self.duration_days} ngày, price={self.price:,}đ)"


class MembershipSubscription(BaseModel):
    """Đăng ký gói tập — ghi lại việc hội viên X đã mua gói tập Y.

    VD: "Hội viên Nguyễn A đăng ký Gói 1 tháng, trả 500,000đ, từ 01/03 đến 31/03, đang active"
    """

    # ── Hằng số trạng thái (Status Constants) ────────────────────────────────
    # Định nghĩa trực tiếp trên class → dùng: MembershipSubscription.STATUS_ACTIVE
    # Tại sao dùng hằng số thay vì gõ "active" trực tiếp?
    #   → Tránh lỗi typo (gõ nhầm "actve" sẽ không bị phát hiện)
    #   → Dễ tìm kiếm và đổi tên trong toàn bộ code
    STATUS_ACTIVE = "active"       # Gói đang hoạt động
    STATUS_EXPIRED = "expired"     # Gói đã hết hạn
    STATUS_CANCELLED = "cancelled" # Gói đã bị hủy

    def __init__(self, member_id, plan_id, duration_days, price_paid, start_date=None, trainer_id=None, *args, **kwargs):
        """Khởi tạo đăng ký gói tập.

        Tham số:
            member_id (str):     ID hội viên (UUID từ bảng members)
            plan_id (str):       ID gói tập (UUID từ bảng membership_plans)
            duration_days (int): Số ngày của gói (lấy từ MembershipPlan.duration_days)
            price_paid (float):  Số tiền thực tế thanh toán (có thể khác giá gốc nếu giảm giá)
            start_date (datetime/date, optional): Ngày bắt đầu — mặc định = hôm nay
        """
        super().__init__(*args, **kwargs)  # Tạo id, created_at, updated_at, is_active
        self.member_id = member_id         # ID hội viên đã đăng ký
        self.plan_id = plan_id             # ID gói tập đã chọn
        self.trainer_id = trainer_id       # ID HLV (None = gói thường, không có HLV)
        self.price_paid = price_paid       # Giá thực tế đã thanh toán (VD: 450000 nếu được giảm giá)

        # ── Xử lý start_date ─────────────────────────────────────────────────
        # Chuẩn hóa về kiểu datetime (vì có khi caller truyền vào kiểu date thuần)
        if start_date is None:
            # Không truyền → dùng thời gian hiện tại
            start_date = datetime.now()
        elif isinstance(start_date, date) and not isinstance(start_date, datetime):
            # Nếu là date thuần (VD: date(2026, 3, 22)) → chuyển thành datetime
            # datetime.combine(date, time) ghép ngày + giờ lại
            # datetime.min.time() = 00:00:00 (nửa đêm)
            start_date = datetime.combine(start_date, datetime.min.time())

        self.start_date = start_date
        # Tính ngày hết hạn = ngày bắt đầu + số ngày gói
        # timedelta(days=30) = khoảng thời gian 30 ngày
        self.end_date = self.start_date + timedelta(days=duration_days)
        self.status = self.STATUS_ACTIVE  # Ban đầu luôn ở trạng thái active

    def is_expired(self):
        """Kiểm tra gói tập đã hết hạn chưa.

        So sánh thời gian hiện tại với end_date:
        - Nếu now > end_date → đã hết hạn → return True
        - Nếu now <= end_date → chưa hết → return False

        VD: end_date = 31/03, hôm nay = 05/04 → True (đã hết hạn)
        """
        return datetime.now() > self.end_date

    def days_remaining(self):
        """Tính số ngày còn lại của gói tập.

        Cách tính:
        - end_date - now = timedelta object
        - .days = lấy số ngày
        - max(..., 0) = nếu âm (đã hết hạn) thì trả 0 thay vì số âm

        VD: end_date = 31/03, hôm nay = 25/03 → 6 ngày
            end_date = 20/03, hôm nay = 25/03 → 0 (không trả -5)
        """
        remaining = (self.end_date - datetime.now()).days
        return max(remaining, 0)  # max(a, b) trả về giá trị lớn hơn

    def cancel(self):
        """Hủy gói tập — chuyển status từ 'active' sang 'cancelled'.

        VD: Hội viên muốn ngừng tập → nhân viên hủy gói
        """
        self.status = self.STATUS_CANCELLED  # Đổi trạng thái thành "cancelled"
        self.update()  # Cập nhật updated_at (gọi BaseModel.update())

    def refresh_status(self):
        """Tự động cập nhật status nếu gói đã hết hạn.

        Chỉ đổi khi: đang 'active' VÀ đã quá ngày hết hạn.
        → Chuyển thành 'expired'

        Hàm này thường được gọi định kỳ hoặc khi hiển thị danh sách.
        """
        if self.status == self.STATUS_ACTIVE and self.is_expired():
            self.status = self.STATUS_EXPIRED
            self.update()

    def __str__(self):
        """Hiển thị thông tin đăng ký khi print().
        strftime('%d/%m/%Y') = format ngày theo kiểu Việt Nam (VD: "22/03/2026")
        """
        return (f"MembershipSubscription(member_id={self.member_id}, "
                f"status={self.status}, end_date={self.end_date.strftime('%d/%m/%Y')})")
