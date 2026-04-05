# ============================================================================
# FILE: gui/user/user_dashboard.py
# MỤC ĐÍCH: Trang chủ hội viên — gói tập active + quick actions.
#
# THIẾT KẾ: Giống admin — plain function DashboardScreen(page),
#            layout: UserSidebar + content area.
# ============================================================================

from datetime import datetime
import flet as ft
from gui import theme
from app.repositories import membership_repo
from app.services import attendance_svc


def DashboardScreen(page: ft.Page) -> ft.Container:
    """Trang chủ hội viên."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    active_subs = membership_repo.get_active_subscriptions_by_member(current_user.id)

    # ── Welcome section ───────────────────────────────────────────────────────
    welcome_section = ft.Container(
        content=ft.Row([
            ft.Column(
                controls=[
                    ft.Text(
                        f"Xin chào, {current_user.name}",
                        size=theme.FONT_2XL, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY,
                    ),
                    ft.Text("Chúc bạn một ngày tập luyện hiệu quả!", size=theme.FONT_MD, color=theme.GRAY),
                ],
                spacing=4,
            ),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Icon(ft.Icons.FITNESS_CENTER, size=32, color=theme.WHITE),
                bgcolor=theme.ORANGE, padding=12, border_radius=16,
                shadow=ft.BoxShadow(blur_radius=15, color=f"{theme.ORANGE}40", offset=ft.Offset(0, 8)),
            ),
        ]),
        margin=ft.margin.only(bottom=32),
    )

    # ── Subscriptions section ─────────────────────────────────────────────────
    if not active_subs:
        subs_section = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.EVENT_BUSY_OUTLINED, size=48, color=theme.GRAY),
                    ft.Text(
                        "Hiện tại bạn chưa đăng ký gói tập nào, hoặc gói tập đã hết hạn.",
                        size=theme.FONT_MD, color=theme.GRAY, text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        "Đăng ký mua gói ngay",
                        icon=ft.Icons.ADD_SHOPPING_CART,
                        bgcolor=theme.ORANGE, color=theme.WHITE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=16),
                        on_click=lambda e: navigate("membership") if navigate else None,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            bgcolor=theme.WHITE, border_radius=20, padding=40,
            alignment=ft.Alignment.CENTER,
            shadow=ft.BoxShadow(blur_radius=20, color="#00000008", offset=ft.Offset(0, 10)),
        )
    else:
        cards = []
        for sub in active_subs:
            plan = membership_repo.get_plan_by_id(sub.plan_id)
            plan_name = plan.name if plan else "Không rõ gói"
            today = datetime.now().date()
            end_date = (
                sub.end_date.date() if hasattr(sub.end_date, "date")
                else datetime.strptime(str(sub.end_date)[:10], "%Y-%m-%d").date()
            )
            days_left = (end_date - today).days
            status_color = theme.GREEN_LIGHT if days_left > 7 else theme.RED_LIGHT
            text_color = theme.GREEN if days_left > 7 else theme.RED

            cards.append(ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.STAR_ROUNDED, color=theme.WHITE),
                        bgcolor=theme.ORANGE, padding=16, border_radius=16,
                    ),
                    ft.Column([
                        ft.Text(plan_name, size=theme.FONT_LG, weight=ft.FontWeight.W_700),
                        ft.Text(f"Hiệu lực đến: {str(sub.end_date)[:10]}", size=theme.FONT_SM, color=theme.GRAY),
                    ], spacing=4),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(f"Còn {days_left} ngày", color=text_color, weight=ft.FontWeight.BOLD),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=12,
                    ),
                ]),
                bgcolor=theme.WHITE, border_radius=16, padding=20,
                margin=ft.margin.only(bottom=16),
                shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
            ))

        subs_section = ft.Column([
            ft.Text("Gói tập hiện tại của bạn", size=theme.FONT_XL, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            *cards,
        ])

    # ── Quick actions ─────────────────────────────────────────────────────────
    def quick_action(title, icon, route):
        return ft.Container(
            content=ft.Row([ft.Icon(icon, color=theme.ORANGE), ft.Text(title, weight=ft.FontWeight.W_600)]),
            bgcolor=theme.WHITE,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            border_radius=16,
            on_click=lambda e, r=route: navigate(r) if navigate else None,
            ink=True,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000005", offset=ft.Offset(0, 4)),
        )

    quick_actions = ft.Container(
        content=ft.Row([
            quick_action("Xem khóa học", ft.Icons.CARD_MEMBERSHIP, "membership"),
            quick_action("Lịch sử mua", ft.Icons.HISTORY_ROUNDED, "history"),
            quick_action("Đổi mật khẩu", ft.Icons.LOCK_RESET_ROUNDED, "profile"),
        ], spacing=20),
        margin=ft.margin.only(top=32),
    )

    # ── Attendance section ───────────────────────────────────────────────────
    att_records = attendance_svc.get_member_attendance(current_user.id, limit=5)
    if att_records:
        att_rows = []
        for att in att_records:
            check_in_str = ""
            if att.check_in:
                try:
                    dt = datetime.fromisoformat(att.check_in)
                    check_in_str = dt.strftime("%d/%m/%Y %H:%M")
                except Exception:
                    check_in_str = str(att.check_in)
            method_label = att.method or "face_id"
            method_color = theme.GREEN if method_label == "face_id" else theme.BLUE
            att_rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=theme.GREEN),
                        ft.Text(check_in_str, size=theme.FONT_SM, expand=True),
                        ft.Container(
                            content=ft.Text(method_label, size=theme.FONT_XS, color=theme.WHITE,
                                            weight=ft.FontWeight.W_600),
                            bgcolor=method_color, border_radius=theme.BADGE_RADIUS,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        ),
                    ], spacing=theme.PAD_SM),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
                )
            )
        attendance_section = ft.Container(
            content=ft.Column([
                ft.Text("Lịch sử điểm danh gần đây", size=theme.FONT_XL, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                *att_rows,
            ]),
            bgcolor=theme.WHITE, border_radius=16, padding=20,
            margin=ft.margin.only(top=24),
            shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
        )
    else:
        attendance_section = ft.Container()

    # ── Layout: sidebar + content ─────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column(
            [welcome_section, subs_section, quick_actions, attendance_section],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "dashboard"), content],
            spacing=0,
            expand=True,
        ),
    )
