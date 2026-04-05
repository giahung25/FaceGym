# ============================================================================
# FILE: gui/user/user_profile.py
# MỤC ĐÍCH: Trang thông tin cá nhân + đổi PIN.
#
# THIẾT KẾ: Giống admin — plain function ProfileScreen(page), state PIN form
#            quản lý bằng ft.TextField refs + closure + page.update().
# ============================================================================

import flet as ft
from gui import theme
from app.services import auth_svc


def ProfileScreen(page: ft.Page) -> ft.Container:
    """Màn hình thông tin tài khoản + đổi mã PIN."""
    current_user = getattr(page, "current_user", None)
    role = getattr(page, "current_role", "member")
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    # ── Info helpers ──────────────────────────────────────────────────────────
    def info_row(label, value):
        return ft.Row([
            ft.Text(label, color=theme.GRAY, width=150),
            ft.Text(str(value), weight=ft.FontWeight.BOLD),
        ])

    info_card = ft.Container(
        content=ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.BADGE, color=theme.ORANGE),
                    ft.Text("Thông tin tài khoản", size=theme.FONT_XL, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Divider(color=theme.GRAY_LIGHT),
                info_row("Họ và tên", current_user.name),
                info_row("Số điện thoại", current_user.phone),
                info_row("Giới tính", getattr(current_user, "gender", None) or "Chưa cập nhật"),
                info_row("SĐT khẩn cấp", getattr(current_user, "emergency_contact", None) or "Chưa cập nhật"),
                info_row("Ngày tham gia", str(getattr(current_user, "created_at", ""))[:10]),
            ],
            spacing=16,
        ),
        bgcolor=theme.WHITE, border_radius=16, padding=32,
        shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
    )

    # ── PIN form — dùng TextField refs + closure + page.update() ─────────────
    pin_input_filter = ft.InputFilter(regex_string=r"[0-9]", allow=True, replacement_string="")
    old_pin_field = ft.TextField(
        label="Mã PIN cũ (6 số)", password=True, can_reveal_password=True,
        max_length=6, border_radius=theme.BUTTON_RADIUS, focused_border_color=theme.ORANGE,
        input_filter=pin_input_filter,
    )
    new_pin_field = ft.TextField(
        label="Mã PIN mới (6 số)", password=True, can_reveal_password=True,
        max_length=6, border_radius=theme.BUTTON_RADIUS, focused_border_color=theme.ORANGE,
        input_filter=pin_input_filter,
    )
    confirm_pin_field = ft.TextField(
        label="Xác nhận PIN mới (6 số)", password=True, can_reveal_password=True,
        max_length=6, border_radius=theme.BUTTON_RADIUS, focused_border_color=theme.ORANGE,
        input_filter=pin_input_filter,
    )
    msg_text = ft.Text("", size=theme.FONT_SM, weight=ft.FontWeight.W_500)

    def handle_change_pin(e):
        old_pin = old_pin_field.value or ""
        new_pin = new_pin_field.value or ""
        confirm_pin = confirm_pin_field.value or ""
        msg_text.color = theme.RED
        msg_text.value = ""

        if not old_pin or not new_pin or not confirm_pin:
            msg_text.value = "Vui lòng nhập đầy đủ các trường."
            page.update()
            return
        if len(old_pin) != 6 or not old_pin.isdigit():
            msg_text.value = "Mã PIN cũ phải gồm đúng 6 chữ số."
            page.update()
            return
        if len(new_pin) != 6 or not new_pin.isdigit():
            msg_text.value = "Mã PIN mới phải gồm đúng 6 chữ số."
            page.update()
            return
        if new_pin != confirm_pin:
            msg_text.value = "Mã PIN xác nhận không khớp."
            page.update()
            return

        try:
            success = auth_svc.change_pin(role, current_user.id, old_pin, new_pin)
        except ValueError as ex:
            msg_text.value = str(ex)
            page.update()
            return

        if success:
            msg_text.color = theme.GREEN
            msg_text.value = "Đổi mã PIN thành công!"
            old_pin_field.value = ""
            new_pin_field.value = ""
            confirm_pin_field.value = ""
        else:
            msg_text.value = "Mã PIN cũ không chính xác."
        page.update()

    pin_card = ft.Container(
        content=ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.VPN_KEY, color=theme.ORANGE),
                    ft.Text("Đổi mã PIN", size=theme.FONT_XL, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Divider(color=theme.GRAY_LIGHT),
                old_pin_field,
                new_pin_field,
                confirm_pin_field,
                msg_text,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Đổi mã PIN",
                            icon=ft.Icons.LOCK_RESET,
                            bgcolor=theme.ORANGE, color=theme.WHITE,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=16),
                            on_click=handle_change_pin,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            spacing=16,
        ),
        bgcolor=theme.WHITE, border_radius=16, padding=32,
        shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
    )

    # ── Layout: sidebar + content ─────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column(
            [info_card, ft.Container(height=16), pin_card],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "profile"), content],
            spacing=0,
            expand=True,
        ),
    )
