# ============================================================================
# FILE: gui/user/user_checkin.py
# MUC DICH: Man hinh CHECK-IN bang khuon mat (User App).
#            Nhan nut -> mo camera CTk (process rieng) -> nhan ket qua qua bridge.
# ============================================================================

import flet as ft
import asyncio
from datetime import datetime

from gui import theme
from gui.user.components.user_sidebar import UserSidebar
from app.services import attendance_svc
from bridge import get_bridge


def CheckinScreen(page: ft.Page) -> ft.Container:
    """Man hinh check-in khuon mat cho hoi vien."""

    navigate = getattr(page, "navigate", None)
    current_user = getattr(page, "current_user", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    bridge = get_bridge()
    DISPLAY_SIZE = (480, 360)

    # ── Ket qua nhan dien ─────────────────────────────────────────────────────
    result_icon = ft.Icon(ft.Icons.FACE, size=48, color=theme.GRAY)
    result_title = ft.Text("Sẵn sàng check-in", size=theme.FONT_2XL,
                           weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY,
                           text_align=ft.TextAlign.CENTER)
    result_message = ft.Text("Nhấn nút bên dưới để bắt đầu",
                             size=theme.FONT_MD, color=theme.TEXT_SECONDARY,
                             text_align=ft.TextAlign.CENTER)
    result_time = ft.Text("", size=theme.FONT_SM, color=theme.GRAY,
                          text_align=ft.TextAlign.CENTER)

    result_card = ft.Container(
        content=ft.Column(
            controls=[result_icon, result_title, result_message, result_time],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=theme.PAD_SM,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=ft.padding.all(theme.PAD_2XL),
        border=ft.border.all(1, theme.BORDER),
        width=DISPLAY_SIZE[0],
        alignment=ft.Alignment.CENTER,
    )

    # ── Camera status placeholder ─────────────────────────────────────────────
    camera_status_icon = ft.Icon(ft.Icons.FACE, size=64, color=theme.GRAY)
    camera_status_text = ft.Text("Bấm nút bên dưới để bắt đầu check-in",
                                  size=theme.FONT_MD, color=theme.GRAY,
                                  text_align=ft.TextAlign.CENTER)

    camera_placeholder = ft.Container(
        content=ft.Column(
            controls=[camera_status_icon, camera_status_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=theme.PAD_MD,
        ),
        width=DISPLAY_SIZE[0],
        height=DISPLAY_SIZE[1],
        bgcolor="#1A1A2E",
        border_radius=12,
        alignment=ft.Alignment.CENTER,
    )

    # ── Lich su diem danh gan day ─────────────────────────────────────────────
    history_list = ft.Column(controls=[], spacing=0)

    def load_history():
        try:
            records = attendance_svc.get_member_attendance(current_user.id, limit=5)
            history_list.controls.clear()
            for att in records:
                check_in_str = ""
                if att.check_in:
                    try:
                        dt = datetime.fromisoformat(att.check_in)
                        check_in_str = dt.strftime("%d/%m/%Y %H:%M")
                    except Exception:
                        check_in_str = str(att.check_in)

                method_label = att.method or "face_id"
                method_color = theme.GREEN if method_label == "face_id" else theme.BLUE

                history_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=theme.GREEN),
                                ft.Text(check_in_str, size=theme.FONT_SM,
                                        color=theme.TEXT_PRIMARY, expand=True),
                                ft.Container(
                                    content=ft.Text(method_label, size=theme.FONT_XS,
                                                    color=theme.WHITE,
                                                    weight=ft.FontWeight.W_600),
                                    bgcolor=method_color,
                                    border_radius=theme.BADGE_RADIUS,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                ),
                            ],
                            spacing=theme.PAD_SM,
                        ),
                        padding=ft.padding.symmetric(horizontal=theme.PAD_MD, vertical=theme.PAD_SM),
                        border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
                    )
                )

            if not records:
                history_list.controls.append(
                    ft.Container(
                        content=ft.Text("Chưa có lịch sử điểm danh",
                                        size=theme.FONT_SM, color=theme.GRAY),
                        padding=ft.padding.all(theme.PAD_LG),
                    )
                )
        except Exception:
            pass

    # ── Xu ly ket qua tu camera process ──────────────────────────────────────
    last_checkin = {"name": "", "time": 0}
    listener_running = {"active": False}

    async def listen_camera_results():
        """Async loop lang nghe result_queue tu camera process."""
        listener_running["active"] = True
        while bridge.is_camera_running():
            msg = bridge.get_result()
            if msg:
                msg_type = msg.get("type", "")

                if msg_type == "recognition":
                    member_id = msg.get("member_id", "")
                    confidence = msg.get("confidence", 0)

                    # Cooldown 10s cho cung 1 nguoi
                    import time
                    now = time.time()
                    if (last_checkin["name"] != member_id or
                            now - last_checkin["time"] > 10):
                        last_checkin["name"] = member_id
                        last_checkin["time"] = now

                        checkin_result = attendance_svc.check_in_by_face(
                            member_id, confidence
                        )
                        status = checkin_result.get("status", "error")
                        member_name = checkin_result.get("member_name", member_id)
                        now_str = datetime.now().strftime("%H:%M:%S")

                        if status == "success":
                            result_icon.icon = ft.Icons.CHECK_CIRCLE
                            result_icon.color = theme.GREEN
                            result_title.value = f"Xin chao, {member_name}!"
                            result_message.value = "Check-in thành công!"
                            result_message.color = theme.GREEN
                            result_time.value = f"Thoi gian: {now_str}"
                            load_history()
                        elif status == "already":
                            result_icon.icon = ft.Icons.INFO
                            result_icon.color = theme.BLUE
                            result_title.value = f"Chao, {member_name}!"
                            result_message.value = "Bạn đã điểm danh hôm nay rồi"
                            result_message.color = theme.BLUE
                            result_time.value = ""
                        elif status == "expired":
                            result_icon.icon = ft.Icons.WARNING
                            result_icon.color = theme.AMBER
                            result_title.value = f"Chao, {member_name}!"
                            result_message.value = "Đã check-in! (Gói tập hết hạn)"
                            result_message.color = theme.AMBER
                            result_time.value = "Vui lòng gia hạn tại quầy"
                            load_history()
                        elif status != "cooldown":
                            result_icon.icon = ft.Icons.ERROR
                            result_icon.color = theme.AMBER
                            result_title.value = "Lỗi"
                            result_message.value = checkin_result.get("message", "")
                            result_message.color = theme.AMBER

                        page.update()

                elif msg_type == "camera_closed":
                    camera_status_icon.icon = ft.Icons.FACE
                    camera_status_icon.color = theme.GRAY
                    camera_status_text.value = "Camera da dong. Bam nut de mo lai."
                    btn_text.value = "Bắt đầu Check-in"
                    btn_icon.icon = ft.Icons.FACE
                    page.update()
                    break

                elif msg_type == "camera_error":
                    camera_status_text.value = f"Lỗi: {msg.get('message', '')}"
                    page.update()

            await asyncio.sleep(0.1)

        listener_running["active"] = False

    # ── Toggle camera ────────────────────────────────────────────────────────
    btn_text = ft.Text("Bắt đầu Check-in", size=theme.FONT_MD,
                       weight=ft.FontWeight.BOLD, color=theme.WHITE)
    btn_icon = ft.Icon(ft.Icons.FACE, size=20, color=theme.WHITE)

    def toggle_camera(e):
        if not bridge.is_camera_running():
            # Mo camera process
            result = bridge.open_camera(mode="recognize")
            if "error" in result:
                camera_status_text.value = result["error"]
                page.update()
                return

            camera_status_icon.icon = ft.Icons.VIDEOCAM
            camera_status_icon.color = theme.ORANGE
            camera_status_text.value = "Camera đang chạy (cửa sổ riêng)"
            btn_text.value = "Dung Camera"
            btn_icon.icon = ft.Icons.STOP
            result_title.value = "Đang quét..."
            result_message.value = "Nhin thang vao camera"
            result_message.color = theme.TEXT_SECONDARY
            result_icon.icon = ft.Icons.FACE
            result_icon.color = theme.ORANGE
            page.update()

            # Bat dau lang nghe ket qua
            if not listener_running["active"]:
                page.run_task(listen_camera_results)
        else:
            # Dong camera
            bridge.close_camera()
            camera_status_icon.icon = ft.Icons.FACE
            camera_status_icon.color = theme.GRAY
            camera_status_text.value = "Bấm nút bên dưới để bắt đầu check-in"
            btn_text.value = "Bắt đầu Check-in"
            btn_icon.icon = ft.Icons.FACE
            result_title.value = "Sẵn sàng check-in"
            result_message.value = "Nhấn nút bên dưới để bắt đầu"
            result_message.color = theme.TEXT_SECONDARY
            result_icon.icon = ft.Icons.FACE
            result_icon.color = theme.GRAY
            result_time.value = ""
            page.update()

    btn_toggle = ft.Container(
        content=ft.Row(
            controls=[btn_icon, btn_text],
            spacing=theme.PAD_SM,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=theme.ORANGE,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=theme.PAD_2XL, vertical=14),
        on_click=toggle_camera,
        ink=True,
        width=DISPLAY_SIZE[0],
        alignment=ft.Alignment.CENTER,
    )

    # ── Layout ────────────────────────────────────────────────────────────────
    main_content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FACE, size=24, color=theme.ORANGE),
                        ft.Text("Check-in bằng khuôn mặt", size=theme.FONT_2XL,
                                weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                    ],
                    spacing=theme.PAD_MD,
                ),
                padding=ft.padding.only(bottom=theme.PAD_LG),
            ),
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[camera_placeholder, btn_toggle],
                        spacing=theme.PAD_MD,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column(
                        controls=[
                            result_card,
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Lịch sử điểm danh gần đây",
                                                size=theme.FONT_MD,
                                                weight=ft.FontWeight.W_600,
                                                color=theme.TEXT_PRIMARY),
                                        history_list,
                                    ],
                                    spacing=theme.PAD_SM,
                                ),
                                bgcolor=theme.CARD_BG,
                                border_radius=theme.CARD_RADIUS,
                                padding=ft.padding.all(theme.PAD_LG),
                                border=ft.border.all(1, theme.BORDER),
                                width=DISPLAY_SIZE[0],
                            ),
                        ],
                        spacing=theme.PAD_MD,
                    ),
                ],
                spacing=theme.PAD_2XL,
                vertical_alignment=ft.CrossAxisAlignment.START,
                scroll=ft.ScrollMode.AUTO,
            ),
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    content = ft.Container(
        content=main_content,
        padding=ft.padding.all(theme.PAD_2XL),
        expand=True,
    )

    load_history()

    return ft.Container(
        content=ft.Row(
            controls=[
                UserSidebar(page, "checkin"),
                content,
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
    )
