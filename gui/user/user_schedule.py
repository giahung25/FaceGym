# ============================================================================
# FILE: gui/user/user_schedule.py
# MỤC ĐÍCH: Màn hình lịch tập của hội viên — xem buổi tập theo tuần.
# ============================================================================

import flet as ft
from datetime import timedelta
from gui import theme
from app.services import schedule_svc, trainer_svc

DAY_NAMES = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def ScheduleScreen(page: ft.Page) -> ft.Container:
    """Màn hình lịch tập của hội viên."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    # State: tuần hiện tại
    current_week = {"start": schedule_svc.get_week_start()}

    # Cache tên HLV
    trainer_cache = {}

    def get_trainer_name(trainer_id):
        if trainer_id not in trainer_cache:
            t = trainer_svc.get_trainer_by_id(trainer_id)
            trainer_cache[trainer_id] = t.name if t else "?"
        return trainer_cache[trainer_id]

    def get_trainer_info(trainer_id):
        return trainer_svc.get_trainer_by_id(trainer_id)

    # ── Dialog chi tiết buổi tập ──────────────────────────────────────────
    detail_body = ft.Column(controls=[], spacing=12)
    detail_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Chi tiết buổi tập", size=theme.FONT_LG, weight=ft.FontWeight.BOLD),
        content=ft.Container(content=detail_body, width=420),
        actions=[
            ft.TextButton("Đóng", on_click=lambda e: setattr(detail_dialog, "open", False) or page.update()),
        ],
    )
    page.overlay.append(detail_dialog)

    def info_row(label, value):
        return ft.Row([
            ft.Text(label, color=theme.GRAY, width=140),
            ft.Text(str(value or "Chưa có"), weight=ft.FontWeight.BOLD, expand=True),
        ])

    def open_detail(session):
        trainer = get_trainer_info(session.trainer_id)
        trainer_name = trainer.name if trainer else "?"
        trainer_spec = (getattr(trainer, "specialization", None) or "Chưa cập nhật") if trainer else "?"

        status_map = {
            "scheduled": "Đã lên lịch",
            "completed": "Đã hoàn thành",
            "cancelled": "Đã hủy",
        }
        status_text = status_map.get(session.status, session.status)

        time_str = session.start_time
        if session.end_time:
            time_str += f" - {session.end_time}"

        detail_body.controls = [
            info_row("Ngày", session.session_date),
            info_row("Thời gian", time_str),
            info_row("Trạng thái", status_text),
            ft.Divider(color=theme.GRAY_LIGHT),
            info_row("Huấn luyện viên", trainer_name),
            info_row("Chuyên môn", trainer_spec),
            ft.Divider(color=theme.GRAY_LIGHT),
            ft.Text("Nội dung buổi tập", color=theme.GRAY, size=theme.FONT_SM,
                     weight=ft.FontWeight.W_600),
            ft.Container(
                content=ft.Text(session.content or "Chưa có nội dung", size=theme.FONT_SM,
                                italic=not session.content,
                                color=theme.GRAY if not session.content else theme.TEXT_PRIMARY),
                bgcolor=theme.GRAY_LIGHT, border_radius=8,
                padding=12,
            ),
        ]
        if session.notes:
            detail_body.controls.extend([
                ft.Divider(color=theme.GRAY_LIGHT),
                ft.Text("Ghi chú của HLV", color=theme.GRAY, size=theme.FONT_SM,
                         weight=ft.FontWeight.W_600),
                ft.Container(
                    content=ft.Text(session.notes, size=theme.FONT_SM, italic=True),
                    bgcolor="#FFF8E1", border_radius=8,
                    padding=12,
                ),
            ])
        detail_dialog.open = True
        page.update()

    # ── Build schedule grid ───────────────────────────────────────────────
    schedule_body = ft.Column(controls=[], spacing=0)
    stats_text = ft.Text("", size=theme.FONT_SM, color=theme.GRAY)
    week_label = ft.Text("", size=theme.FONT_LG, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY)

    def rebuild_schedule():
        ws = current_week["start"]
        we = ws + timedelta(days=6)
        week_label.value = f"{ws.strftime('%d/%m')} — {we.strftime('%d/%m/%Y')}"

        sessions = schedule_svc.get_member_week_sessions(current_user.id, ws) if current_user else []

        # Nhóm theo ngày
        by_date = {}
        for s in sessions:
            by_date.setdefault(s.session_date, []).append(s)

        total_sessions = len(sessions)
        stats_text.value = f"Tổng: {total_sessions} buổi tập trong tuần"

        day_rows = []
        for i in range(7):
            day = ws + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_label = DAY_NAMES[i]
            day_date = day.strftime("%d/%m")

            day_sessions = by_date.get(day_str, [])

            session_controls = []
            for s in day_sessions:
                trainer_name = get_trainer_name(s.trainer_id)
                time_str = s.start_time
                if s.end_time:
                    time_str += f" - {s.end_time}"
                content_str = s.content or "Chưa có nội dung"

                status_color = theme.GREEN if s.status == "scheduled" else (
                    theme.BLUE if s.status == "completed" else theme.RED
                )

                session_controls.append(ft.Container(
                    content=ft.Row([
                        # Cột trái: thời gian + HLV + nội dung
                        ft.Column([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(time_str, size=theme.FONT_XS, color=theme.WHITE,
                                                    weight=ft.FontWeight.BOLD),
                                    bgcolor=status_color, border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                ),
                                ft.Text(f"HLV: {trainer_name}", size=theme.FONT_SM,
                                        weight=ft.FontWeight.W_500),
                            ], spacing=8),
                            ft.Text(content_str, size=theme.FONT_XS, color=theme.GRAY,
                                    italic=not s.content),
                        ], spacing=2, expand=True),
                        # Nút chi tiết
                        ft.Container(
                            content=ft.Text("Chi tiết", size=theme.FONT_XS, color=theme.BLUE,
                                            weight=ft.FontWeight.W_600),
                            border=ft.border.all(1, theme.BLUE), border_radius=6,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            on_click=lambda e, sess=s: open_detail(sess),
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=ft.padding.symmetric(vertical=4),
                ))

            if not session_controls:
                session_controls = [
                    ft.Text("(Không có buổi tập)", size=theme.FONT_XS, color=theme.GRAY, italic=True),
                ]

            day_rows.append(ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(day_label, size=theme.FONT_SM, weight=ft.FontWeight.BOLD,
                                    color=theme.TEXT_PRIMARY),
                            ft.Text(day_date, size=theme.FONT_XS, color=theme.GRAY),
                        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        width=80,
                    ),
                    ft.VerticalDivider(width=1, color=theme.BORDER),
                    ft.Column(
                        controls=session_controls,
                        spacing=2, expand=True,
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
            ))

        schedule_body.controls = day_rows
        page.update()

    rebuild_schedule()

    # ── Điều hướng tuần ───────────────────────────────────────────────────
    def prev_week(e):
        current_week["start"] -= timedelta(days=7)
        rebuild_schedule()

    def next_week(e):
        current_week["start"] += timedelta(days=7)
        rebuild_schedule()

    def go_today(e):
        current_week["start"] = schedule_svc.get_week_start()
        rebuild_schedule()

    week_nav = ft.Row([
        ft.Text("Lịch tập của tôi", size=theme.FONT_2XL, weight=ft.FontWeight.W_800,
                 color=theme.TEXT_PRIMARY),
        ft.Container(expand=True),
        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=prev_week, icon_color=theme.ORANGE),
        week_label,
        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=next_week, icon_color=theme.ORANGE),
        ft.TextButton("Hôm nay", on_click=go_today),
    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # ── Layout ─────────────────────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column([
            week_nav,
            ft.Container(height=8),
            ft.Container(
                content=ft.Column([schedule_body], spacing=0),
                bgcolor=theme.WHITE, border_radius=theme.CARD_RADIUS,
                shadow=ft.BoxShadow(blur_radius=8, color="#00000008", offset=ft.Offset(0, 2)),
            ),
            ft.Container(height=8),
            stats_text,
        ], scroll=ft.ScrollMode.AUTO),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "schedule"), content],
            spacing=0, expand=True,
        ),
    )
