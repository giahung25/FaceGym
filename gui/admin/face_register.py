# ============================================================================
# FILE: gui/admin/face_register.py
# MUC DICH: Man hinh DANG KY KHUON MAT cho hoi vien.
#            Chon hoi vien -> mo camera CTk (process rieng) -> chup anh -> encode.
# ============================================================================

import flet as ft
import asyncio
import os

from gui import theme
from gui.admin.components.sidebar import Sidebar
from gui.admin.components.header import Header
from app.services import face_svc
from app.repositories import member_repo
from app.core.config import DATASET_PATH
from bridge import get_bridge


def FaceRegisterScreen(page: ft.Page) -> ft.Row:
    """Man hinh dang ky khuon mat — chon member, mo camera, chup anh, encode."""

    navigate = getattr(page, "navigate", None)
    bridge = get_bridge()

    # ── State ─────────────────────────────────────────────────────────────────
    selected_member = {"obj": None}
    listener_running = {"active": False}

    # ── Danh sach hoi vien ────────────────────────────────────────────────────
    member_list = ft.Column(controls=[], spacing=0, scroll=ft.ScrollMode.AUTO, height=400)
    search_field = ft.TextField(
        label="Tim hoi vien...",
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
            ft.Text(f"SDT: {member.phone}", size=theme.FONT_SM, color=theme.TEXT_SECONDARY),
            ft.Container(
                content=ft.Text(
                    "Da dang ky Face ID" if is_registered else "Chua dang ky Face ID",
                    size=theme.FONT_XS, color=theme.WHITE, weight=ft.FontWeight.W_600,
                ),
                bgcolor=theme.GREEN if is_registered else theme.AMBER,
                border_radius=theme.BADGE_RADIUS,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            ),
        ])

        progress_bar.value = 0
        progress_text.value = "0/10 anh"
        status_text.value = "Bam 'Mo Camera' de dang ky khuon mat"
        status_text.color = theme.GRAY
        page.update()

    # ── Camera status area ────────────────────────────────────────────────────
    camera_status_icon = ft.Icon(ft.Icons.CAMERA_ALT, size=48, color=theme.GRAY)
    camera_status_text = ft.Text("Chon hoi vien va mo camera",
                                  size=theme.FONT_MD, color=theme.GRAY)

    camera_placeholder = ft.Container(
        content=ft.Column(
            controls=[camera_status_icon, camera_status_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=theme.PAD_SM,
        ),
        width=400,
        height=300,
        bgcolor="#1A1A2E",
        border_radius=theme.CARD_RADIUS,
        alignment=ft.Alignment.CENTER,
    )

    camera_container = ft.Container(
        content=camera_placeholder,
        width=400,
        height=300,
    )

    # ── Progress ──────────────────────────────────────────────────────────────
    progress_bar = ft.ProgressBar(value=0, width=400, color=theme.ORANGE,
                                  bgcolor=theme.GRAY_LIGHT)
    progress_text = ft.Text("0/10 anh", size=theme.FONT_SM, color=theme.GRAY)
    status_text = ft.Text("Chon hoi vien de bat dau", size=theme.FONT_SM, color=theme.GRAY)

    # ── Lang nghe ket qua tu camera process ──────────────────────────────────
    async def listen_camera_results():
        """Async loop lang nghe register progress tu camera process."""
        listener_running["active"] = True
        while bridge.is_camera_running():
            msg = bridge.get_result()
            if msg:
                msg_type = msg.get("type", "")

                if msg_type == "register_progress":
                    current = msg.get("current", 0)
                    total = msg.get("total", 10)
                    progress_bar.value = current / total
                    progress_text.value = f"{current}/{total} anh"
                    status_text.value = "Dang chup... Hay xoay mat nhe qua cac goc"
                    status_text.color = theme.ORANGE
                    page.update()

                elif msg_type == "register_complete":
                    member = selected_member["obj"]
                    if member:
                        status_text.value = "Dang encode khuon mat..."
                        status_text.color = theme.BLUE
                        page.update()

                        # Encode trong main process (co DB access)
                        try:
                            member_dir = os.path.join(DATASET_PATH, str(member.id))
                            image_paths = [
                                os.path.join(member_dir, f)
                                for f in os.listdir(member_dir)
                                if f.endswith('.jpg')
                            ]
                            result = face_svc.register_face_from_images(member.id, image_paths)

                            if result.get("success"):
                                status_text.value = f"Dang ky thanh cong! ({result.get('encodings', 0)} encodings)"
                                status_text.color = theme.GREEN
                                load_members()
                                updated = member_repo.get_by_id(member.id)
                                if updated:
                                    select_member(updated)
                            else:
                                status_text.value = "Khong tim thay khuon mat trong anh!"
                                status_text.color = theme.RED
                        except Exception as ex:
                            status_text.value = f"Loi encode: {ex}"
                            status_text.color = theme.RED

                        page.update()

                elif msg_type == "register_failed":
                    captured = msg.get("captured", 0)
                    status_text.value = f"Chup bi gian doan ({captured} anh). Thu lai."
                    status_text.color = theme.RED
                    page.update()

                elif msg_type == "camera_closed":
                    camera_status_icon.icon = ft.Icons.CAMERA_ALT
                    camera_status_icon.color = theme.GRAY
                    camera_status_text.value = "Camera da dong"
                    page.update()
                    break

                elif msg_type == "camera_error":
                    status_text.value = f"Loi camera: {msg.get('message', '')}"
                    status_text.color = theme.RED
                    page.update()

            await asyncio.sleep(0.1)

        listener_running["active"] = False

    # ── Buttons ───────────────────────────────────────────────────────────────
    def open_camera(e):
        if not selected_member["obj"]:
            status_text.value = "Vui long chon hoi vien truoc!"
            status_text.color = theme.RED
            page.update()
            return

        if bridge.is_camera_running():
            status_text.value = "Camera dang ban!"
            status_text.color = theme.RED
            page.update()
            return

        member = selected_member["obj"]
        result = bridge.open_camera(
            mode="register",
            member_id=str(member.id),
            count=10,
        )

        if "error" in result:
            status_text.value = result["error"]
            status_text.color = theme.RED
            page.update()
            return

        camera_status_icon.icon = ft.Icons.VIDEOCAM
        camera_status_icon.color = theme.GREEN
        camera_status_text.value = "Camera dang chay (cua so rieng)"
        status_text.value = "Camera da mo. Bam 'Bat dau chup' tren cua so camera."
        status_text.color = theme.ORANGE
        page.update()

        if not listener_running["active"]:
            page.run_task(listen_camera_results)

    def remove_face(e):
        member = selected_member["obj"]
        if not member:
            return
        try:
            face_svc.remove_face(member.id)
            status_text.value = "Da xoa du lieu khuon mat"
            status_text.color = theme.AMBER
            load_members()
            updated = member_repo.get_by_id(member.id)
            if updated:
                select_member(updated)
        except Exception as ex:
            status_text.value = f"Loi xoa: {ex}"
            status_text.color = theme.RED
        page.update()

    btn_open_cam = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.VIDEOCAM, size=14, color=theme.WHITE),
                ft.Text("Mo Camera", size=theme.FONT_SM, weight=ft.FontWeight.W_600,
                        color=theme.WHITE),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=theme.GREEN,
        border_radius=theme.BUTTON_RADIUS,
        padding=ft.padding.symmetric(horizontal=theme.PAD_LG, vertical=10),
        on_click=open_camera,
        ink=True,
    )

    btn_remove = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.DELETE, size=14, color=theme.WHITE),
                ft.Text("Xoa Face ID", size=theme.FONT_SM, weight=ft.FontWeight.W_600,
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

    # ── Layout ────────────────────────────────────────────────────────────────
    left_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Chon hoi vien", size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
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
            ft.Text("Dang ky khuon mat", size=theme.FONT_XL, weight=ft.FontWeight.BOLD,
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
                controls=[btn_open_cam, btn_remove],
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
