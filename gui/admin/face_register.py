# ============================================================================
# FILE: gui/admin/face_register.py
# MỤC ĐÍCH: Màn hình ĐĂNG KÝ KHUÔN MẶT cho hội viên.
#            Chọn hội viên → bật camera → chụp ảnh → encode → lưu.
# ============================================================================

import flet as ft
import cv2
import base64
import threading
import time
import os

from gui import theme
from gui.admin.components.sidebar import Sidebar
from gui.admin.components.header import Header
from app.services import face_svc
from app.repositories import member_repo
from app.core.config import DATASET_PATH


def FaceRegisterScreen(page: ft.Page) -> ft.Row:
    """Màn hình đăng ký khuôn mặt — chọn member, chụp ảnh, encode."""

    navigate = getattr(page, "navigate", None)

    # ── State ────────────────────────────────────────────────────────────────
    selected_member = {"obj": None}
    camera_state = {"running": False, "cap": None}
    captured_photos = {"count": 0, "target": 10}

    # ── Danh sách hội viên ───────────────────────────────────────────────────
    member_list = ft.Column(controls=[], spacing=0, scroll=ft.ScrollMode.AUTO, height=400)
    search_field = ft.TextField(
        label="Tìm hội viên...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=theme.BUTTON_RADIUS,
        on_change=lambda e: load_members(e.control.value),
    )

    selected_info = ft.Column(controls=[], spacing=theme.PAD_SM)

    def load_members(query=""):
        try:
            all_members = member_repo.get_all(active_only=True)
            if query:
                query_lower = query.lower()
                all_members = [m for m in all_members
                               if query_lower in m.name.lower() or query_lower in (m.phone or "")]

            member_list.controls.clear()
            for m in all_members:
                is_registered = getattr(m, "face_registered", False)
                status_icon = ft.Icons.CHECK_CIRCLE if is_registered else ft.Icons.FACE_RETOUCHING_OFF
                status_color = theme.GREEN if is_registered else theme.GRAY

                def on_select(e, member=m):
                    select_member(member)

                member_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        m.name[0].upper() if m.name else "?",
                                        color=theme.WHITE, size=theme.FONT_SM,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    width=32, height=32,
                                    bgcolor=theme.ORANGE if not is_registered else theme.GREEN,
                                    border_radius=16,
                                    alignment=ft.Alignment.CENTER,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(m.name, size=theme.FONT_SM,
                                                weight=ft.FontWeight.W_500,
                                                color=theme.TEXT_PRIMARY),
                                        ft.Text(m.phone or "", size=theme.FONT_XS,
                                                color=theme.TEXT_SECONDARY),
                                    ],
                                    spacing=0, tight=True, expand=True,
                                ),
                                ft.Icon(status_icon, size=18, color=status_color),
                            ],
                            spacing=theme.PAD_MD,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(horizontal=theme.PAD_MD, vertical=theme.PAD_SM),
                        border=ft.border.only(bottom=ft.BorderSide(1, theme.BORDER)),
                        on_click=on_select,
                        ink=True,
                    )
                )
            page.update()
        except Exception as ex:
            print(f"[ERROR] load_members: {ex}")

    def select_member(member):
        selected_member["obj"] = member
        is_registered = getattr(member, "face_registered", False)

        selected_info.controls.clear()
        selected_info.controls.extend([
            ft.Text(member.name, size=theme.FONT_LG, weight=ft.FontWeight.BOLD,
                    color=theme.TEXT_PRIMARY),
            ft.Text(f"SĐT: {member.phone}", size=theme.FONT_SM, color=theme.TEXT_SECONDARY),
            ft.Container(
                content=ft.Text(
                    "Đã đăng ký Face ID" if is_registered else "Chưa đăng ký Face ID",
                    size=theme.FONT_XS, color=theme.WHITE, weight=ft.FontWeight.W_600,
                ),
                bgcolor=theme.GREEN if is_registered else theme.AMBER,
                border_radius=theme.BADGE_RADIUS,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            ),
        ])

        captured_photos["count"] = 0
        progress_bar.value = 0
        progress_text.value = "0/10 ảnh"
        status_text.value = "Bấm 'Bắt đầu chụp' để đăng ký khuôn mặt"
        status_text.color = theme.GRAY
        page.update()

    # ── Camera ───────────────────────────────────────────────────────────────
    # src="" thay cho src_base64=""; fit=ft.BoxFit (API mới)
    camera_image = ft.Image(
        src="",
        width=400,
        height=300,
        fit=ft.BoxFit.CONTAIN,
        border_radius=theme.CARD_RADIUS,
    )

    camera_placeholder = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.CAMERA_ALT, size=48, color=theme.GRAY),
                ft.Text("Chọn hội viên và bật camera", size=theme.FONT_MD, color=theme.GRAY),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=theme.PAD_SM,
        ),
        width=400,
        height=300,
        bgcolor="#1A1A2E",
        border_radius=theme.CARD_RADIUS,
        alignment=ft.Alignment.CENTER,
    )

    camera_container = ft.Container(content=camera_placeholder, width=400, height=300)

    # ── Progress ─────────────────────────────────────────────────────────────
    progress_bar = ft.ProgressBar(value=0, width=400, color=theme.ORANGE, bgcolor=theme.GRAY_LIGHT)
    progress_text = ft.Text("0/10 ảnh", size=theme.FONT_SM, color=theme.GRAY)
    status_text = ft.Text("Chọn hội viên để bắt đầu", size=theme.FONT_SM, color=theme.GRAY)

    # ── Camera preview loop ──────────────────────────────────────────────────
    def camera_preview_loop():
        cap = cv2.VideoCapture(0)
        camera_state["cap"] = cap

        if not cap.isOpened():
            status_text.value = "Không thể mở camera!"
            status_text.color = theme.RED
            page.update()
            return

        while camera_state["running"]:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.03)
                continue

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            img_base64 = base64.b64encode(buffer).decode()
            camera_image.src = img_base64   # API mới: dùng .src

            try:
                page.update()
            except Exception:
                break

            time.sleep(0.03)

        cap.release()
        camera_state["cap"] = None

    def start_capture_loop():
        member = selected_member["obj"]
        if not member:
            return

        cap = camera_state["cap"]
        if not cap or not cap.isOpened():
            return

        member_dir = os.path.join(DATASET_PATH, str(member.id))
        os.makedirs(member_dir, exist_ok=True)

        captured_photos["count"] = 0
        target = captured_photos["target"]

        status_text.value = "Đang chụp... Hãy xoay mặt nhẹ qua các góc"
        status_text.color = theme.ORANGE
        page.update()

        for i in range(target):
            if not camera_state["running"]:
                break

            ret, frame = cap.read()
            if not ret:
                continue

            photo_path = os.path.join(member_dir, f"photo_{i+1}.jpg")
            cv2.imwrite(photo_path, frame)
            captured_photos["count"] = i + 1

            progress_bar.value = (i + 1) / target
            progress_text.value = f"{i + 1}/{target} ảnh"

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            img_base64 = base64.b64encode(buffer).decode()
            camera_image.src = img_base64   # API mới

            try:
                page.update()
            except Exception:
                break

            time.sleep(0.5)

        if captured_photos["count"] >= target:
            status_text.value = "Đang encode khuôn mặt..."
            status_text.color = theme.BLUE
            page.update()

            try:
                image_paths = [
                    os.path.join(member_dir, f)
                    for f in os.listdir(member_dir)
                    if f.endswith('.jpg')
                ]
                result = face_svc.register_face_from_images(member.id, image_paths)

                if result.get("success"):
                    status_text.value = f"Đăng ký thành công! ({result.get('encodings', 0)} encodings)"
                    status_text.color = theme.GREEN
                    load_members()
                    updated = member_repo.get_by_id(member.id)
                    if updated:
                        select_member(updated)
                else:
                    status_text.value = "Không tìm thấy khuôn mặt trong ảnh!"
                    status_text.color = theme.RED
            except Exception as ex:
                status_text.value = f"Lỗi encode: {ex}"
                status_text.color = theme.RED

            page.update()

    def toggle_camera(e):
        if not camera_state["running"]:
            if not selected_member["obj"]:
                status_text.value = "Vui lòng chọn hội viên trước!"
                status_text.color = theme.RED
                page.update()
                return

            camera_state["running"] = True
            camera_container.content = camera_image
            page.update()
            t = threading.Thread(target=camera_preview_loop, daemon=True)
            t.start()
        else:
            camera_state["running"] = False
            camera_container.content = camera_placeholder
            camera_image.src = ""   # API mới
            page.update()

    def start_capture(e):
        if not camera_state["running"]:
            status_text.value = "Bật camera trước!"
            status_text.color = theme.RED
            page.update()
            return
        if not selected_member["obj"]:
            status_text.value = "Chọn hội viên trước!"
            status_text.color = theme.RED
            page.update()
            return

        t = threading.Thread(target=start_capture_loop, daemon=True)
        t.start()

    def remove_face(e):
        member = selected_member["obj"]
        if not member:
            return
        try:
            face_svc.remove_face(member.id)
            status_text.value = "Đã xóa dữ liệu khuôn mặt"
            status_text.color = theme.AMBER
            load_members()
            updated = member_repo.get_by_id(member.id)
            if updated:
                select_member(updated)
        except Exception as ex:
            status_text.value = f"Lỗi xóa: {ex}"
            status_text.color = theme.RED
        page.update()

    # ── Buttons ──────────────────────────────────────────────────────────────
    btn_toggle_cam = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.VIDEOCAM, size=14, color=theme.WHITE),
                ft.Text("Bật/Tắt Camera", size=theme.FONT_SM, weight=ft.FontWeight.W_600,
                        color=theme.WHITE),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=theme.GREEN,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=10),
        on_click=toggle_camera,
        ink=True,
    )

    btn_capture = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CAMERA, size=14, color=theme.WHITE),
                ft.Text("Bắt đầu chụp", size=theme.FONT_SM, weight=ft.FontWeight.W_600,
                        color=theme.WHITE),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=theme.ORANGE,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=10),
        on_click=start_capture,
        ink=True,
    )

    btn_remove = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.DELETE, size=14, color=theme.WHITE),
                ft.Text("Xóa Face ID", size=theme.FONT_SM, weight=ft.FontWeight.W_600,
                        color=theme.WHITE),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=theme.RED,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=10),
        on_click=remove_face,
        ink=True,
    )

    # ── Layout ───────────────────────────────────────────────────────────────
    left_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Chọn hội viên", size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
                        color=theme.TEXT_PRIMARY),
                search_field,
                ft.Container(
                    content=member_list,
                    bgcolor=theme.CARD_BG,
                    border_radius=theme.CARD_RADIUS,
                    border=ft.border.all(1, theme.BORDER),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    expand=True,
                ),
            ],
            spacing=theme.PAD_MD,
            expand=True,
        ),
        width=300,
        expand=False,
    )

    right_panel = ft.Column(
        controls=[
            ft.Text("Đăng ký khuôn mặt", size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
                    color=theme.TEXT_PRIMARY),
            ft.Container(
                content=selected_info,
                bgcolor=theme.CARD_BG,
                border_radius=theme.CARD_RADIUS,
                padding=ft.padding.all(theme.PAD_LG),
                border=ft.border.all(1, theme.BORDER),
            ),
            camera_container,
            progress_bar,
            ft.Row(
                controls=[progress_text, ft.Container(expand=True), status_text],
            ),
            ft.Row(
                controls=[btn_toggle_cam, btn_capture, btn_remove],
                spacing=theme.PAD_MD,
            ),
        ],
        spacing=theme.PAD_MD,
        expand=True,
    )

    content = ft.Container(
        content=ft.Row(
            controls=[left_panel, right_panel],
            spacing=theme.PAD_2XL,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=ft.padding.all(theme.PAD_2XL),
        expand=True,
    )

    load_members()

    return ft.Row(
        controls=[
            Sidebar(page, "face_register"),
            ft.Column(
                controls=[Header(page), content],
                spacing=0,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
