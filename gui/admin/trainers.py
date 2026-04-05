# ============================================================================
# FILE: gui/admin/trainers.py
# MỤC ĐÍCH: Màn hình QUẢN LÝ HUẤN LUYỆN VIÊN — hiển thị danh sách, thêm/sửa/xóa HLV.
#
# CHỨC NĂNG:
#   1. Hiển thị bảng danh sách HLV (tên, SĐT, email, chuyên môn)
#   2. Tìm kiếm HLV (theo tên, SĐT, chuyên môn)
#   3. Thêm HLV mới (dialog popup)
#   4. Sửa thông tin HLV (dialog popup)
#   5. Reset PIN HLV (dialog riêng)
#   6. Xóa HLV (soft delete, có xác nhận)
#
# LAYOUT:
#   ┌──────────┬─────────────────────────────────────────────────┐
#   │ SIDEBAR  │  Header                                        │
#   │          │  ───────────────────────────────────────────    │
#   │          │  Trainers          [🔍] [+ Thêm HLV]          │
#   │          │  Tổng: 5                                       │
#   │          │  ┌─────────────────────────────────────────┐   │
#   │          │  │ HLV | Email | Chuyên môn | Hành động    │   │
#   │          │  │ Tuấn| t@..  | Boxing    | Sửa Reset Xóa│   │
#   │          │  └─────────────────────────────────────────┘   │
#   └──────────┴─────────────────────────────────────────────────┘
# ============================================================================

import flet as ft
from gui import theme
from gui.admin.components.header import Header
from gui.admin.components.sidebar import Sidebar
from app.services import trainer_svc


