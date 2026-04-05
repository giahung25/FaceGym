# ============================================================================
# FILE: gui/user/user_notifications.py
# MỤC ĐÍCH: Trang thông báo hệ thống.
#
# THIẾT KẾ: Giống admin — plain function NotificationsScreen(page).
#            Refresh sau khi mark read: page.navigate("notifications") rebuild screen.
# ============================================================================

import flet as ft
from gui import theme
from app.services import notification_svc


def NotificationsScreen(page: ft.Page) -> ft.Container:
    """Màn hình thông báo — xem + đánh dấu đã đọc."""
    current_user = getattr(page, "current_user", None)
    role = getattr(page, "current_role", "member")
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    notifs = notification_svc.get_notifications(current_user.id, role)

    def handle_mark_one(notif_id):
        notification_svc.mark_read(notif_id)
        # Rebuild toàn màn hình để cập nhật badge + danh sách
        if navigate:
            navigate("notifications")

    def handle_mark_all(e):
        notification_svc.mark_all_read(current_user.id, role)
        if navigate:
            navigate("notifications")

    # ── Notification cards ────────────────────────────────────────────────────
    if not notifs:
        list_content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.NOTIFICATIONS_OFF_OUTLINED, size=48, color=theme.GRAY),
                    ft.Text("Bạn không có thông báo nào.", color=theme.GRAY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=40,
            alignment=ft.Alignment.CENTER,
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
                        ft.Icons.NOTIFICATIONS_NONE_ROUNDED if is_read else ft.Icons.NOTIFICATIONS_ACTIVE_ROUNDED,
                        color=icon_color,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                notif.title,
                                weight=ft.FontWeight.BOLD if not is_read else ft.FontWeight.NORMAL,
                                size=theme.FONT_MD,
                            ),
                            ft.Text(notif.message, color=theme.GRAY, size=theme.FONT_SM),
                            ft.Text(str(notif.created_at)[:16], color=theme.GRAY_LIGHT, size=theme.FONT_XS),
                        ],
                        spacing=2,
                        expand=True,
                    ),
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

    # ── Layout: sidebar + content ─────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column(
            [
                ft.Row([
                    ft.Text("Thông báo hệ thống", size=theme.FONT_2XL, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "Đánh dấu đã đọc tất cả",
                        icon=ft.Icons.DONE_ALL_ROUNDED,
                        on_click=handle_mark_all,
                    ),
                ]),
                ft.Container(height=16),
                list_content,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "notifications"), content],
            spacing=0,
            expand=True,
        ),
    )
