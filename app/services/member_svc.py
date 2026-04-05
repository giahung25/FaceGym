# ============================================================================
# FILE: app/services/member_svc.py
# MỤC ĐÍCH: Tầng SERVICE cho hội viên — chứa LOGIC NGHIỆP VỤ (business logic).
#
# KIẾN TRÚC: GUI → Service → Repository → Database
#   - Service = nơi đặt các quy tắc nghiệp vụ: validation, tính toán, xử lý...
#   - Service gọi Repository để đọc/ghi database
#   - GUI gọi Service (KHÔNG gọi Repository trực tiếp)
#
# TẠI SAO TÁCH SERVICE VÀ REPOSITORY?
#   - Repository CHỈ biết cách đọc/ghi database (SQL)
#   - Service chứa logic: "SĐT phải hợp lệ", "email phải có @"
#   - Nếu đổi database (VD: từ SQLite sang PostgreSQL) → chỉ sửa Repository
#   - Logic nghiệp vụ trong Service KHÔNG thay đổi
# ============================================================================

import re  # Thư viện Regular Expression — dùng để kiểm tra pattern (mẫu) chuỗi
from datetime import datetime
from app.models.member import Member
from app.repositories import member_repo  # Import module repository (không import từng hàm)


def _validate(name: str, phone: str, email: str = None):
    """Kiểm tra dữ liệu đầu vào (validation) trước khi lưu vào database.

    Hàm private (bắt đầu bằng _) — chỉ được gọi BÊN TRONG file này.
    Nếu dữ liệu KHÔNG hợp lệ → raise ValueError (ném lỗi) → caller sẽ catch lỗi này.

    Tham số:
        name (str):  Tên hội viên
        phone (str): Số điện thoại
        email (str): Email (tùy chọn)

    Raises:
        ValueError: nếu dữ liệu không hợp lệ (tên trống, SĐT sai format, email sai...)
    """
    # Kiểm tra tên: không được None và không được chỉ là khoảng trắng
    if not name or not name.strip():
        raise ValueError("Tên hội viên không được để trống")

    # Kiểm tra SĐT: không được trống
    if not phone or not phone.strip():
        raise ValueError("Số điện thoại không được để trống")

    # Kiểm tra SĐT bằng regex (Regular Expression):
    # r"[0-9+\-\s]{7,15}" nghĩa là:
    #   [0-9+\-\s] = cho phép: chữ số (0-9), dấu +, dấu -, khoảng trắng
    #   {7,15}     = độ dài từ 7 đến 15 ký tự
    # fullmatch = toàn bộ chuỗi phải khớp pattern (không phải chỉ một phần)
    # VD hợp lệ: "0901234567", "+84-901-234-567"
    # VD không hợp lệ: "abc", "123" (quá ngắn)
    if not re.fullmatch(r"[0-9+\-\s]{7,15}", phone.strip()):
        raise ValueError("Số điện thoại không hợp lệ")

    # Kiểm tra email (chỉ khi có giá trị):
    # r"[^@]+@[^@]+\.[^@]+" nghĩa là:
    #   [^@]+  = 1 hoặc nhiều ký tự KHÔNG phải @
    #   @      = phải có ký tự @
    #   [^@]+  = 1 hoặc nhiều ký tự KHÔNG phải @
    #   \.     = dấu chấm
    #   [^@]+  = 1 hoặc nhiều ký tự
    # VD hợp lệ: "a@gmail.com"
    # VD không hợp lệ: "abc", "@gmail.com", "a@"
    if email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email.strip()):
        raise ValueError("Email không hợp lệ")


def register_member(name: str, phone: str, email: str = None, gender: str = None,
                    date_of_birth=None, address: str = None,
                    emergency_contact: str = None) -> Member:
    """Đăng ký hội viên MỚI.

    Flow:
    1. Validate dữ liệu (kiểm tra hợp lệ)
    2. Tạo đối tượng Member (với id, created_at tự động)
    3. Gọi repository để lưu vào database
    4. Trả về Member đã lưu

    Tham số: thông tin hội viên (tên, SĐT, email...)
    Trả về: Member đã được tạo và lưu vào DB
    Raises: ValueError nếu dữ liệu không hợp lệ
    """
    _validate(name, phone, email)  # Bước 1: validate — nếu sai sẽ raise ValueError

    # Bước 1b: Kiểm tra trùng SĐT — mỗi hội viên phải có SĐT duy nhất (dùng để đăng nhập)
    existing = member_repo.get_by_phone(phone.strip())
    if existing:
        raise ValueError("Số điện thoại đã được đăng ký bởi hội viên khác")

    # Bước 2: Tạo đối tượng Member
    # .strip() xóa khoảng trắng thừa đầu/cuối
    member = Member(
        name=name.strip(),
        phone=phone.strip(),
        email=email.strip() if email else None,  # Nếu email có giá trị → strip, nếu None → giữ None
        gender=gender,
        date_of_birth=date_of_birth,
        address=address,
        emergency_contact=emergency_contact,
    )

    # Bước 3: Lưu vào database qua repository
    return member_repo.create(member)


def update_member(member: Member) -> Member:
    """Cập nhật thông tin hội viên đã tồn tại.

    CÁCH DÙNG: Caller (GUI) tự sửa các field trước, rồi gọi hàm này:
        member.name = "Tên mới"
        member.phone = "0909999999"
        member_svc.update_member(member)

    Hàm này sẽ:
    1. Validate dữ liệu mới
    2. Gọi repository để ghi vào DB

    Tham số:
        member (Member): đối tượng đã được sửa thuộc tính

    Trả về:
        Member: đối tượng đã cập nhật
    """
    _validate(member.name, member.phone, member.email)  # Validate dữ liệu mới
    # Kiểm tra trùng SĐT với hội viên khác (trừ chính mình)
    existing = member_repo.get_by_phone(member.phone.strip())
    if existing and existing.id != member.id:
        raise ValueError("Số điện thoại đã được đăng ký bởi hội viên khác")
    return member_repo.update(member)                    # Ghi vào DB


def get_member_stats() -> dict:
    """Tính thống kê tổng quan về hội viên.

    Trả về dict:
    {
        "total": 100,          # Tổng số hội viên (kể cả đã xóa mềm)
        "active": 85,          # Số hội viên đang hoạt động
        "new_this_month": 12,  # Số hội viên đăng ký THÁNG NÀY
    }

    Được dùng ở: Dashboard (hiển thị KPI) và Members screen (dòng tổng kết)
    """
    # Lấy TẤT CẢ hội viên (kể cả đã xóa) để tính total
    all_members = member_repo.get_all(active_only=False)

    # Lọc ra hội viên đang active
    # List comprehension: [m for m in list if điều_kiện]
    active = [m for m in all_members if m.is_active]

    # Đếm hội viên mới tháng này
    now = datetime.now()
    new_this_month = [
        m for m in active
        # So sánh năm VÀ tháng của created_at với năm/tháng hiện tại
        if m.created_at.year == now.year and m.created_at.month == now.month
    ]

    return {
        "total": len(all_members),        # len() = đếm số phần tử trong list
        "active": len(active),
        "new_this_month": len(new_this_month),
    }
