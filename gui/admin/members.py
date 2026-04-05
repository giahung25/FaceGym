# ============================================================================
# FILE: gui/admin/members.py
# MỤC ĐÍCH: Màn hình QUẢN LÝ HỘI VIÊN — hiển thị danh sách, thêm/sửa/xóa hội viên.
#
# CHỨC NĂNG:
#   1. Hiển thị bảng danh sách hội viên (tên, SĐT, email, giới tính)
#   2. Tìm kiếm hội viên (theo tên, SĐT, email)
#   3. Lọc theo giới tính và trạng thái gói tập
#   4. Thêm hội viên mới (dialog popup)
#   5. Sửa thông tin hội viên (dialog popup)
#   6. Xóa hội viên (soft delete, có xác nhận)
#   7. Xem chi tiết lịch sử gói tập của hội viên
#
# LAYOUT:
#   ┌──────────┬─────────────────────────────────────────────────┐
#   │ SIDEBAR  │  Header                                        │
#   │          │  ───────────────────────────────────────────    │
#   │          │  Hội viên            [🔍] [Filter] [+ Thêm]   │
#   │          │  Tổng: 50 | Active: 45 | Mới: 5               │
#   │          │  ┌─────────────────────────────────────────┐   │
#   │          │  │ Hội viên | Email | Giới tính | Hành động│   │
#   │          │  │ Nguyễn A | a@..  | Nam       | Sửa Xóa │   │
#   │          │  │ Trần B   | b@..  | Nữ        | Sửa Xóa │   │
#   │          │  └─────────────────────────────────────────┘   │
#   └──────────┴─────────────────────────────────────────────────┘
# ============================================================================

import flet as ft
from gui import theme
from gui.admin.components.header import Header
from gui.admin.components.sidebar import Sidebar
from app.repositories import member_repo, membership_repo  # Truy cập database
from app.services import member_svc                         # Logic nghiệp vụ


