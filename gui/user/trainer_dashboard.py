# ============================================================================
# FILE: gui/user/trainer_dashboard.py
# MỤC ĐÍCH: Trang chủ HLV — thông tin cá nhân + danh sách học viên.
#
# THIẾT KẾ: Giống admin — plain function TrainerDashboardScreen(page).
# ============================================================================

import flet as ft
from gui import theme
from app.services import trainer_svc


def TrainerDashboardScreen(page: ft.Page) -> ft.Container:
    """Trang chủ Huấn luyện viên."""
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    students_info = trainer_svc.get_trainer_members(current_user.id)

    # ── Welcome section ───────────────────────────────────────────────────────
    welcome_section = ft.Container(
        content=ft.Row([
            ft.Column(
                controls=[
                    ft.Text(
                        f"Xin chào HLV, {current_user.name}",
                        size=theme.FONT_2XL, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        f"Chuyên môn: {getattr(current_user, 'specialization', None) or 'Chưa rõ'}",
                        size=theme.FONT_MD, color=theme.ORANGE, weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=4,
            ),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Icon(ft.Icons.SPORTS, size=32, color=theme.WHITE),
                bgcolor=theme.ORANGE, padding=12, border_radius=16,
                shadow=ft.BoxShadow(blur_radius=15, color=f"{theme.ORANGE}40", offset=ft.Offset(0, 8)),
            ),
        ]),
        margin=ft.margin.only(bottom=32),
    )

    # ── Trainer info card ─────────────────────────────────────────────────────
    info_card = ft.Container(
        content=ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.BADGE, color=theme.ORANGE),
                    ft.Text("Thông tin Huấn luyện viên", size=theme.FONT_LG, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Divider(color=theme.GRAY_LIGHT),
                ft.Row([ft.Text("Họ tên", color=theme.GRAY, width=150), ft.Text(current_user.name, weight=ft.FontWeight.BOLD)]),
                ft.Row([ft.Text("Số điện thoại", color=theme.GRAY, width=150), ft.Text(current_user.phone, weight=ft.FontWeight.BOLD)]),
                ft.Row([
                    ft.Text("Chuyên môn", color=theme.GRAY, width=150),
                    ft.Text(getattr(current_user, "specialization", None) or "Chưa cập nhật", weight=ft.FontWeight.BOLD),
                ]),
            ],
            spacing=12,
        ),
        bgcolor=theme.WHITE, border_radius=16, padding=24,
        margin=ft.margin.only(bottom=24),
        shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
    )

    # ── Student list ──────────────────────────────────────────────────────────
    if not students_info:
        students_content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=48, color=theme.GRAY),
                    ft.Text(
                        "Hiện tại bạn chưa quản lý học viên nào có gói đang kích hoạt.",
                        color=theme.GRAY, text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12,
            ),
            padding=32, alignment=ft.Alignment.CENTER,
        )
    else:
        student_cards = []
        for stu in students_info:
            member_obj = stu["member"]
            sub_obj = stu.get("subscription")
            assignment_obj = stu.get("assignment")
            avatar_letter = member_obj.name[0].upper() if member_obj.name else "U"

            # Hiển thị thông tin gói hoặc ghi chú assignment
            if sub_obj:
                detail_text = f"SĐT: {member_obj.phone}  •  Gói đến {str(sub_obj.end_date)[:10]}"
            elif assignment_obj and assignment_obj.notes:
                detail_text = f"SĐT: {member_obj.phone}  •  {assignment_obj.notes}"
            else:
                detail_text = f"SĐT: {member_obj.phone}  •  Đang kèm"

            student_cards.append(ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(avatar_letter, size=20, weight=ft.FontWeight.BOLD, color=theme.WHITE),
                        bgcolor=theme.ORANGE, width=48, height=48,
                        border_radius=24, alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column([
                        ft.Text(member_obj.name, weight=ft.FontWeight.BOLD, size=theme.FONT_LG),
                        ft.Text(detail_text, color=theme.GRAY, size=theme.FONT_SM),
                    ], spacing=4),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, icon_color=theme.GRAY),
                ]),
                bgcolor=theme.WHITE, padding=20, border_radius=16,
                shadow=ft.BoxShadow(blur_radius=15, color="#00000005", offset=ft.Offset(0, 5)),
            ))

        students_content = ft.Column(
            [
                ft.Text(f"Danh sách Học viên ({len(students_info)})", size=theme.FONT_XL, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                *student_cards,
            ],
            spacing=16,
        )

    # ── Layout: sidebar + content ─────────────────────────────────────────────
    content = ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        padding=32,
        content=ft.Column(
            [welcome_section, info_card, ft.Divider(color=theme.GRAY_LIGHT), ft.Container(height=16), students_content],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    from gui.user.components.user_sidebar import UserSidebar
    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[UserSidebar(page, "trainer"), content],
            spacing=0,
            expand=True,
        ),
    )
