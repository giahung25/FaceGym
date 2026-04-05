# ============================================================================
# FILE: app/user_main.py
# MỤC ĐÍCH: ĐIỂM KHỞI ĐỘNG của User App (hội viên + HLV).
#
# THIẾT KẾ: Giống admin main.py — plain main(page), monkey-patch page.navigate,
#            lưu auth state trực tiếp trên page, lazy import trong navigate().
#
# FLOW:
#   1. ft.run(main) → Flet tạo cửa sổ, gọi main(page)
#   2. main() khởi tạo DB, cấu hình page, gắn navigate
#   3. Hiển thị LoginScreen đầu tiên
# ============================================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from app.core.database import init_db


def main(page: ft.Page):
    # ── Bước 1: Khởi tạo database ────────────────────────────────────────────
    try:
        init_db()
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo database: {e}")
        raise

    # ── Bước 2: Cấu hình cửa sổ ──────────────────────────────────────────────
    page.title = "GymFit — Ứng dụng hội viên"
    page.window.width = 1100
    page.window.height = 700
    page.bgcolor = "#F5F5F5"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # ── Bước 3: Auth state — monkey-patch trực tiếp lên page ─────────────────
    # Bất kỳ screen nào cũng truy cập: page.current_user, page.current_role
    page.current_user = None
    page.current_role = "member"  # "member" | "trainer"

    # ── Bước 4: Hàm điều hướng ───────────────────────────────────────────────
    def navigate(route: str):
        """Chuyển màn hình — xóa controls cũ, thêm screen mới, gọi page.update().

        Mọi screen đều nhận page làm tham số duy nhất:  Screen(page) → ft.Container
        Import lazy (bên trong hàm) để tránh circular import và chỉ load khi cần.
        """
        page.overlay.clear()
        page.controls.clear()
        page.on_search_change = None

        if route == "login":
            from gui.user.user_login import LoginScreen
            page.add(LoginScreen(page))
        elif route == "dashboard":
            from gui.user.user_dashboard import DashboardScreen
            page.add(DashboardScreen(page))
        elif route == "profile":
            from gui.user.user_profile import ProfileScreen
            page.add(ProfileScreen(page))
        elif route == "membership":
            from gui.user.user_membership import MembershipScreen
            page.add(MembershipScreen(page))
        elif route == "schedule":
            from gui.user.user_schedule import ScheduleScreen
            page.add(ScheduleScreen(page))
        elif route == "history":
            from gui.user.user_history import HistoryScreen
            page.add(HistoryScreen(page))
        elif route == "attendance_history":
            from gui.user.user_attendance import AttendanceHistoryScreen
            page.add(AttendanceHistoryScreen(page))
        elif route == "notifications":
            from gui.user.user_notifications import NotificationsScreen
            page.add(NotificationsScreen(page))
        elif route == "trainer":
            from gui.user.trainer_dashboard import TrainerDashboardScreen
            page.add(TrainerDashboardScreen(page))
        elif route == "trainer_students":
            from gui.user.trainer_students import TrainerStudentsScreen
            page.add(TrainerStudentsScreen(page))
        elif route == "trainer_schedule":
            from gui.user.trainer_schedule import TrainerScheduleScreen
            page.add(TrainerScheduleScreen(page))
        elif route == "trainer_profile":
            from gui.user.trainer_profile import TrainerProfileScreen
            page.add(TrainerProfileScreen(page))
        elif route == "trainer_notifications":
            from gui.user.trainer_notifications import TrainerNotificationsScreen
            page.add(TrainerNotificationsScreen(page))
        else:
            from gui.user.user_login import LoginScreen
            page.add(LoginScreen(page))

        page.update()

    # ── Bước 5: Gắn navigate vào page (monkey patching) ──────────────────────
    page.navigate = navigate

    # ── Bước 6: Màn hình đầu tiên ────────────────────────────────────────────
    navigate("login")


ft.run(main)
