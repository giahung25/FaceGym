# ============================================================================
# FILE: gui/user/trainer_notifications.py
# MỤC ĐÍCH: Thông báo cho HLV — tái sử dụng notification_svc.
# ============================================================================

import flet as ft
from gui import theme
from app.services import notification_svc


def TrainerNotificationsScreen(page: ft.Page) -> ft.Container:
    """Màn hình thông báo cho HLV."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    # Kiểm tra thông báo tự động khi mở trang
    notification_svc.check_trainer_notifications(current_user.id)

    notifs = notification_svc.get_notifications(current_user.id, "trainer")

    def handle_mark_one(notif_id):
        notification_svc.mark_read(notif_id)
        if navigate:
            navigate("trainer_notifications")

    def handle_mark_all(e):
        notification_svc.mark_all_read(current_user.id, "trainer")
        if navigate:
            navigate("trainer_notifications")

    # ── Notification cards ──────────────────────────────────────────────────
    if not notifs:
        list_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.NOTIFICATIONS_OFF_OUTLINED, size=48, color=theme.GRAY),
                ft.Text("Bạn không có thông báo nào.", color=theme.GRAY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            padding=40, alignment=ft.Alignment.CENTER,
        )
    else:
        cards = []
        for notif in notifs:
            is_read = notif.is_read
            icon_color = theme.GRAY if is_read else theme.ORANGE
            bg_color = theme.WHITE if is_read else "#FFF4ED"

            cards.append(ft.Container(
                content=ft.Row([
                    ft.Icon(
                        ft.Icons.NOTIFICATIONS_NONE_ROUNDED if is_read
                        else ft.Icons.NOTIFICATIONS_ACTIVE_ROUNDED,
                        color=icon_color,
                    ),
                    ft.Column([
                        ft.Text(
                            notif.title,
                            weight=ft.FontWeight.BOLD if not is_read else ft.FontWeight.NORMAL,
                            size=theme.FONT_MD,
                        ),
                        ft.Text(notif.message, color=theme.GRAY, size=theme.FONT_SM),
                        ft.Text(str(notif.created_at)[:16], color=theme.GRAY_LIGHT, size=theme.FONT_XS),
                    ], spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
                        icon_color=theme.GREEN if is_read else theme.GRAY,
                        disabled=is_read,
                        on_click=lambda e, nid=notif.id: handle_mark_one(nid),
                    ),
                ]),
                bgcolor=bg_color, padding=20, border_radius=16,
                shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
            ))

        list_content = ft.Column(controls=cards, spacing=16)

    # ── Layout ──────────────────────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column([
            ft.Row([
                ft.Text("Thông báo", size=theme.FONT_2XL,
                         weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
                ft.Container(expand=True),
                ft.TextButton(
                    "Đánh dấu đã đọc tất cả",
                    icon=ft.Icons.DONE_ALL_ROUNDED,
                    on_click=handle_mark_all,
                ),
            ]),
            ft.Container(height=16),
            list_content,
        ], scroll=ft.ScrollMode.AUTO),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "trainer_notifications"), content],
            spacing=0, expand=True,
        ),
    )
