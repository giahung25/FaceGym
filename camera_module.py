# ============================================================================
# FILE: camera_module.py
# MUC DICH: Cua so camera doc lap dung CustomTkinter, chay trong process rieng.
#            Ho tro 2 mode: "recognize" (nhan dien) va "register" (dang ky).
# ============================================================================

import sys
import os

# Dam bao import duoc cac module trong project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import time
import queue as queue_module
import face_recognition

from app.core.config import (
    CAMERA_ID, FRAME_WIDTH, FRAME_HEIGHT, DATASET_PATH
)
from app.face_id.face_recognizer import FaceRecognitionSystem
from app.face_id.image_processing import draw_bbox


# ── Helper: Ve khung huong dan khuon mat ─────────────────────────────────────

def draw_face_guide(frame, color=(255, 255, 255), thickness=2, label=None):
    """Ve khung oval huong dan vi tri khuon mat o giua frame.

    Args:
        frame: BGR frame (se bi modify in-place)
        color: BGR color tuple
        thickness: do day net ve
        label: text hien thi phia tren khung (optional)
    """
    h, w = frame.shape[:2]
    center_x, center_y = w // 2, h // 2

    # Kich thuoc oval: ~40% chieu rong, ~55% chieu cao frame
    axis_x = int(w * 0.20)
    axis_y = int(h * 0.28)

    # Ve oval
    cv2.ellipse(frame, (center_x, center_y), (axis_x, axis_y),
                0, 0, 360, color, thickness, cv2.LINE_AA)

    # Ve 4 dau + o 4 goc oval de de nhin
    mark_len = 15
    # Top
    cv2.line(frame, (center_x, center_y - axis_y - mark_len),
             (center_x, center_y - axis_y + mark_len), color, thickness, cv2.LINE_AA)
    # Bottom
    cv2.line(frame, (center_x, center_y + axis_y - mark_len),
             (center_x, center_y + axis_y + mark_len), color, thickness, cv2.LINE_AA)
    # Left
    cv2.line(frame, (center_x - axis_x - mark_len, center_y),
             (center_x - axis_x + mark_len, center_y), color, thickness, cv2.LINE_AA)
    # Right
    cv2.line(frame, (center_x + axis_x - mark_len, center_y),
             (center_x + axis_x + mark_len, center_y), color, thickness, cv2.LINE_AA)

    # Label phia tren khung
    if label:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        (tw, th), _ = cv2.getTextSize(label, font, font_scale, 1)
        text_x = center_x - tw // 2
        text_y = center_y - axis_y - 20
        # Background cho text de doc
        cv2.rectangle(frame, (text_x - 4, text_y - th - 4),
                      (text_x + tw + 4, text_y + 4), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, label, (text_x, text_y),
                    font, font_scale, color, 1, cv2.LINE_AA)

    return frame


def is_face_in_guide_zone(face_location, frame_shape):
    """Kiem tra khuon mat co nam trong vung khung guide khong.

    Args:
        face_location: (top, right, bottom, left) tu face_recognition
        frame_shape: (h, w, channels)

    Returns:
        bool
    """
    h, w = frame_shape[:2]
    center_x, center_y = w // 2, h // 2
    axis_x = int(w * 0.20)
    axis_y = int(h * 0.28)

    top, right, bottom, left = face_location
    face_cx = (left + right) // 2
    face_cy = (top + bottom) // 2

    # Kiem tra tam khuon mat nam trong ellipse
    dx = (face_cx - center_x) / axis_x
    dy = (face_cy - center_y) / axis_y
    return (dx * dx + dy * dy) <= 1.5  # cho phep sai lech 1 chut