def MembersScreen(page: ft.Page) -> ft.Row:
    """Tạo màn hình quản lý hội viên.

    Tham số:
        page (ft.Page): đối tượng Page

    Trả về:
        ft.Row: layout gồm [Sidebar | Content Area]
    """

    # ══════════════════════════════════════════════════════════════════════════
    # STATE (Trạng thái) — lưu trữ dữ liệu tạm thời của màn hình
    # ══════════════════════════════════════════════════════════════════════════
    # Dùng dict thay vì biến thường vì:
    # - Biến thường trong closure (hàm lồng hàm) bị giới hạn bởi scope
    # - Dict là mutable (thay đổi được) → có thể sửa value từ bên trong hàm con
    search_query = {"value": ""}          # Từ khóa tìm kiếm hiện tại
    selected_member = {"obj": None}       # Hội viên đang được chọn để sửa (None = thêm mới)
    filter_gender = {"value": None}       # Lọc giới tính: None = tất cả
    filter_sub_status = {"value": None}   # Lọc gói tập: None | "active" | "no_active"

    # ══════════════════════════════════════════════════════════════════════════
    # DIALOG: Thêm / Sửa hội viên
    # ══════════════════════════════════════════════════════════════════════════
    # Dialog = popup modal hiện lên trước content, user phải tương tác xong mới đóng

    # ── Các ô nhập trong dialog ───────────────────────────────────────────────
    f_name = ft.TextField(label="Họ tên *", expand=True)         # * = bắt buộc
    f_phone = ft.TextField(label="Số điện thoại *", expand=True)
    f_email = ft.TextField(label="Email", expand=True)
    f_gender = ft.Dropdown(
        label="Giới tính",
        options=[
            ft.dropdown.Option("male", "Nam"),      # value="male", display="Nam"
            ft.dropdown.Option("female", "Nữ"),
            ft.dropdown.Option("other", "Khác"),
        ],
        expand=True,
    )
    f_dob = ft.TextField(label="Ngày sinh (YYYY-MM-DD)", expand=True)
    f_address = ft.TextField(label="Địa chỉ", expand=True)
    f_emergency = ft.TextField(label="Liên hệ khẩn cấp", expand=True)
    dialog_error = ft.Text("", color=theme.RED, size=theme.FONT_SM)  # Thông báo lỗi trong dialog
    dialog_title = ft.Text("", size=theme.FONT_LG, weight=ft.FontWeight.BOLD)  # Tiêu đề dialog

    def clear_form():
        """Xóa tất cả giá trị trong form (reset về trống).
        Được gọi trước khi mở dialog thêm/sửa.
        """
        for f in [f_name, f_phone, f_email, f_dob, f_address, f_emergency]:
            f.value = ""       # Xóa giá trị các TextField
        f_gender.value = None  # Reset Dropdown về chưa chọn
        dialog_error.value = "" # Xóa thông báo lỗi

    def save_member(e):
        """Xử lý khi click nút "Lưu" trong dialog thêm/sửa.

        Logic:
        - Nếu selected_member là None → THÊM MỚI (gọi register_member)
        - Nếu selected_member có giá trị → SỬA (gọi update_member)
        - Nếu lỗi (ValueError) → hiện thông báo lỗi trong dialog
        """
        try:
            if selected_member["obj"] is None:
                # ── THÊM MỚI ─────────────────────────────────────────────
                member_svc.register_member(
                    name=f_name.value,
                    phone=f_phone.value,
                    email=f_email.value or None,    # Rỗng → None
                    gender=f_gender.value,
                    date_of_birth=f_dob.value or None,
                    address=f_address.value or None,
                    emergency_contact=f_emergency.value or None,
                )
            else:
                # ── CẬP NHẬT ─────────────────────────────────────────────
                m = selected_member["obj"]
                # Sửa trực tiếp các thuộc tính của Member object
                m.name = f_name.value.strip()
                m.phone = f_phone.value.strip()
                m.email = f_email.value.strip() if f_email.value else None
                m.gender = f_gender.value
                m.date_of_birth = f_dob.value or None
                m.address = f_address.value or None
                m.emergency_contact = f_emergency.value or None
                member_svc.update_member(m)  # Validate + lưu DB

            member_dialog.open = False  # Đóng dialog
            page.update()
            refresh_table()             # Làm mới bảng danh sách
        except ValueError as ex:
            # Lỗi validation → hiện thông báo trong dialog
            dialog_error.value = str(ex)
            page.update()

    # ── Tạo dialog (AlertDialog = popup modal) ───────────────────────────────
    member_dialog = ft.AlertDialog(
        modal=True,  # modal = user PHẢI đóng dialog trước khi tương tác content phía sau
        title=dialog_title,
        content=ft.Column(
            controls=[
                ft.Row(controls=[f_name, f_phone], spacing=theme.PAD_MD),    # 2 ô trên 1 hàng
                ft.Row(controls=[f_email, f_gender], spacing=theme.PAD_MD),
                ft.Row(controls=[f_dob, f_emergency], spacing=theme.PAD_MD),
                f_address,
                dialog_error,
            ],
            spacing=theme.PAD_MD,
            width=560,    # Chiều rộng dialog
            tight=True,
        ),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(member_dialog, "open", False) or page.update()),
            # ↑ setattr(obj, "open", False) tương đương member_dialog.open = False
            #   Dùng setattr vì lambda chỉ cho phép 1 expression
            #   `or page.update()` = luôn gọi page.update() sau setattr
            ft.ElevatedButton("Lưu", on_click=save_member, bgcolor=theme.ORANGE, color=theme.WHITE),
        ],
    )

    def open_add_dialog(e):
        """Mở dialog THÊM hội viên mới."""
        selected_member["obj"] = None  # Đánh dấu: đang thêm mới (không phải sửa)
        clear_form()                    # Reset form
        dialog_title.value = "Thêm hội viên mới"
        member_dialog.open = True       # Mở dialog
        page.update()

    def open_edit_dialog(m):
        """Mở dialog SỬA thông tin hội viên.

        Tham số:
            m (Member): đối tượng hội viên cần sửa
        """
        selected_member["obj"] = m    # Lưu reference tới member đang sửa
        clear_form()
        dialog_title.value = "Chỉnh sửa hội viên"
        # Điền thông tin hiện tại vào form
        f_name.value = m.name
        f_phone.value = m.phone
        f_email.value = m.email or ""          # None → "" (tránh hiện "None")
        f_gender.value = m.gender
        f_dob.value = str(m.date_of_birth) if m.date_of_birth else ""
        f_address.value = m.address or ""
        f_emergency.value = m.emergency_contact or ""
        member_dialog.open = True
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    # DIALOG: Chi tiết — Lịch sử gói tập của hội viên
    # ══════════════════════════════════════════════════════════════════════════
    detail_body = ft.Column(controls=[], spacing=0, scroll=ft.ScrollMode.AUTO)
    detail_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Lịch sử gói tập", size=theme.FONT_LG, weight=ft.FontWeight.BOLD),
        content=ft.Container(content=detail_body, width=540, height=320),
        actions=[
            ft.TextButton("Đóng", on_click=lambda e: setattr(detail_dialog, "open", False) or page.update()),
        ],
    )

    # Mapping: status → (màu nền badge, màu chữ badge)
    STATUS_COLORS = {
        "active": (theme.GREEN_LIGHT, theme.GREEN),
        "expired": (theme.AMBER_LIGHT, theme.AMBER),
        "cancelled": (theme.RED_LIGHT, theme.RED),
    }

    def open_detail_dialog(m):
        """Mở dialog xem lịch sử gói tập của hội viên.

        Tham số:
            m (Member): hội viên cần xem chi tiết
        """
        # Lấy tất cả đăng ký gói tập của hội viên này
        subs = membership_repo.get_subscriptions_by_member(m.id)
        # Tạo mapping plan_id → tên gói (để hiển thị tên thay vì UUID)
        plans_map = {p.id: p.name for p in membership_repo.get_all_plans(active_only=False)}

        if not subs:
            # Chưa có lịch sử → hiện thông báo
            detail_body.controls = [
                ft.Text("Chưa có lịch sử đăng ký gói tập.", size=theme.FONT_SM, color=theme.GRAY)
            ]
        else:
            # Tạo danh sách các row hiển thị từng đăng ký
            rows = []
            for s in subs:
                bg, fg = STATUS_COLORS.get(s.status, (theme.GRAY_LIGHT, theme.GRAY))
                rows.append(ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    # Tên gói tập
                                    ft.Text(plans_map.get(s.plan_id, "?"), size=theme.FONT_SM,
                                            weight=ft.FontWeight.W_500, color=theme.TEXT_PRIMARY),
                                    # Khoảng thời gian: ngày bắt đầu → ngày kết thúc
                                    ft.Text(
                                        f"{s.start_date.strftime('%d/%m/%Y')} → {s.end_date.strftime('%d/%m/%Y')}",
                                        size=theme.FONT_XS, color=theme.GRAY,
                                    ),
                                ],
                                spacing=2, expand=True,
                            ),
                            # Badge trạng thái (active/expired/cancelled)
                            ft.Container(
                                content=ft.Text(s.status, size=theme.FONT_XS, color=fg,
                                                weight=ft.FontWeight.W_600),
                                bgcolor=bg, border_radius=theme.BADGE_RADIUS,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                            # Giá đã thanh toán
                            ft.Text(f"{int(s.price_paid):,}đ", size=theme.FONT_SM,
                                    color=theme.ORANGE, width=90),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(horizontal=theme.PAD_MD, vertical=theme.PAD_MD),
                    border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
                ))
            detail_body.controls = rows

        # Cập nhật tiêu đề dialog với tên hội viên
        detail_dialog.title = ft.Text(
            f"Lịch sử gói tập — {m.name}",
            size=theme.FONT_LG, weight=ft.FontWeight.BOLD,
        )
        detail_dialog.open = True
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    # DIALOG: Xác nhận xóa hội viên
    # ══════════════════════════════════════════════════════════════════════════
    delete_target = {"id": None}  # Lưu ID hội viên sắp xóa

    def confirm_delete(m):
        """Mở dialog xác nhận trước khi xóa.

        Tham số:
            m (Member): hội viên cần xóa
        """
        delete_target["id"] = m.id
        confirm_dlg.content = ft.Text(f"Xóa hội viên '{m.name}'? Hành động này không thể hoàn tác.")
        confirm_dlg.open = True
        page.update()

    def do_delete(e):
        """Thực hiện xóa (soft delete) sau khi user xác nhận."""
        member_repo.delete(delete_target["id"])  # Soft delete: is_active = 0
        confirm_dlg.open = False
        page.update()
        refresh_table()  # Làm mới bảng

    confirm_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Xác nhận xóa"),
        actions=[
            ft.TextButton("Hủy", on_click=lambda e: setattr(confirm_dlg, "open", False) or page.update()),
            ft.ElevatedButton("Xóa", on_click=do_delete, bgcolor=theme.RED, color=theme.WHITE),
        ],
    )

    # ══════════════════════════════════════════════════════════════════════════
    # BẢNG DANH SÁCH HỘI VIÊN
    # ══════════════════════════════════════════════════════════════════════════
    table_body = ft.Column(controls=[], spacing=0)  # Container chứa các row hội viên

    def _make_row(m) -> ft.Container:
        """Tạo 1 dòng trong bảng danh sách cho 1 hội viên.

        Tham số:
            m (Member): đối tượng hội viên

        Trả về:
            ft.Container: widget dòng bảng chứa [avatar + tên | email | giới tính | nút hành động]
        """
        # Tạo chữ cái đầu tên (initials) cho avatar
        # VD: "Nguyễn Văn A" → ["Nguyễn", "Văn"] → "N" + "V" → "NV"
        initials = "".join(w[0].upper() for w in m.name.split()[:2])

        # Chọn màu avatar dựa trên hash của ID (mỗi hội viên có màu khác nhau)
        colors = ["#8B5CF6", "#3B82F6", "#EC4899", "#10B981", "#F59E0B"]
        avatar_color = colors[hash(m.id) % len(colors)]
        # ↑ hash(m.id) = số nguyên lớn, % len(colors) = lấy dư → index 0-4

        return ft.Container(
            content=ft.Row(
                controls=[
                    # ── Cột 1: Avatar + Tên + SĐT ────────────────────────
                    ft.Row(
                        controls=[
                            # Avatar tròn với chữ cái đầu
                            ft.Container(
                                content=ft.Text(initials, color=theme.WHITE, size=theme.FONT_SM,
                                                weight=ft.FontWeight.BOLD),
                                width=36, height=36, bgcolor=avatar_color,
                                border_radius=18,  # 36/2 = 18 → hình tròn
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(m.name, size=theme.FONT_SM, weight=ft.FontWeight.W_500,
                                            color=theme.TEXT_PRIMARY),
                                    ft.Text(m.phone, size=theme.FONT_XS, color=theme.GRAY),
                                ],
                                spacing=0, tight=True,
                            ),
                        ],
                        spacing=theme.PAD_MD, expand=True,
                    ),
                    # ── Cột 2: Email ──────────────────────────────────────
                    ft.Text(m.email or "—", size=theme.FONT_SM, color=theme.GRAY, width=180),
                    # ── Cột 3: Giới tính ──────────────────────────────────
                    ft.Text(
                        {"male": "Nam", "female": "Nữ", "other": "Khác"}.get(m.gender or "", "—"),
                        # ↑ Dict.get(): chuyển "male"→"Nam", "female"→"Nữ", None→"—"
                        size=theme.FONT_SM, color=theme.GRAY, width=60,
                    ),
                    # ── Cột 4: Các nút hành động ─────────────────────────
                    ft.Row(
                        controls=[
                            # Nút "Chi tiết" (xanh dương)
                            ft.Container(
                                content=ft.Text("Chi tiết", size=theme.FONT_XS, color=theme.BLUE,
                                                weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, theme.BLUE), border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                on_click=lambda e, member=m: open_detail_dialog(member),
                                # ↑ member=m: binding giá trị m tại thời điểm tạo lambda
                            ),
                            # Nút "Sửa" (cam)
                            ft.Container(
                                content=ft.Text("Sửa", size=theme.FONT_XS, color=theme.ORANGE,
                                                weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, theme.ORANGE), border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                on_click=lambda e, member=m: open_edit_dialog(member),
                            ),
                            # Nút "Xóa" (đỏ)
                            ft.Container(
                                content=ft.Text("Xóa", size=theme.FONT_XS, color=theme.RED,
                                                weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, theme.RED), border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                on_click=lambda e, member=m: confirm_delete(member),
                            ),
                        ],
                        spacing=theme.PAD_SM,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_MD),
            border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),  # Viền dưới
        )

    # ══════════════════════════════════════════════════════════════════════════
    # HÀM LÀM MỚI BẢNG (với filter)
    # ══════════════════════════════════════════════════════════════════════════
    def refresh_table():
        """Tải lại dữ liệu và render bảng, áp dụng các bộ lọc (filter).

        Flow:
        1. Lấy danh sách hội viên (có tìm kiếm hoặc không)
        2. Lọc theo giới tính (nếu có)
        3. Lọc theo trạng thái gói tập (nếu có)
        4. Tạo lại các row trong bảng
        5. Cập nhật dòng thống kê
        6. Gọi page.update() để render
        """
        # Bước 1: Tìm kiếm hoặc lấy tất cả
        kw = search_query["value"].strip()
        members = member_repo.search(kw) if kw else member_repo.get_all()

        # Bước 2: Lọc theo giới tính
        gf = filter_gender["value"]
        if gf:
            members = [m for m in members if m.gender == gf]

        # Bước 3: Lọc theo trạng thái subscription
        sf = filter_sub_status["value"]
        if sf:
            # Lấy tập hợp (set) member_id có subscription active
            active_ids = {
                s.member_id
                for s in membership_repo.get_all_subscriptions()
                if s.status == "active"
            }
            if sf == "active":
                # Chỉ giữ hội viên CÓ gói active
                members = [m for m in members if m.id in active_ids]
            else:
                # Chỉ giữ hội viên KHÔNG có gói active
                members = [m for m in members if m.id not in active_ids]

        # Bước 4: Tạo lại các row
        table_body.controls = [_make_row(m) for m in members]

        # Bước 5: Cập nhật dòng thống kê
        stats = member_svc.get_member_stats()
        total_text.value = (
            f"Tổng: {stats['total']}  |  Active: {stats['active']}  |  Mới tháng này: {stats['new_this_month']}"
            + (f"  |  Đang lọc: {len(members)}" if gf or sf else "")  # Thêm số lượng lọc nếu có filter
        )
        page.update()

    total_text = ft.Text("", size=theme.FONT_SM, color=theme.GRAY)  # Dòng thống kê

    def on_search(e):
        """Callback khi user gõ vào ô tìm kiếm trên trang Members."""
        search_query["value"] = e.control.value  # Lưu từ khóa
        refresh_table()                           # Làm mới bảng

    # ══════════════════════════════════════════════════════════════════════════
    # FILTER CONTROLS (Bộ lọc)
    # ══════════════════════════════════════════════════════════════════════════
    # Dropdown lọc giới tính
    # gender_filter = ft.Dropdown(
    #     label="Giới tính",
    #     width=130,
    #     border=ft.InputBorder.UNDERLINE,
    #     enable_filter=True,
    #     editable=True,
    #     leading_icon=ft.Icons.SEARCH,
    #     options=[
    #         ft.dropdown.Option("", "Tất cả"),
    #         ft.dropdown.Option("male", "Nam"),
    #         ft.dropdown.Option("female", "Nữ"),
    #         ft.dropdown.Option("other", "Khác"),
    #     ],
    #     value="",  # Mặc định: tất cả
    # )

    # def on_gender_change(e):
    #     """Callback khi thay đổi filter giới tính."""
    #     filter_gender.update({"value": e.control.value or None})  # "" → None (tất cả)
    #     refresh_table()

    # gender_filter.on_change = on_gender_change  # Gắn callback

    # # Dropdown lọc trạng thái gói tập
    # sub_status_filter = ft.Dropdown(
    #     label="Gói tập",
    #     width=150,
    #     border=ft.InputBorder.UNDERLINE,
    #     enable_filter=True,
    #     editable=True,
    #     leading_icon=ft.Icons.SEARCH,
    #     options=[
    #         ft.dropdown.Option("", "Tất cả"),
    #         ft.dropdown.Option("active", "Đang active"),
    #         ft.dropdown.Option("no_active", "Không active"),
    #     ],
    #     value="",
    # )

    # def on_sub_status_change(e):
    #     """Callback khi thay đổi filter gói tập."""
    #     filter_sub_status.update({"value": e.control.value or None})
    #     refresh_table()

    # sub_status_filter.on_change = on_sub_status_change

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT (Bố cục giao diện)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Thanh tìm kiếm (SearchBar chuẩn Flet) ─────────────────────────────────
    search_field = ft.SearchBar(
        bar_hint_text="Tìm theo tên, SĐT, email...",
        bar_leading=ft.Icon(ft.Icons.SEARCH, color=theme.GRAY, size=16),
        bar_bgcolor=theme.WHITE,
        bar_border_side=ft.BorderSide(1, theme.BORDER),
        bar_text_style=ft.TextStyle(size=theme.FONT_SM, color=theme.TEXT_PRIMARY),
        bar_hint_text_style=ft.TextStyle(size=theme.FONT_SM, color=theme.GRAY),
        on_change=on_search,
        width=260,
        height=40,
    )

    # ── Header row: tiêu đề + ô tìm kiếm + filter + nút thêm ────────────────
    header_row = ft.Row(
        controls=[
            ft.Text("Hội viên", size=theme.FONT_2XL, weight=ft.FontWeight.BOLD,
                    color=theme.TEXT_PRIMARY),
            ft.Row(
                controls=[
                    search_field,
                    # Nút thêm hội viên
                    ft.ElevatedButton(
                        "+ Thêm hội viên",
                        bgcolor=theme.ORANGE, color=theme.WHITE,
                        on_click=open_add_dialog,
                    ),
                ],
                spacing=theme.PAD_MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ── Header bảng (tên các cột) ────────────────────────────────────────────
    col_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("Hội viên", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, expand=True),
                ft.Text("Email", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=180),
                ft.Text("Giới tính", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=60),
                ft.Text("Hành động", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=170),
            ],
        ),
        bgcolor=theme.BG,  # Nền xám nhạt cho header bảng
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_SM),
    )

    # ── Bảng (bọc header + body) ─────────────────────────────────────────────
    member_table = ft.Container(
        content=ft.Column(controls=[col_header, table_body], spacing=0),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
    )

    # ── Đăng ký dialog vào overlay ────────────────────────────────────────────
    # Flet yêu cầu dialog phải nằm trong page.overlay mới hiển thị được
    page.overlay.extend([member_dialog, confirm_dlg, detail_dialog])

    # ── Layout chính ──────────────────────────────────────────────────────────
    main_content = ft.Column(
        controls=[
            Header(page),  # Header trên cùng
            ft.Container(
                content=ft.Column(
                    controls=[
                        header_row,      # Tiêu đề + tìm kiếm + filter
                        total_text,      # Dòng thống kê
                        member_table,    # Bảng danh sách
                    ],
                    spacing=theme.PAD_LG,
                    scroll=ft.ScrollMode.AUTO,  # Cho phép cuộn nếu nội dung dài
                    expand=True,
                ),
                padding=ft.padding.all(theme.PAD_2XL),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )

    # ── Đăng ký callback cho header search bar ────────────────────────────────
    # Khi user gõ vào ô search trên Header → gọi _header_search → refresh bảng
    def _header_search(value: str):
        search_query["value"] = value
        refresh_table()

    page.on_search_change = _header_search  # Gắn callback cho Header

    # ── Tải dữ liệu lần đầu ──────────────────────────────────────────────────
    refresh_table()

    # ── Trả về layout: Sidebar + Content ──────────────────────────────────────
    return ft.Row(
        controls=[Sidebar(page, active_route="members"), main_content],
        spacing=0,
        expand=True,
    )