def TrainersScreen(page: ft.Page) -> ft.Row:
    """Tạo màn hình quản lý huấn luyện viên.

    Tham số:
        page (ft.Page): đối tượng Page

    Trả về:
        ft.Row: layout gồm [Sidebar | Content Area]
    """

    # ══════════════════════════════════════════════════════════════════════════
    # STATE
    # ══════════════════════════════════════════════════════════════════════════
    search_query = {"value": ""}
    selected_trainer = {"obj": None}

    # ══════════════════════════════════════════════════════════════════════════
    # DIALOG: Thêm / Sửa HLV
    # ══════════════════════════════════════════════════════════════════════════
    f_name = ft.TextField(label="Họ tên *", expand=True)
    f_phone = ft.TextField(label="Số điện thoại *", expand=True)
    f_email = ft.TextField(label="Email", expand=True)
    f_specialization = ft.TextField(label="Chuyên môn (VD: Yoga, Boxing...)", expand=True)
    dialog_error = ft.Text("", color=theme.RED, size=theme.FONT_SM)
    dialog_title = ft.Text("", size=theme.FONT_LG, weight=ft.FontWeight.BOLD)

    def clear_form():
        for f in [f_name, f_phone, f_email, f_specialization]:
            f.value = ""
        dialog_error.value = ""

    def save_trainer(e):
        try:
            if selected_trainer["obj"] is None:
                trainer_svc.register_trainer(
                    name=f_name.value,
                    phone=f_phone.value,
                    email=f_email.value or None,
                    specialization=f_specialization.value or None,
                )
            else:
                t = selected_trainer["obj"]
                t.name = f_name.value.strip()
                t.phone = f_phone.value.strip()
                t.email = f_email.value.strip() if f_email.value else None
                t.specialization = f_specialization.value.strip() if f_specialization.value else None
                trainer_svc.update_trainer(t)

            trainer_dialog.open = False
            page.update()
            refresh_table()
        except ValueError as ex:
            dialog_error.value = str(ex)
            page.update()

    trainer_dialog = ft.AlertDialog(
        modal=True,
        title=dialog_title,
        content=ft.Column(
            controls=[
                ft.Row(controls=[f_name, f_phone], spacing=theme.PAD_MD),
                ft.Row(controls=[f_email, f_specialization], spacing=theme.PAD_MD),
                dialog_error,
            ],
            spacing=theme.PAD_MD,
            width=520,
            tight=True,
        ),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(trainer_dialog, "open", False) or page.update()),
            ft.ElevatedButton("Lưu", on_click=save_trainer, bgcolor=theme.ORANGE, color=theme.WHITE),
        ],
    )

    def open_add_dialog(e):
        selected_trainer["obj"] = None
        clear_form()
        dialog_title.value = "Thêm huấn luyện viên mới"
        trainer_dialog.open = True
        page.update()

    def open_edit_dialog(t):
        selected_trainer["obj"] = t
        clear_form()
        dialog_title.value = "Chỉnh sửa huấn luyện viên"
        f_name.value = t.name
        f_phone.value = t.phone
        f_email.value = t.email or ""
        f_specialization.value = t.specialization or ""
        trainer_dialog.open = True
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    # DIALOG: Reset PIN
    # ══════════════════════════════════════════════════════════════════════════
    f_new_pin = ft.TextField(
        label="PIN mới (6 chữ số)",
        password=True,
        can_reveal_password=True,
        expand=True,
        max_length=6,
    )
    pin_error = ft.Text("", color=theme.RED, size=theme.FONT_SM)
    pin_target = {"id": None, "name": ""}
    pin_dialog_title = ft.Text("", size=theme.FONT_LG, weight=ft.FontWeight.BOLD)

    def do_reset_pin(e):
        try:
            trainer_svc.reset_pin(pin_target["id"], f_new_pin.value)
            pin_dialog.open = False
            page.update()
            refresh_table()
        except ValueError as ex:
            pin_error.value = str(ex)
            page.update()

    pin_dialog = ft.AlertDialog(
        modal=True,
        title=pin_dialog_title,
        content=ft.Column(
            controls=[
                f_new_pin,
                pin_error,
            ],
            spacing=theme.PAD_MD,
            width=320,
            tight=True,
        ),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(pin_dialog, "open", False) or page.update()),
            ft.ElevatedButton("Đặt PIN", on_click=do_reset_pin, bgcolor=theme.BLUE, color=theme.WHITE),
        ],
    )

    def open_pin_dialog(t):
        pin_target["id"] = t.id
        pin_target["name"] = t.name
        f_new_pin.value = ""
        pin_error.value = ""
        pin_dialog_title.value = f"Đặt lại PIN — {t.name}"
        pin_dialog.open = True
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    # DIALOG: Xác nhận xóa HLV
    # ══════════════════════════════════════════════════════════════════════════
    delete_target = {"obj": None}

    def confirm_delete(t):
        delete_target["obj"] = t
        confirm_dlg.content = ft.Text(
            f"Xóa huấn luyện viên '{t.name}'? Hành động này không thể hoàn tác.",
            size=theme.FONT_SM,
        )
        confirm_dlg.open = True
        page.update()

    def do_delete(e):
        t = delete_target["obj"]
        t.delete()  # BaseModel.delete() → is_active = False
        trainer_svc.update_trainer(t)  # Lưu vào DB
        confirm_dlg.open = False
        page.update()
        refresh_table()

    confirm_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Xác nhận xóa"),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(confirm_dlg, "open", False) or page.update()),
            ft.ElevatedButton("Xóa", on_click=do_delete, bgcolor=theme.RED, color=theme.WHITE),
        ],
    )

    # ══════════════════════════════════════════════════════════════════════════
    # DIALOG: Xem học viên của HLV
    # ══════════════════════════════════════════════════════════════════════════
    students_dialog_title = ft.Text("", size=theme.FONT_LG, weight=ft.FontWeight.BOLD)
    students_dialog_body = ft.Column(controls=[], spacing=8)

    students_dialog = ft.AlertDialog(
        modal=True,
        title=students_dialog_title,
        content=ft.Container(
            content=students_dialog_body,
            width=480,
        ),
        actions=[
            ft.TextButton("Đóng", on_click=lambda e: setattr(students_dialog, "open", False) or page.update()),
        ],
    )

    def open_students_dialog(t):
        """Mở dialog xem danh sách học viên đang kèm của HLV."""
        from app.services import assignment_svc
        students = assignment_svc.get_trainer_students(t.id)
        students_dialog_title.value = f"Học viên của {t.name}"

        if not students:
            students_dialog_body.controls = [
                ft.Text("Chưa có học viên nào được gán.", color=theme.GRAY, size=theme.FONT_SM),
            ]
        else:
            rows = []
            for stu in students:
                m = stu["member"]
                a = stu["assignment"]
                sub = stu.get("subscription")
                sub_info = ""
                if sub:
                    sub_info = f"  •  Gói đến {sub.end_date.strftime('%d/%m/%Y')}"
                rows.append(ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(m.name, weight=ft.FontWeight.W_600, size=theme.FONT_SM),
                            ft.Text(f"SĐT: {m.phone}{sub_info}", color=theme.GRAY, size=theme.FONT_XS),
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Text(
                                a.notes or "—",
                                size=theme.FONT_XS, color=theme.GRAY, italic=True,
                            ),
                            width=150,
                        ),
                    ]),
                    padding=ft.padding.symmetric(vertical=6),
                    border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
                ))
            students_dialog_body.controls = rows

        students_dialog.open = True
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    # BẢNG DANH SÁCH HLV
    # ══════════════════════════════════════════════════════════════════════════
    table_body = ft.Column(controls=[], spacing=0)
    stats_text = ft.Text("", size=theme.FONT_SM, color=theme.GRAY)

    def _make_row(t) -> ft.Container:
        initials = "".join(w[0].upper() for w in t.name.split()[:2])
        colors = ["#8B5CF6", "#3B82F6", "#EC4899", "#10B981", "#F59E0B"]
        avatar_color = colors[hash(t.id) % len(colors)]

        return ft.Container(
            content=ft.Row(
                controls=[
                    # ── Cột 1: Avatar + Tên + SĐT ────────────────────────
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(initials, color=theme.WHITE, size=theme.FONT_SM,
                                                weight=ft.FontWeight.BOLD),
                                width=36, height=36, bgcolor=avatar_color,
                                border_radius=18,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(t.name, size=theme.FONT_SM, weight=ft.FontWeight.W_500,
                                            color=theme.TEXT_PRIMARY),
                                    ft.Text(t.phone, size=theme.FONT_XS, color=theme.GRAY),
                                ],
                                spacing=0, tight=True,
                            ),
                        ],
                        spacing=theme.PAD_MD, expand=True,
                    ),
                    # ── Cột 2: Email ──────────────────────────────────────
                    ft.Text(t.email or "—", size=theme.FONT_SM, color=theme.GRAY, width=180),
                    # ── Cột 3: Chuyên môn ────────────────────────────────
                    ft.Container(
                        content=ft.Text(
                            t.specialization or "—",
                            size=theme.FONT_XS,
                            color=theme.BLUE,
                            weight=ft.FontWeight.W_600,
                        ),
                        bgcolor=theme.BLUE_LIGHT if t.specialization else "transparent",
                        border_radius=theme.BADGE_RADIUS,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3) if t.specialization else None,
                        width=120,
                    ),
                    # ── Cột 4: Nút hành động ─────────────────────────────
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text("Học viên", size=theme.FONT_XS, color=theme.GREEN,
                                                weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, theme.GREEN), border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                on_click=lambda e, trainer=t: open_students_dialog(trainer),
                                ink=True,
                            ),
                            ft.Container(
                                content=ft.Text("Sửa", size=theme.FONT_XS, color=theme.ORANGE,
                                                weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, theme.ORANGE), border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                on_click=lambda e, trainer=t: open_edit_dialog(trainer),
                                ink=True,
                            ),
                            ft.Container(
                                content=ft.Text("Đặt lại PIN", size=theme.FONT_XS, color=theme.BLUE,
                                                weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, theme.BLUE), border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                on_click=lambda e, trainer=t: open_pin_dialog(trainer),
                                ink=True,
                            ),
                            ft.Container(
                                content=ft.Text("Xóa", size=theme.FONT_XS, color=theme.RED,
                                                weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, theme.RED), border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                on_click=lambda e, trainer=t: confirm_delete(trainer),
                                ink=True,
                            ),
                        ],
                        spacing=theme.PAD_SM,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_MD),
            border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
        )

    def refresh_table():
        q = search_query["value"].lower()
        all_trainers = trainer_svc.get_all_trainers(active_only=True)

        if q:
            filtered = [
                t for t in all_trainers
                if q in t.name.lower()
                or q in t.phone.lower()
                or q in (t.specialization or "").lower()
            ]
        else:
            filtered = all_trainers

        stats_text.value = f"Tổng: {len(all_trainers)} HLV  •  Hiển thị: {len(filtered)}"

        if not filtered:
            table_body.controls = [
                ft.Container(
                    content=ft.Text(
                        "Không tìm thấy huấn luyện viên nào." if q else "Chưa có huấn luyện viên.",
                        size=theme.FONT_SM, color=theme.GRAY,
                    ),
                    padding=ft.padding.symmetric(vertical=theme.PAD_2XL),
                    alignment=ft.Alignment.CENTER,
                )
            ]
        else:
            table_body.controls = [_make_row(t) for t in filtered]

        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    # THANH TÌM KIẾM & TOOLBAR
    # ══════════════════════════════════════════════════════════════════════════
    search_field = ft.TextField(
        hint_text="Tìm theo tên, SĐT, chuyên môn...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=theme.BUTTON_RADIUS,
        height=40,
        text_size=theme.FONT_SM,
        width=320,
        on_change=lambda e: (
            search_query.update({"value": e.control.value}),
            refresh_table(),
        ),
    )

    toolbar = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Huấn luyện viên", size=theme.FONT_2XL, weight=ft.FontWeight.BOLD,
                            color=theme.TEXT_PRIMARY),
                    stats_text,
                ],
                spacing=2,
                expand=True,
            ),
            search_field,
            ft.ElevatedButton(
                "Thêm HLV",
                icon=ft.Icons.ADD,
                bgcolor=theme.ORANGE,
                color=theme.WHITE,
                on_click=open_add_dialog,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ── Header của bảng ───────────────────────────────────────────────────────
    table_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("Huấn luyện viên", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, expand=True),
                ft.Text("Email", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=180),
                ft.Text("Chuyên môn", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=120),
                ft.Text("Hành động", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=280),
            ],
        ),
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_MD),
        bgcolor=theme.CARD_BG,
        border_radius=ft.border_radius.only(top_left=theme.CARD_RADIUS, top_right=theme.CARD_RADIUS),
        border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
    )

    # ── Card bảng ─────────────────────────────────────────────────────────────
    table_card = ft.Container(
        content=ft.Column(
            controls=[table_header, table_body],
            spacing=0,
        ),
        bgcolor=theme.WHITE,
        border_radius=theme.CARD_RADIUS,
        border=ft.border.all(1, theme.BORDER),
    )

    # ══════════════════════════════════════════════════════════════════════════
    # CONTENT AREA
    # ══════════════════════════════════════════════════════════════════════════
    content_area = ft.Column(
        controls=[
            ft.Container(content=toolbar, padding=ft.padding.only(bottom=theme.PAD_LG)),
            table_card,
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # ĐĂNG KÝ DIALOGS VÀ TẢI DỮ LIỆU
    # ══════════════════════════════════════════════════════════════════════════
    page.overlay.extend([trainer_dialog, pin_dialog, confirm_dlg, students_dialog])
    refresh_table()

    # ── Layout tổng thể ───────────────────────────────────────────────────────
    return ft.Row(
        controls=[
            Sidebar(page, active_route="trainers"),
            ft.Column(
                controls=[
                    Header(page),
                    ft.Container(
                        content=content_area,
                        expand=True,
                        padding=ft.padding.all(theme.PAD_2XL),
                    ),
                ],
                expand=True,
                spacing=0,
            ),
        ],
        expand=True,
        spacing=0,
    )
