# ============================================================================
# FILE: gui/admin/components/sidebar.py
# MỤC ĐÍCH: Component SIDEBAR — thanh menu bên trái của ứng dụng.
#            Chứa: logo, các menu item (Dashboard, Members, Packages, Equipment, Reports),
#            và nút "Add Member".
#
# CÁCH DÙNG:
#   from gui.admin.components.sidebar import Sidebar
#   sidebar = Sidebar(page, active_route="dashboard")  # Menu Dashboard đang active
#
# LAYOUT TỔNG THỂ:
#   ┌─────────────┬────────────────────────────────────────────┐
#   │  SIDEBAR    │                                            │
#   │  ────────   │              CONTENT AREA                  │
#   │  Dashboard  │              (thay đổi theo route)         │
#   │  Members    │                                            │
#   │  Packages   │                                            │
#   │  Equipment  │                                            │
#   │  Reports    │                                            │
#   │             │                                            │
#   │ [Add Member]│                                            │
#   └─────────────┴────────────────────────────────────────────┘
# ============================================================================

import flet as ft
from gui import theme


def Sidebar(page: ft.Page, active_route: str = "dashboard") -> ft.Container:
    """Tạo component Sidebar — menu điều hướng bên trái.

    Tham số:
        page (ft.Page): đối tượng Page — để gọi navigate khi click menu
        active_route (str): route đang active — để highlight menu tương ứng
                            VD: "dashboard", "members", "packages", "equipment", "reports"

    Trả về:
        ft.Container: widget sidebar hoàn chỉnh (chiều rộng 220px)
    """

    # ── Danh sách icon cho từng menu item ─────────────────────────────────────
    # Dictionary: key = route name, value = Flet icon
    nav_icons = {
        "dashboard": ft.Icons.DASHBOARD_ROUNDED,
        "members": ft.Icons.PEOPLE_ALT_ROUNDED,
        "packages": ft.Icons.FITNESS_CENTER_ROUNDED,
        "attendance": ft.Icons.FACT_CHECK_ROUNDED,
        "face_register": ft.Icons.FACE_RETOUCHING_NATURAL,
        "equipment": ft.Icons.SETTINGS_ROUNDED,
        "trainers": ft.Icons.SPORTS_ROUNDED,
        "reports": ft.Icons.BAR_CHART_ROUNDED,
    }

    # ── Danh sách label (tên hiển thị) cho từng menu ──────────────────────────
    nav_labels = {
        "dashboard": "Bảng điều khiển",
        "members": "Hội viên",
        "packages": "Gói tập",
        "attendance": "Điểm danh",
        "face_register": "Đăng ký Face ID",
        "equipment": "Thiết bị",
        "trainers": "Huấn luyện viên",
        "reports": "Báo cáo",
    }

    # ── Lấy hàm navigate từ page ─────────────────────────────────────────────
    # getattr(page, "navigate", None): lấy thuộc tính navigate, nếu không có → None
    # navigate được gắn vào page ở main.py (monkey patching)
    navigate = getattr(page, "navigate", None)

    def make_nav_item(route: str) -> ft.Container:
        """Tạo 1 menu item trong sidebar.

        Tham số:
            route (str): route tương ứng (VD: "dashboard", "members")

        Trả về:
            ft.Container: widget menu item với icon + label

        Logic:
        - Nếu route == active_route → highlight (nền cam, chữ trắng)
        - Nếu không → bình thường (nền trong suốt, chữ xám)
        """
        is_active = route == active_route  # True nếu menu này đang được chọn
        label = nav_labels[route]           # Lấy tên hiển thị

        def on_click(e, r=route):
            """Xử lý khi click menu item.

            LƯU Ý: r=route dùng kỹ thuật "default parameter binding"
            - Nếu viết: lambda e: navigate(route) → route luôn là giá trị CUỐI CÙNG
              (vì Python closure capture biến, không capture giá trị)
            - Viết: lambda e, r=route → r được gán = giá trị route TẠI THỜI ĐIỂM tạo
            """
            if navigate:       # Kiểm tra navigate tồn tại
                navigate(r)    # Chuyển sang màn hình tương ứng

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        nav_icons[route],
                        size=18,
                        # Active → trắng, inactive → xám
                        color=theme.WHITE if is_active else theme.GRAY,
                    ),
                    ft.Text(
                        label,
                        size=theme.FONT_SM,
                        # Active → bold, inactive → normal
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_400,
                        color=theme.WHITE if is_active else theme.GRAY,
                    ),
                ],
                spacing=theme.PAD_MD,
            ),
            # Active → nền cam, inactive → trong suốt
            bgcolor=theme.ORANGE if is_active else "transparent",
            border_radius=theme.BUTTON_RADIUS,
            padding=ft.padding.symmetric(horizontal=theme.PAD_MD, vertical=10),
            margin=ft.margin.symmetric(horizontal=theme.PAD_SM, vertical=2),
            on_click=on_click,  # Gắn hàm xử lý click
            ink=True,            # Hiệu ứng ripple khi click (Material Design)
        )

    # ── Tạo tất cả nav items ─────────────────────────────────────────────────
    # List comprehension: tạo 1 menu item cho mỗi route trong nav_icons
    nav_controls = [make_nav_item(r) for r in nav_icons]

    # ── Logo section (phần trên cùng sidebar) ─────────────────────────────────
    logo_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        # Logo: chữ "P" trên nền cam, bo góc
                        ft.Container(
                            content=ft.Text("P", color=theme.WHITE, size=20, weight=ft.FontWeight.BOLD),
                            width=36, height=36,
                            bgcolor=theme.ORANGE,
                            border_radius=8,
                            alignment=ft.Alignment.CENTER,
                        ),
                        # Tên app + subtitle
                        ft.Column(
                            controls=[
                                ft.Text("GymAdmin", color=theme.WHITE, size=theme.FONT_MD,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text("HỆ THỐNG QUẢN LÝ", color=theme.GRAY, size=8,
                                        weight=ft.FontWeight.W_500),
                            ],
                            spacing=0, tight=True,
                        ),
                    ],
                    spacing=theme.PAD_SM,
                ),
            ],
        ),
        padding=ft.padding.all(theme.PAD_XL),
    )

    # ── Nút "Add Member" (phần dưới sidebar) ─────────────────────────────────
    add_member_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD, color=theme.WHITE, size=16),
                ft.Text("Thêm hội viên", color=theme.WHITE, size=theme.FONT_SM,
                        weight=ft.FontWeight.W_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Căn giữa nội dung
            spacing=theme.PAD_XS,
        ),
        bgcolor=theme.ORANGE,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=10),
        margin=ft.margin.symmetric(horizontal=theme.PAD_MD, vertical=theme.PAD_MD),
        # Click → chuyển sang trang Members
        on_click=lambda e: navigate("members") if navigate else None,
        ink=True,
    )

    # ── Trả về Container sidebar hoàn chỉnh ──────────────────────────────────
    return ft.Container(
        content=ft.Column(
            controls=[
                logo_section,                          # Logo trên cùng
                ft.Divider(color="#2D2D44", height=1, thickness=1),  # Đường kẻ ngang
                ft.Container(
                    content=ft.Column(controls=nav_controls, spacing=0),  # Các menu items
                    padding=ft.padding.symmetric(vertical=theme.PAD_MD),
                    expand=True,  # Chiếm hết chiều cao còn lại (đẩy nút Add xuống dưới)
                ),
                add_member_btn,                        # Nút "Add Member" ở dưới cùng
            ],
            spacing=0,
            expand=True,
        ),
        width=theme.SIDEBAR_WIDTH,  # Chiều rộng cố định 220px
        bgcolor=theme.SIDEBAR_BG,    # Nền xanh đen
        expand=False,                 # KHÔNG co giãn theo cửa sổ
    )
