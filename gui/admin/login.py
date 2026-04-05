# ============================================================================
# FILE: gui/admin/login.py
# MỤC ĐÍCH: Màn hình ĐĂNG NHẬP — màn hình đầu tiên khi mở app.
#            User nhập username/password → kiểm tra → chuyển sang Dashboard.
#
# LAYOUT:
#   ┌────────────────────────────────────────────────────────────┐
#   │                    (gradient background)                    │
#   │                                                            │
#   │                  ┌──────────────────┐                      │
#   │                  │     [G] Logo     │                      │
#   │                  │    GymAdmin      │                      │
#   │                  │                  │                      │
#   │                  │  Đăng nhập       │                      │
#   │                  │  [👤 Username ]  │                      │
#   │                  │  [🔒 Password ]  │                      │
#   │                  │  [  Đăng nhập ]  │                      │
#   │                  └──────────────────┘                      │
#   │                                                            │
#   └────────────────────────────────────────────────────────────┘
# ============================================================================

import flet as ft
from gui import theme
from app.core.security import check_login  # Hàm kiểm tra username/password


def LoginScreen(page: ft.Page) -> ft.Container:
    """Tạo màn hình đăng nhập.

    Tham số:
        page (ft.Page): đối tượng Page — dùng để navigate sang Dashboard khi login thành công

    Trả về:
        ft.Container: toàn bộ màn hình login (nền gradient + card đăng nhập)
    """

    # ── Khởi tạo các widget (controls) ────────────────────────────────────────
    # ft.Text hiển thị thông báo lỗi (ban đầu trống "")
    error_text = ft.Text("", color=theme.RED, size=theme.FONT_SM)

    # Ô nhập username
    username_field = ft.TextField(
        label="Tên đăng nhập",                     # Label hiển thị bên trong ô
        prefix_icon=ft.Icons.PERSON_OUTLINE,        # Icon người ở đầu ô
        border_radius=theme.BUTTON_RADIUS,          # Bo góc 8px
        focused_border_color=theme.ORANGE,          # Viền cam khi focus (click vào)
    )

    # Ô nhập password
    password_field = ft.TextField(
        label="Mật khẩu",
        prefix_icon=ft.Icons.LOCK_OUTLINE,          # Icon ổ khóa
        password=True,                               # Ẩn ký tự (hiện •••)
        can_reveal_password=True,                    # Cho phép click icon mắt để hiện password
        border_radius=theme.BUTTON_RADIUS,
        focused_border_color=theme.ORANGE,
    )

    # ── Hàm xử lý đăng nhập ─────────────────────────────────────────────────
    def do_login(e):
        """Được gọi khi: click nút "Đăng nhập" HOẶC nhấn Enter trong ô password.

        Tham số:
            e: event object từ Flet (chứa thông tin sự kiện click/submit)

        Flow:
        1. Xóa thông báo lỗi cũ
        2. Kiểm tra có nhập đủ username/password không
        3. Gọi check_login() để xác thực
        4. Nếu đúng → navigate sang Dashboard
        5. Nếu sai → hiện thông báo lỗi, xóa password
        """
        error_text.value = ""  # Xóa lỗi cũ

        # Kiểm tra nhập đủ thông tin
        # not username_field.value = True khi value là None hoặc "" (rỗng)
        if not username_field.value or not password_field.value:
            error_text.value = "Vui lòng nhập đầy đủ thông tin."
            page.update()  # Cập nhật UI để hiện thông báo lỗi
            return         # Dừng hàm, không kiểm tra tiếp

        # Kiểm tra đăng nhập
        if check_login(username_field.value, password_field.value):
            # Đúng → chuyển sang Dashboard
            page.navigate("dashboard")
        else:
            # Sai → hiện lỗi + xóa password (bảo mật)
            error_text.value = "Tên đăng nhập hoặc mật khẩu không đúng."
            password_field.value = ""    # Xóa password đã nhập
            page.update()

    # Cho phép nhấn Enter trong ô password để đăng nhập (thay vì phải click nút)
    password_field.on_submit = do_login

    # ── Card đăng nhập (khung trắng ở giữa) ──────────────────────────────────
    login_card = ft.Container(
        width=400,  # Chiều rộng card cố định 400px
        content=ft.Column(
            controls=[
                # ── Phần logo ─────────────────────────────────────────────
                ft.Column(
                    controls=[
                        # Logo: chữ "G" trên nền cam
                        ft.Container(
                            content=ft.Text("G", color=theme.WHITE, size=36,
                                            weight=ft.FontWeight.BOLD),
                            width=64, height=64,
                            bgcolor=theme.ORANGE,
                            border_radius=16,
                            alignment=ft.Alignment.CENTER,
                        ),
                        # Tên app
                        ft.Text("GymAdmin", size=theme.FONT_2XL,
                                weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                        # Subtitle
                        ft.Text("HỆ THỐNG QUẢN LÝ", size=theme.FONT_XS,
                                color=theme.GRAY, weight=ft.FontWeight.W_500),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Căn giữa ngang
                    spacing=theme.PAD_SM,
                ),

                ft.Container(height=theme.PAD_LG),  # Spacer (khoảng trống)

                # ── Tiêu đề form ──────────────────────────────────────────
                ft.Text("Đăng nhập", size=theme.FONT_LG, weight=ft.FontWeight.BOLD,
                        color=theme.TEXT_PRIMARY),
                ft.Container(height=theme.PAD_XS),

                # ── Các ô nhập ────────────────────────────────────────────
                username_field,      # Ô username
                password_field,      # Ô password
                error_text,          # Thông báo lỗi (ẩn khi chưa có lỗi)

                ft.Container(height=theme.PAD_XS),

                # ── Nút đăng nhập ─────────────────────────────────────────
                ft.Container(
                    content=ft.Text("Đăng nhập", color=theme.WHITE, size=theme.FONT_MD,
                                    weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                    bgcolor=theme.ORANGE,                        # Nền cam
                    border_radius=theme.BUTTON_RADIUS,
                    padding=ft.padding.symmetric(vertical=14),   # Padding dọc cho nút cao hơn
                    alignment=ft.Alignment.CENTER,
                    on_click=do_login,                           # Click → gọi do_login
                    ink=True,                                     # Hiệu ứng ripple
                ),
            ],
            spacing=theme.PAD_MD,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,  # Các control giãn hết chiều ngang
            tight=True,  # Column co lại vừa đúng nội dung
        ),
        bgcolor=theme.CARD_BG,         # Nền trắng
        border_radius=theme.CARD_RADIUS,  # Bo góc 12px
        padding=ft.padding.all(theme.PAD_2XL + theme.PAD_MD),  # Padding 36px (24+12)
        # Đổ bóng nhẹ cho card nổi lên khỏi nền
        shadow=ft.BoxShadow(blur_radius=24, color="#00000018", offset=ft.Offset(0, 4)),
    )

    # ── Container ngoài cùng (toàn màn hình) ─────────────────────────────────
    return ft.Container(
        expand=True,          # Chiếm toàn bộ diện tích page
        bgcolor=theme.BG,
        # Gradient nền: cam nhạt ở trên → xám ở dưới
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,     # Bắt đầu từ trên
            end=ft.Alignment.BOTTOM_CENTER,    # Kết thúc ở dưới
            colors=["#FFF0E6", theme.BG],      # Cam nhạt → xám
            stops=[0.0, 0.4],                  # Gradient kết thúc ở 40% chiều cao
        ),
        alignment=ft.Alignment.CENTER,  # Căn card vào GIỮA cả ngang lẫn dọc
        content=login_card,
    )
