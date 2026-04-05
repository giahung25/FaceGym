# ============================================================================
# FILE: gui/user/user_membership.py
# MỤC ĐÍCH: Trang đăng ký gói tập — xem gói hiện tại và mua gói mới.
#
# THIẾT KẾ: Giống admin — plain function MembershipScreen(page).
#            Tab switching: mutable list + direct control update + page.update().
#            Refresh sau mua: page.navigate("membership") rebuild toàn bộ screen.
# ============================================================================

from datetime import datetime, timedelta
import flet as ft
from gui import theme
from app.repositories import membership_repo
from app.models.membership import MembershipSubscription


def MembershipScreen(page: ft.Page) -> ft.Container:
    """Màn hình đăng ký & xem gói tập."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    active_subs = membership_repo.get_active_subscriptions_by_member(current_user.id)
    all_plans = membership_repo.get_all_plans(active_only=True)
    selected_tab = [0]  # mutable closure state: 0 = hiện tại, 1 = mua

    # ── Tab buttons ───────────────────────────────────────────────────────────
    btn_current = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.VERIFIED_USER_ROUNDED, size=16, color=theme.WHITE),
                ft.Text("Trạng thái hiện tại", color=theme.WHITE, weight=ft.FontWeight.W_600, size=theme.FONT_MD),
            ],
            spacing=8,
        ),
        bgcolor=theme.ORANGE, border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=20, vertical=10), ink=True,
    )
    btn_buy = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SHOPPING_BAG_ROUNDED, size=16, color=theme.GRAY),
                ft.Text("Danh mục Gói tập", color=theme.GRAY, weight=ft.FontWeight.W_600, size=theme.FONT_MD),
            ],
            spacing=8,
        ),
        bgcolor="transparent", border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=20, vertical=10), ink=True,
    )

    # Content area — sẽ được swap khi đổi tab
    content_area = ft.Column(controls=[], spacing=16)

    # ── Build current subscriptions panel ─────────────────────────────────────
    def build_current():
        if not active_subs:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.EVENT_BUSY_OUTLINED, size=48, color=theme.GRAY),
                        ft.Text("Bạn chưa đăng ký gói tập nào.", color=theme.GRAY),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12,
                ),
                padding=32, alignment=ft.Alignment.CENTER,
            )

        sub_cards = []
        for sub in active_subs:
            plan = membership_repo.get_plan_by_id(sub.plan_id)
            sub_cards.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.FITNESS_CENTER_ROUNDED, color=theme.ORANGE, size=32),
                    ft.Column([
                        ft.Text(plan.name if plan else "Gói tập", size=theme.FONT_LG, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"Bắt đầu: {str(sub.start_date)[:10]} — Kết thúc: {str(sub.end_date)[:10]}",
                            color=theme.GRAY, size=theme.FONT_SM,
                        ),
                    ], spacing=4),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text("ĐANG HOẠT ĐỘNG", color=theme.GREEN, size=theme.FONT_SM, weight=ft.FontWeight.BOLD),
                        bgcolor=theme.GREEN_LIGHT, padding=8, border_radius=8,
                    ),
                ]),
                bgcolor=theme.WHITE, padding=20, border_radius=16,
                shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
            ))
        return ft.Column(controls=sub_cards, spacing=16)

    # ── Build buy plans panel ─────────────────────────────────────────────────
    def open_buy_dialog(plan):
        def do_pay(e):
            page.close(confirm_dlg)
            now = datetime.now()
            end = now + timedelta(days=plan.duration_days)
            sub = MembershipSubscription(
                member_id=current_user.id,
                plan_id=plan.id,
                price_paid=float(plan.price),
                start_date=now,
                end_date=end,
                status="active",
            )
            membership_repo.create_subscription(sub)

            success_dlg = ft.AlertDialog(
                title=ft.Text("Thanh toán thành công!"),
                content=ft.Text(f"Bạn đã đăng ký thành công gói {plan.name}."),
                actions=[
                    ft.TextButton("Đồng ý", on_click=lambda e: (page.close(success_dlg), navigate("membership") if navigate else None)),
                ],
            )
            page.open(success_dlg)

        confirm_dlg = ft.AlertDialog(
            title=ft.Text("Xác nhận Đăng ký"),
            content=ft.Column(
                [
                    ft.Text(f"Đăng ký: {plan.name}"),
                    ft.Text(f"Số tiền: {plan.price:,.0f} đ", color=theme.ORANGE, weight=ft.FontWeight.BOLD),
                    ft.Text("Xác nhận thanh toán hệ thống nội bộ?", color=theme.GRAY),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Hủy", on_click=lambda e: page.close(confirm_dlg)),
                ft.ElevatedButton(
                    "Thanh toán",
                    bgcolor=theme.ORANGE, color=theme.WHITE,
                    on_click=do_pay,
                ),
            ],
        )
        page.open(confirm_dlg)

    def build_buy():
        if not all_plans:
            return ft.Text("Hệ thống chưa có gói tập nào.", color=theme.GRAY)

        plan_cards = []
        for p in all_plans:
            plan_cards.append(ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WORKSPACE_PREMIUM_ROUNDED, color=theme.ORANGE, size=40),
                            alignment=ft.Alignment.CENTER, padding=16,
                        ),
                        ft.Text(p.name, size=theme.FONT_XL, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{p.duration_days} Ngày", size=theme.FONT_MD, color=theme.GRAY, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{p.price:,.0f} đ", size=theme.FONT_2XL, color=theme.ORANGE, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Mua gói này",
                            bgcolor=theme.ORANGE, color=theme.WHITE,
                            width=float("inf"),
                            on_click=lambda e, plan=p: open_buy_dialog(plan),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=theme.WHITE, padding=24, border_radius=16,
                width=260,
                shadow=ft.BoxShadow(blur_radius=15, color="#0000000A", offset=ft.Offset(0, 5)),
            ))
        return ft.Row(controls=plan_cards, spacing=16, wrap=True)

    # Khởi tạo tab đầu tiên
    content_area.controls.append(build_current())

    # ── Tab switch handler ────────────────────────────────────────────────────
    def show_tab(idx: int):
        selected_tab[0] = idx
        is_current = idx == 0
        btn_current.bgcolor = theme.ORANGE if is_current else "transparent"
        btn_buy.bgcolor = theme.ORANGE if not is_current else "transparent"
        btn_current.content.controls[0].color = theme.WHITE if is_current else theme.GRAY
        btn_current.content.controls[1].color = theme.WHITE if is_current else theme.GRAY
        btn_buy.content.controls[0].color = theme.GRAY if is_current else theme.WHITE
        btn_buy.content.controls[1].color = theme.GRAY if is_current else theme.WHITE
        content_area.controls.clear()
        content_area.controls.append(build_current() if idx == 0 else build_buy())
        page.update()

    btn_current.on_click = lambda e: show_tab(0)
    btn_buy.on_click = lambda e: show_tab(1)

    tab_row = ft.Container(
        content=ft.Row(controls=[btn_current, btn_buy], spacing=4),
        bgcolor=theme.GRAY_LIGHT, border_radius=theme.BUTTON_RADIUS, padding=4,
    )

    # ── Layout: sidebar + content ─────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column(
            [
                ft.Text("Đăng ký Gói tập", size=theme.FONT_2XL, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
                ft.Container(height=8),
                tab_row,
                ft.Container(height=24),
                content_area,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "membership"), content],
            spacing=0,
            expand=True,
        ),
    )
