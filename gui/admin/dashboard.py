# ============================================================================
# FILE: gui/admin/dashboard.py
# MỤC ĐÍCH: Màn hình DASHBOARD — trang chủ sau khi đăng nhập.
#            Hiển thị tổng quan: KPI, biểu đồ doanh thu, hội viên gần đây,
#            gói tập phổ biến, thiết bị, gói sắp hết hạn.
#
# ĐÂY LÀ MÀN HÌNH PHỨC TẠP NHẤT — gồm nhiều section:
#   1. Stat Cards (KPI): tổng hội viên, sắp hết hạn, doanh thu, thiết bị cần bảo trì
#   2. Expiring Soon: danh sách gói tập sắp hết hạn 7 ngày
#   3. Member Activity Table: 5 hội viên gần nhất
#   4. Revenue Chart: biểu đồ cột doanh thu 6 tháng
#   5. Active Growth Chart: progress bar top 3 gói phổ biến
#   6. Packages Section: danh sách gói tập dạng card
#   7. Equipment Section: tình trạng thiết bị dạng card
#   8. Footer
# ============================================================================

import flet as ft
from gui import theme
from gui.admin.components.sidebar import Sidebar
from gui.admin.components.header import Header


# ══════════════════════════════════════════════════════════════════════════════
# CÁC HÀM TẠO WIDGET CON (Helper functions)
# Mỗi hàm tạo 1 loại widget tái sử dụng trong Dashboard
# ══════════════════════════════════════════════════════════════════════════════

