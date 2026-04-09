# ============================================================================
# FILE: gui/user/trainer_students.py
# MỤC ĐÍCH: Danh sách học viên đang kèm + lịch sử đã kết thúc.
# ============================================================================

import flet as ft
from gui import theme
from app.services import assignment_svc


def TrainerStudentsScreen(page: ft.Page) -> ft.Container:
    """Màn hình danh sách học viên của HLV."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    students = assignment_svc.get_trainer_students(current_user.id)
    history = assignment_svc.get_trainer_history(current_user.id)

    search_query = {"value": ""}

    # ── Dialog ghi chú ──────────────────────────────────────────────────────
    notes_field = ft.TextField(
        label="Ghi chú", multiline=True, min_lines=3, max_lines=5,
        max_length=500,
        border_radius=theme.BUTTON_RADIUS, focused_border_color=theme.ORANGE,
    )
    notes_target = {"assignment_id": None}
    notes_msg = ft.Text("", size=theme.FONT_SM)

    def save_notes(e):
        try:
            assignment_svc.update_assignment_notes(
                notes_target["assignment_id"], notes_field.value or ""
            )
            notes_msg.value = "Đã lưu ghi chú!"
            notes_msg.color = theme.GREEN
            page.update()
            # Rebuild screen
            if navigate:
                navigate("trainer_students")
        except ValueError as ex:
            notes_msg.value = str(ex)
            notes_msg.color = theme.RED
            page.update()

    notes_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Ghi chú học viên", size=theme.FONT_LG, weight=ft.FontWeight.BOLD),
        content=ft.Column([notes_field, notes_msg], spacing=theme.PAD_MD, width=400, tight=True),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(notes_dialog, "open", False) or page.update()),
            ft.ElevatedButton("Lưu", on_click=save_notes, bgcolor=theme.ORANGE, color=theme.WHITE),
        ],
    )

    def open_notes(assignment_id, current_notes):
        notes_target["assignment_id"] = assignment_id
        notes_field.value = current_notes or ""
        notes_msg.value = ""
        notes_dialog.open = True
        page.update()

    # ── Dialog chi tiết ─────────────────────────────────────────────────────
    detail_body = ft.Column(controls=[], spacing=12)
    detail_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Chi tiết học viên", size=theme.FONT_LG, weight=ft.FontWeight.BOLD),
        content=ft.Container(content=detail_body, width=420),
        actions=[
            ft.TextButton("Đóng", on_click=lambda e: setattr(detail_dialog, "open", False) or page.update()),
        ],
    )

    def info_row(label, value):
        return ft.Row([
            ft.Text(label, color=theme.GRAY, width=130),
            ft.Text(str(value or "Chưa có"), weight=ft.FontWeight.BOLD),
        ])

    def open_detail(member, sub, assignment):
        detail_body.controls = [
            info_row("Họ tên", member.name),
            info_row("SĐT", member.phone),
            info_row("Email", getattr(member, "email", None)),
            info_row("Giới tính", getattr(member, "gender", None)),
        ]
        if sub:
            detail_body.controls.extend([
                ft.Divider(color=theme.GRAY_LIGHT),
                info_row("Gói tập", ""),
                info_row("Bắt đầu", sub.start_date.strftime("%d/%m/%Y")),
                info_row("Kết thúc", sub.end_date.strftime("%d/%m/%Y")),
                info_row("Còn lại", f"{sub.days_remaining()} ngày"),
                info_row("Trạng thái", sub.status),
            ])
        if assignment.notes:
            detail_body.controls.extend([
                ft.Divider(color=theme.GRAY_LIGHT),
                info_row("Ghi chú", assignment.notes),
            ])
        detail_dialog.open = True
        page.update()

    page.overlay.extend([notes_dialog, detail_dialog])

    # ── Filter students ─────────────────────────────────────────────────────
    def filter_students(items, q):
        if not q:
            return items
        q = q.lower()
        return [s for s in items
                if q in s["member"].name.lower() or q in s["member"].phone.lower()]

    # ── Build student card ──────────────────────────────────────────────────
    def make_student_card(stu):
        m = stu["member"]
        a = stu["assignment"]
        sub = stu.get("subscription")
        avatar_letter = m.name[0].upper() if m.name else "?"

        if sub:
            remaining = sub.days_remaining()
            pkg_text = f"Gói tập  •  Còn {remaining} ngày"
        else:
            pkg_text = "Kèm cá nhân"

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(avatar_letter, size=18, weight=ft.FontWeight.BOLD, color=theme.WHITE),
                        bgcolor=theme.ORANGE, width=44, height=44,
                        border_radius=22, alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column([
                        ft.Text(m.name, weight=ft.FontWeight.BOLD, size=theme.FONT_LG),
                        ft.Text(f"SDT: {m.phone}", color=theme.GRAY, size=theme.FONT_SM),
                    ], spacing=2, expand=True),
                ]),
                ft.Row([
                    ft.Icon(ft.Icons.FITNESS_CENTER, size=14, color=theme.BLUE),
                    ft.Text(pkg_text, size=theme.FONT_SM, color=theme.BLUE),
                ], spacing=6),
                ft.Row([
                    ft.Icon(ft.Icons.NOTE_ALT_OUTLINED, size=14, color=theme.GRAY),
                    ft.Text(a.notes or "Chưa có ghi chú", size=theme.FONT_SM,
                            color=theme.GRAY, italic=True, expand=True),
                ], spacing=6),
                ft.Row([
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text("Ghi chú", size=theme.FONT_XS, color=theme.ORANGE,
                                        weight=ft.FontWeight.W_600),
                        border=ft.border.all(1, theme.ORANGE), border_radius=6,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        on_click=lambda e, aid=a.id, n=a.notes: open_notes(aid, n),
                    ),
                    ft.Container(
                        content=ft.Text("Chi tiết", size=theme.FONT_XS, color=theme.BLUE,
                                        weight=ft.FontWeight.W_600),
                        border=ft.border.all(1, theme.BLUE), border_radius=6,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        on_click=lambda e, mem=m, s=sub, asn=a: open_detail(mem, s, asn),
                    ),
                ], spacing=8),
            ], spacing=10),
            bgcolor=theme.WHITE, padding=20, border_radius=16,
            shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
        )

    # ── Active students section ─────────────────────────────────────────────
    students_column = ft.Column(controls=[], spacing=16)

    def rebuild_list():
        q = search_query["value"]
        filtered = filter_students(students, q)
        cards = [make_student_card(s) for s in filtered]
        students_column.controls = cards if cards else [
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=48, color=theme.GRAY),
                    ft.Text("Không tìm thấy học viên nào." if q else "Chưa có học viên nào.",
                            color=theme.GRAY, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                padding=32, alignment=ft.Alignment.CENTER,
            )
        ]
        page.update()

    rebuild_list()

    # ── History section ─────────────────────────────────────────────────────
    if history:
        history_cards = []
        for h in history:
            m = h["member"]
            a = h["assignment"]
            end_str = a.end_date.strftime("%d/%m/%Y") if a.end_date else "?"
            start_str = a.start_date.strftime("%d/%m/%Y") if a.start_date else "?"
            history_cards.append(ft.Container(
                content=ft.Row([
                    ft.Text(m.name, weight=ft.FontWeight.W_500, size=theme.FONT_SM, expand=True),
                    ft.Text(f"{start_str} → {end_str}", color=theme.GRAY, size=theme.FONT_XS),
                    ft.Container(
                        content=ft.Text("Đã xong", size=theme.FONT_XS, color=theme.AMBER,
                                        weight=ft.FontWeight.W_600),
                        bgcolor=theme.AMBER_LIGHT, border_radius=theme.BADGE_RADIUS,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    ),
                ]),
                bgcolor=theme.WHITE, padding=ft.padding.symmetric(horizontal=20, vertical=14),
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=8, color="#00000005", offset=ft.Offset(0, 3)),
            ))
        history_section = ft.Column([
            ft.Container(height=16),
            ft.Text("Lịch sử đã kết thúc", size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
                     color=theme.TEXT_PRIMARY),
            ft.Container(height=8),
            *history_cards,
        ], spacing=8)
    else:
        history_section = ft.Container()

    # ── Search bar ──────────────────────────────────────────────────────────
    search_field = ft.TextField(
        hint_text="Tìm kiếm học viên...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=theme.BUTTON_RADIUS,
        height=40, text_size=theme.FONT_SM, expand=True,
        focused_border_color=theme.ORANGE,
        on_change=lambda e: (search_query.update({"value": e.control.value}), rebuild_list()),
    )

    # ── Layout ──────────────────────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column([
            ft.Text("Học viên của bạn", size=theme.FONT_2XL,
                     weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
            ft.Container(height=8),
            search_field,
            ft.Container(height=8),
            ft.Text(f"Đang kèm ({len(students)} người)", size=theme.FONT_LG,
                     weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
            students_column,
            history_section,
        ], scroll=ft.ScrollMode.AUTO),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "trainer_students"), content],
            spacing=0, expand=True,
        ),
    )
