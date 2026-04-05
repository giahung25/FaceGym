# ============================================================================
# FILE: gui/user/trainer_profile.py
# MỤC ĐÍCH: Thông tin cá nhân HLV + thống kê + đổi PIN.
# ============================================================================

import flet as ft
from gui import theme
from app.services import auth_svc, assignment_svc, schedule_svc


def TrainerProfileScreen(page: ft.Page) -> ft.Container:
    """Màn hình thông tin cá nhân HLV."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    # ── Thống kê ────────────────────────────────────────────────────────────
    student_count = len(assignment_svc.get_trainer_students(current_user.id))
    session_count = schedule_svc.count_sessions_this_month(current_user.id)

    # ── Info helpers ────────────────────────────────────────────────────────
    def info_row(label, value):
        return ft.Row([
            ft.Text(label, color=theme.GRAY, width=150),
            ft.Text(str(value), weight=ft.FontWeight.BOLD),
        ])

    info_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.BADGE, color=theme.ORANGE),
                ft.Text("Thông tin cá nhân", size=theme.FONT_XL, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Divider(color=theme.GRAY_LIGHT),
            info_row("Họ tên", current_user.name),
            info_row("SĐT", current_user.phone),
            info_row("Email", getattr(current_user, "email", None) or "Chưa cập nhật"),
            info_row("Chuyên môn", getattr(current_user, "specialization", None) or "Chưa cập nhật"),
            info_row("Ngày tham gia", str(getattr(current_user, "created_at", ""))[:10]),
        ], spacing=16),
        bgcolor=theme.WHITE, border_radius=16, padding=32,
        shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
    )

    # ── Stats cards ─────────────────────────────────────────────────────────
    def stat_card(value, label, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(str(value), size=theme.FONT_3XL, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=theme.FONT_SM, color=theme.GRAY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            bgcolor=theme.WHITE, border_radius=16, padding=24,
            shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
            expand=True,
        )

    stats_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.INSIGHTS, color=theme.ORANGE),
                ft.Text("Thống kê", size=theme.FONT_XL, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=8),
            ft.Row([
                stat_card(student_count, "Học viên đang kèm", theme.BLUE),
                stat_card(session_count, "Buổi tập tháng này", theme.GREEN),
            ], spacing=16),
        ], spacing=0),
    )

    # ── PIN form ────────────────────────────────────────────────────────────
    pin_input_filter = ft.InputFilter(regex_string=r"[0-9]", allow=True, replacement_string="")
    old_pin = ft.TextField(
        label="PIN hiện tại (6 số)", password=True, can_reveal_password=True,
        max_length=6, border_radius=theme.BUTTON_RADIUS, focused_border_color=theme.ORANGE,
        input_filter=pin_input_filter,
    )
    new_pin = ft.TextField(
        label="PIN mới (6 số)", password=True, can_reveal_password=True,
        max_length=6, border_radius=theme.BUTTON_RADIUS, focused_border_color=theme.ORANGE,
        input_filter=pin_input_filter,
    )
    confirm_pin = ft.TextField(
        label="Xác nhận PIN mới", password=True, can_reveal_password=True,
        max_length=6, border_radius=theme.BUTTON_RADIUS, focused_border_color=theme.ORANGE,
        input_filter=pin_input_filter,
    )
    msg_text = ft.Text("", size=theme.FONT_SM, weight=ft.FontWeight.W_500)

    def handle_change_pin(e):
        msg_text.color = theme.RED
        msg_text.value = ""

        if not old_pin.value or not new_pin.value or not confirm_pin.value:
            msg_text.value = "Vui lòng nhập đầy đủ các trường."
            page.update()
            return
        if len(old_pin.value) != 6 or not old_pin.value.isdigit():
            msg_text.value = "PIN hiện tại phải gồm đúng 6 chữ số."
            page.update()
            return
        if len(new_pin.value) != 6 or not new_pin.value.isdigit():
            msg_text.value = "PIN mới phải gồm đúng 6 chữ số."
            page.update()
            return
        if new_pin.value != confirm_pin.value:
            msg_text.value = "PIN xác nhận không khớp."
            page.update()
            return

        try:
            success = auth_svc.change_pin("trainer", current_user.id, old_pin.value, new_pin.value)
        except ValueError as ex:
            msg_text.value = str(ex)
            page.update()
            return

        if success:
            msg_text.color = theme.GREEN
            msg_text.value = "Đổi PIN thành công!"
            old_pin.value = new_pin.value = confirm_pin.value = ""
        else:
            msg_text.value = "PIN hiện tại không chính xác."
        page.update()

    pin_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.VPN_KEY, color=theme.ORANGE),
                ft.Text("Đổi mã PIN", size=theme.FONT_XL, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Divider(color=theme.GRAY_LIGHT),
            old_pin, new_pin, confirm_pin, msg_text,
            ft.Row([
                ft.ElevatedButton(
                    "Đổi mã PIN", icon=ft.Icons.LOCK_RESET,
                    bgcolor=theme.ORANGE, color=theme.WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=16),
                    on_click=handle_change_pin,
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], spacing=16),
        bgcolor=theme.WHITE, border_radius=16, padding=32,
        shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
    )

    # ── Layout ──────────────────────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column([
            info_card,
            ft.Container(height=16),
            stats_section,
            ft.Container(height=16),
            pin_card,
        ], scroll=ft.ScrollMode.AUTO),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "trainer_profile"), content],
            spacing=0, expand=True,
        ),
    )
