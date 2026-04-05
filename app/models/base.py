# ============================================================================
# FILE: app/models/base.py
# MỤC ĐÍCH: Định nghĩa class CHA (BaseModel) cho tất cả các model trong hệ thống.
#            Mọi model (Member, Equipment, MembershipPlan...) đều KẾ THỪA từ class này.
#            BaseModel cung cấp các thuộc tính/phương thức CHUNG mà model nào cũng cần.
#
# KIẾN THỨC:
#   - Class = bản thiết kế / khuôn mẫu để tạo đối tượng
#   - Kế thừa (inheritance) = class con tự động có tất cả thuộc tính/phương thức của class cha
#   - UUID = chuỗi ID duy nhất toàn cầu (không bao giờ trùng)
# ============================================================================

import uuid                  # Thư viện tạo UUID — ID duy nhất (VD: "f47ac10b-58cc-4372-a567-0e02b2c3d479")
from datetime import datetime  # Thư viện xử lý ngày giờ


class BaseModel:
    """Class cha cho tất cả model. Cung cấp: id, created_at, updated_at, is_active.

    Khi một class khác kế thừa BaseModel (VD: class Member(BaseModel)),
    thì Member tự động có tất cả thuộc tính và phương thức bên dưới.
    """

    def __init__(self, *args, **kwargs):
        """Hàm khởi tạo — được gọi tự động khi tạo đối tượng mới.

        VD: member = Member("Nguyễn Văn A", "0901234567")
            → Python sẽ gọi __init__() để thiết lập các thuộc tính ban đầu

        *args, **kwargs:
            - *args = nhận thêm tham số vị trí bất kỳ (không dùng ở đây, để tương thích kế thừa)
            - **kwargs = nhận thêm tham số tên bất kỳ (không dùng ở đây, để tương thích kế thừa)
        """
        # Tạo ID duy nhất bằng UUID phiên bản 4 (ngẫu nhiên), chuyển sang chuỗi (str)
        # VD: "f47ac10b-58cc-4372-a567-0e02b2c3d479"
        self.id = str(uuid.uuid4())

        # Lưu thời điểm tạo đối tượng — datetime.now() trả về thời gian hiện tại
        # VD: datetime(2026, 3, 22, 14, 30, 0)
        self.created_at = datetime.now()

        # Thời điểm cập nhật gần nhất — ban đầu = thời điểm tạo
        self.updated_at = datetime.now()

        # Trạng thái hoạt động: True = đang active, False = đã bị xóa (soft delete)
        self.is_active = True

    def update(self):
        """Cập nhật thời gian chỉnh sửa (updated_at) về thời điểm hiện tại.

        Gọi hàm này MỖI KHI thay đổi dữ liệu của đối tượng, để biết lần cuối
        nó được sửa là khi nào.

        VD:
            member.name = "Tên mới"
            member.update()  # → updated_at = thời gian hiện tại
        """
        self.updated_at = datetime.now()

    def delete(self):
        """Xóa mềm (soft delete): KHÔNG xóa khỏi database, chỉ đánh dấu is_active = False.

        Tại sao dùng soft delete thay vì xóa thật?
        → Để có thể khôi phục dữ liệu nếu cần, và giữ lịch sử cho báo cáo.

        VD:
            member.delete()
            # member.is_active → False (vẫn còn trong DB nhưng bị ẩn)
        """
        self.is_active = False   # Đánh dấu ngừng hoạt động
        self.update()            # Cập nhật thời gian sửa đổi

    def to_dict(self):
        """Chuyển đối tượng thành dictionary (dict).

        Rất hữu ích khi cần:
        - Chuyển sang JSON để gửi qua API
        - In ra debug
        - Lưu vào file

        Cách hoạt động:
        - self.__dict__ = dictionary chứa TẤT CẢ thuộc tính của đối tượng
          VD: {"id": "abc123", "name": "Nguyễn A", "created_at": datetime(...), ...}
        - Dùng dict comprehension để duyệt qua từng cặp (key, value):
          + Nếu value là kiểu datetime → chuyển sang chuỗi ISO format (VD: "2026-03-22T14:30:00")
          + Nếu không phải datetime → giữ nguyên giá trị

        Trả về:
            dict: VD {"id": "abc123", "name": "Nguyễn A", "created_at": "2026-03-22T14:30:00", ...}
        """
        return {
            k: v.isoformat() if isinstance(v, datetime) else v
            # ↑ isinstance(v, datetime) kiểm tra: v có phải kiểu datetime không?
            #   Nếu đúng → gọi .isoformat() chuyển thành chuỗi
            #   Nếu sai → giữ nguyên v
            for k, v in self.__dict__.items()
            # ↑ Duyệt qua tất cả thuộc tính: k = tên thuộc tính, v = giá trị
        }
