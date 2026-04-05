# ============================================================================
# FILE: gui/user/user_checkin.py
# MỤC ĐÍCH: Màn hình CHECK-IN bằng khuôn mặt (User App).
#            Hiển thị camera, tự động nhận diện, hiển thị kết quả.
# ============================================================================

import flet as ft
import cv2
import base64
import threading
import time
from datetime import datetime

from gui import theme
from gui.user.components.user_sidebar import UserSidebar
from app.services import attendance_svc, face_svc


def CheckinScreen(page: ft.Page) -> ft.Container:
    """Màn hình check-in khuôn mặt cho hội viên."""

    navigate = getattr(page, "navigate", None)
    current_user = getattr(page, "current_user", None)

    if not current_user:
        if navigate:
            navigate("login")
        return ft.Container()

    # ── State ────────────────────────────────────────────────────────────────
    camera_state = {"running": False, "cap": None}
    last_result = {"name": "", "time": 0}

    # ── Camera ───────────────────────────────────────────────────────────────
    # src="" thay cho src_base64=""; fit=ft.BoxFit (API mới)
    camera_image = ft.Image(
        src="",
        width=480,
        height=360,
        fit=ft.BoxFit.CONTAIN,
        border_radius=12,
    )

    camera_placeholder = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.FACE, size=64, color=theme.GRAY),
                ft.Text("Bấm nút bên dưới để bắt đầu check-in",
                        size=theme.FONT_MD, color=theme.GRAY,
                        text_align=ft.TextAlign.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=theme.PAD_MD,
        ),
        width=480,
        height=360,
        bgcolor="#1A1A2E",
        border_radius=12,
        alignment=ft.Alignment.CENTER,
    )

    camera_container = ft.Container(content=camera_placeholder, width=480, height=360)

    # ── Kết quả ──────────────────────────────────────────────────────────────
    result_icon = ft.Icon(ft.Icons.FACE, size=48, color=theme.GRAY)
    result_title = ft.Text("Sẵn sàng check-in", size=theme.FONT_2XL,
                           weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY,
                           text_align=ft.TextAlign.CENTER)
    result_message = ft.Text("Nhìn thẳng vào camera để nhận diện",
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
        width=480,
        alignment=ft.Alignment.CENTER,
    )

    # ── Lịch sử điểm danh gần đây ──────────────────────────────────────────
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

    # ── Camera loop ──────────────────────────────────────────────────────────
    def camera_loop():
        cap = cv2.VideoCapture(0)
        camera_state["cap"] = cap

        if not cap.isOpened():
            result_title.value = "Không thể mở camera!"
            result_icon.color = theme.RED
            result_icon.icon = ft.Icons.ERROR
            page.update()
            return

        frame_count = {"value": 0}

        while camera_state["running"]:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.03)
                continue

            display_frame = frame.copy()
            frame_count["value"] += 1

            if frame_count["value"] % 5 == 0:
                try:
                    results = face_svc.recognize_frame(frame)
                    if results:
                        for res in results:
                            name = res.get("name", "Unknown")
                            confidence = res.get("confidence", 0)
                            bbox = res.get("bbox", None)

                            if bbox:
                                top, right, bottom, left = bbox
                                cv2.rectangle(display_frame, (left, top), (right, bottom),
                                              (0, 255, 0), 2)

                            if name != "Unknown" and confidence > 0:
                                now = time.time()
                                if (last_result["name"] != name or
                                        now - last_result["time"] > 10):
                                    checkin_result = attendance_svc.check_in_by_face(
                                        name, confidence
                                    )
                                    status = checkin_result.get("status", "error")
                                    member_name = checkin_result.get("member_name", name)

                                    last_result["name"] = name
                                    last_result["time"] = now

                                    now_str = datetime.now().strftime("%H:%M:%S")

                                    if status == "success":
                                        result_icon.icon = ft.Icons.CHECK_CIRCLE
                                        result_icon.color = theme.GREEN
                                        result_title.value = f"Xin chào, {member_name}!"
                                        result_message.value = "Check-in thành công!"
                                        result_message.color = theme.GREEN
                                        result_time.value = f"Thời gian: {now_str}"
                                        load_history()
                                    elif status == "already":
                                        result_icon.icon = ft.Icons.INFO
                                        result_icon.color = theme.BLUE
                                        result_title.value = f"Chào, {member_name}!"
                                        result_message.value = "Bạn đã điểm danh hôm nay rồi"
                                        result_message.color = theme.BLUE
                                        result_time.value = ""
                                    elif status == "expired":
                                        result_icon.icon = ft.Icons.WARNING
                                        result_icon.color = theme.RED
                                        result_title.value = member_name
                                        result_message.value = "Gói tập đã hết hạn!"
                                        result_message.color = theme.RED
                                        result_time.value = "Vui lòng gia hạn tại quầy"
                                    elif status != "cooldown":
                                        result_icon.icon = ft.Icons.ERROR
                                        result_icon.color = theme.AMBER
                                        result_title.value = "Lỗi"
                                        result_message.value = checkin_result.get("message", "")
                                        result_message.color = theme.AMBER
                except Exception as ex:
                    print(f"[ERROR] Face recognition: {ex}")

            # API mới: camera_image.src thay vì .src_base64
            _, buffer = cv2.imencode('.jpg', display_frame,
                                     [cv2.IMWRITE_JPEG_QUALITY, 70])
            img_base64 = base64.b64encode(buffer).decode()
            camera_image.src = img_base64

            try:
                page.update()
            except Exception:
                break

            time.sleep(0.03)

        cap.release()
        camera_state["cap"] = None

    # ── Toggle camera ────────────────────────────────────────────────────────
    btn_text = ft.Text("Bắt đầu Check-in", size=theme.FONT_MD, weight=ft.FontWeight.BOLD,
                       color=theme.WHITE)
    btn_icon = ft.Icon(ft.Icons.FACE, size=20, color=theme.WHITE)

    def toggle_camera(e):
        if not camera_state["running"]:
            camera_state["running"] = True
            camera_container.content = camera_image
            btn_text.value = "Dừng Camera"
            btn_icon.icon = ft.Icons.STOP
            result_title.value = "Đang quét..."
            result_message.value = "Nhìn thẳng vào camera"
            result_message.color = theme.TEXT_SECONDARY
            result_icon.icon = ft.Icons.FACE
            result_icon.color = theme.ORANGE
            page.update()
            t = threading.Thread(target=camera_loop, daemon=True)
            t.start()
        else:
            camera_state["running"] = False
            camera_container.content = camera_placeholder
            btn_text.value = "Bắt đầu Check-in"
            btn_icon.icon = ft.Icons.FACE
            camera_image.src = ""   # API mới
            result_title.value = "Sẵn sàng check-in"
            result_message.value = "Nhìn thẳng vào camera để nhận diện"
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
        width=480,
        alignment=ft.Alignment.CENTER,
    )

    # ── Layout ───────────────────────────────────────────────────────────────
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
                        controls=[camera_container, btn_toggle],
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
                                width=480,
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