class CameraWindow(ctk.CTk):
    """Cua so camera CustomTkinter — chay trong process rieng."""

    def __init__(self, command_queue, result_queue, mode="recognize", **kwargs):
        super().__init__()

        self.command_queue = command_queue
        self.result_queue = result_queue
        self.mode = mode

        # Name mapping: {member_id(UUID): member_name} de hien thi ten thay vi UUID
        self.name_map = kwargs.pop("name_map", {})

        # Camera state
        self.cap = None
        self.running = False
        self._photo_image = None  # prevent GC
        self._fail_count = 0  # dem frame loi lien tiep (USB disconnect)

        # FPS tracking
        self._frame_times = []
        self._fps = 0

        # Recognition state
        self.recog_system = None
        self.recog_lock = threading.Lock()
        self.recog_busy = False
        self.recog_frame = None
        self.last_recog_results = []
        self.frame_count = 0

        # Register mode state
        self.register_member_id = kwargs.get("member_id", "")
        self.register_target = kwargs.get("count", 10)
        self.register_count = 0
        self.capturing = False
        self._last_capture_time = 0
        self._no_face_warnings = 0

        # Face detection state (for register auto-capture)
        self._detect_busy = False
        self._detect_frame = None
        self._detected_faces = []  # face_locations from last detection
        self._detect_lock = threading.Lock()

        self._setup_ui()
        self._open_camera()

        if mode == "recognize":
            self._init_recognition()
        elif mode == "register":
            # Start face detection thread cho auto-capture
            threading.Thread(target=self._face_detect_worker, daemon=True).start()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Start loops
        self._update_frame()
        self._check_commands()

    # ── UI Setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self):
        """Tao giao dien cua so camera."""
        if self.mode == "recognize":
            self.title("Camera - Nhan dien khuon mat")
        else:
            self.title(f"Camera - Dang ky khuon mat [{self.register_member_id}]")

        self.geometry("680x600")
        self.resizable(False, False)

        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Video frame
        self.video_frame = ctk.CTkFrame(self, width=640, height=480, corner_radius=8)
        self.video_frame.pack(padx=10, pady=(10, 5))
        self.video_frame.pack_propagate(False)

        self.video_label = ctk.CTkLabel(self.video_frame, text="Dang khoi tao camera...",
                                        font=ctk.CTkFont(size=16))
        self.video_label.pack(expand=True, fill="both")

        # Warning label (hien thi thong bao khi khong detect duoc mat)
        self.warning_label = ctk.CTkLabel(self, text="",
                                           font=ctk.CTkFont(size=13),
                                           text_color="#FF6B6B")
        self.warning_label.pack(padx=10, pady=(0, 2))

        # Bottom bar
        bottom_frame = ctk.CTkFrame(self, height=50)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Status
        self.status_label = ctk.CTkLabel(bottom_frame, text="Dang khoi tao...",
                                          font=ctk.CTkFont(size=13))
        self.status_label.pack(side="left", padx=10, pady=8)

        # FPS
        self.fps_label = ctk.CTkLabel(bottom_frame, text="FPS: --",
                                       font=ctk.CTkFont(size=12),
                                       text_color="gray")
        self.fps_label.pack(side="right", padx=10, pady=8)

        # Register mode: progress label
        if self.mode == "register":
            self.progress_label = ctk.CTkLabel(
                bottom_frame,
                text=f"0/{self.register_target} anh",
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            self.progress_label.pack(side="left", padx=10)

    # ── Camera ────────────────────────────────────────────────────────────────

    def _open_camera(self):
        """Mo camera vat ly."""
        self.cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            self.status_label.configure(text="LOI: Khong the mo camera!")
            self._send_result({"type": "camera_error", "message": "Khong the mo camera"})
            self.after(3000, self._on_close)
            return

        self.running = True
        if self.mode == "register":
            self.status_label.configure(text="Dua mat vao khung tron de tu dong chup")
        else:
            self.status_label.configure(text="Camera san sang")
        self._send_result({"type": "camera_ready"})

    def _init_recognition(self):
        """Khoi tao he thong nhan dien khuon mat (background thread)."""
        def init_worker():
            try:
                self.recog_system = FaceRecognitionSystem()
                self.status_label.configure(text="San sang nhan dien")
            except Exception as ex:
                self.status_label.configure(text=f"LOI AI: {ex}")

        threading.Thread(target=init_worker, daemon=True).start()

        # Start recognition worker thread
        threading.Thread(target=self._recog_worker, daemon=True).start()

    def _recog_worker(self):
        """Background thread: nhan dien khuon mat tren frame duoc gui tu main loop."""
        while self.running:
            frame = self.recog_frame
            if frame is not None and self.recog_system is not None:
                self.recog_frame = None
                self.recog_busy = True
                try:
                    results = self.recog_system.recognize_frame(frame)
                    with self.recog_lock:
                        self.last_recog_results = results

                    # Gui ket qua qua result_queue
                    for res in results:
                        name = res.get("name", "Unknown")
                        confidence = res.get("confidence", 0)
                        if name != "Unknown" and confidence > 0:
                            self._send_result({
                                "type": "recognition",
                                "member_id": name,
                                "confidence": confidence,
                            })
                        else:
                            self._send_result({"type": "unknown_face"})
                except Exception as ex:
                    print(f"[CAMERA] Recognition error: {ex}")
                finally:
                    self.recog_busy = False
            else:
                time.sleep(0.02)

    # ── Face detection worker (cho register mode auto-capture) ───────────────

    def _face_detect_worker(self):
        """Background thread: detect khuon mat cho register mode."""
        while self.running:
            frame = self._detect_frame
            if frame is not None:
                self._detect_frame = None
                self._detect_busy = True
                try:
                    # Resize nho de detect nhanh
                    small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                    locations = face_recognition.face_locations(rgb_small, model="hog")
                    # Scale lai ve kich thuoc goc
                    scaled = [(t*2, r*2, b*2, l*2) for (t, r, b, l) in locations]
                    with self._detect_lock:
                        self._detected_faces = scaled
                except Exception:
                    with self._detect_lock:
                        self._detected_faces = []
                finally:
                    self._detect_busy = False
            else:
                time.sleep(0.03)

    # ── Main frame update loop (Tkinter main thread) ─────────────────────────

    def _update_frame(self):
        """Doc frame tu camera, hien thi len CTk, gui frame cho recognition."""
        if not self.running or not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self._fail_count += 1
            if self._fail_count > 30:
                # Camera bi ngat (USB rut ra)
                self.status_label.configure(text="LOI: Camera bi ngat ket noi!")
                self._send_result({"type": "camera_error", "message": "Camera bi ngat ket noi"})
                self.after(2000, self._on_close)
                return
            self.after(33, self._update_frame)
            return

        self._fail_count = 0  # Reset khi doc frame thanh cong
        self.frame_count += 1

        # FPS tracking
        now = time.time()
        self._frame_times.append(now)
        self._frame_times = [t for t in self._frame_times if now - t < 1.0]
        self._fps = len(self._frame_times)
        if self.frame_count % 10 == 0:
            self.fps_label.configure(text=f"FPS: {self._fps}")

        # Mode-specific processing
        display_frame = frame.copy()

        if self.mode == "recognize":
            # Gui frame cho recognition moi 8 frame
            if self.frame_count % 8 == 0 and not self.recog_busy:
                self.recog_frame = frame.copy()

            # Ve bbox nhan dien
            with self.recog_lock:
                has_results = len(self.last_recog_results) > 0
                for res in self.last_recog_results:
                    bbox = res.get("bbox")
                    if bbox:
                        raw_name = res.get("name", "Unknown")
                        display_name = self._get_display_name(raw_name)
                        draw_bbox(display_frame, bbox,
                                  name=display_name,
                                  confidence=res.get("confidence", 0))

            # Ve khung guide khi chua nhan dien duoc ai
            if not has_results:
                draw_face_guide(display_frame, color=(100, 200, 255), thickness=2,
                                label="Dat mat vao khung")
            else:
                # Van ve khung guide mo khi da nhan dien
                draw_face_guide(display_frame, color=(0, 200, 0), thickness=1)

        elif self.mode == "register":
            # Gui frame cho face detection moi 6 frame
            if self.frame_count % 6 == 0 and not self._detect_busy:
                self._detect_frame = frame.copy()

            # Lay ket qua detected faces
            with self._detect_lock:
                detected = list(self._detected_faces)

            face_in_zone = False
            if detected:
                for (top, right, bottom, left) in detected:
                    in_zone = is_face_in_guide_zone((top, right, bottom, left), frame.shape)
                    face_in_zone = face_in_zone or in_zone

                    # Ve bbox quanh mat detected
                    box_color = (0, 255, 0) if in_zone else (0, 165, 255)
                    cv2.rectangle(display_frame, (left, top), (right, bottom),
                                  box_color, 2, cv2.LINE_AA)

            # Ve khung guide
            if face_in_zone:
                guide_color = (0, 255, 0)  # Xanh la: mat dung vi tri
                guide_label = "Dang chup..." if self.capturing else "Phat hien khuon mat!"
            elif detected:
                guide_color = (0, 165, 255)  # Cam: co mat nhung chua dung vi tri
                guide_label = "Di chuyen mat vao khung"
            else:
                guide_color = (100, 200, 255)  # Xanh nhat: chua phat hien mat
                guide_label = "Dat mat vao khung tron"

            draw_face_guide(display_frame, color=guide_color, thickness=2,
                            label=guide_label)

            # Auto-capture: tu dong chup khi phat hien mat trong vung guide
            if face_in_zone and not self.capturing:
                self._auto_start_capture()

            if self.capturing and face_in_zone:
                self._capture_photo(frame)

        # Convert BGR -> RGB -> PIL -> CTkImage
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image,
                                  size=(640, 480))
        self.video_label.configure(image=ctk_image, text="")
        self._photo_image = ctk_image  # prevent GC

        # ~30 FPS
        self.after(33, self._update_frame)

    # ── Register mode: capture photos ─────────────────────────────────────────

    def _auto_start_capture(self):
        """Tu dong bat dau chup khi phat hien khuon mat trong khung guide."""
        if self.capturing:
            return

        # Tao thu muc cho member
        member_dir = os.path.join(DATASET_PATH, str(self.register_member_id))
        os.makedirs(member_dir, exist_ok=True)
        self.member_dir = member_dir

        self.register_count = 0
        self._no_face_warnings = 0
        self.capturing = True
        self._last_capture_time = 0
        self.status_label.configure(text="Dang chup... Xoay mat nhe qua cac goc")
        self.warning_label.configure(text="")

    def _capture_photo(self, frame):
        """Chup 1 anh (goi tu _update_frame, cach nhau 0.5s).
        Kiem tra co khuon mat trong anh truoc khi luu."""
        now = time.time()
        if now - self._last_capture_time < 0.5:
            return

        if self.register_count >= self.register_target:
            self.capturing = False
            self._on_register_complete()
            return

        self._last_capture_time = now

        # Kiem tra co khuon mat trong frame khong truoc khi luu
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_small, model="hog")

        if not faces:
            # Khong tim thay khuon mat -> canh bao, khong dem anh nay
            self._no_face_warnings += 1
            self.warning_label.configure(
                text=f"Khong nhan dien duoc khuon mat! ({self._no_face_warnings} lan)"
            )
            self.status_label.configure(text="Nhin thang vao camera, du anh sang")
            return

        # Co khuon mat -> luu anh
        self.warning_label.configure(text="")
        self.register_count += 1

        photo_path = os.path.join(self.member_dir, f"photo_{self.register_count}.jpg")
        cv2.imwrite(photo_path, frame)

        self.progress_label.configure(text=f"{self.register_count}/{self.register_target} anh")
        self.status_label.configure(text=f"Da chup {self.register_count}/{self.register_target} - Xoay mat nhe")
        self._send_result({
            "type": "register_progress",
            "member_id": self.register_member_id,
            "current": self.register_count,
            "total": self.register_target,
        })

    def _on_register_complete(self):
        """Chup xong tat ca anh."""
        self.status_label.configure(text="Chup xong! Dang xu ly...")
        self.warning_label.configure(text="")

        self._send_result({
            "type": "register_complete",
            "member_id": self.register_member_id,
            "photos": self.register_count,
        })

        # Tu dong dong sau 2 giay
        self.after(2000, self._on_close)

    # ── Command queue listener ────────────────────────────────────────────────

    def _check_commands(self):
        """Kiem tra command_queue moi 100ms."""
        if not self.running:
            return

        try:
            cmd = self.command_queue.get_nowait()
            action = cmd.get("action", "")

            if action == "stop":
                self._on_close()
                return
            elif action == "reload_encodings" and self.recog_system:
                self.recog_system.reload_encodings()
                self.status_label.configure(text="Da reload encodings")
        except queue_module.Empty:
            pass
        except Exception:
            pass

        self.after(100, self._check_commands)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def _on_close(self):
        """Dong cua so: giai phong camera, gui thong bao, destroy."""
        self.running = False

        if self.capturing and self.register_count < self.register_target:
            self._send_result({
                "type": "register_failed",
                "member_id": self.register_member_id,
                "captured": self.register_count,
            })

        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

        self._send_result({"type": "camera_closed"})

        try:
            self.destroy()
        except Exception:
            pass

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _get_display_name(self, member_id):
        """Chuyen UUID thanh ten hoi vien de hien thi.
        Tra ve ten tu name_map, hoac member_id neu khong tim thay."""
        if member_id == "Unknown":
            return "Unknown"
        return self.name_map.get(member_id, member_id)

    def _send_result(self, msg):
        """Gui message vao result_queue (an toan)."""
        try:
            self.result_queue.put_nowait(msg)
        except Exception:
            pass


# ── Entry point cho multiprocessing.Process ──────────────────────────────────

def run_camera_window(command_queue, result_queue, mode="recognize", **kwargs):
    """Ham chay trong process rieng — tao va chay cua so camera CTk."""
    try:
        app = CameraWindow(command_queue, result_queue, mode, **kwargs)
        app.mainloop()
    except Exception as ex:
        try:
            result_queue.put_nowait({
                "type": "camera_error",
                "message": str(ex),
            })
            result_queue.put_nowait({"type": "camera_closed"})
        except Exception:
            pass
