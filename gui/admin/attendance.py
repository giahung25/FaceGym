# ============================================================================
# FILE: gui/admin/attendance.py
# MỤC ĐÍCH: Màn hình ĐIỂM DANH (Admin) — camera feed + nhận diện khuôn mặt
#            + bảng lịch sử điểm danh hôm nay + check-in thủ công.
# ============================================================================

import flet as ft
import cv2
import base64
import threading
import time
from datetime import datetime

from gui import theme
from gui.admin.components.sidebar import Sidebar
from gui.admin.components.header import Header
from app.services import attendance_svc, face_svc
from app.repositories import member_repo


def AttendanceScreen(page: ft.Page) -> ft.Row:
    """Màn hình điểm danh — camera + face recognition + bảng điểm danh."""

    navigate = getattr(page, "navigate", None)

    # ── State ────────────────────────────────────────────────────────────────
    camera_state = {"running": False, "cap": None, "thread": None}
    last_result = {"name": "", "status": "", "time": 0}

    # ── Camera feed image ─────────────────────────────────────────────────────
    # src="" dùng cho base64, fit dùng ft.BoxFit (API mới)
    camera_image = ft.Image(
        src="",
        width=480,
        height=360,
        fit=ft.BoxFit.CONTAIN,
        border_radius=theme.CARD_RADIUS,
    )

    camera_placeholder = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.VIDEOCAM_OFF, size=48, color=theme.GRAY),
                ft.Text("Camera chưa bật", size=theme.FONT_MD, color=theme.GRAY),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=theme.PAD_SM,
        ),
        width=480,
        height=360,
        bgcolor="#1A1A2E",
        border_radius=theme.CARD_RADIUS,
        alignment=ft.Alignment.CENTER,
    )

    camera_container = ft.Container(
        content=camera_placeholder,
        width=480,
        height=360,
    )

    # ── Kết quả nhận diện ────────────────────────────────────────────────────
    # Dùng ft.Ref để thay icon động; hoặc đặt trong Column có thể rebuild
    result_icon = ft.Icon(ft.Icons.FACE, size=28, color=theme.GRAY)
    result_name = ft.Text("Chờ nhận diện...", size=theme.FONT_LG, weight=ft.FontWeight.W_600,
                          color=theme.TEXT_PRIMARY)
    result_status = ft.Text("", size=theme.FONT_SM, color=theme.GRAY)

    result_card = ft.Container(
        content=ft.Row(
            controls=[
                result_icon,
                ft.Column(
                    controls=[result_name, result_status],
                    spacing=2, tight=True,
                ),
            ],
            spacing=theme.PAD_MD,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=ft.padding.all(theme.PAD_LG),
        border=ft.border.all(1, theme.BORDER),
    )

    # ── Thống kê nhanh ──────────────────────────────────────────────────────
    stat_today_count = ft.Text("0", size=theme.FONT_3XL, weight=ft.FontWeight.BOLD,
                               color=theme.ORANGE)
    stat_today_label = ft.Text("Check-in hôm nay", size=theme.FONT_SM, color=theme.GRAY)

    stats_card = ft.Container(
        content=ft.Column(
            controls=[stat_today_count, stat_today_label],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=ft.padding.all(theme.PAD_LG),
        border=ft.border.all(1, theme.BORDER),
        width=160,
        alignment=ft.Alignment.CENTER,
    )

    # ── Bảng điểm danh hôm nay ──────────────────────────────────────────────
    attendance_table = ft.Column(controls=[], spacing=0, scroll=ft.ScrollMode.AUTO)

    def build_attendance_row(record):
        att = record["attendance"]
        member = record["member"]
        name = member.name if member else "Không xác định"
        check_in_str = ""
        if att.check_in:
            try:
                dt = datetime.fromisoformat(att.check_in)
                check_in_str = dt.strftime("%H:%M:%S")
            except Exception:
                check_in_str = str(att.check_in)

        check_out_str = ""
        if att.check_out:
            try:
                dt = datetime.fromisoformat(att.check_out)
                check_out_str = dt.strftime("%H:%M:%S")
            except Exception:
                check_out_str = str(att.check_out)

        method_colors = {
            "face_id": theme.GREEN,
            "manual": theme.BLUE,
            "qr_code": theme.AMBER,
        }
        method_label = att.method or "face_id"
        method_color = method_colors.get(method_label, theme.GRAY)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            name[0].upper() if name else "?",
                            color=theme.WHITE, size=theme.FONT_SM,
                            weight=ft.FontWeight.BOLD,
                        ),
                        width=32, height=32,
                        bgcolor=theme.ORANGE,
                        border_radius=16,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text(name, size=theme.FONT_SM, color=theme.TEXT_PRIMARY,
                            weight=ft.FontWeight.W_500, expand=True),
                    ft.Text(check_in_str, size=theme.FONT_SM, color=theme.TEXT_SECONDARY, width=80),
                    ft.Text(check_out_str or "—", size=theme.FONT_SM, color=theme.TEXT_SECONDARY, width=80),
                    ft.Container(
                        content=ft.Text(method_label, size=theme.FONT_XS, color=theme.WHITE,
                                        weight=ft.FontWeight.W_600),
                        bgcolor=method_color,
                        border_radius=theme.BADGE_RADIUS,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=theme.PAD_MD,
            ),
            padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_SM),
            border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
        )

    def load_today_attendance():
        try:
            records = attendance_svc.get_today_attendance()
            count = attendance_svc.count_today()
            stat_today_count.value = str(count)

            attendance_table.controls.clear()
            if not records:
                attendance_table.controls.append(
                    ft.Container(
                        content=ft.Text("Chưa có ai điểm danh hôm nay",
                                        size=theme.FONT_SM, color=theme.GRAY,
                                        text_align=ft.TextAlign.CENTER),
                        padding=ft.padding.all(theme.PAD_2XL),
                        alignment=ft.Alignment.CENTER,
                    )
                )
            else:
                for record in records:
                    attendance_table.controls.append(build_attendance_row(record))

            page.update()
        except Exception as ex:
            print(f"[ERROR] load_today_attendance: {ex}")

    # ── Camera loop (chạy trên thread riêng) ─────────────────────────────────
    def camera_loop():
        cap = cv2.VideoCapture(0)
        camera_state["cap"] = cap

        if not cap.isOpened():
            result_name.value = "Không thể mở camera!"
            result_icon.color = theme.RED
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

            # Nhận diện mỗi 5 frame
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
                                cv2.putText(display_frame, f"{name}",
                                            (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                            0.6, (0, 255, 0), 2)

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
                                    last_result["status"] = status
                                    last_result["time"] = now

                                    if status == "success":
                                        result_icon.icon = ft.Icons.CHECK_CIRCLE
                                        result_icon.color = theme.GREEN
                                        result_name.value = member_name
                                        result_status.value = f"Check-in thành công! ({confidence:.0%})"
                                        result_status.color = theme.GREEN
                                        load_today_attendance()
                                    elif status == "already":
                                        result_icon.icon = ft.Icons.INFO
                                        result_icon.color = theme.BLUE
                                        result_name.value = member_name
                                        result_status.value = "Đã điểm danh hôm nay"
                                        result_status.color = theme.BLUE
                                    elif status == "expired":
                                        result_icon.icon = ft.Icons.WARNING
                                        result_icon.color = theme.RED
                                        result_name.value = member_name
                                        result_status.value = "Hết hạn gói tập!"
                                        result_status.color = theme.RED
                                    elif status == "cooldown":
                                        pass
                                    else:
                                        result_icon.icon = ft.Icons.ERROR
                                        result_icon.color = theme.AMBER
                                        result_name.value = member_name
                                        result_status.value = checkin_result.get("message", "Lỗi")
                                        result_status.color = theme.AMBER
                    else:
                        if time.time() - last_result["time"] > 3:
                            result_icon.icon = ft.Icons.FACE
                            result_icon.color = theme.GRAY
                            result_name.value = "Đang quét..."
                            result_status.value = ""
                except Exception as ex:
                    print(f"[ERROR] Face recognition: {ex}")

            # Encode frame → base64, dùng camera_image.src (API mới)
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

    # ── Nút bật/tắt camera ──────────────────────────────────────────────────
    btn_camera_text = ft.Text("Bật Camera", size=theme.FONT_SM, weight=ft.FontWeight.W_600,
                              color=theme.WHITE)
    btn_camera_icon = ft.Icon(ft.Icons.VIDEOCAM, size=16, color=theme.WHITE)

    def toggle_camera(e):
        if not camera_state["running"]:
            camera_state["running"] = True
            camera_container.content = camera_image
            btn_camera_text.value = "Tắt Camera"
            btn_camera_icon.icon = ft.Icons.VIDEOCAM_OFF
            page.update()
            t = threading.Thread(target=camera_loop, daemon=True)
            camera_state["thread"] = t
            t.start()
        else:
            camera_state["running"] = False
            camera_container.content = camera_placeholder
            btn_camera_text.value = "Bật Camera"
            btn_camera_icon.icon = ft.Icons.VIDEOCAM
            result_name.value = "Chờ nhận diện..."
            result_status.value = ""
            result_icon.color = theme.GRAY
            result_icon.icon = ft.Icons.FACE
            camera_image.src = ""
            page.update()

    btn_camera = ft.Container(
        content=ft.Row(
            controls=[btn_camera_icon, btn_camera_text],
            spacing=theme.PAD_SM,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=theme.GREEN,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=10),
        on_click=toggle_camera,
        ink=True,
    )

    # ── Check-in thủ công ────────────────────────────────────────────────────
    manual_phone = ft.TextField(
        label="SĐT hội viên",
        hint_text="Nhập số điện thoại...",
        width=200,
        border_radius=theme.BUTTON_RADIUS,
    )
    manual_error = ft.Text("", size=theme.FONT_XS, color=theme.RED)

    def do_manual_checkin(e):
        phone = manual_phone.value.strip() if manual_phone.value else ""
        if not phone:
            manual_error.value = "Nhập SĐT"
            page.update()
            return

        member = member_repo.get_by_phone(phone)
        if not member:
            manual_error.value = "Không tìm thấy hội viên"
            page.update()
            return

        result = attendance_svc.check_in(member.id, method="manual")
        if result["status"] == "success":
            manual_error.value = ""
            manual_phone.value = ""
            result_icon.icon = ft.Icons.CHECK_CIRCLE
            result_icon.color = theme.GREEN
            result_name.value = member.name
            result_status.value = "Check-in thủ công thành công!"
            result_status.color = theme.GREEN
            load_today_attendance()
        else:
            manual_error.value = result.get("message", "Lỗi")
        page.update()

    btn_manual = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PERSON_ADD, size=14, color=theme.WHITE),
                ft.Text("Check-in", size=theme.FONT_SM, weight=ft.FontWeight.W_600,
                        color=theme.WHITE),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=theme.BLUE,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=theme.PAD_MD, vertical=8),
        on_click=do_manual_checkin,
        ink=True,
    )

    manual_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Check-in thủ công", size=theme.FONT_MD, weight=ft.FontWeight.W_600,
                        color=theme.TEXT_PRIMARY),
                ft.Row(
                    controls=[manual_phone, btn_manual],
                    spacing=theme.PAD_SM,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                manual_error,
            ],
            spacing=theme.PAD_SM,
        ),
        bgcolor=theme.CARD_BG,
        border_radius=theme.CARD_RADIUS,
        padding=ft.padding.all(theme.PAD_LG),
        border=ft.border.all(1, theme.BORDER),
    )

    # ── Table header ─────────────────────────────────────────────────────────
    table_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(width=32),
                ft.Text("Hội viên", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, expand=True),
                ft.Text("Vào", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=80),
                ft.Text("Ra", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=80),
                ft.Text("Phương thức", size=theme.FONT_XS, color=theme.GRAY,
                        weight=ft.FontWeight.W_600, width=80),
            ],
            spacing=theme.PAD_MD,
        ),
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=theme.PAD_SM),
        bgcolor="#F9FAFB",
        border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
    )

    # ── Layout tổng thể ─────────────────────────────────────────────────────
    left_col = ft.Column(
        controls=[
            ft.Text("Camera Nhận Diện", size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
                    color=theme.TEXT_PRIMARY),
            camera_container,
            ft.Row(
                controls=[btn_camera, stats_card],
                spacing=theme.PAD_MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            result_card,
            manual_section,
        ],
        spacing=theme.PAD_LG,
        width=520,
    )

    right_col = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Điểm danh hôm nay", size=theme.FONT_XL,
                            weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.REFRESH, size=14, color=theme.ORANGE),
                                ft.Text("Làm mới", size=theme.FONT_SM, color=theme.ORANGE,
                                        weight=ft.FontWeight.W_600),
                            ],
                            spacing=4,
                        ),
                        on_click=lambda e: load_today_attendance(),
                        ink=True,
                        border_radius=theme.BUTTON_RADIUS,
                        padding=ft.padding.symmetric(horizontal=theme.PAD_SM, vertical=4),
                    ),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[table_header, attendance_table],
                    spacing=0,
                ),
                bgcolor=theme.CARD_BG,
                border_radius=theme.CARD_RADIUS,
                border=ft.border.all(1, theme.BORDER),
                expand=True,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
        ],
        spacing=theme.PAD_MD,
        expand=True,
    )

    content = ft.Container(
        content=ft.Row(
            controls=[left_col, right_col],
            spacing=theme.PAD_2XL,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=ft.padding.all(theme.PAD_2XL),
        expand=True,
    )

    load_today_attendance()

    return ft.Row(
        controls=[
            Sidebar(page, "attendance"),
            ft.Column(
                controls=[Header(page), content],
                spacing=0,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
