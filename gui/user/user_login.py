# ============================================================================
# FILE: gui/user/user_login.py
# MỤC ĐÍCH: Màn hình đăng nhập — hội viên + HLV.
#
# THIẾT KẾ: Giống admin — plain function LoginScreen(page), dùng closure
#            để quản lý state role toggle, lưu user vào page.current_user.
# ============================================================================

import flet as ft
from gui import theme
from app.services import auth_svc, notification_svc


def LoginScreen(page: ft.Page) -> ft.Container:
    """Màn hình đăng nhập.

    Sau khi đăng nhập thành công:
      - Gán page.current_user, page.current_role
      - Gọi page.navigate("dashboard") hoặc page.navigate("trainer")
    """
    navigate = getattr(page, "navigate", None)
    selected_role = ["member"]  # list để closure có thể mutate

    # ── Role toggle buttons ───────────────────────────────────────────────────
    btn_member = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PERSON, size=18, color=theme.WHITE),
                ft.Text("Hội viên", weight=ft.FontWeight.BOLD, color=theme.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        expand=1,
        border_radius=theme.BUTTON_RADIUS,
        padding=10,
        bgcolor=theme.ORANGE,
        ink=True,
    )
    btn_trainer = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SPORTS, size=18, color=theme.GRAY),
                ft.Text("Huấn luyện viên", weight=ft.FontWeight.BOLD, color=theme.GRAY),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        expand=1,
        border_radius=theme.BUTTON_RADIUS,
        padding=10,
        bgcolor="transparent",
        ink=True,
    )

    def set_role(role: str):
        """Cập nhật UI role toggle + lưu state vào closure."""
        selected_role[0] = role
        is_member = role == "member"
        btn_member.bgcolor = theme.ORANGE if is_member else "transparent"
        btn_trainer.bgcolor = theme.ORANGE if not is_member else "transparent"
        btn_member.content.controls[0].color = theme.WHITE if is_member else theme.GRAY
        btn_member.content.controls[1].color = theme.WHITE if is_member else theme.GRAY
        btn_trainer.content.controls[0].color = theme.GRAY if is_member else theme.WHITE
        btn_trainer.content.controls[1].color = theme.GRAY if is_member else theme.WHITE
        page.update()

    btn_member.on_click = lambda e: set_role("member")
    btn_trainer.on_click = lambda e: set_role("trainer")

    role_selector = ft.Container(
        content=ft.Row(controls=[btn_member, btn_trainer], spacing=4),
        bgcolor=theme.GRAY_LIGHT,
        border_radius=theme.BUTTON_RADIUS,
        padding=4,
    )

    # ── Input fields ──────────────────────────────────────────────────────────
    phone_field = ft.TextField(
        label="Số điện thoại",
        prefix_icon=ft.Icons.PHONE,
        border_radius=theme.BUTTON_RADIUS,
        focused_border_color=theme.ORANGE,
        focused_color=theme.TEXT_PRIMARY,
        text_size=theme.FONT_MD,
        content_padding=16,
        max_length=11,
        input_filter=ft.InputFilter(regex_string=r"[0-9]", allow=True, replacement_string=""),
    )
    pin_field = ft.TextField(
        label="Mã PIN (6 số)",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_radius=theme.BUTTON_RADIUS,
        focused_border_color=theme.ORANGE,
        focused_color=theme.TEXT_PRIMARY,
        text_size=theme.FONT_MD,
        max_length=6,
        content_padding=16,
        input_filter=ft.InputFilter(regex_string=r"[0-9]", allow=True, replacement_string=""),
    )
    error_text = ft.Text("", color=theme.RED, size=theme.FONT_SM, weight=ft.FontWeight.W_500)

    # ── Login handler ─────────────────────────────────────────────────────────
    def do_login(e):
        phone = (phone_field.value or "").strip()
        pin = (pin_field.value or "").strip()
        error_text.value = ""

        if not phone or not pin:
            error_text.value = "Vui lòng nhập đầy đủ Số điện thoại và Mã PIN."
            page.update()
            return
        if not phone.isdigit() or len(phone) < 9 or len(phone) > 11:
            error_text.value = "Số điện thoại phải gồm 9-11 chữ số."
            page.update()
            return
        if not pin.isdigit() or len(pin) != 6:
            error_text.value = "Mã PIN phải gồm đúng 6 chữ số."
            page.update()
            return

        role = selected_role[0]
        if role == "member":
            user = auth_svc.login_member(phone, pin)
            if user:
                try:
                    notification_svc.check_expiring_subscriptions(user.id)
                except Exception:
                    pass
                page.current_user = user
                page.current_role = "member"
                if navigate:
                    navigate("dashboard")
                return
        else:
            user = auth_svc.login_trainer(phone, pin)
            if user:
                page.current_user = user
                page.current_role = "trainer"
                if navigate:
                    navigate("trainer")
                return

        error_text.value = "Số điện thoại hoặc mã PIN không đúng."
        page.update()

    pin_field.on_submit = do_login

    # ── Login button ──────────────────────────────────────────────────────────
    login_btn = ft.Container(
        content=ft.Text(
            "Đăng nhập",
            color=theme.WHITE,
            size=theme.FONT_MD,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        ),
        bgcolor=theme.ORANGE,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(vertical=16),
        alignment=ft.Alignment.CENTER,
        on_click=do_login,
        ink=True,
        shadow=ft.BoxShadow(blur_radius=15, color=f"{theme.ORANGE}40", offset=ft.Offset(0, 8)),
    )

    # ── Card ──────────────────────────────────────────────────────────────────
    login_card = ft.Container(
        width=420,
        content=ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.FITNESS_CENTER_ROUNDED, size=40, color=theme.WHITE),
                            width=80, height=80,
                            bgcolor=theme.ORANGE,
                            border_radius=24,
                            alignment=ft.Alignment.CENTER,
                            shadow=ft.BoxShadow(blur_radius=20, color=f"{theme.ORANGE}50", offset=ft.Offset(0, 10)),
                        ),
                        ft.Container(height=8),
                        ft.Text("GymFit", size=theme.FONT_3XL, weight=ft.FontWeight.W_900, color=theme.TEXT_PRIMARY),
                        ft.Text("CỔNG HỘI VIÊN", size=theme.FONT_XS, color=theme.GRAY, weight=ft.FontWeight.BOLD),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                ft.Container(height=24),
                role_selector,
                ft.Container(height=12),
                phone_field,
                ft.Container(height=16),
                pin_field,
                error_text,
                ft.Container(height=8),
                login_btn,
                ft.Container(height=16),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=theme.GRAY),
                        ft.Text("Lần đầu đăng nhập dùng PIN: 000000", size=theme.FONT_SM, color=theme.GRAY, italic=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        bgcolor=theme.WHITE,
        border_radius=24,
        padding=ft.padding.all(40),
        shadow=ft.BoxShadow(blur_radius=40, color="#00000010", offset=ft.Offset(0, 20)),
    )

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#FFF0E6", "#FFE4D6", "#F3F4F6"],
            stops=[0.0, 0.5, 1.0],
        ),
        alignment=ft.Alignment.CENTER,
        content=login_card,
    )