def stat_card(icon, label: str, value: str, badge_text: str,
              badge_color: str, badge_text_color: str = theme.WHITE) -> ft.Container:
    """Tạo 1 card KPI thống kê (hàng trên cùng Dashboard).

    Cấu trúc:
    ┌──────────────────────────┐
    │  [🔶 icon]    [badge]   │  ← icon + badge (VD: "+5 tháng này")
    │  128                     │  ← value (số lớn, in đậm)
    │  Tổng hội viên           │  ← label (mô tả)
    └──────────────────────────┘

    Tham số:
        icon: Flet icon (VD: ft.Icons.PEOPLE_ALT)
        label (str): nhãn mô tả (VD: "Tổng hội viên")
        value (str): giá trị hiển thị (VD: "128")
        badge_text (str): text trong badge (VD: "+5 tháng này")
        badge_color (str): màu nền badge
        badge_text_color (str): màu chữ badge (mặc định trắng)
    """
    return ft.Container(
        content=ft.Column(
            controls=[
                # Hàng 1: Icon (nền cam nhạt) + Badge
                ft.Row(
                    controls=[
                        # Icon bọc trong container tròn
                        ft.Container(
                            content=ft.Icon(icon, color=theme.ORANGE, size=20),
                            width=40, height=40,
                            bgcolor=theme.ORANGE_LIGHT,   # Nền cam nhạt
                            border_radius=10,
                            alignment=ft.Alignment.CENTER,
                        ),
                        # Badge (nhãn nhỏ góc phải)
                        ft.Container(
                            content=ft.Text(badge_text, size=theme.FONT_XS,
                                            color=badge_text_color, weight=ft.FontWeight.W_600),
                            bgcolor=badge_color,
                            border_radius=theme.BADGE_RADIUS,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Hàng 2: Giá trị lớn (VD: "128")
                ft.Text(value, size=theme.FONT_3XL, weight=ft.FontWeight.BOLD,
                        color=theme.TEXT_PRIMARY),
                # Hàng 3: Nhãn mô tả (VD: "Tổng hội viên")
                ft.Text(label, size=theme.FONT_SM, color=theme.GRAY),
            ],
            spacing=theme.PAD_SM,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=theme.PAD_XL,
        expand=True,  # Chia đều chiều rộng với các card khác
        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
    )


def member_row(name: str, initials: str, avatar_color: str,
               status: str, joined: str) -> ft.Container:
    """Tạo 1 dòng trong bảng "Recent Member Activity".

    Tham số:
        name (str): tên hội viên
        initials (str): chữ cái đầu (VD: "NV" cho "Nguyễn Văn")
        avatar_color (str): màu nền avatar
        status (str): "Active" | "Expired" | "New"
        joined (str): ngày tham gia (VD: "Mar 22, 2026")
    """
    # Xác định màu badge dựa trên status
    if status == "Đang hoạt động":
        badge_color = theme.GREEN_LIGHT
        badge_text_color = theme.GREEN
    elif status == "Đã hết hạn":
        badge_color = theme.AMBER_LIGHT
        badge_text_color = theme.AMBER
    else:
        badge_color = theme.BLUE_LIGHT
        badge_text_color = theme.BLUE

    return ft.Container(
        content=ft.Row(
            controls=[
                # Cột 1: Avatar tròn + Tên
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(initials, color=theme.WHITE, size=theme.FONT_SM,
                                            weight=ft.FontWeight.BOLD),
                            width=36, height=36, bgcolor=avatar_color,
                            border_radius=18, alignment=ft.Alignment.CENTER,
                        ),
                        ft.Text(name, size=theme.FONT_SM, weight=ft.FontWeight.W_500,
                                color=theme.TEXT_PRIMARY),
                    ],
                    spacing=theme.PAD_MD, expand=True,
                ),
                # Cột 2: Badge trạng thái
                ft.Container(
                    content=ft.Text(status, size=theme.FONT_XS, color=badge_text_color,
                                    weight=ft.FontWeight.W_600),
                    bgcolor=badge_color, border_radius=theme.BADGE_RADIUS,
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    width=80, alignment=ft.Alignment.CENTER,
                ),
                # Cột 3: Ngày tham gia
                ft.Text(joined, size=theme.FONT_SM, color=theme.GRAY, width=100),
                # Cột 4: Nút "View"
                ft.Container(
                    content=ft.Text("Xem", size=theme.FONT_XS, color=theme.ORANGE,
                                    weight=ft.FontWeight.W_600),
                    border=ft.border.all(1, theme.ORANGE), border_radius=6,
                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_MD),
        border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
    )


def revenue_chart(monthly_data: list[tuple[str, float]]) -> ft.Container:
    """Tạo biểu đồ CỘT doanh thu 6 tháng gần nhất.

    Vì Flet không có chart widget sẵn, ta tự vẽ bằng Container + height.

    Tham số:
        monthly_data: list các tuple (label, value)
                      VD: [("T10", 5000000), ("T11", 6000000), ...]

    Logic vẽ cột:
    - Tìm giá trị lớn nhất (max_val)
    - Mỗi cột: height = (value / max_val) * max_height_px
    - Cột cuối cùng (tháng hiện tại) được tô cam đậm, còn lại cam nhạt
    """
    max_h = 120  # Chiều cao tối đa của cột (pixel)
    max_val = max((v for _, v in monthly_data), default=0)  # Giá trị lớn nhất

    bars = []
    for i, (label, val) in enumerate(monthly_data):
        # Tính chiều cao cột tỉ lệ với giá trị
        bar_h = int((val / max_val) * max_h) if max_val > 0 else 0
        bars.append(
            ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Container(
                            # Cột cuối = cam đậm, còn lại = cam nhạt
                            bgcolor=theme.ORANGE if i == len(monthly_data) - 1 else "#FED7AA",
                            border_radius=ft.border_radius.only(top_left=4, top_right=4),
                            height=bar_h,  # Chiều cao tỉ lệ thuận với giá trị
                            width=28,
                        ),
                        height=max_h,  # Container cha cao cố định
                        alignment=ft.Alignment.BOTTOM_CENTER,  # Cột dính đáy
                    ),
                    ft.Text(label, size=theme.FONT_XS, color=theme.GRAY),  # Label dưới cột
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            )
        )

    # Tính tổng doanh thu
    total = sum(v for _, v in monthly_data)
    total_text = f"{int(total):,}đ"  # Format có dấu phẩy (VD: "30,000,000đ")

    return ft.Container(
        content=ft.Column(
            controls=[
                # Header: tiêu đề + subtitle
                ft.Row(
                    controls=[
                        ft.Text("Tổng quan doanh thu", size=theme.FONT_LG,
                                weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                        ft.Text("6 tháng gần nhất", size=theme.FONT_XS, color=theme.GRAY),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=theme.PAD_MD),  # Spacer
                # Các cột biểu đồ
                ft.Row(controls=bars, alignment=ft.MainAxisAlignment.SPACE_AROUND),
                ft.Container(height=theme.PAD_SM),
                # Dòng tổng
                ft.Row(
                    controls=[
                        ft.Text("Tổng: ", size=theme.FONT_SM, color=theme.GRAY),
                        ft.Text(total_text, size=theme.FONT_LG, weight=ft.FontWeight.BOLD,
                                color=theme.ORANGE),
                    ],
                ),
            ],
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=theme.PAD_XL,
        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
    )


def active_growth_chart(plan_stats: list[tuple[str, int]]) -> ft.Container:
    """Tạo biểu đồ "Active Growth" — top 3 gói tập phổ biến nhất.

    Dùng ProgressBar để hiển thị tỉ lệ.

    Tham số:
        plan_stats: list các tuple (tên_gói, số_lượng_active)
                    VD: [("Gói 1 tháng", 45), ("Gói 6 tháng", 30)]
    """
    colors = [theme.ORANGE, theme.BLUE, theme.GREEN]  # Màu cho mỗi gói
    max_count = max((c for _, c in plan_stats), default=0)

    rows = []
    for i, (plan_name, count) in enumerate(plan_stats):
        color = colors[i % len(colors)]  # Xoay vòng màu
        pct = count / max_count if max_count > 0 else 0.0  # Tỉ lệ phần trăm

        rows.append(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(plan_name, size=theme.FONT_SM, color=theme.TEXT_PRIMARY,
                                    expand=True),
                            ft.Text(str(count), size=theme.FONT_SM, weight=ft.FontWeight.W_600,
                                    color=color),
                        ],
                    ),
                    # Progress bar: value 0.0 → 1.0 (tỉ lệ so với gói nhiều nhất)
                    ft.ProgressBar(value=pct, color=color, bgcolor=theme.GRAY_LIGHT,
                                   height=6, border_radius=3),
                ],
                spacing=4,
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Tăng trưởng đăng ký", size=theme.FONT_LG, weight=ft.FontWeight.BOLD,
                        color=theme.TEXT_PRIMARY),
                ft.Text("Theo loại gói tập", size=theme.FONT_XS, color=theme.GRAY),
                ft.Container(height=theme.PAD_MD),
                *rows,  # Unpack: thêm tất cả row vào Column
                # ↑ *rows = rows[0], rows[1], rows[2] (thay vì [rows])
            ],
            spacing=theme.PAD_MD,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=theme.PAD_XL,
        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
    )


