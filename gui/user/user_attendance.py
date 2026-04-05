# ============================================================================
# FILE: gui/user/user_attendance.py
# MỤC ĐÍCH: Lịch sử điểm danh của hội viên.
# ============================================================================

import flet as ft
from datetime import datetime, date
from gui import theme
from app.services import attendance_svc


def AttendanceHistoryScreen(page: ft.Page) -> ft.Container:
    """Màn hình lịch sử điểm danh của hội viên."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    # ── State ────────────────────────────────────────────────────────────────
    filter_state = {"value": "all"}  # "all" | "month" | "week"

    # ── Helper format thời gian ──────────────────────────────────────────────
    def fmt_dt(dt_str):
        if not dt_str:
            return "—"
        try:
            return datetime.fromisoformat(str(dt_str)).strftime("%d/%m/%Y %H:%M")
        except Exception:
            return str(dt_str)[:16]

    def fmt_time(dt_str):
        if not dt_str:
            return "—"
        try:
            return datetime.fromisoformat(str(dt_str)).strftime("%H:%M")
        except Exception:
            return str(dt_str)[:5]

    def fmt_date(dt_str):
        if not dt_str:
            return "—"
        try:
            return datetime.fromisoformat(str(dt_str)).strftime("%d/%m/%Y")
        except Exception:
            return str(dt_str)[:10]

    # ── Tính thời gian tập (check_in → check_out) ────────────────────────────
    def duration_str(check_in, check_out):
        if not check_in or not check_out:
            return ""
        try:
            t_in = datetime.fromisoformat(str(check_in))
            t_out = datetime.fromisoformat(str(check_out))
            mins = int((t_out - t_in).total_seconds() / 60)
            if mins < 60:
                return f"{mins} phút"
            h = mins // 60
            m = mins % 60
            return f"{h}h{m:02d}" if m else f"{h}h"
        except Exception:
            return ""

    # ── Method badge ─────────────────────────────────────────────────────────
    def method_badge(method):
        method = method or "face_id"
        labels = {"face_id": "Face ID", "manual": "Thủ công", "qr_code": "QR Code"}
        colors = {"face_id": theme.GREEN, "manual": theme.BLUE, "qr_code": theme.AMBER}
        label = labels.get(method, method)
        color = colors.get(method, theme.GRAY)
        return ft.Container(
            content=ft.Text(label, size=theme.FONT_XS, color=theme.WHITE,
                            weight=ft.FontWeight.W_600),
            bgcolor=color,
            border_radius=theme.BADGE_RADIUS,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )

    # ── Stats tháng này ──────────────────────────────────────────────────────
    def calc_stats(records):
        now = datetime.now()
        this_month = [r for r in records if r.check_in
                      and datetime.fromisoformat(str(r.check_in)).month == now.month
                      and datetime.fromisoformat(str(r.check_in)).year == now.year]
        total_mins = 0
        for r in this_month:
            if r.check_in and r.check_out:
                try:
                    t_in = datetime.fromisoformat(str(r.check_in))
                    t_out = datetime.fromisoformat(str(r.check_out))
                    total_mins += int((t_out - t_in).total_seconds() / 60)
                except Exception:
                    pass
        return len(records), len(this_month), total_mins

    # ── Build list ───────────────────────────────────────────────────────────
    list_column = ft.Column(controls=[], spacing=12, scroll=ft.ScrollMode.AUTO)
    stats_row = ft.Row(controls=[], spacing=16)
    filter_tabs = ft.Row(controls=[], spacing=8)

    def build_card(att):
        dur = duration_str(att.check_in, att.check_out)
        is_checked_out = att.check_out is not None

        return ft.Container(
            content=ft.Row(
                controls=[
                    # Icon cột trái
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.FITNESS_CENTER if is_checked_out else ft.Icons.LOGIN,
                            size=22,
                            color=theme.WHITE,
                        ),
                        width=44, height=44,
                        bgcolor=theme.GREEN if is_checked_out else theme.ORANGE,
                        border_radius=22,
                        alignment=ft.Alignment.CENTER,
                    ),
                    # Nội dung chính
                    ft.Column(
                        controls=[
                            ft.Text(fmt_date(att.check_in),
                                    weight=ft.FontWeight.BOLD, size=theme.FONT_MD,
                                    color=theme.TEXT_PRIMARY),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.LOGIN, size=13, color=theme.GRAY),
                                    ft.Text(f"Vào: {fmt_time(att.check_in)}",
                                            size=theme.FONT_SM, color=theme.GRAY),
                                    ft.Container(width=8),
                                    ft.Icon(ft.Icons.LOGOUT, size=13, color=theme.GRAY),
                                    ft.Text(
                                        f"Ra: {fmt_time(att.check_out)}" if att.check_out else "Chưa check-out",
                                        size=theme.FONT_SM,
                                        color=theme.GRAY if att.check_out else theme.AMBER,
                                    ),
                                ],
                                spacing=4,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    # Cột phải: badge + thời gian tập
                    ft.Column(
                        controls=[
                            method_badge(att.method),
                            ft.Text(dur, size=theme.FONT_XS, color=theme.GRAY,
                                    text_align=ft.TextAlign.RIGHT) if dur else ft.Container(),
                        ],
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            bgcolor=theme.WHITE,
            border_radius=16,
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
            shadow=ft.BoxShadow(blur_radius=10, color="#00000008", offset=ft.Offset(0, 4)),
        )

    def load(filter_val="all"):
        filter_state["value"] = filter_val
        try:
            all_records = attendance_svc.get_member_attendance(current_user.id, limit=100)
        except Exception:
            all_records = []

        now = datetime.now()

        if filter_val == "month":
            records = [r for r in all_records if r.check_in and
                       datetime.fromisoformat(str(r.check_in)).month == now.month and
                       datetime.fromisoformat(str(r.check_in)).year == now.year]
        elif filter_val == "week":
            this_week = now.isocalendar()[1]
            records = [r for r in all_records if r.check_in and
                       datetime.fromisoformat(str(r.check_in)).isocalendar()[1] == this_week and
                       datetime.fromisoformat(str(r.check_in)).year == now.year]
        else:
            records = all_records

        # Stats
        total, month_count, total_mins = calc_stats(all_records)
        h = total_mins // 60
        m = total_mins % 60
        time_str = f"{h}h{m:02d}" if h else f"{m} phút"

        stats_row.controls = [
            _stat_mini(str(total), "Tổng lần", ft.Icons.CALENDAR_MONTH, theme.ORANGE),
            _stat_mini(str(month_count), "Tháng này", ft.Icons.DATE_RANGE, theme.BLUE),
            _stat_mini(time_str if total_mins else "0 phút", "Tổng giờ tập", ft.Icons.TIMER, theme.GREEN),
        ]

        # Filter tabs active state
        for tab in filter_tabs.controls:
            tab.bgcolor = theme.ORANGE if tab.data == filter_val else theme.CARD_BG
            lbl = tab.content
            if isinstance(lbl, ft.Text):
                lbl.color = theme.WHITE if tab.data == filter_val else theme.TEXT_SECONDARY

        # List
        list_column.controls.clear()
        if not records:
            list_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.EVENT_BUSY, size=48, color=theme.GRAY),
                            ft.Text("Không có lịch sử điểm danh", color=theme.GRAY,
                                    size=theme.FONT_MD),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=ft.padding.all(40),
                    alignment=ft.Alignment.CENTER,
                )
            )
        else:
            for att in records:
                list_column.controls.append(build_card(att))

        page.update()

    def _stat_mini(value, label, icon, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon, size=16, color=color),
                            ft.Text(value, size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
                                    color=theme.TEXT_PRIMARY),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(label, size=theme.FONT_XS, color=theme.GRAY),
                ],
                spacing=2,
                tight=True,
            ),
            bgcolor=theme.WHITE,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            shadow=ft.BoxShadow(blur_radius=8, color="#00000008", offset=ft.Offset(0, 2)),
            expand=True,
        )

    # ── Filter tabs ──────────────────────────────────────────────────────────
    tab_defs = [("all", "Tất cả"), ("month", "Tháng này"), ("week", "Tuần này")]
    for key, lbl in tab_defs:
        def on_tab(e, k=key):
            load(k)
        tab = ft.Container(
            content=ft.Text(lbl, size=theme.FONT_SM, weight=ft.FontWeight.W_600,
                            color=theme.WHITE if key == "all" else theme.TEXT_SECONDARY),
            bgcolor=theme.ORANGE if key == "all" else theme.CARD_BG,
            border_radius=theme.BADGE_RADIUS,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border=ft.border.all(1, theme.BORDER),
            on_click=on_tab,
            ink=True,
            data=key,
        )
        filter_tabs.controls.append(tab)

    # Load lần đầu
    load("all")

    # ── Layout ───────────────────────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column(
            controls=[
                # Tiêu đề
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FACT_CHECK_ROUNDED, size=26, color=theme.ORANGE),
                        ft.Text("Lịch sử điểm danh", size=theme.FONT_2XL,
                                weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
                    ],
                    spacing=12,
                ),
                ft.Container(height=16),
                # Stats
                stats_row,
                ft.Container(height=8),
                # Filter tabs
                filter_tabs,
                ft.Container(height=8),
                # List
                list_column,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "attendance_history"), content],
            spacing=0,
            expand=True,
        ),
    )
