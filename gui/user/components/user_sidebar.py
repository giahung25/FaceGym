# ============================================================================
# FILE: gui/user/components/user_sidebar.py
# MỤC ĐÍCH: Sidebar điều hướng User App.
#
# THIẾT KẾ: Giống admin Sidebar(page, active_route) — plain function,
#            lấy state từ page.current_role, gọi page.navigate(route).
# ============================================================================

import flet as ft
from gui import theme
from app.services import notification_svc


def UserSidebar(page: ft.Page, active_route: str = "dashboard") -> ft.Container:
    """Tạo sidebar điều hướng User App.

    Tham số:
        page (ft.Page): đối tượng Page — truy cập page.current_role, page.navigate
        active_route (str): route đang active — VD: "dashboard", "profile", ...

    Trả về:
        ft.Container: sidebar hoàn chỉnh (width=260px)
    """
    role = getattr(page, "current_role", "member")
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    # ── Unread notifications badge ────────────────────────────────────────────
    unread_count = 0
    if current_user:
        try:
            unread_count = notification_svc.get_unread_count(current_user.id, role)
        except Exception:
            unread_count = 0

    # ── Nav items theo role ───────────────────────────────────────────────────
    if role == "member":
        nav_items = [
            ("dashboard",      ft.Icons.HOME_ROUNDED,              "Trang chủ"),
            ("profile",        ft.Icons.PERSON_ROUNDED,            "Thông tin cá nhân"),
            ("schedule",       ft.Icons.CALENDAR_MONTH_ROUNDED,    "Lịch tập"),
            ("membership",     ft.Icons.CARD_MEMBERSHIP_ROUNDED,   "Khóa học & Gói tập"),
            ("history",             ft.Icons.HISTORY_ROUNDED,           "Lịch sử mua"),
            ("attendance_history",  ft.Icons.FACT_CHECK_ROUNDED,        "Lịch sử điểm danh"),
            ("notifications",       ft.Icons.NOTIFICATIONS_ROUNDED,     "Thông báo"),
        ]
    else:
        nav_items = [
            ("trainer",                ft.Icons.HOME_ROUNDED,              "Trang chủ"),
            ("trainer_students",       ft.Icons.PEOPLE_ROUNDED,            "Học viên"),
            ("trainer_schedule",       ft.Icons.CALENDAR_MONTH_ROUNDED,    "Lịch dạy"),
            ("trainer_profile",        ft.Icons.PERSON_ROUNDED,            "Thông tin cá nhân"),
            ("trainer_notifications",  ft.Icons.NOTIFICATIONS_ROUNDED,     "Thông báo"),
        ]

    def make_nav_item(route: str, icon, label: str) -> ft.Container:
        is_active = route == active_route

        # Badge thông báo chưa đọc
        badge_control = None
        if route in ("notifications", "trainer_notifications") and unread_count > 0:
            badge_control = ft.Container(
                content=ft.Text(str(unread_count), size=10, weight=ft.FontWeight.BOLD, color=theme.WHITE),
                bgcolor=theme.RED,
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.Alignment.CENTER,
            )

        row_controls = [
            ft.Icon(icon, size=18, color=theme.WHITE if is_active else theme.GRAY),
            ft.Text(
                label,
                size=theme.FONT_SM,
                weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_400,
                color=theme.WHITE if is_active else theme.GRAY,
            ),
        ]
        if badge_control:
            row_controls.append(ft.Container(expand=True))
            row_controls.append(badge_control)

        def on_click(e, r=route):
            if navigate:
                navigate(r)

        return ft.Container(
            content=ft.Row(controls=row_controls, spacing=theme.PAD_MD),
            bgcolor=theme.ORANGE if is_active else "transparent",
            border_radius=theme.BUTTON_RADIUS,
            padding=ft.padding.symmetric(horizontal=theme.PAD_MD, vertical=10),
            margin=ft.margin.symmetric(horizontal=theme.PAD_SM, vertical=2),
            on_click=on_click,
            ink=True,
        )

    nav_controls = [make_nav_item(r, ic, lbl) for r, ic, lbl in nav_items]

    # ── Logout ────────────────────────────────────────────────────────────────
    def do_logout(e):
        page.current_user = None
        page.current_role = "member"
        if navigate:
            navigate("login")

    logout_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOGOUT, color=theme.RED, size=20),
                ft.Text("Đăng xuất", color=theme.RED, size=theme.FONT_MD, weight=ft.FontWeight.W_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        ),
        bgcolor=f"{theme.RED}1A",
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=16, vertical=14),
        margin=ft.margin.all(20),
        on_click=do_logout,
        ink=True,
    )

    # ── Logo ──────────────────────────────────────────────────────────────────
    logo_section = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.FITNESS_CENTER_ROUNDED, size=24, color=theme.WHITE),
                    width=48, height=48,
                    bgcolor=theme.ORANGE,
                    border_radius=12,
                    alignment=ft.Alignment.CENTER,
                    shadow=ft.BoxShadow(blur_radius=12, color=f"{theme.ORANGE}40", offset=ft.Offset(0, 4)),
                ),
                ft.Column(
                    controls=[
                        ft.Text("GymFit", color=theme.WHITE, size=22, weight=ft.FontWeight.W_900),
                        ft.Text("CỔNG HỘI VIÊN", color=theme.GRAY, size=10, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=0,
                    tight=True,
                ),
            ],
            spacing=16,
        ),
        padding=ft.padding.only(left=24, right=24, top=32, bottom=32),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                logo_section,
                ft.Divider(color="#2D2D44", height=1, thickness=1),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column(controls=nav_controls, spacing=0),
                    expand=True,
                ),
                logout_btn,
            ],
            spacing=0,
            expand=True,
        ),
        width=260,
        bgcolor="#18182A",
        expand=False,
    )