def package_card(name: str, price: str, period: str, member_count: int,
                 duration_label: str, is_popular: bool = False) -> ft.Container:
    """Tạo card hiển thị 1 gói tập trong section "Gym Packages".

    Tham số:
        name (str): tên gói (VD: "Gói 1 tháng")
        price (str): giá format (VD: "500,000đ")
        period (str): chu kỳ (VD: "tháng", "năm")
        member_count (int): số hội viên đang dùng
        duration_label (str): nhãn thời hạn (VD: "30 ngày")
        is_popular (bool): True = gói phổ biến nhất (viền cam, badge "POPULAR")
    """
    # Header: tên gói + badge "POPULAR" (nếu phổ biến)
    header_controls = [
        ft.Text(name, size=theme.FONT_MD, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
    ]
    if is_popular:
        header_controls.append(
            ft.Container(
                content=ft.Text("PHỔ BIẾN", size=8, color=theme.WHITE, weight=ft.FontWeight.BOLD),
                bgcolor=theme.ORANGE, border_radius=4,
                padding=ft.padding.symmetric(horizontal=6, vertical=3),
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=header_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                # Giá + chu kỳ
                ft.Row(
                    controls=[
                        ft.Text(price, size=theme.FONT_2XL, weight=ft.FontWeight.BOLD,
                                color=theme.ORANGE),
                        ft.Text(f"/{period}", size=theme.FONT_SM, color=theme.GRAY),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.END, spacing=4,
                ),
                ft.Divider(color=theme.BORDER, height=1),  # Đường kẻ ngang
                # Số members
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PEOPLE_ALT, color=theme.GRAY, size=14),
                        ft.Text(f"{member_count} hội viên", size=theme.FONT_SM, color=theme.GRAY),
                    ],
                    spacing=4,
                ),
                # Thời hạn
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ACCESS_TIME, color=theme.GRAY, size=14),
                        ft.Text(duration_label, size=theme.FONT_SM, color=theme.GRAY),
                    ],
                    spacing=4,
                ),
                # Nút "Manage"
                ft.Container(
                    content=ft.Text("Quản lý", size=theme.FONT_SM, color=theme.ORANGE,
                                    weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                    border=ft.border.all(1, theme.ORANGE),
                    border_radius=theme.BUTTON_RADIUS,
                    padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=8),
                    alignment=ft.Alignment.CENTER, expand=True,
                ),
            ],
            spacing=theme.PAD_SM,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=theme.PAD_XL,
        # Gói phổ biến: viền cam 2px, còn lại: viền xám 1px
        border=ft.border.all(2, theme.ORANGE) if is_popular else ft.border.all(1, theme.BORDER),
        expand=True,
        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
    )


