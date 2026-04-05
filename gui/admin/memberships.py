# ============================================================================
# FILE: gui/admin/memberships.py
# MỤC ĐÍCH: Màn hình QUẢN LÝ GÓI TẬP & ĐĂNG KÝ — có 2 tab:
#   Tab 1: Gói tập (MembershipPlan) — CRUD danh sách gói
#   Tab 2: Đăng ký (Subscription) — quản lý việc hội viên đăng ký gói
#
# LAYOUT:
#   ┌──────────┬─────────────────────────────────────────────────┐
#   │ SIDEBAR  │  Header                                        │
#   │          │  ───────────────────────────────────────────    │
#   │          │  Gói tập & Đăng ký                             │
#   │          │  [Tab: Gói tập] [Tab: Đăng ký]                 │
#   │          │  ┌─────────────────────────────────────────┐   │
#   │          │  │ (Nội dung tab hiện tại)                  │   │
#   │          │  └─────────────────────────────────────────┘   │
#   └──────────┴─────────────────────────────────────────────────┘
# ============================================================================

import flet as ft
from gui import theme
from gui.admin.components.header import Header
from gui.admin.components.sidebar import Sidebar
from app.repositories import membership_repo, member_repo   # Truy cập database
from app.services import membership_svc                       # Logic nghiệp vụ
from app.services import trainer_svc                           # Lấy danh sách HLV
from app.models.membership import MembershipSubscription      # Dùng STATUS constants


