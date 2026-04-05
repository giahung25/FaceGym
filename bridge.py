# ============================================================================
# FILE: bridge.py
# MUC DICH: Quan ly giao tiep giua Flet (main process) va Camera (subprocess).
#            Dung 2-way multiprocessing.Queue: command_queue va result_queue.
# ============================================================================

import multiprocessing
import queue


class CameraBridge:
    """Cau noi giua Flet GUI va Camera process (CustomTkinter).

    Cung cap API don gian:
        bridge.open_camera(mode)   - Mo camera o mode chi dinh
        bridge.close_camera()      - Dong camera an toan
        bridge.is_camera_running() - Kiem tra camera co dang chay khong
        bridge.get_result()        - Lay ket qua tu camera (non-blocking)
    """

    def __init__(self):
        self.command_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.cam_process = None

    def open_camera(self, mode="recognize", **kwargs):
        """Mo camera o mode chi dinh.

        Args:
            mode: "recognize" (nhan dien) hoac "register" (dang ky)
            **kwargs: Tham so bo sung:
                - member_id (str): ID hoi vien (mode register)
                - count (int): So anh can chup (mode register, mac dinh 10)

        Returns:
            dict: {"status": "started"} hoac {"error": "..."}
        """
        if self.is_camera_running():
            return {"error": "Camera dang ban"}

        # Clear old queues
        self._clear_queue(self.command_queue)
        self._clear_queue(self.result_queue)

        # Build name mapping {member_id: member_name} de camera hien thi ten
        if "name_map" not in kwargs:
            try:
                from app.repositories import member_repo
                members = member_repo.get_all(active_only=True)
                kwargs["name_map"] = {str(m.id): m.name for m in members}
            except Exception:
                kwargs["name_map"] = {}

        from camera_module import run_camera_window

        self.cam_process = multiprocessing.Process(
            target=run_camera_window,
            args=(self.command_queue, self.result_queue, mode),
            kwargs=kwargs,
        )
        self.cam_process.daemon = True
        self.cam_process.start()
        return {"status": "started"}

    def close_camera(self):
        """Dong camera an toan: gui lenh stop, doi process thoat, force kill neu can."""
        if self.cam_process and self.cam_process.is_alive():
            try:
                self.command_queue.put({"action": "stop"})
                self.cam_process.join(timeout=5)
            except Exception:
                pass
            if self.cam_process.is_alive():
                self.cam_process.terminate()
        self.cam_process = None

    def is_camera_running(self):
        """Kiem tra camera process con song khong."""
        return self.cam_process is not None and self.cam_process.is_alive()

    def get_result(self):
        """Lay 1 message tu result_queue (non-blocking).

        Returns:
            dict hoac None neu khong co message.

        Message types:
            {"type": "recognition", "member_id": str, "confidence": float}
            {"type": "unknown_face"}
            {"type": "register_progress", "member_id": str, "current": int, "total": int}
            {"type": "register_complete", "member_id": str, "photos": int}
            {"type": "register_failed", "member_id": str, "captured": int}
            {"type": "camera_error", "message": str}
            {"type": "camera_closed"}
            {"type": "camera_ready"}
        """
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

    def _clear_queue(self, q):
        """Xoa het message cu trong queue."""
        try:
            while True:
                q.get_nowait()
        except (queue.Empty, Exception):
            pass


# ── Singleton ──────────────────────────────────────────────────────────────────
_bridge = None


def get_bridge():
    """Lay singleton CameraBridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = CameraBridge()
    return _bridge