def equipment_card(name: str, wear_pct: float, purchased: str,
                   status: str) -> ft.Container:
    """Tạo card hiển thị 1 thiết bị trong section "Equipment Status".

    Tham số:
        name (str): tên thiết bị
        wear_pct (float): mức độ hao mòn 0.0 → 1.0
        purchased (str): ngày mua
        status (str): "Good" | "Fair" | "Poor"
    """
    # Xác định màu dựa trên status
    if status == "Tốt":
        status_color = theme.GREEN
        status_bg = theme.GREEN_LIGHT
        bar_color = theme.GREEN
    elif status == "Khá":
        status_color = theme.AMBER
        status_bg = theme.AMBER_LIGHT
        bar_color = theme.AMBER
    else:
        status_color = theme.RED
        status_bg = theme.RED_LIGHT
        bar_color = theme.RED

    return ft.Container(
        content=ft.Column(
            controls=[
                # Tên + badge trạng thái
                ft.Row(
                    controls=[
                        ft.Text(name, size=theme.FONT_MD, weight=ft.FontWeight.W_600,
                                color=theme.TEXT_PRIMARY, expand=True),
                        ft.Container(
                            content=ft.Text(status, size=theme.FONT_XS, color=status_color,
                                            weight=ft.FontWeight.W_600),
                            bgcolor=status_bg, border_radius=theme.BADGE_RADIUS,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        ),
                    ],
                ),
                # Progress bar mức hao mòn
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Mức hao mòn", size=theme.FONT_XS, color=theme.GRAY,
                                        expand=True),
                                ft.Text(f"{int(wear_pct * 100)}%", size=theme.FONT_XS,
                                        color=bar_color, weight=ft.FontWeight.W_600),
                            ],
                        ),
                        ft.ProgressBar(value=wear_pct, color=bar_color, bgcolor=theme.GRAY_LIGHT,
                                       height=6, border_radius=3),
                    ],
                    spacing=4,
                ),
                # Ngày mua
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, color=theme.GRAY, size=12),
                        ft.Text(f"Mua: {purchased}", size=theme.FONT_XS, color=theme.GRAY),
                    ],
                    spacing=4,
                ),
            ],
            spacing=theme.PAD_SM,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=theme.PAD_LG,
        expand=True,
        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
    )


# ══════════════════════════════════════════════════════════════════════════════
# HÀM CHÍNH: DashboardScreen
# ══════════════════════════════════════════════════════════════════════════════