def MembershipsScreen(page: ft.Page) -> ft.Row:
    """Tạo màn hình quản lý gói tập và đăng ký."""

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1: GÓI TẬP (Plans)
    # ══════════════════════════════════════════════════════════════════════════
    plans_body = ft.Column(controls=[], spacing=0)  # Container chứa danh sách gói
    selected_plan = {"obj": None}                    # Gói đang sửa (None = thêm mới)

    # ── Form fields cho dialog thêm/sửa gói ──────────────────────────────────
    fp_name = ft.TextField(label="Tên gói *", expand=True)
    fp_days = ft.TextField(label="Số ngày *", expand=True, keyboard_type=ft.KeyboardType.NUMBER)
    fp_price = ft.TextField(label="Giá (VND) *", expand=True, keyboard_type=ft.KeyboardType.NUMBER)
    fp_desc = ft.TextField(label="Mô tả", expand=True, multiline=True, min_lines=2)
    plan_dialog_error = ft.Text("", color=theme.RED, size=theme.FONT_SM)
    plan_dialog_title = ft.Text("", size=theme.FONT_LG, weight=ft.FontWeight.BOLD)

    def save_plan(e):
        """Lưu gói tập (thêm mới hoặc cập nhật).

        Flow:
        1. Parse số ngày và giá từ string → int/float
        2. Nếu thêm mới → gọi membership_svc.create_plan()
        3. Nếu sửa → gọi membership_svc.update_plan()
        4. Đóng dialog + refresh danh sách
        """
        try:
            days = int(fp_days.value or 0)      # Chuyển string → int (0 nếu rỗng)
            price = float(fp_price.value or 0)  # Chuyển string → float
            if selected_plan["obj"] is None:
                # THÊM MỚI
                membership_svc.create_plan(
                    name=fp_name.value,
                    duration_days=days,
                    price=price,
                    description=fp_desc.value or None,
                )
            else:
                # CẬP NHẬT
                p = selected_plan["obj"]
                membership_svc.update_plan(p, name=fp_name.value, duration_days=days,
                                           price=price, description=fp_desc.value or None)
            plan_dialog.open = False
            page.update()
            refresh_plans()
        except (ValueError, TypeError) as ex:
            plan_dialog_error.value = str(ex)
            page.update()

    # ── Dialog thêm/sửa gói ──────────────────────────────────────────────────
    plan_dialog = ft.AlertDialog(
        modal=True,
        title=plan_dialog_title,
        content=ft.Column(
            controls=[
                ft.Row(controls=[fp_name], spacing=theme.PAD_MD),
                ft.Row(controls=[fp_days, fp_price], spacing=theme.PAD_MD),
                fp_desc,
                plan_dialog_error,
            ],
            spacing=theme.PAD_MD, width=480, tight=True,
        ),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(plan_dialog, "open", False) or page.update()),
            ft.ElevatedButton("Lưu", on_click=save_plan, bgcolor=theme.ORANGE, color=theme.WHITE),
        ],
    )

    def open_add_plan(e):
        """Mở dialog thêm gói tập mới — reset form trước."""
        selected_plan["obj"] = None
        fp_name.value = fp_days.value = fp_price.value = fp_desc.value = ""
        plan_dialog_error.value = ""
        plan_dialog_title.value = "Thêm gói tập mới"
        plan_dialog.open = True
        page.update()

    def open_edit_plan(p):
        """Mở dialog sửa gói tập — điền thông tin hiện tại vào form."""
        selected_plan["obj"] = p
        fp_name.value = p.name
        fp_days.value = str(p.duration_days)
        fp_price.value = str(int(p.price))
        fp_desc.value = p.description or ""
        plan_dialog_error.value = ""
        plan_dialog_title.value = "Chỉnh sửa gói tập"
        plan_dialog.open = True
        page.update()

    # ── Dialog xác nhận xóa gói ──────────────────────────────────────────────
    delete_plan_id = {"id": None}
    confirm_plan_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Xác nhận xóa gói tập"),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(confirm_plan_dlg, "open", False) or page.update()),
            ft.ElevatedButton("Xóa", bgcolor=theme.RED, color=theme.WHITE,
                              on_click=lambda e: [membership_repo.delete_plan(delete_plan_id["id"]),
                                                  setattr(confirm_plan_dlg, "open", False),
                                                  page.update(), refresh_plans()]),
            # ↑ Lambda chứa list [] để thực hiện nhiều hành động:
            #   1. Xóa gói trong DB
            #   2. Đóng dialog
            #   3. Cập nhật UI
            #   4. Refresh danh sách
        ],
    )

    def refresh_plans():
        """Tải lại danh sách gói tập từ database và render ra UI."""
        plans = membership_repo.get_all_plans()
        rows = []
        for p in plans:
            rows.append(ft.Container(
                content=ft.Row(
                    controls=[
                        # Cột trái: tên gói + mô tả
                        ft.Column(
                            controls=[
                                ft.Text(p.name, size=theme.FONT_MD, weight=ft.FontWeight.W_600,
                                        color=theme.TEXT_PRIMARY),
                                ft.Text(f"{p.duration_days} ngày  •  {p.description or ''}",
                                        size=theme.FONT_XS, color=theme.GRAY),
                            ],
                            spacing=2, expand=True,
                        ),
                        # Giá (cam, in đậm)
                        ft.Text(f"{int(p.price):,}đ", size=theme.FONT_LG,
                                weight=ft.FontWeight.BOLD, color=theme.ORANGE, width=120),
                        # Nút sửa/xóa
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text("Sửa", size=theme.FONT_XS, color=theme.ORANGE,
                                                    weight=ft.FontWeight.W_600),
                                    border=ft.border.all(1, theme.ORANGE), border_radius=6,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=3),
                                    on_click=lambda e, plan=p: open_edit_plan(plan),
                                ),
                                ft.Container(
                                    content=ft.Text("Xóa", size=theme.FONT_XS, color=theme.RED,
                                                    weight=ft.FontWeight.W_600),
                                    border=ft.border.all(1, theme.RED), border_radius=6,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=3),
                                    on_click=lambda e, plan=p: [
                                        delete_plan_id.update({"id": plan.id}),
                                        setattr(confirm_plan_dlg, "open", True),
                                        page.update(),
                                    ],
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
            ))
        plans_body.controls = rows  # Gán danh sách row mới vào container
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2: ĐĂNG KÝ GÓI TẬP (Subscriptions)
    # ══════════════════════════════════════════════════════════════════════════
    subs_body = ft.Column(controls=[], spacing=0)

    # ── Form đăng ký mới ──────────────────────────────────────────────────────
    fs_member = ft.Dropdown(label="Hội viên *", expand=True)   # Dropdown chọn hội viên
    fs_plan = ft.Dropdown(label="Gói tập *", expand=True)      # Dropdown chọn gói
    fs_trainer = ft.Dropdown(label="Huấn luyện viên (tùy chọn)", expand=True)  # Dropdown chọn HLV
    fs_price = ft.TextField(label="Giá thực tế (để trống = giá gốc)", expand=True,
                            keyboard_type=ft.KeyboardType.NUMBER)
    fs_start = ft.TextField(label="Ngày bắt đầu (YYYY-MM-DD, để trống = hôm nay)", expand=True)
    sub_dialog_error = ft.Text("", color=theme.RED, size=theme.FONT_SM)

    def save_sub(e):
        """Lưu đăng ký gói tập mới."""
        try:
            from datetime import datetime as dt
            # Parse ngày bắt đầu (nếu có nhập)
            start = dt.fromisoformat(fs_start.value) if fs_start.value.strip() else None
            # Parse giá thực tế (nếu có nhập)
            price = float(fs_price.value) if fs_price.value.strip() else None
            # Gọi service để đăng ký
            trainer_id = fs_trainer.value if fs_trainer.value else None
            membership_svc.subscribe_member(
                member_id=fs_member.value,   # ID hội viên đã chọn trong dropdown
                plan_id=fs_plan.value,       # ID gói tập đã chọn
                price_paid=price,
                start_date=start,
                trainer_id=trainer_id,        # HLV (None = gói thường)
            )
            sub_dialog.open = False
            page.update()
            refresh_subs()
        except Exception as ex:
            sub_dialog_error.value = str(ex)
            page.update()

    # ── Dialog đăng ký mới ────────────────────────────────────────────────────
    sub_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Đăng ký gói tập", size=theme.FONT_LG, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                ft.Row(controls=[fs_member, fs_plan], spacing=theme.PAD_MD),
                ft.Row(controls=[fs_trainer], spacing=theme.PAD_MD),
                ft.Row(controls=[fs_price, fs_start], spacing=theme.PAD_MD),
                sub_dialog_error,
            ],
            spacing=theme.PAD_MD, width=540, tight=True,
        ),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(sub_dialog, "open", False) or page.update()),
            ft.ElevatedButton("Đăng ký", on_click=save_sub, bgcolor=theme.ORANGE, color=theme.WHITE),
        ],
    )

    def open_add_sub(e):
        """Mở dialog đăng ký gói tập mới.

        Load danh sách hội viên + gói tập từ DB vào dropdown trước khi mở.
        """
        members = member_repo.get_all()
        plans = membership_repo.get_all_plans()
        trainers = trainer_svc.get_all_trainers(active_only=True)
        # Tạo options cho dropdown hội viên: hiển thị tên, value = ID
        fs_member.options = [ft.dropdown.Option(m.id, m.name) for m in members]
        # Tạo options cho dropdown gói: hiển thị "tên (số ngày - giá)"
        fs_plan.options = [ft.dropdown.Option(p.id, f"{p.name} ({p.duration_days}d - {int(p.price):,}đ)")
                           for p in plans]
        # Tạo options cho dropdown HLV: "Không có" + danh sách HLV
        fs_trainer.options = [ft.dropdown.Option("", "Không có (gói thường)")] + [
            ft.dropdown.Option(t.id, f"{t.name} — {t.specialization or 'Chưa rõ'}")
            for t in trainers
        ]
        fs_member.value = fs_plan.value = None  # Reset selection
        fs_trainer.value = ""  # Mặc định: không chọn HLV
        fs_price.value = fs_start.value = ""
        sub_dialog_error.value = ""
        sub_dialog.open = True
        page.update()

    # ── Mapping màu status ────────────────────────────────────────────────────
    STATUS_COLORS = {
        "active": (theme.GREEN_LIGHT, theme.GREEN),
        "expired": (theme.AMBER_LIGHT, theme.AMBER),
        "cancelled": (theme.RED_LIGHT, theme.RED),
    }
    STATUS_LABELS = {
        "active": "Đang dùng",
        "expired": "Hết hạn",
        "cancelled": "Đã hủy",
    }

    # ── Dialog xác nhận hủy gói ──────────────────────────────────────────────
    cancel_confirm_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Xác nhận hủy gói tập"),
        content=ft.Text("Hủy gói tập này? Hành động không thể hoàn tác."),
    )
    cancel_target_id = {"id": None}

    def do_cancel(e):
        """Thực hiện hủy gói tập sau khi user xác nhận."""
        try:
            membership_svc.cancel_subscription(cancel_target_id["id"])
        except ValueError:
            pass  # Bỏ qua nếu gói không thể hủy (đã expired/cancelled)
        cancel_confirm_dlg.open = False
        page.update()
        refresh_subs()

    cancel_confirm_dlg.actions = [
        ft.TextButton("Đóng", on_click=lambda e: setattr(cancel_confirm_dlg, "open", False) or page.update()),
        ft.ElevatedButton("Hủy gói", on_click=do_cancel, bgcolor=theme.RED, color=theme.WHITE),
    ]

    def open_cancel_confirm(sub_id: str):
        """Mở dialog xác nhận hủy gói tập."""
        cancel_target_id["id"] = sub_id
        cancel_confirm_dlg.open = True
        page.update()

    def refresh_subs():
        """Tải lại danh sách đăng ký gói tập từ database.

        Cũng gọi auto_expire để tự động chuyển gói quá hạn → 'expired'.
        """
        membership_svc.auto_expire_subscriptions()  # Tự động expire các gói quá hạn
        # Tự động kết thúc assignment khi gói hết hạn
        from app.services import assignment_svc
        assignment_svc.auto_end_expired_assignments()
        subs = membership_repo.get_all_subscriptions()
        # Tạo mapping ID → tên (để hiển thị tên thay vì UUID)
        members_map = {m.id: m.name for m in member_repo.get_all(active_only=False)}
        plans_map = {p.id: p.name for p in membership_repo.get_all_plans(active_only=False)}
        trainers_map = {t.id: t.name for t in trainer_svc.get_all_trainers(active_only=False)}

        rows = []
        for s in subs:
            bg, fg = STATUS_COLORS.get(s.status, (theme.GRAY_LIGHT, theme.GRAY))
            # Nút "Hủy" chỉ hiện khi gói đang active
            cancel_btn = ft.Container(
                content=ft.Text("Hủy", size=theme.FONT_XS, color=theme.RED,
                                weight=ft.FontWeight.W_600),
                border=ft.border.all(1, theme.RED), border_radius=6,
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                on_click=lambda e, sid=s.id: open_cancel_confirm(sid),
            ) if s.status == MembershipSubscription.STATUS_ACTIVE else ft.Container(width=46)
            # ↑ Nếu không active → tạo container rỗng cùng kích thước (giữ layout đều)

            rows.append(ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(members_map.get(s.member_id, "?"), size=theme.FONT_SM,
                                weight=ft.FontWeight.W_500, color=theme.TEXT_PRIMARY, expand=True),
                        ft.Text(plans_map.get(s.plan_id, "?"), size=theme.FONT_SM,
                                color=theme.GRAY, width=140),
                        ft.Text(
                            trainers_map.get(getattr(s, 'trainer_id', None), "—"),
                            size=theme.FONT_SM, color=theme.BLUE if getattr(s, 'trainer_id', None) else theme.GRAY,
                            width=120,
                        ),
                        ft.Text(s.start_date.strftime("%d/%m/%Y"), size=theme.FONT_SM,
                                color=theme.GRAY, width=90),
                        ft.Text(s.end_date.strftime("%d/%m/%Y"), size=theme.FONT_SM,
                                color=theme.GRAY, width=90),
                        # Badge trạng thái
                        ft.Container(
                            content=ft.Text(STATUS_LABELS.get(s.status, s.status), size=theme.FONT_XS, color=fg,
                                            weight=ft.FontWeight.W_600),
                            bgcolor=bg, border_radius=theme.BADGE_RADIUS,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3), width=80,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Text(f"{int(s.price_paid):,}đ", size=theme.FONT_SM,
                                color=theme.ORANGE, width=100),
                        cancel_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_MD),
                border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
            ))
        subs_body.controls = rows
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    # TABS (Chuyển đổi giữa Gói tập và Đăng ký)
    # ══════════════════════════════════════════════════════════════════════════
    # Đăng ký tất cả dialog vào overlay
    page.overlay.extend([plan_dialog, confirm_plan_dlg, sub_dialog, cancel_confirm_dlg])

    # ── Nội dung Tab "Gói tập" ────────────────────────────────────────────────
    plans_tab_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Danh sách gói tập", size=theme.FONT_LG,
                                weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                        ft.ElevatedButton("+ Thêm gói", bgcolor=theme.ORANGE,
                                          color=theme.WHITE, on_click=open_add_plan),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(
                    content=ft.Column(controls=[plans_body], spacing=0),
                    bgcolor=theme.CARD_BG,
                    border_radius=theme.CARD_RADIUS,
                    shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
                ),
            ],
            spacing=theme.PAD_LG,
        ),
        padding=ft.padding.all(theme.PAD_2XL),
    )

    # ── Header cột cho tab Đăng ký ────────────────────────────────────────────
    subs_col_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("Hội viên", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, expand=True),
                ft.Text("Gói tập", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=140),
                ft.Text("HLV", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=120),
                ft.Text("Bắt đầu", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=90),
                ft.Text("Kết thúc", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=90),
                ft.Text("Trạng thái", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=80),
                ft.Text("Giá trả", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=100),
                ft.Text("", width=46),  # Cột nút hủy (trống cho header)
            ],
        ),
        bgcolor=theme.BG,
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_SM),
    )

    # ── Nội dung Tab "Đăng ký" ────────────────────────────────────────────────
    subs_tab_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Đăng ký gói tập", size=theme.FONT_LG,
                                weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                        ft.ElevatedButton("+ Đăng ký mới", bgcolor=theme.ORANGE,
                                          color=theme.WHITE, on_click=open_add_sub),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(
                    content=ft.Column(controls=[subs_col_header, subs_body], spacing=0),
                    bgcolor=theme.CARD_BG,
                    border_radius=theme.CARD_RADIUS,
                    shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
                ),
            ],
            spacing=theme.PAD_LG,
        ),
        padding=ft.padding.all(theme.PAD_2XL),
    )

    def on_tab_change(e):
        """Callback khi user chuyển tab.
        Tab 0 = Gói tập → refresh plans
        Tab 1 = Đăng ký → refresh subs
        """
        if e.control.selected_index == 0:
            refresh_plans()
        else:
            refresh_subs()

    # ── Widget Tabs (Flet) ────────────────────────────────────────────────────
    tabs = ft.Tabs(
        selected_index=0,   # Tab mặc định: Gói tập
        length=2,            # Số lượng tab
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Gói tập"),
                        ft.Tab(label="Đăng ký"),
                    ],
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        plans_tab_content,   # Nội dung tab 1
                        subs_tab_content,    # Nội dung tab 2
                    ],
                ),
            ],
        ),
        on_change=on_tab_change,
    )

    # ── Layout chính ──────────────────────────────────────────────────────────
    main_content = ft.Column(
        controls=[
            Header(page),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Gói tập & Đăng ký", size=theme.FONT_2XL,
                                weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                        tabs,
                    ],
                    spacing=theme.PAD_LG,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=ft.padding.only(left=theme.PAD_2XL, right=theme.PAD_2XL, top=theme.PAD_2XL),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )

    refresh_plans()  # Load dữ liệu tab 1 khi mở màn hình

    return ft.Row(
        controls=[Sidebar(page, active_route="packages"), main_content],
        spacing=0,
        expand=True,
    )
