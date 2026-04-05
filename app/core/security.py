# ============================================================================
# FILE: app/core/security.py
# MỤC ĐÍCH: Xử lý xác thực (authentication) — kiểm tra đăng nhập.
#            Hiện tại chỉ so sánh đơn giản với username/password cố định.
# ============================================================================

from app.core.config import ADMIN_USERNAME, ADMIN_PASSWORD
# ↑ Import username và password mặc định từ file cấu hình


def check_login(username: str, password: str) -> bool:
    """Kiểm tra thông tin đăng nhập. Trả về True nếu hợp lệ, False nếu sai.

    Cách hoạt động:
    1. username.strip() — xóa khoảng trắng đầu/cuối (VD: "  admin  " → "admin")
    2. So sánh với ADMIN_USERNAME (mặc định "admin") VÀ ADMIN_PASSWORD ("admin123")
    3. Dùng toán tử `and`: CẢ HAI điều kiện đều phải đúng → mới trả True

    Tham số:
        username (str): Tên đăng nhập người dùng nhập vào
        password (str): Mật khẩu người dùng nhập vào

    Trả về:
        bool: True nếu đúng cả username lẫn password, False nếu sai
    """
    return username.strip() == ADMIN_USERNAME and password == ADMIN_PASSWORD