def DashboardScreen(page: ft.Page) -> ft.Row:
    """Tạo toàn bộ màn hình Dashboard.

    Flow:
    1. Lấy dữ liệu thống kê từ các service/repository
    2. Dùng dữ liệu để tạo các widget (stat cards, charts, tables...)
    3. Sắp xếp các widget theo layout
    4. Trả về ft.Row([Sidebar, Content])
    """
    # ── Import services & repositories ────────────────────────────────────────
    from app.services import member_svc, membership_svc, equipment_svc, attendance_svc, face_svc
    from app.repositories import member_repo, membership_repo, equipment_repo

    # ══════════════════════════════════════════════════════════════════════════
    # BƯỚC 1: LẤY DỮ LIỆU TỪ DATABASE
    # ══════════════════════════════════════════════════════════════════════════
    member_stats = member_svc.get_member_stats()           # {total, active, new_this_month}
    revenue_stats = membership_svc.get_revenue_stats()     # {monthly, yearly, total}
    eq_summary = equipment_svc.get_equipment_summary()     # {total, working, broken, maintenance}
    attendance_today = attendance_svc.count_today()         # Số check-in hôm nay
    try:
        face_registered = face_svc.get_registered_count()  # Số hội viên đã đăng ký face
    except Exception:
        face_registered = 0
    expiring_subs = membership_repo.get_expiring_soon(days=7)  # Gói sắp hết hạn
    expiring_count = len(expiring_subs)
    monthly_revenue = membership_svc.get_monthly_revenue(months=6)  # Doanh thu 6 tháng
    plan_stats = membership_svc.get_plan_subscription_stats()       # Top 3 gói phổ biến

    # ══════════════════════════════════════════════════════════════════════════
    # BƯỚC 2: TẠO CÁC SECTION
    # ══════════════════════════════════════════════════════════════════════════

    # ── [Section 1] KPI Stat Cards ────────────────────────────────────────────
    stat_cards = ft.Row(
        controls=[
            stat_card(ft.Icons.PEOPLE_ALT, "Tổng hội viên", str(member_stats["active"]),
                      f"+{member_stats['new_this_month']} tháng này", theme.GREEN_LIGHT, theme.GREEN),
            stat_card(ft.Icons.SCHEDULE, "Sắp hết hạn", str(expiring_count),
                      "7 ngày tới", theme.AMBER_LIGHT, theme.AMBER),
            stat_card(ft.Icons.ATTACH_MONEY, "Doanh thu tháng", f"{int(revenue_stats['monthly']):,}đ",
                      f"Năm: {int(revenue_stats['yearly']):,}đ", theme.GREEN_LIGHT, theme.GREEN),
            stat_card(ft.Icons.FACT_CHECK, "Điểm danh hôm nay", str(attendance_today),
                      f"{face_registered} Face ID", theme.BLUE_LIGHT, theme.BLUE),
        ],
        spacing=theme.PAD_LG,
    )

    # ── [Section 2] Member Activity Table ─────────────────────────────────────
    # Lấy 5 hội viên gần nhất
    recent_members = member_repo.get_all()[:5]  # [:5] = slice lấy 5 phần tử đầu

    # Xác định trạng thái: có gói active hay không
    subs_map = {}
    for m in recent_members:
        active_subs = membership_repo.get_active_subscriptions_by_member(m.id)
        subs_map[m.id] = "Đang hoạt động" if active_subs else "Đã hết hạn"

    # Chuẩn bị dữ liệu cho bảng
    colors_list = ["#8B5CF6", "#3B82F6", "#EC4899", "#10B981", "#F59E0B"]
    members_data = [
        (m.name,
         "".join(w[0].upper() for w in m.name.split()[:2]),  # Initials: "Nguyễn Văn" → "NV"
         colors_list[i % len(colors_list)],                   # Xoay vòng màu avatar
         subs_map.get(m.id, "Đã hết hạn"),                    # Status
         m.created_at.strftime("%d/%m/%Y"))                   # Format: "22/03/2026"
        for i, m in enumerate(recent_members)
        # ↑ enumerate() trả cả index (i) và giá trị (m)
    ]

    # Tạo các row cho bảng
    member_rows = [member_row(n, ini, c, s, j) for n, ini, c, s, j in members_data]

    # Bọc bảng trong card
    member_table = ft.Container(
        content=ft.Column(
            controls=[
                # Header bảng
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Hoạt động hội viên gần đây", size=theme.FONT_LG,
                                    weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                            ft.Text("Xem tất cả", size=theme.FONT_SM, color=theme.ORANGE,
                                    weight=ft.FontWeight.W_600),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.all(theme.PAD_LG),
                ),
                # Tên các cột
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Hội viên", size=theme.FONT_XS, color=theme.GRAY,
                                    weight=ft.FontWeight.W_600, expand=True),
                            ft.Text("Trạng thái", size=theme.FONT_XS, color=theme.GRAY,
                                    weight=ft.FontWeight.W_600, width=100),
                            ft.Text("Ngày tham gia", size=theme.FONT_XS, color=theme.GRAY,
                                    weight=ft.FontWeight.W_600, width=100),
                            ft.Text("Hành động", size=theme.FONT_XS, color=theme.GRAY,
                                    weight=ft.FontWeight.W_600, width=60),
                        ],
                    ),
                    bgcolor=theme.BG,
                    padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_SM),
                ),
                # Các row dữ liệu
                ft.Column(controls=member_rows, spacing=0),
            ],
            spacing=0,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
        expand=True,
    )

    # ── [Section 3] Packages ──────────────────────────────────────────────────
    plans = membership_repo.get_all_plans(active_only=True)
    all_subs = membership_repo.get_all_subscriptions()
    from app.models.membership import MembershipSubscription
    # Đếm số đăng ký active cho mỗi gói
    active_subs_list = [s for s in all_subs if s.status == MembershipSubscription.STATUS_ACTIVE]
    sub_counts: dict = {}
    for s in active_subs_list:
        sub_counts[s.plan_id] = sub_counts.get(s.plan_id, 0) + 1
    # Tìm gói phổ biến nhất (nhiều active sub nhất)
    popular_id = max(sub_counts, key=lambda pid: sub_counts[pid]) if sub_counts else None

    def _period_label(days: int) -> str:
        """Chuyển số ngày → label chu kỳ.
        30 ngày → "tháng", 365 → "năm", còn lại → "Xngày"
        """
        if days == 30:
            return "tháng"
        if days == 365:
            return "năm"
        return f"{days}ngày"

    # Tạo cards cho các gói
    if plans:
        pkg_controls = [
            package_card(
                name=p.name,
                price=f"{int(p.price):,}đ",
                period=_period_label(p.duration_days),
                member_count=sub_counts.get(p.id, 0),
                duration_label=f"{p.duration_days} ngày",
                is_popular=(p.id == popular_id),  # True nếu là gói phổ biến nhất
            )
            for p in plans
        ]
    else:
        pkg_controls = [ft.Text("Chưa có gói tập nào", size=theme.FONT_SM, color=theme.GRAY)]

    packages_section = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Gói tập", size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
                            color=theme.TEXT_PRIMARY),
                    ft.Text("Xem tất cả", size=theme.FONT_SM, color=theme.ORANGE,
                            weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Row(controls=pkg_controls, spacing=theme.PAD_LG),
        ],
        spacing=theme.PAD_MD,
    )

    # ── [Section 4] Equipment Status ──────────────────────────────────────────
    from app.models.equipment import Equipment
    equipments = equipment_repo.get_all(active_only=True)[:4]  # Lấy 4 thiết bị đầu

    def _eq_status(status: str) -> tuple[str, float]:
        """Chuyển status DB → (label hiển thị, mức hao mòn).
        working → ("Tốt", 0.25), maintenance → ("Khá", 0.65), broken → ("Kém", 0.90)
        """
        if status == Equipment.STATUS_WORKING:
            return "Tốt", 0.25
        if status == Equipment.STATUS_MAINTENANCE:
            return "Khá", 0.65
        return "Kém", 0.90

    if equipments:
        eq_controls = [
            equipment_card(
                name=eq.name,
                wear_pct=_eq_status(eq.status)[1],      # Mức hao mòn
                purchased=str(eq.purchase_date) if eq.purchase_date else "N/A",
                status=_eq_status(eq.status)[0],         # Label: Tốt/Khá/Kém
            )
            for eq in equipments
        ]
    else:
        eq_controls = [ft.Text("Chưa có thiết bị nào", size=theme.FONT_SM, color=theme.GRAY)]

    equipment_section = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Tình trạng thiết bị", size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
                            color=theme.TEXT_PRIMARY),
                    ft.Text("Xem tất cả", size=theme.FONT_SM, color=theme.ORANGE,
                            weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Row(controls=eq_controls, spacing=theme.PAD_LG),
        ],
        spacing=theme.PAD_MD,
    )

    # ── [Section 5] Expiring Soon ─────────────────────────────────────────────
    # Mapping ID → tên (để hiển thị tên thay vì UUID)
    all_members_map = {m.id: m.name for m in member_repo.get_all(active_only=False)}
    all_plans_map = {p.id: p.name for p in membership_repo.get_all_plans(active_only=False)}

    if expiring_subs:
        expiring_rows = []
        for s in expiring_subs:
            remaining = s.days_remaining()
            # <= 3 ngày: đỏ (urgent), > 3 ngày: vàng (warning)
            badge_color = theme.RED_LIGHT if remaining <= 3 else theme.AMBER_LIGHT
            badge_fg = theme.RED if remaining <= 3 else theme.AMBER
            expiring_rows.append(ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(all_members_map.get(s.member_id, "?"), size=theme.FONT_SM,
                                weight=ft.FontWeight.W_500, color=theme.TEXT_PRIMARY, expand=True),
                        ft.Text(all_plans_map.get(s.plan_id, "?"), size=theme.FONT_SM,
                                color=theme.GRAY, width=160),
                        ft.Text(s.end_date.strftime("%d/%m/%Y"), size=theme.FONT_SM,
                                color=theme.GRAY, width=90),
                        ft.Container(
                            content=ft.Text(f"Còn {remaining} ngày", size=theme.FONT_XS,
                                            color=badge_fg, weight=ft.FontWeight.W_600),
                            bgcolor=badge_color, border_radius=theme.BADGE_RADIUS,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_MD),
                border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
            ))
        expiring_body = ft.Column(controls=expiring_rows, spacing=0)
    else:
        expiring_body = ft.Container(
            content=ft.Text("Không có gói tập nào sắp hết hạn trong 7 ngày tới.",
                            size=theme.FONT_SM, color=theme.GRAY),
            padding=ft.padding.all(theme.PAD_LG),
        )

    expiring_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=theme.AMBER, size=18),
                                ft.Text("Gói tập sắp hết hạn (7 ngày tới)",
                                        size=theme.FONT_LG, weight=ft.FontWeight.BOLD,
                                        color=theme.TEXT_PRIMARY),
                            ],
                            spacing=theme.PAD_SM,
                        ),
                        ft.Text("Xem tất cả", size=theme.FONT_SM, color=theme.ORANGE,
                                weight=ft.FontWeight.W_600),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                expiring_body,
            ],
            spacing=0,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=ft.padding.only(left=0, right=0, top=theme.PAD_LG, bottom=0),
        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
    )

    # ── Middle Row: Member Table + Charts (cạnh nhau) ─────────────────────────
    middle_row = ft.Row(
        controls=[
            member_table,  # Bảng hội viên (bên trái, expand)
            ft.Column(
                controls=[
                    revenue_chart(monthly_revenue),       # Biểu đồ doanh thu
                    active_growth_chart(plan_stats),       # Biểu đồ gói phổ biến
                ],
                spacing=theme.PAD_LG,
                width=300,  # Cố định chiều rộng cột phải
            ),
        ],
        spacing=theme.PAD_LG,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    footer = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("Hệ thống quản lý GymAdmin", size=theme.FONT_XS, color=theme.GRAY),
                ft.Text("v1.0.0  •  2026", size=theme.FONT_XS, color=theme.GRAY),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=theme.PAD_2XL, vertical=theme.PAD_LG),
        border=ft.border.only(top=ft.BorderSide(1, theme.BORDER)),
    )

    # ══════════════════════════════════════════════════════════════════════════
    # BƯỚC 3: GHÉP TẤT CẢ THÀNH LAYOUT
    # ══════════════════════════════════════════════════════════════════════════
    main_content = ft.Column(
        controls=[
            Header(page),  # Header trên cùng
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Tiêu đề + lời chào
                        ft.Text("Bảng điều khiển", size=theme.FONT_2XL, weight=ft.FontWeight.BOLD,
                                color=theme.TEXT_PRIMARY),
                        ft.Text("Chào mừng trở lại! Đây là tổng quan hôm nay.",
                                size=theme.FONT_SM, color=theme.GRAY),
                        ft.Container(height=4),    # Spacer nhỏ
                        stat_cards,                # Dãy KPI
                        ft.Container(height=4),
                        expiring_section,          # Gói sắp hết hạn
                        ft.Container(height=4),
                        middle_row,                # Bảng + biểu đồ
                        ft.Container(height=4),
                        packages_section,          # Danh sách gói tập
                        ft.Container(height=4),
                        equipment_section,         # Tình trạng thiết bị
                        ft.Container(height=theme.PAD_LG),
                    ],
                    spacing=theme.PAD_LG,
                    scroll=ft.ScrollMode.AUTO,  # Cuộn nếu nội dung dài
                    expand=True,
                ),
                padding=ft.padding.all(theme.PAD_2XL),
                expand=True,
            ),
            footer,  # Footer dưới cùng
        ],
        spacing=0,
        expand=True,
    )

    # Trả về layout: Sidebar (trái) + Content (phải)
    return ft.Row(
        controls=[
            Sidebar(page, active_route="dashboard"),  # Sidebar với menu "Dashboard" active
            main_content,
        ],
        spacing=0,
        expand=True,
    )
