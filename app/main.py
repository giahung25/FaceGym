# ============================================================================
# FILE: app/main.py
# MỤC ĐÍCH: ĐIỂM KHỞI ĐỘNG (Entry Point) của toàn bộ ứng dụng.
#            Khi chạy `python app/main.py` → Python thực thi file này đầu tiên.
#
# FLOW KHỞI ĐỘNG:
#   1. Thêm thư mục gốc vào sys.path (để import được các module)
#   2. ft.run(main) → Flet tạo cửa sổ desktop và gọi hàm main(page)
#   3. main() khởi tạo database, cấu hình page, định nghĩa navigate
#   4. Hiển thị màn hình Login đầu tiên
# ============================================================================

import sys  # Thư viện hệ thống — dùng để thao tác với sys.path (danh sách đường dẫn tìm module)
import os   # Thư viện OS — dùng để xử lý đường dẫn file/thư mục

# ── Thêm thư mục gốc vào sys.path ────────────────────────────────────────────
# Vấn đề: Khi chạy `python app/main.py`, Python chỉ biết thư mục `app/`
#          → Không thể import `gui.dashboard` vì `gui/` nằm NGOÀI `app/`
# Giải pháp: Thêm thư mục GỐC (gym_management/) vào sys.path
#
# __file__                = "app/main.py"
# os.path.abspath(__file__) = "E:/gym_management/app/main.py"
# dirname(...)            = "E:/gym_management/app/"
# dirname(dirname(...))   = "E:/gym_management/"  ← thư mục gốc
#
# sys.path.insert(0, ...) = thêm vào ĐẦU danh sách tìm kiếm (ưu tiên cao nhất)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft  # Flet = framework GUI cho Python (tạo giao diện desktop/web)
from app.core.config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT  # Hằng số cấu hình
from app.core.database import init_db  # Hàm tạo bảng database


def main(page: ft.Page):
    """Hàm chính — được Flet gọi khi cửa sổ ứng dụng được tạo.

    Tham số:
        page (ft.Page): đối tượng Page do Flet tạo — đại diện cho CỬA SỔ ứng dụng.
                        Mọi thao tác UI (thêm control, cập nhật, điều hướng) đều qua page.
    """

    # ── Bước 1: Khởi tạo database ────────────────────────────────────────────
    # Tạo các bảng (members, membership_plans, subscriptions, equipment) nếu chưa có
    # try/except: bắt lỗi nếu khởi tạo DB thất bại (VD: file bị khóa, hết dung lượng)
    try:
        init_db()  # Gọi hàm trong database.py → CREATE TABLE IF NOT EXISTS...
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo database: {e}")
        raise  # Ném lại lỗi → app dừng (không nên chạy tiếp khi DB lỗi)

    # ── Bước 2: Cấu hình cửa sổ ──────────────────────────────────────────────
    page.title = APP_TITLE              # Tiêu đề cửa sổ: "GymAdmin Management System"
    page.window_width = WINDOW_WIDTH    # Chiều rộng: 1280px
    page.window_height = WINDOW_HEIGHT  # Chiều cao: 800px
    page.bgcolor = "#F5F5F5"            # Màu nền xám nhạt
    page.padding = 0                    # Không có padding (control chiếm toàn bộ cửa sổ)

    # ── Bước 3: Định nghĩa hàm điều hướng (navigation) ──────────────────────
    def navigate(route: str):
        """Chuyển đổi giữa các màn hình trong ứng dụng.

        Tham số:
            route (str): tên màn hình cần chuyển tới
                         VD: "login", "dashboard", "members", "packages", "equipment", "reports"

        Flow:
        1. Xóa tất cả overlay và controls hiện tại (clear màn hình cũ)
        2. Import và tạo màn hình mới theo route
        3. Thêm màn hình mới vào page
        4. Gọi page.update() để render lên cửa sổ

        LƯU Ý: Import được đặt BÊN TRONG hàm (lazy import) thay vì đầu file.
        → Tránh import vòng (circular import) và chỉ load module khi cần.
        """
        # Xóa trạng thái cũ trước khi chuyển màn hình
        page.overlay.clear()        # Xóa các dialog/popup đang mở
        page.controls.clear()       # Xóa tất cả controls (nội dung) trên page
        page.on_search_change = None  # Reset callback tìm kiếm (mỗi screen có callback riêng)

        # Chọn màn hình theo route (giống switch/case trong các ngôn ngữ khác)
        if route == "login":
            from gui.admin.login import LoginScreen       # Import lazy — chỉ khi cần
            page.add(LoginScreen(page))              # Tạo và thêm màn hình Login
        elif route == "dashboard":
            from gui.admin.dashboard import DashboardScreen
            page.add(DashboardScreen(page))
        elif route == "members":
            from gui.admin.members import MembersScreen
            page.add(MembersScreen(page))
        elif route == "packages":
            from gui.admin.memberships import MembershipsScreen
            page.add(MembershipsScreen(page))
        elif route == "equipment":
            from gui.admin.equipment import EquipmentScreen
            page.add(EquipmentScreen(page))
        elif route == "trainers":
            from gui.admin.trainers import TrainersScreen
            page.add(TrainersScreen(page))
        elif route == "attendance":
            from gui.admin.attendance import AttendanceScreen
            page.add(AttendanceScreen(page))
        elif route == "face_register":
            from gui.admin.face_register import FaceRegisterScreen
            page.add(FaceRegisterScreen(page))
        elif route == "reports":
            from gui.admin.reports import ReportsScreen
            page.add(ReportsScreen(page))
        else:
            # Route không hợp lệ → mặc định về Login
            from gui.admin.login import LoginScreen
            page.add(LoginScreen(page))

        page.update()  # BẮT BUỘC gọi sau khi thay đổi controls → Flet render lại UI

    # ── Bước 4: Gắn hàm navigate vào page ────────────────────────────────────
    # page.navigate KHÔNG phải thuộc tính mặc định của Flet
    # Đây là kỹ thuật "monkey patching" — thêm thuộc tính tùy chỉnh vào object
    # → Cho phép BẤT KỲ screen nào cũng có thể gọi: page.navigate("dashboard")
    page.navigate = navigate

    # ── Bước 5: Hiển thị màn hình đầu tiên ───────────────────────────────────
    navigate("login")  # Khởi động tại màn hình đăng nhập


# ══════════════════════════════════════════════════════════════════════════════
# KHỞI CHẠY ỨNG DỤNG
# ══════════════════════════════════════════════════════════════════════════════
# ft.run(main) = Flet khởi tạo cửa sổ desktop, rồi gọi main(page)
# Đây là dòng code ĐẦU TIÊN được thực thi khi chạy: python app/main.py
ft.run(main)
