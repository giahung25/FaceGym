# ============================================================================
# FILE: gui/admin/reports.py
# MỤC ĐÍCH: Màn hình BÁO CÁO — tổng hợp thống kê về hội viên, doanh thu, thiết bị.
#            Chỉ hiển thị dữ liệu (read-only), không có thao tác thêm/sửa/xóa.
#
# NỘI DUNG HIỂN THỊ:
#   1. Dãy KPI cards: tổng hội viên, active, mới tháng này, doanh thu tháng/năm
#   2. Tình trạng thiết bị: số lượng hoạt động / bảo trì / hỏng
#   3. Gói tập sắp hết hạn (7 ngày tới)
#   4. Nút "Làm mới" để reload dữ liệu
# ============================================================================

import flet as ft
from gui import theme
from gui.admin.components.header import Header
from gui.admin.components.sidebar import Sidebar
from app.services import member_svc, membership_svc, equipment_svc  # Các service tính thống kê
from app.repositories import membership_repo                         # Truy cập DB subscriptions


def ReportsScreen(page: ft.Page) -> ft.Row:
    """Tạo màn hình báo cáo."""

    def build_content():
        """Xây dựng toàn bộ nội dung báo cáo từ dữ liệu database.

        Hàm này được gọi lại mỗi khi user click "Làm mới".
        Tách thành hàm riêng để dễ refresh: chỉ cần gọi build_content() lại.

        Trả về:
            ft.Column: toàn bộ nội dung báo cáo đã render
        """

        # ── Lấy dữ liệu thống kê từ các service ─────────────────────────────
        member_stats = member_svc.get_member_stats()       # {total, active, new_this_month}
        revenue_stats = membership_svc.get_revenue_stats() # {monthly, yearly, total}
        eq_summary = equipment_svc.get_equipment_summary() # {total, working, broken, maintenance}
        expiring = membership_repo.get_expiring_soon(days=7)  # Gói sắp hết hạn 7 ngày tới

        # Tạo mapping ID → tên (để hiển thị)
        from app.repositories import member_repo
        members_map = {m.id: m.name for m in member_repo.get_all(active_only=False)}
        from app.repositories import membership_repo as mr
        plans_map = {p.id: p.name for p in mr.get_all_plans(active_only=False)}

        # ── Hàm tạo KPI card ─────────────────────────────────────────────────
        def kpi_card(label, value, color=theme.TEXT_PRIMARY):
            """Tạo 1 card KPI nhỏ hiển thị giá trị thống kê.

            Tham số:
                label (str): nhãn mô tả (VD: "Tổng hội viên")
                value (str): giá trị hiển thị (VD: "85")
                color (str): màu chữ giá trị
            """
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(value, size=theme.FONT_3XL, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(label, size=theme.FONT_SM, color=theme.GRAY),
                    ],
                    spacing=4,
                ),
                bgcolor=theme.CARD_BG,
                border_radius=theme.CARD_RADIUS,
                padding=theme.PAD_XL,
                expand=True,  # Chia đều chiều rộng với các card khác trong Row
                shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
            )

        # ── Dãy KPI cards ────────────────────────────────────────────────────
        kpi_row = ft.Row(
            controls=[
                kpi_card("Tổng hội viên", str(member_stats["total"])),
                kpi_card("Hội viên active", str(member_stats["active"]), theme.GREEN),
                kpi_card("Mới tháng này", str(member_stats["new_this_month"]), theme.BLUE),
                kpi_card("Doanh thu tháng này", f"{int(revenue_stats['monthly']):,}đ", theme.ORANGE),
                kpi_card("Doanh thu năm nay", f"{int(revenue_stats['yearly']):,}đ", theme.ORANGE),
            ],
            spacing=theme.PAD_LG,
        )

        # ── Section tình trạng thiết bị ──────────────────────────────────────
        eq_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Tình trạng thiết bị", size=theme.FONT_LG,
                            weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                    ft.Row(
                        controls=[
                            # 3 cột: Hoạt động (xanh), Bảo trì (vàng), Hỏng (đỏ)
                            ft.Column(
                                controls=[
                                    ft.Text(str(eq_summary["working"]), size=theme.FONT_2XL,
                                            weight=ft.FontWeight.BOLD, color=theme.GREEN),
                                    ft.Text("Hoạt động", size=theme.FONT_SM, color=theme.GRAY),
                                ],
                                spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(str(eq_summary["maintenance"]), size=theme.FONT_2XL,
                                            weight=ft.FontWeight.BOLD, color=theme.AMBER),
                                    ft.Text("Bảo trì", size=theme.FONT_SM, color=theme.GRAY),
                                ],
                                spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(str(eq_summary["broken"]), size=theme.FONT_2XL,
                                            weight=ft.FontWeight.BOLD, color=theme.RED),
                                    ft.Text("Hỏng", size=theme.FONT_SM, color=theme.GRAY),
                                ],
                                spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=theme.PAD_2XL,
                    ),
                ],
                spacing=theme.PAD_MD,
            ),
            bgcolor=theme.CARD_BG, border_radius=theme.CARD_RADIUS,
            padding=theme.PAD_XL,
            shadow=ft.BoxShadow(blur_radius=4, color="#0000000A", offset=ft.Offset(0, 1)),
        )

        # ── Section gói tập sắp hết hạn ──────────────────────────────────────
        expiring_rows = []
        for s in expiring:
            remaining = s.days_remaining()  # Số ngày còn lại
            expiring_rows.append(ft.Container(
                content=ft.Row(
                    controls=[
                        # Tên hội viên
                        ft.Text(members_map.get(s.member_id, "?"), size=theme.FONT_SM,
                                weight=ft.FontWeight.W_500, color=theme.TEXT_PRIMARY, expand=True),
                        # Tên gói tập
                        ft.Text(plans_map.get(s.plan_id, "?"), size=theme.FONT_SM,
                                color=theme.GRAY, width=160),
                        # Ngày hết hạn
                        ft.Text(s.end_date.strftime("%d/%m/%Y"), size=theme.FONT_SM,
                                color=theme.GRAY, width=100),
                        # Badge "Còn X ngày" — đỏ nếu <= 3 ngày, vàng nếu > 3
                        ft.Container(
                            content=ft.Text(f"Còn {remaining} ngày", size=theme.FONT_XS,
                                            color=theme.RED if remaining <= 3 else theme.AMBER,
                                            weight=ft.FontWeight.W_600),
                            bgcolor=theme.RED_LIGHT if remaining <= 3 else theme.AMBER_LIGHT,
                            border_radius=theme.BADGE_RADIUS,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_MD),
                border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
            ))

        expiring_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Gói tập sắp hết hạn (7 ngày tới)", size=theme.FONT_LG,
                            weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                    ft.Container(
                        content=ft.Column(
                            # Nếu có gói sắp hết hạn → hiện danh sách, nếu không → thông báo
                            controls=expiring_rows if expiring_rows else [
                                ft.Text("Không có gói tập nào sắp hết hạn.",
                                        size=theme.FONT_SM, color=theme.GRAY)
                            ],
                            spacing=0,
                        ),
                        bgcolor=theme.CARD_BG, border_radius=theme.CARD_RADIUS,
                        shadow=ft.BoxShadow(blur_radius=4, color="#0000000A",
                                            offset=ft.Offset(0, 1)),
                    ),
                ],
                spacing=theme.PAD_MD,
            ),
        )

        # ── Trả về toàn bộ nội dung ──────────────────────────────────────────
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Báo cáo", size=theme.FONT_2XL, weight=ft.FontWeight.BOLD,
                                color=theme.TEXT_PRIMARY),
                        # Nút "Làm mới" — gọi refresh() để reload dữ liệu
                        ft.ElevatedButton("Làm mới", bgcolor=theme.ORANGE, color=theme.WHITE,
                                          on_click=lambda e: refresh()),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                kpi_row,
                ft.Row(controls=[eq_section], spacing=theme.PAD_LG),
                expiring_section,
            ],
            spacing=theme.PAD_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # REFRESH LOGIC
    # ══════════════════════════════════════════════════════════════════════════
    content_area = ft.Container(expand=True)  # Container chứa nội dung (sẽ bị thay thế khi refresh)

    def refresh():
        """Tải lại toàn bộ dữ liệu và render lại nội dung báo cáo."""
        content_area.content = build_content()  # Tạo nội dung mới từ DB
        page.update()                            # Render lại UI

    content_area.content = build_content()  # Render lần đầu

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT
    # ══════════════════════════════════════════════════════════════════════════
    main_content = ft.Column(
        controls=[
            Header(page),
            ft.Container(
                content=content_area,
                padding=ft.padding.all(theme.PAD_2XL),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )

    return ft.Row(
        controls=[Sidebar(page, active_route="reports"), main_content],
        spacing=0,
        expand=True,
    )
