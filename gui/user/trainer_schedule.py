# ============================================================================
# FILE: gui/user/trainer_schedule.py
# MỤC ĐÍCH: Lịch dạy HLV theo tuần — thêm/sửa/xóa buổi tập.
# ============================================================================

import flet as ft
from datetime import datetime, timedelta
from gui import theme
from app.services import schedule_svc, assignment_svc


# Tên thứ trong tuần tiếng Việt
DAY_NAMES = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def TrainerScheduleScreen(page: ft.Page) -> ft.Container:
    """Màn hình lịch dạy theo tuần."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    # State: tuần hiện tại
    current_week = {"start": schedule_svc.get_week_start()}

    # ── Lấy học viên đang kèm (cho dropdown) ───────────────────────────────
    students = assignment_svc.get_trainer_students(current_user.id) if current_user else []

    # ── Tạo options giờ/phút cho dropdown ────────────────────────────────────
    hour_options = [ft.dropdown.Option(f"{h:02d}", f"{h:02d}") for h in range(5, 23)]
    minute_options = [ft.dropdown.Option(f"{m:02d}", f"{m:02d}") for m in range(0, 60, 5)]

    # ── Dialog thêm/sửa buổi tập ───────────────────────────────────────────
    fs_member = ft.Dropdown(label="Học viên *", expand=True)
    fs_date = ft.TextField(label="Ngày (YYYY-MM-DD) *", expand=True, read_only=True)
    # Giờ bắt đầu: dropdown giờ + dropdown phút
    fs_start_h = ft.Dropdown(label="Giờ BĐ *", options=list(hour_options), width=90)
    fs_start_m = ft.Dropdown(label="Phút *", options=list(minute_options), width=90)
    # Giờ kết thúc: dropdown giờ + dropdown phút
    fs_end_h = ft.Dropdown(label="Giờ KT", options=list(hour_options), width=90)
    fs_end_m = ft.Dropdown(label="Phút", options=list(minute_options), width=90)
    fs_content = ft.TextField(label="Nội dung buổi tập", expand=True, max_length=500)
    session_error = ft.Text("", color=theme.RED, size=theme.FONT_SM)
    session_dialog_title = ft.Text("", size=theme.FONT_LG, weight=ft.FontWeight.BOLD)
    editing_session = {"obj": None}

    def _get_start_time():
        """Ghép dropdown giờ+phút thành 'HH:MM'."""
        if not fs_start_h.value or not fs_start_m.value:
            return ""
        return f"{fs_start_h.value}:{fs_start_m.value}"

    def _get_end_time():
        """Ghép dropdown giờ+phút thành 'HH:MM', trả '' nếu chưa chọn."""
        if not fs_end_h.value or not fs_end_m.value:
            return ""
        return f"{fs_end_h.value}:{fs_end_m.value}"

    def _set_time_dropdowns(time_str, h_dropdown, m_dropdown):
        """Điền HH:MM vào 2 dropdown giờ/phút."""
        if time_str and ":" in time_str:
            parts = time_str.split(":")
            h_dropdown.value = parts[0].zfill(2)
            # Làm tròn phút về bội số 5 gần nhất
            m_val = int(parts[1])
            m_rounded = (m_val // 5) * 5
            m_dropdown.value = f"{m_rounded:02d}"
        else:
            h_dropdown.value = None
            m_dropdown.value = None

    def save_session(e):
        try:
            start_time = _get_start_time()
            end_time = _get_end_time()

            if editing_session["obj"] is None:
                schedule_svc.create_session(
                    trainer_id=current_user.id,
                    member_id=fs_member.value,
                    session_date=fs_date.value.strip(),
                    start_time=start_time,
                    end_time=end_time or None,
                    content=fs_content.value.strip() or None,
                )
            else:
                s = editing_session["obj"]
                s.member_id = fs_member.value
                s.session_date = fs_date.value.strip()
                s.start_time = start_time
                s.end_time = end_time or None
                s.content = fs_content.value.strip() or None
                schedule_svc.update_session(s)

            session_dialog.open = False
            page.update()
            rebuild_schedule()
        except (ValueError, TypeError) as ex:
            session_error.value = str(ex)
            page.update()

    session_dialog = ft.AlertDialog(
        modal=True,
        title=session_dialog_title,
        content=ft.Column([
            ft.Row([fs_member], spacing=theme.PAD_MD),
            fs_date,
            ft.Text("Giờ bắt đầu *", size=theme.FONT_SM, color=theme.GRAY, weight=ft.FontWeight.W_600),
            ft.Row([fs_start_h, ft.Text(":", size=theme.FONT_LG, weight=ft.FontWeight.BOLD), fs_start_m],
                   spacing=theme.PAD_SM, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Text("Giờ kết thúc (tùy chọn)", size=theme.FONT_SM, color=theme.GRAY, weight=ft.FontWeight.W_600),
            ft.Row([fs_end_h, ft.Text(":", size=theme.FONT_LG, weight=ft.FontWeight.BOLD), fs_end_m],
                   spacing=theme.PAD_SM, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            fs_content,
            session_error,
        ], spacing=theme.PAD_MD, width=520, tight=True),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(session_dialog, "open", False) or page.update()),
            ft.ElevatedButton("Lưu", on_click=save_session, bgcolor=theme.ORANGE, color=theme.WHITE),
        ],
    )

    def open_add_session(date_str):
        editing_session["obj"] = None
        session_dialog_title.value = "Thêm buổi tập"
        fs_member.options = [
            ft.dropdown.Option(s["member"].id, s["member"].name) for s in students
        ]
        fs_member.value = None
        fs_date.value = date_str
        _set_time_dropdowns(None, fs_start_h, fs_start_m)
        _set_time_dropdowns(None, fs_end_h, fs_end_m)
        fs_content.value = ""
        session_error.value = ""
        session_dialog.open = True
        page.update()

    def open_edit_session(session_obj):
        editing_session["obj"] = session_obj
        session_dialog_title.value = "Sửa buổi tập"
        fs_member.options = [
            ft.dropdown.Option(s["member"].id, s["member"].name) for s in students
        ]
        fs_member.value = session_obj.member_id
        fs_date.value = session_obj.session_date
        _set_time_dropdowns(session_obj.start_time, fs_start_h, fs_start_m)
        _set_time_dropdowns(session_obj.end_time, fs_end_h, fs_end_m)
        fs_content.value = session_obj.content or ""
        session_error.value = ""
        session_dialog.open = True
        page.update()

    # ── Dialog xác nhận xóa ─────────────────────────────────────────────────
    delete_target = {"id": None}
    confirm_delete_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Xác nhận xóa buổi tập"),
        content=ft.Text("Xóa buổi tập này?"),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(confirm_delete_dlg, "open", False) or page.update()),
            ft.ElevatedButton("Xóa", bgcolor=theme.RED, color=theme.WHITE,
                              on_click=lambda e: [
                                  schedule_svc.delete_session(delete_target["id"]),
                                  setattr(confirm_delete_dlg, "open", False),
                                  page.update(),
                                  rebuild_schedule(),
                              ]),
        ],
    )

    page.overlay.extend([session_dialog, confirm_delete_dlg])

    # ── Build schedule grid ─────────────────────────────────────────────────
    schedule_body = ft.Column(controls=[], spacing=0)
    stats_text = ft.Text("", size=theme.FONT_SM, color=theme.GRAY)
    week_label = ft.Text("", size=theme.FONT_LG, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY)

    # Mapping member_id → name
    members_map = {s["member"].id: s["member"].name for s in students}

    def rebuild_schedule():
        ws = current_week["start"]
        we = ws + timedelta(days=6)
        week_label.value = f"{ws.strftime('%d/%m')} — {we.strftime('%d/%m/%Y')}"

        sessions = schedule_svc.get_week_sessions(current_user.id, ws) if current_user else []

        # Nhóm theo ngày
        by_date = {}
        for s in sessions:
            by_date.setdefault(s.session_date, []).append(s)

        total_sessions = len(sessions)
        unique_members = len(set(s.member_id for s in sessions))
        stats_text.value = f"Tổng: {total_sessions} buổi • {unique_members} học viên"

        day_rows = []
        for i in range(7):
            day = ws + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_label = DAY_NAMES[i]
            day_date = day.strftime("%d/%m")

            day_sessions = by_date.get(day_str, [])

            session_controls = []
            for s in day_sessions:
                member_name = members_map.get(s.member_id, "?")
                time_str = s.start_time
                if s.end_time:
                    time_str += f" - {s.end_time}"
                content_str = s.content or ""

                status_color = theme.GREEN if s.status == "scheduled" else (
                    theme.BLUE if s.status == "completed" else theme.RED
                )

                session_controls.append(ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(time_str, size=theme.FONT_XS, color=theme.WHITE,
                                            weight=ft.FontWeight.BOLD),
                            bgcolor=status_color, border_radius=4,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        ),
                        ft.Text(f"{member_name}", size=theme.FONT_SM, weight=ft.FontWeight.W_500,
                                expand=True),
                        ft.Text(content_str, size=theme.FONT_XS, color=theme.GRAY, width=150),
                        ft.IconButton(
                            icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=theme.ORANGE,
                            on_click=lambda e, sess=s: open_edit_session(sess),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=theme.RED,
                            on_click=lambda e, sid=s.id: [
                                delete_target.update({"id": sid}),
                                setattr(confirm_delete_dlg, "open", True),
                                page.update(),
                            ],
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=ft.padding.symmetric(vertical=4),
                ))

            if not session_controls:
                session_controls = [
                    ft.Text("(Trống)", size=theme.FONT_XS, color=theme.GRAY, italic=True),
                ]

            # Nút thêm buổi
            add_btn = ft.Container(
                content=ft.Text("+ Thêm buổi", size=theme.FONT_XS, color=theme.ORANGE,
                                weight=ft.FontWeight.W_600),
                on_click=lambda e, ds=day_str: open_add_session(ds),
                padding=ft.padding.symmetric(vertical=4),
            )

            day_rows.append(ft.Container(
                content=ft.Row([
                    # Cột ngày
                    ft.Container(
                        content=ft.Column([
                            ft.Text(day_label, size=theme.FONT_SM, weight=ft.FontWeight.BOLD,
                                    color=theme.TEXT_PRIMARY),
                            ft.Text(day_date, size=theme.FONT_XS, color=theme.GRAY),
                        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        width=80,
                    ),
                    ft.VerticalDivider(width=1, color=theme.BORDER),
                    # Cột buổi tập
                    ft.Column(
                        controls=[*session_controls, add_btn],
                        spacing=2, expand=True,
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
            ))

        schedule_body.controls = day_rows
        page.update()

    rebuild_schedule()

    # ── Navigation tuần ─────────────────────────────────────────────────────
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
        ft.Text("Lịch dạy", size=theme.FONT_2XL, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
        ft.Container(expand=True),
        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=prev_week, icon_color=theme.ORANGE),
        week_label,
        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=next_week, icon_color=theme.ORANGE),
        ft.TextButton("Hôm nay", on_click=go_today),
    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # ── Layout ──────────────────────────────────────────────────────────────
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
            controls=[UserSidebar(page, "trainer_schedule"), content],
            spacing=0, expand=True,
        ),
    )
