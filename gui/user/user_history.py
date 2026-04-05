# ============================================================================
# FILE: gui/user/user_history.py
# MỤC ĐÍCH: Lịch sử đăng ký gói tập của hội viên.
#
# THIẾT KẾ: Giống admin — plain function HistoryScreen(page).
# ============================================================================

import flet as ft
from gui import theme
from app.repositories import membership_repo


def HistoryScreen(page: ft.Page) -> ft.Container:
    """Màn hình lịch sử mua gói tập."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    subs = membership_repo.get_subscriptions_by_member(current_user.id)

    if not subs:
        list_content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, size=48, color=theme.GRAY),
                    ft.Text("Bạn chưa có lịch sử đăng ký gói tập nào.", color=theme.GRAY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=40,
            alignment=ft.Alignment.CENTER,
        )
    else:
        cards = []
        for sub in subs:
            plan = membership_repo.get_plan_by_id(sub.plan_id)
            plan_name = plan.name if plan else "Không rõ"

            if sub.status == "active":
                status_color, status_bg, status_text = theme.GREEN, theme.GREEN_LIGHT, "ĐANG HOẠT ĐỘNG"
            elif sub.status == "expired":
                status_color, status_bg, status_text = theme.RED, theme.RED_LIGHT, "ĐÃ HẾT HẠN"
            else:
                status_color, status_bg, status_text = theme.GRAY, theme.GRAY_LIGHT, "ĐÃ HỦY"

            cards.append(ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, color=theme.GRAY),
                        bgcolor=theme.GRAY_LIGHT, padding=16, border_radius=12,
                    ),
                    ft.Column([
                        ft.Text(plan_name, weight=ft.FontWeight.BOLD, size=theme.FONT_LG),
                        ft.Text(
                            f"Bắt đầu: {str(sub.start_date)[:10]} — Kết thúc: {str(sub.end_date)[:10]}",
                            color=theme.GRAY, size=theme.FONT_SM,
                        ),
                    ], spacing=4),
                    ft.Container(expand=True),
                    ft.Text(f"{sub.price_paid:,.0f} đ", size=theme.FONT_LG, weight=ft.FontWeight.BOLD, color=theme.ORANGE),
                    ft.Container(width=16),
                    ft.Container(
                        content=ft.Text(status_text, color=status_color, size=theme.FONT_XS, weight=ft.FontWeight.BOLD),
                        bgcolor=status_bg,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=8,
                    ),
                ]),
                bgcolor=theme.WHITE, padding=20, border_radius=16,
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
                ft.Text("Lịch sử mua gói tập", size=theme.FONT_2XL, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
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
            controls=[UserSidebar(page, "history"), content],
            spacing=0,
            expand=True,
        ),
    )
