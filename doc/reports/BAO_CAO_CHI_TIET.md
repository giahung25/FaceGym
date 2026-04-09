# BÁO CÁO KỸ THUẬT CHI TIẾT — Gym Management System (FaceGym)

**Ngày tạo:** 2026-03-20 21:40
**Cập nhật lần cuối:** 2026-04-09
**Người viết:** Claude Code (AI Assistant)
**Phạm vi:** Toàn bộ hệ thống — `app/`, `gui/`, `app/face_id/`, `bridge.py`, `camera_module.py`
**Trạng thái dự án:** Đang phát triển (Admin App ~95% | User App ~85% | Face ID ~90% | Tests 0%)

---

## MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Sơ đồ kiến trúc tổng thể](#2-sơ-đồ-kiến-trúc-tổng-thể)
3. [Phân tích chi tiết từng tầng (Layer)](#3-phân-tích-chi-tiết-từng-tầng)
   - 3.1 [Core Layer — Cấu hình, Database, Bảo mật](#31-core-layer)
   - 3.2 [Models Layer — Cấu trúc dữ liệu](#32-models-layer)
   - 3.3 [Repositories Layer — Data Access](#33-repositories-layer)
   - 3.4 [Services Layer — Business Logic](#34-services-layer)
   - 3.5 [Face ID Layer — Nhận diện khuôn mặt](#35-face-id-layer)
   - 3.6 [GUI Admin Layer — Giao diện quản trị](#36-gui-admin-layer)
   - 3.7 [GUI User Layer — Giao diện người dùng](#37-gui-user-layer)
   - 3.8 [Bridge & Camera Module — IPC đa tiến trình](#38-bridge--camera-module)
4. [Phân tích luồng dữ liệu (Data Flow)](#4-phân-tích-luồng-dữ-liệu)
5. [Đánh giá kỹ thuật](#5-đánh-giá-kỹ-thuật)
6. [Lịch sử thay đổi & sửa lỗi](#6-lịch-sử-thay-đổi--sửa-lỗi)
7. [Tổng kết](#7-tổng-kết)

---

## 1. Tổng quan hệ thống

### 1.1 Mục đích

**FaceGym** (Gym Management System) là ứng dụng desktop quản lý phòng gym tích hợp nhận diện khuôn mặt, bao gồm **2 ứng dụng riêng biệt**:

**Admin App** (`app/main.py`) — Dành cho quản trị viên:
- **Quản lý hội viên** (CRUD, tìm kiếm, lọc theo giới tính / trạng thái gói tập)
- **Quản lý gói tập** (tạo gói, đăng ký hội viên, hủy, tự động hết hạn)
- **Quản lý thiết bị** (CRUD, lọc theo trạng thái hoạt động / bảo trì / hỏng)
- **Quản lý huấn luyện viên** (CRUD, reset PIN, xem danh sách học viên)
- **Điểm danh bằng Face ID** (camera nhận diện, check-in tự động, check-in thủ công)
- **Đăng ký khuôn mặt** (chụp ảnh, encode face embeddings, quản lý face data)
- **Dashboard tổng quan** (KPI, biểu đồ doanh thu, cảnh báo sắp hết hạn, thống kê điểm danh)
- **Báo cáo** (thống kê hội viên, doanh thu, thiết bị)

**User App** (`app/user_main.py`) — Dành cho hội viên & huấn luyện viên:
- **Đăng nhập** bằng SĐT + PIN (phân biệt Member / Trainer)
- **Dashboard hội viên** (gói tập active, ngày còn lại, lịch sử điểm danh gần đây)
- **Hồ sơ cá nhân** + đổi PIN
- **Xem & đăng ký gói tập**
- **Lịch sử gói tập** + lịch sử điểm danh
- **Thông báo** (tự động khi gói sắp hết hạn ≤7 ngày)
- **Lịch tập** (xem lịch buổi tập được gán)
- **Check-in bằng khuôn mặt** (user tự check-in)
- **Dashboard HLV** (thông tin cá nhân, danh sách học viên)
- **Quản lý lịch dạy** (tạo/sửa buổi tập theo tuần)
- **Quản lý học viên** (ghi chú, theo dõi tiến độ)

### 1.2 Stack công nghệ

| Thành phần | Công nghệ | Phiên bản | Vai trò |
|-----------|-----------|-----------|---------|
| Ngôn ngữ | Python | 3.10+ | Ngôn ngữ chính, không dùng ORM |
| GUI Framework | Flet | 0.82.2 (pinned) | Render giao diện desktop (Admin + User) |
| Camera GUI | CustomTkinter | — | Cửa sổ camera riêng (subprocess) |
| Database | SQLite3 | Built-in | Lưu trữ dữ liệu cục bộ (10 bảng) |
| Face Recognition | face_recognition | — | Nhận diện khuôn mặt (dlib backend) |
| Computer Vision | OpenCV (cv2) | — | Xử lý ảnh, camera capture |
| Image Processing | Pillow (PIL) | — | Xử lý ảnh cho GUI |
| Numerical | NumPy | — | Tính toán vector embeddings |
| Auth | Plaintext compare | — | MVP, chưa có password hashing |

### 1.3 Cấu trúc thư mục tổng thể

```
FaceGym/
├── app/                              # Backend: core + models + repos + services + face_id
│   ├── main.py                       # Entry point ADMIN app: ft.run(main)
│   ├── user_main.py                  # Entry point USER app: ft.run(main)
│   ├── core/
│   │   ├── config.py                 # Biến cấu hình (DB path, credentials, camera, face settings)
│   │   ├── database.py               # SQLite3 connection + schema init (10 bảng + 18 indexes)
│   │   └── security.py               # check_login() cho admin
│   ├── models/
│   │   ├── base.py                   # BaseModel (UUID, timestamps, soft delete)
│   │   ├── member.py                 # Member (+ pin, face_registered, member_code)
│   │   ├── membership.py            # MembershipPlan + MembershipSubscription
│   │   ├── equipment.py              # Equipment
│   │   ├── trainer.py                # Trainer (+ pin, specialization)
│   │   ├── notification.py           # Notification (không kế thừa BaseModel)
│   │   ├── trainer_assignment.py     # TrainerAssignment (HLV ↔ hội viên)
│   │   ├── training_session.py       # TrainingSession (buổi tập)
│   │   ├── attendance.py             # Attendance (điểm danh)
│   │   └── transaction.py            # Transaction (giao dịch thanh toán)
│   ├── repositories/
│   │   ├── member_repo.py            # CRUD + search Members
│   │   ├── membership_repo.py        # CRUD Plans + Subscriptions + expiring_soon
│   │   ├── equipment_repo.py         # CRUD + filter by status/category
│   │   ├── trainer_repo.py           # CRUD + get_by_phone (đăng nhập)
│   │   ├── notification_repo.py      # CRUD + get_by_user + deduplication
│   │   ├── trainer_assignment_repo.py # CRUD + get_by_trainer/member
│   │   ├── training_session_repo.py  # CRUD + get_by_week
│   │   ├── attendance_repo.py        # CRUD + get_today + history
│   │   └── transaction_repo.py       # CRUD + revenue queries
│   ├── services/
│   │   ├── member_svc.py             # Validate + CRUD + stats
│   │   ├── membership_svc.py         # Plans + Subscriptions + revenue + auto-expire
│   │   ├── equipment_svc.py          # Validate + CRUD + summary
│   │   ├── trainer_svc.py            # Validate + CRUD HLV + reset PIN
│   │   ├── auth_svc.py               # Login member/trainer + đổi PIN
│   │   ├── notification_svc.py       # CRUD thông báo + auto-notify hết hạn
│   │   ├── assignment_svc.py         # Gán HLV ↔ hội viên + auto-end
│   │   ├── schedule_svc.py           # CRUD buổi tập + validate date/time
│   │   ├── attendance_svc.py         # Check-in/out + Face ID check-in + stats
│   │   ├── face_svc.py               # Đăng ký/nhận diện khuôn mặt + reload encodings
│   │   └── payment_svc.py            # ❌ Stub trống (chưa implement)
│   ├── face_id/                      # Module AI nhận diện khuôn mặt
│   │   ├── __init__.py               # Export: FaceEncoder, FaceDetector, FaceRecognitionSystem, FaceRegistration
│   │   ├── face_encoder.py           # Encode ảnh → vector 128 chiều
│   │   ├── face_recognizer.py        # Nhận diện real-time từ camera frame
│   │   ├── face_register.py          # Đăng ký khuôn mặt (chụp + encode + lưu)
│   │   └── image_processing.py       # Vẽ bbox, resize, convert BGR↔RGB
│   ├── api/                          # ❌ Stub trống (không sử dụng)
│   └── utils/
│       ├── email.py                  # Tiện ích email (stub)
│       └── helpers.py                # Hàm tiện ích chung
├── gui/                              # Frontend: Flet screens + components
│   ├── theme.py                      # Design tokens (màu, font, spacing)
│   ├── admin/                        # GUI Admin (quản trị viên)
│   │   ├── login.py                  # Màn hình đăng nhập admin
│   │   ├── dashboard.py              # Dashboard tổng quan
│   │   ├── members.py                # Quản lý hội viên
│   │   ├── memberships.py            # Gói tập & Đăng ký
│   │   ├── equipment.py              # Quản lý thiết bị
│   │   ├── trainers.py               # Quản lý huấn luyện viên
│   │   ├── attendance.py             # Điểm danh bằng Face ID (MỚI)
│   │   ├── face_register.py          # Đăng ký khuôn mặt (MỚI)
│   │   ├── reports.py                # Báo cáo thống kê
│   │   └── components/
│   │       ├── sidebar.py            # Sidebar điều hướng (reusable)
│   │       └── header.py             # Header + search bar (reusable)
│   └── user/                         # GUI User (hội viên & HLV)
│       ├── user_login.py             # Đăng nhập SĐT + PIN (Member / Trainer)
│       ├── user_dashboard.py         # Dashboard hội viên
│       ├── user_profile.py           # Hồ sơ cá nhân + đổi PIN
│       ├── user_membership.py        # Gói tập hiện tại + đăng ký
│       ├── user_schedule.py          # Lịch tập hội viên
│       ├── user_history.py           # Lịch sử gói tập
│       ├── user_attendance.py        # Lịch sử điểm danh
│       ├── user_checkin.py           # Check-in bằng khuôn mặt
│       ├── user_notifications.py     # Thông báo hội viên
│       ├── trainer_dashboard.py      # Dashboard HLV
│       ├── trainer_profile.py        # Hồ sơ HLV + đổi PIN
│       ├── trainer_schedule.py       # Lịch dạy HLV (tạo/sửa buổi tập)
│       ├── trainer_students.py       # Danh sách học viên + ghi chú
│       ├── trainer_notifications.py  # Thông báo HLV
│       ├── app_state.py              # ⚠️ Không còn sử dụng (state trên page object)
│       └── components/
│           └── user_sidebar.py       # Sidebar user (menu theo role)
├── bridge.py                         # IPC bridge: Flet ↔ Camera subprocess (multiprocessing)
├── camera_module.py                  # CustomTkinter camera window (chạy trong subprocess)
├── data/
│   ├── gym_db.db                     # SQLite database file
│   ├── dataset/                      # Ảnh khuôn mặt gốc (theo member_id)
│   └── encodings/                    # File pickle chứa face embeddings
│       └── face_encodings.pkl
├── doc/                              # Tài liệu dự án
├── requirements.txt                  # Dependencies
└── CLAUDE.md                         # Hướng dẫn cho AI assistant
```

---

## 2. Sơ đồ kiến trúc tổng thể

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GUI Layer (Flet)                                   │
│                                                                              │
│  ┌── Admin App (gui/admin/) ──────────────────────────────────────────────┐  │
│  │ login │ dashboard │ members │ memberships │ equipment │ trainers       │  │
│  │ attendance │ face_register │ reports                                   │  │
│  │ components/: sidebar.py + header.py                                   │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌── User App (gui/user/) ────────────────────────────────────────────────┐  │
│  │ user_login │ user_dashboard │ user_profile │ user_membership           │  │
│  │ user_schedule │ user_history │ user_attendance │ user_checkin          │  │
│  │ user_notifications                                                     │  │
│  │ trainer_dashboard │ trainer_profile │ trainer_schedule                 │  │
│  │ trainer_students │ trainer_notifications                               │  │
│  │ components/: user_sidebar.py                                          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌── Camera Module (subprocess) ──────────────────────────────────────────┐  │
│  │ bridge.py (IPC multiprocessing) ↔ camera_module.py (CustomTkinter)    │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────┤
│                          Services Layer                                      │
│  ┌─────────────┐ ┌────────────────┐ ┌───────────────┐ ┌──────────────┐      │
│  │member_svc   │ │membership_svc  │ │equipment_svc  │ │trainer_svc   │      │
│  └─────────────┘ └────────────────┘ └───────────────┘ └──────────────┘      │
│  ┌─────────────┐ ┌────────────────┐ ┌───────────────┐ ┌──────────────┐      │
│  │auth_svc     │ │notification_svc│ │assignment_svc │ │schedule_svc  │      │
│  └─────────────┘ └────────────────┘ └───────────────┘ └──────────────┘      │
│  ┌─────────────┐ ┌────────────────┐                                          │
│  │attendance_svc│ │face_svc       │  Validation → Business Logic → Repo     │
│  └─────────────┘ └────────────────┘                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                       Repositories Layer                                     │
│  ┌─────────────┐ ┌────────────────┐ ┌───────────────┐ ┌──────────────┐      │
│  │member_repo  │ │membership_repo │ │equipment_repo │ │trainer_repo  │      │
│  └─────────────┘ └────────────────┘ └───────────────┘ └──────────────┘      │
│  ┌──────────────────┐ ┌─────────────────────┐ ┌──────────────────────┐      │
│  │notification_repo │ │trainer_assignment_repo│ │training_session_repo│      │
│  └──────────────────┘ └─────────────────────┘ └──────────────────────┘      │
│  ┌──────────────────┐ ┌──────────────────┐                                   │
│  │attendance_repo   │ │transaction_repo  │  SQL thuần → Model objects        │
│  └──────────────────┘ └──────────────────┘                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                         Models Layer                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ ┌───────────┐ ┌───────────┐│
│  │ BaseModel│ │ Member   │ │MembershipPlan    │ │ Equipment │ │ Trainer   ││
│  │          │ │          │ │MembershipSubscr. │ │           │ │           ││
│  └──────────┘ └──────────┘ └──────────────────┘ └───────────┘ └───────────┘│
│  ┌──────────────────┐ ┌──────────────────┐ ┌────────────┐ ┌──────────────┐ │
│  │TrainerAssignment │ │TrainingSession   │ │ Attendance │ │ Transaction  │ │
│  └──────────────────┘ └──────────────────┘ └────────────┘ └──────────────┘ │
│  ┌──────────────┐                                                           │
│  │ Notification │ (không kế thừa BaseModel)                                 │
│  └──────────────┘                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                        Face ID Layer                                         │
│  ┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐                 │
│  │face_encoder  │ │face_recognizer   │ │face_register     │                 │
│  │(128D vectors)│ │(real-time match) │ │(capture + encode)│                 │
│  └──────────────┘ └──────────────────┘ └──────────────────┘                 │
│  ┌────────────────────┐                                                      │
│  │image_processing    │  OpenCV + face_recognition + NumPy                   │
│  └────────────────────┘                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                        Core Layer                                            │
│  ┌──────────┐ ┌────────────┐ ┌──────────────┐                               │
│  │ config.py│ │ database.py│ │ security.py  │                               │
│  └──────────┘ └────────────┘ └──────────────┘                               │
│  Settings     SQLite3 conn     check_login()                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                      SQLite3 Database (10 bảng)                              │
│  ┌──────────┐ ┌────────────────┐ ┌──────────────┐ ┌──────────┐             │
│  │ members  │ │membership_plans│ │subscriptions │ │equipment │             │
│  └──────────┘ └────────────────┘ └──────────────┘ └──────────┘             │
│  ┌──────────┐ ┌──────────────┐ ┌─────────────────────┐ ┌─────────────────┐ │
│  │ trainers │ │notifications │ │trainer_assignments  │ │training_sessions│ │
│  └──────────┘ └──────────────┘ └─────────────────────┘ └─────────────────┘ │
│  ┌────────────┐ ┌──────────────┐                                            │
│  │ attendance │ │ transactions │                                            │
│  └────────────┘ └──────────────┘                                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Navigation Flow — Admin App

```
ft.run(main)  [app/main.py]
    │
    ├── init_db()                    # Tạo/migrate 10 bảng
    ├── page.navigate = navigate     # Inject router function
    └── navigate("login")
         │
         ├── LoginScreen ──[đăng nhập thành công]──→ DashboardScreen
         │                                                │
         │         Sidebar điều hướng: ←──────────────────┘
         │         ├── "dashboard"     → DashboardScreen
         │         ├── "members"       → MembersScreen
         │         ├── "packages"      → MembershipsScreen
         │         ├── "equipment"     → EquipmentScreen
         │         ├── "trainers"      → TrainersScreen
         │         ├── "attendance"    → AttendanceScreen       ← MỚI
         │         ├── "face_register" → FaceRegisterScreen     ← MỚI
         │         └── "reports"       → ReportsScreen
         │
         └── Mỗi lần navigate():
              page.overlay.clear()      # Xóa dialog cũ
              page.controls.clear()     # Xóa UI cũ
              page.on_search_change = None  # Reset search callback
              page.add(NewScreen(page))
              page.update()
```

### 2.3 Navigation Flow — User App

```
ft.run(main)  [app/user_main.py]
    │
    ├── init_db()
    ├── page.current_user = None     # Auth state
    ├── page.current_role = None     # "member" hoặc "trainer"
    ├── page.navigate = navigate
    └── navigate("login")
         │
         ├── LoginScreen (chọn role: Hội viên / HLV)
         │    │
         │    ├──[login member thành công]──→ DashboardScreen (hội viên)
         │    │   │
         │    │   │  UserSidebar (menu hội viên): ←────────────────┐
         │    │   │  ├── "dashboard"          → DashboardScreen    │
         │    │   │  ├── "profile"            → ProfileScreen      │
         │    │   │  ├── "schedule"           → ScheduleScreen     │
         │    │   │  ├── "membership"         → MembershipScreen   │
         │    │   │  ├── "history"            → HistoryScreen      │
         │    │   │  ├── "attendance_history" → AttendanceHistoryScreen
         │    │   │  ├── "notifications"      → NotificationsScreen│
         │    │   │  └── Đăng xuất → navigate("login")             │
         │    │   │                                                 │
         │    └──[login trainer thành công]──→ TrainerDashboardScreen
         │        │
         │        │  UserSidebar (menu HLV): ←─────────────────────┐
         │        │  ├── "trainer"               → TrainerDashboard│
         │        │  ├── "trainer_students"       → TrainerStudents │
         │        │  ├── "trainer_schedule"       → TrainerSchedule │
         │        │  ├── "trainer_profile"        → TrainerProfile  │
         │        │  ├── "trainer_notifications"  → TrainerNotifications
         │        │  └── Đăng xuất → navigate("login")             │
         │
         └── Guard clause: Mọi screen (trừ login) kiểm tra current_user
              if not current_user:
                  navigate("login")
                  return ft.Container()
```

### 2.4 Kiến trúc Camera — Multiprocessing

```
┌───────────────────────────┐          ┌───────────────────────────┐
│     FLET (Main Process)   │          │   CAMERA (Subprocess)     │
│                           │          │                           │
│  gui/admin/attendance.py  │          │  camera_module.py         │
│  gui/admin/face_register  │          │  (CustomTkinter window)   │
│  gui/user/user_checkin.py │          │                           │
│         │                 │          │  ┌───────────────────┐    │
│         ▼                 │          │  │ OpenCV VideoCapture│    │
│  ┌─────────────────┐      │          │  └───────┬───────────┘    │
│  │  bridge.py      │      │          │          │                │
│  │  CameraBridge   │      │          │  ┌───────▼───────────┐    │
│  │                 │      │          │  │ face_recognizer    │    │
│  │ command_queue ──┼──────┼─────────►│  │ face_register      │    │
│  │ (open/close)    │      │          │  └───────┬───────────┘    │
│  │                 │      │          │          │                │
│  │ result_queue  ◄─┼──────┼──────────│  result_queue.put()      │
│  │ (recognition,   │      │          │  {"type":"recognition",   │
│  │  register_prog, │      │          │   "member_id":"...",      │
│  │  camera_error)  │      │          │   "confidence":0.85}      │
│  └─────────────────┘      │          │                           │
│         │                 │          └───────────────────────────┘
│         ▼                 │
│  async listen_camera()    │   Message types:
│  → poll result_queue      │   - recognition: nhận diện thành công
│  → update UI              │   - unknown_face: không nhận ra
│                           │   - register_progress: tiến độ chụp
│                           │   - register_complete: hoàn thành
│                           │   - register_failed: thất bại
│                           │   - camera_error: lỗi camera
│                           │   - camera_closed: đã đóng
└───────────────────────────┘
```

**Tại sao cần multiprocessing?**
- Flet chạy event loop riêng — nếu camera chạy cùng process sẽ block UI.
- CustomTkinter cần mainloop riêng — hai GUI framework không thể chạy chung process.
- Multiprocessing.Queue thread-safe, process-safe → IPC an toàn.

---

## 3. Phân tích chi tiết từng tầng

---

### 3.1 Core Layer

#### 3.1.1 `app/core/config.py` — Cấu hình hệ thống

**Mục đích:** Tập trung toàn bộ hằng số cấu hình, tránh hardcode rải rác.

```python
# Dòng 4: Tính đường dẫn gốc dự án
# os.path.abspath(__file__) → E:/FaceGym/app/core/config.py
# dirname x3 → E:/FaceGym/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Dòng 6: Database nằm tại data/gym_db.db (tương đối từ gốc dự án)
DB_PATH = os.path.join(BASE_DIR, "data", "gym_db.db")

# Dòng 8-10: Cấu hình cửa sổ Flet
APP_TITLE = "GymAdmin Management System"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

# Dòng 13-14: Credentials — có thể override qua biến môi trường
# Ví dụ: GYM_USERNAME=admin2 python app/main.py
ADMIN_USERNAME = os.environ.get("GYM_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("GYM_PASSWORD", "admin123")
```

| Biến | Giá trị mặc định | Override qua env | Mô tả |
|------|-------------------|:----------------:|-------|
| `BASE_DIR` | (tự tính) | ❌ | Thư mục gốc dự án |
| `DB_PATH` | `data/gym_db.db` | ❌ | Đường dẫn database |
| `APP_TITLE` | `"GymAdmin Management System"` | ❌ | Tiêu đề cửa sổ |
| `WINDOW_WIDTH` | `1280` | ❌ | Chiều rộng cửa sổ (Admin) |
| `WINDOW_HEIGHT` | `800` | ❌ | Chiều cao cửa sổ (Admin) |
| `ADMIN_USERNAME` | `"admin"` | ✅ `GYM_USERNAME` | Tên đăng nhập admin |
| `ADMIN_PASSWORD` | `"admin123"` | ✅ `GYM_PASSWORD` | Mật khẩu admin |

**Liên kết:** `database.py` import `DB_PATH`, `security.py` import `ADMIN_USERNAME/PASSWORD`, `main.py` import `APP_TITLE/WIDTH/HEIGHT`.

---

#### 3.1.2 `app/core/database.py` — Kết nối SQLite3

**Mục đích:** Quản lý kết nối database và khởi tạo schema (10 bảng + 18 indexes).

##### Khối 1: Context Manager `get_db()`

```python
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)     # Mở kết nối SQLite
    conn.row_factory = sqlite3.Row       # Trả kết quả dạng dict-like thay vì tuple
    conn.execute("PRAGMA foreign_keys = ON")  # Bật kiểm tra Foreign Key
    try:
        yield conn          # Trả connection cho caller dùng
        conn.commit()       # Nếu không lỗi → commit
    except Exception:
        conn.rollback()     # Nếu lỗi → rollback
        raise
    finally:
        conn.close()        # Luôn đóng connection
```

**Tại sao dùng Context Manager?**
- Đảm bảo `commit/rollback/close` tự động, tránh leak connection.
- Các repository dùng pattern `with get_db() as conn:` → an toàn transaction.

**`row_factory = sqlite3.Row`**: Cho phép truy cập cột bằng tên (`row["name"]`) thay vì index (`row[1]`), code dễ đọc và bảo trì hơn.

**`PRAGMA foreign_keys = ON`**: SQLite mặc định TẮT kiểm tra FK. Dòng này bật lên để đảm bảo tính toàn vẹn dữ liệu.

##### Khối 2: `init_db()` — Tạo schema (10 bảng)

```python
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        # 10 bảng chính
        conn.execute("CREATE TABLE IF NOT EXISTS members (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS membership_plans (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS subscriptions (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS equipment (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS trainers (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS notifications (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS trainer_assignments (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS training_sessions (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS attendance (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS transactions (...)")

        # 18 indexes tăng tốc query
        # ... (chi tiết bên dưới)

        # Migrations cho DB cũ
        # ALTER TABLE members ADD COLUMN pin ...
        # ALTER TABLE members ADD COLUMN face_registered ...
        # ALTER TABLE members ADD COLUMN member_code ...
        # ALTER TABLE subscriptions ADD COLUMN trainer_id ...
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

##### Database Schema — 10 bảng

| Bảng | Cột | Kiểu | Ràng buộc | Mô tả |
|------|-----|------|-----------|-------|
| **members** | `id` | TEXT | PK | UUID4 |
| | `name` | TEXT | NOT NULL | Họ tên |
| | `phone` | TEXT | NOT NULL, UNIQUE | SĐT (dùng đăng nhập user app) |
| | `email` | TEXT | — | Email |
| | `gender` | TEXT | — | male/female/other |
| | `date_of_birth` | TEXT | — | YYYY-MM-DD |
| | `address` | TEXT | — | Địa chỉ |
| | `emergency_contact` | TEXT | — | Liên hệ khẩn cấp |
| | `photo` | TEXT | — | Đường dẫn ảnh |
| | `pin` | TEXT | NOT NULL DEFAULT '000000', CHECK(LENGTH=6) | PIN 6 chữ số |
| | `member_code` | TEXT | UNIQUE | Mã hội viên (GYM-YYYYMMDD-XXX) |
| | `face_registered` | INTEGER | DEFAULT 0 | Đã đăng ký Face ID (0/1) |
| | `photo_path` | TEXT | — | Đường dẫn ảnh Face ID |
| | `created_at/updated_at` | TEXT | NOT NULL | ISO datetime |
| | `is_active` | INTEGER | NOT NULL DEFAULT 1 | Soft delete flag |
| **membership_plans** | `id` | TEXT | PK | UUID4 |
| | `name` | TEXT | NOT NULL | Tên gói tập |
| | `duration_days` | INTEGER | NOT NULL | Số ngày hiệu lực |
| | `price` | REAL | NOT NULL | Giá (VND) |
| | `description` | TEXT | — | Mô tả |
| | `created_at/updated_at/is_active` | — | — | (giống members) |
| **subscriptions** | `id` | TEXT | PK | UUID4 |
| | `member_id` | TEXT | NOT NULL, FK → members(id) | Hội viên |
| | `plan_id` | TEXT | NOT NULL, FK → membership_plans(id) | Gói tập |
| | `price_paid` | REAL | NOT NULL | Giá thực tế |
| | `start_date` | TEXT | NOT NULL | ISO datetime |
| | `end_date` | TEXT | NOT NULL | ISO datetime |
| | `status` | TEXT | NOT NULL DEFAULT 'active' | active/expired/cancelled |
| | `trainer_id` | TEXT | FK → trainers(id), nullable | HLV được gán |
| | `created_at/updated_at/is_active` | — | — | (giống members) |
| **equipment** | `id` | TEXT | PK | UUID4 |
| | `name` | TEXT | NOT NULL | Tên thiết bị |
| | `category` | TEXT | NOT NULL | Loại (Cardio/Strength...) |
| | `quantity` | INTEGER | NOT NULL DEFAULT 1 | Số lượng |
| | `status` | TEXT | NOT NULL DEFAULT 'working' | working/broken/maintenance |
| | `purchase_date` | TEXT | — | Ngày mua |
| | `location` | TEXT | — | Vị trí đặt |
| | `notes` | TEXT | — | Ghi chú |
| | `created_at/updated_at/is_active` | — | — | (giống members) |
| **trainers** | `id` | TEXT | PK | UUID4 |
| | `name` | TEXT | NOT NULL | Họ tên HLV |
| | `phone` | TEXT | NOT NULL, UNIQUE | SĐT (đăng nhập user app) |
| | `email` | TEXT | — | Email |
| | `specialization` | TEXT | — | Chuyên môn: Yoga, Boxing, Gym... |
| | `pin` | TEXT | NOT NULL DEFAULT '000000', CHECK(LENGTH=6) | PIN 6 chữ số |
| | `created_at/updated_at/is_active` | — | — | (giống members) |
| **notifications** | `id` | TEXT | PK | UUID4 |
| | `user_id` | TEXT | NOT NULL | ID hội viên hoặc HLV |
| | `user_type` | TEXT | NOT NULL | 'member' hoặc 'trainer' |
| | `title` | TEXT | NOT NULL | Tiêu đề thông báo |
| | `message` | TEXT | NOT NULL | Nội dung |
| | `is_read` | INTEGER | DEFAULT 0 | Đã đọc (0/1) |
| | `created_at` | TEXT | NOT NULL | ISO datetime |
| **trainer_assignments** | `id` | TEXT | PK | UUID4 |
| | `member_id` | TEXT | NOT NULL, FK → members(id) | Hội viên được gán |
| | `trainer_id` | TEXT | NOT NULL, FK → trainers(id) | HLV |
| | `subscription_id` | TEXT | FK → subscriptions(id) | Gói tập liên kết |
| | `start_date` | TEXT | NOT NULL | Ngày bắt đầu |
| | `end_date` | TEXT | — | Ngày kết thúc (null = đang active) |
| | `status` | TEXT | NOT NULL DEFAULT 'active' | active/ended |
| | `notes` | TEXT | — | Ghi chú |
| | `created_at/updated_at/is_active` | — | — | (giống members) |
| **training_sessions** | `id` | TEXT | PK | UUID4 |
| | `trainer_id` | TEXT | NOT NULL, FK → trainers(id) | HLV |
| | `member_id` | TEXT | NOT NULL, FK → members(id) | Hội viên |
| | `assignment_id` | TEXT | FK → trainer_assignments(id) | Assignment liên kết |
| | `session_date` | TEXT | NOT NULL | YYYY-MM-DD |
| | `start_time` | TEXT | NOT NULL | HH:MM |
| | `end_time` | TEXT | NOT NULL | HH:MM |
| | `content` | TEXT | — | Nội dung buổi tập |
| | `status` | TEXT | DEFAULT 'scheduled' | scheduled/completed/cancelled |
| | `notes` | TEXT | — | Ghi chú |
| | `created_at/updated_at/is_active` | — | — | (giống members) |
| **attendance** | `id` | TEXT | PK | UUID4 |
| | `member_id` | TEXT | NOT NULL, FK → members(id) | Hội viên |
| | `check_in` | TEXT | NOT NULL | ISO datetime check-in |
| | `check_out` | TEXT | — | ISO datetime check-out (nullable) |
| | `method` | TEXT | DEFAULT 'face_id' | face_id/manual/qr_code |
| | `confidence` | REAL | — | Độ tin cậy nhận diện (0.0-1.0) |
| | `created_at/is_active` | — | — | Timestamps |
| **transactions** | `id` | TEXT | PK | UUID4 |
| | `member_id` | TEXT | NOT NULL, FK → members(id) | Hội viên |
| | `subscription_id` | TEXT | FK → subscriptions(id) | Gói tập (nullable) |
| | `amount` | REAL | NOT NULL | Số tiền |
| | `payment_method` | TEXT | — | cash/transfer/card |
| | `note` | TEXT | — | Ghi chú |
| | `created_at/is_active` | — | — | Timestamps |

**Quan hệ giữa các bảng:**

```
members ──1:N──→ subscriptions ←──N:1── membership_plans
    │                  │
    │                  └── trainer_id FK ──→ trainers
    │
    ├──1:N──→ trainer_assignments ←──N:1── trainers
    │                  │
    │                  └──1:N──→ training_sessions
    │
    ├──1:N──→ attendance
    │
    ├──1:N──→ transactions
    │
    └──1:N──→ notifications ←──N:1── trainers (qua user_id + user_type)

equipment: bảng độc lập, không có FK
```

##### 18 Indexes

| Bảng | Index | Cột | Mục đích |
|------|-------|-----|----------|
| members | `idx_members_phone` | phone | Tìm kiếm theo SĐT |
| members | `idx_members_is_active` | is_active | Lọc active/inactive |
| members | `idx_members_phone_unique` | phone (UNIQUE) | Đảm bảo SĐT duy nhất |
| subscriptions | `idx_subs_member_id` | member_id | JOIN với members |
| subscriptions | `idx_subs_plan_id` | plan_id | JOIN với plans |
| subscriptions | `idx_subs_status` | status | Lọc active/expired |
| equipment | `idx_equipment_status` | status | Lọc theo trạng thái |
| trainers | `idx_trainers_phone` | phone | Tìm kiếm SĐT |
| trainers | `idx_trainers_phone_unique` | phone (UNIQUE) | Đảm bảo SĐT duy nhất |
| notifications | `idx_notif_user` | user_id, user_type | Lấy thông báo theo user |
| notifications | `idx_notif_is_read` | is_read | Đếm chưa đọc |
| trainer_assignments | `idx_ta_member` | member_id | Tìm HLV của hội viên |
| trainer_assignments | `idx_ta_trainer` | trainer_id | Tìm học viên của HLV |
| trainer_assignments | `idx_ta_status` | status | Lọc active/ended |
| training_sessions | `idx_ts_trainer` | trainer_id | Lịch dạy HLV |
| training_sessions | `idx_ts_date` | session_date | Tìm theo ngày |
| attendance | `idx_att_member` | member_id | Lịch sử điểm danh |
| attendance | `idx_att_checkin` | check_in | Tìm theo ngày check-in |
| attendance | `idx_att_method` | method | Thống kê theo phương thức |
| transactions | `idx_tx_member` | member_id | Lịch sử giao dịch |
| transactions | `idx_tx_created` | created_at | Thống kê theo ngày |

---

#### 3.1.3 `app/core/security.py` — Xác thực Admin

**Mục đích:** Kiểm tra thông tin đăng nhập admin.

```python
from app.core.config import ADMIN_USERNAME, ADMIN_PASSWORD

def check_login(username: str, password: str) -> bool:
    """Kiểm tra thông tin đăng nhập. Trả về True nếu hợp lệ."""
    return username.strip() == ADMIN_USERNAME and password == ADMIN_PASSWORD
```

- `username.strip()`: Bỏ khoảng trắng đầu/cuối → người dùng gõ thừa space vẫn đăng nhập được.
- `password` **không strip**: Mật khẩu có thể chứa space ở đầu/cuối theo ý người dùng.
- So sánh plaintext — **chấp nhận cho MVP**, cần chuyển sang bcrypt/hashlib cho production.

**Liên kết:** `gui/admin/login.py` gọi `check_login()` khi user nhấn nút đăng nhập.

**Lưu ý:** User app (hội viên/HLV) KHÔNG dùng `security.py` mà dùng `auth_svc.py` (xem mục 3.4.5).

---

### 3.2 Models Layer

#### 3.2.1 `app/models/base.py` — BaseModel (Lớp nền)

**Mục đích:** Cung cấp các field và method chung cho mọi model.

```python
import uuid
from datetime import datetime

class BaseModel:
    def __init__(self, *args, **kwargs):
        self.id = str(uuid.uuid4())       # Tạo ID duy nhất dạng UUID4
        self.created_at = datetime.now()   # Thời điểm tạo record
        self.updated_at = datetime.now()   # Thời điểm cập nhật gần nhất
        self.is_active = True              # Soft delete flag (True = đang hoạt động)
```

**Tại sao dùng UUID4 thay vì auto-increment?**
- SQLite không có auto-increment kiểu MySQL. UUID đảm bảo ID duy nhất mà không cần DB tự quản.
- Tạo ID trước khi INSERT → không cần query lại để lấy `lastrowid`.

```python
    def update(self):
        """Cập nhật updated_at mỗi khi dữ liệu thay đổi"""
        self.updated_at = datetime.now()

    def delete(self):
        """Xóa ảo (soft delete) — đánh dấu is_active = False"""
        self.is_active = False
        self.update()

    def to_dict(self):
        """Chuyển object → dict, datetime → ISO string"""
        return {
            k: v.isoformat() if isinstance(v, datetime) else v
            for k, v in self.__dict__.items()
        }
```

**Soft Delete pattern:** Không xóa record khỏi database, chỉ đánh dấu `is_active = 0`. Lợi ích:
- Giữ lịch sử dữ liệu (audit trail)
- Có thể khôi phục nếu xóa nhầm
- Không phá vỡ FK ở các bảng liên quan

**Cascade Soft Delete (cập nhật 2026-04-04):** Khi soft delete member/trainer, hệ thống cascade tới subscriptions, assignments, sessions, notifications.

---

#### 3.2.2 `app/models/member.py` — Member

```python
class Member(BaseModel):
    def __init__(self, name, phone, email=None, gender=None,
                 date_of_birth=None, address=None, emergency_contact=None,
                 photo=None, pin="000000", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.phone = phone
        self.email = email
        self.gender = gender                        # 'male' | 'female' | 'other'
        self.date_of_birth = date_of_birth          # datetime.date
        self.address = address
        self.emergency_contact = emergency_contact  # số điện thoại khẩn cấp
        self.photo = photo                          # đường dẫn file ảnh
        self.pin = pin                              # PIN 6 chữ số (đăng nhập user app)
        self.member_code = None                     # Mã hội viên (GYM-YYYYMMDD-XXX)
        self.face_registered = 0                    # Đã đăng ký Face ID (0/1)
        self.photo_path = None                      # Đường dẫn ảnh Face ID
```

| Field | Kiểu | Bắt buộc | Mô tả |
|-------|------|:--------:|-------|
| `name` | str | ✅ | Họ tên — validate ở service |
| `phone` | str | ✅ | SĐT — validate regex, dùng đăng nhập user app |
| `email` | str/None | ❌ | Email — validate regex ở service |
| `gender` | str/None | ❌ | `male`/`female`/`other` |
| `date_of_birth` | str/None | ❌ | Dạng `YYYY-MM-DD` |
| `address` | str/None | ❌ | Địa chỉ |
| `emergency_contact` | str/None | ❌ | Liên hệ khẩn cấp |
| `photo` | str/None | ❌ | Đường dẫn ảnh (chưa implement upload) |
| `pin` | str | ✅ | PIN 6 chữ số, mặc định 000000 |
| `member_code` | str/None | ❌ | Mã hội viên tự tạo |
| `face_registered` | int | ❌ | 0 = chưa, 1 = đã đăng ký Face ID |
| `photo_path` | str/None | ❌ | Đường dẫn ảnh khuôn mặt |

---

#### 3.2.3 `app/models/membership.py` — MembershipPlan + MembershipSubscription

*(Giữ nguyên nội dung từ bản trước — xem mục 3.2.3 bản gốc)*

##### MembershipPlan

```python
class MembershipPlan(BaseModel):
    def __init__(self, name, duration_days, price, description=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name                    # "Gói 1 tháng", "Gói 6 tháng"
        self.duration_days = duration_days  # 30, 90, 180, 365...
        self.price = price                  # VND
        self.description = description
```

##### MembershipSubscription — phức tạp nhất

```python
class MembershipSubscription(BaseModel):
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, member_id, plan_id, duration_days, price_paid,
                 start_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_id = member_id
        self.plan_id = plan_id
        self.price_paid = price_paid

        # Chuẩn hóa start_date
        if start_date is None:
            start_date = datetime.now()
        elif isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        self.start_date = start_date
        self.end_date = self.start_date + timedelta(days=duration_days)
        self.status = self.STATUS_ACTIVE
```

**Methods quan trọng:** `is_expired()`, `days_remaining()`, `cancel()`, `refresh_status()`.

---

#### 3.2.4 `app/models/equipment.py` — Equipment

*(Giữ nguyên nội dung từ bản trước — xem mục 3.2.4 bản gốc)*

```python
class Equipment(BaseModel):
    STATUS_WORKING = "working"
    STATUS_BROKEN = "broken"
    STATUS_MAINTENANCE = "maintenance"

    def __init__(self, name, category, quantity=1,
                 purchase_date=None, location=None, notes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.category = category
        self.quantity = quantity
        self.status = self.STATUS_WORKING
        self.purchase_date = purchase_date
        self.location = location
        self.notes = notes
```

---

#### 3.2.5 `app/models/trainer.py` — Trainer (Huấn luyện viên)

```python
class Trainer(BaseModel):
    def __init__(self, name, phone, email=None, specialization=None,
                 pin="000000", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.phone = phone
        self.email = email
        self.specialization = specialization   # "Yoga", "Boxing", "Gym"
        self.pin = pin                          # PIN 6 chữ số, mặc định 000000
```

| Field | Kiểu | Bắt buộc | Mô tả |
|-------|------|:--------:|-------|
| `name` | str | ✅ | Họ tên HLV — validate ở service |
| `phone` | str | ✅ | SĐT — dùng để đăng nhập user app |
| `email` | str/None | ❌ | Email — validate regex ở service |
| `specialization` | str/None | ❌ | Chuyên môn: Yoga, Boxing, Gym... |
| `pin` | str | ✅ | PIN 6 chữ số — admin set, HLV dùng đăng nhập |

---

#### 3.2.6 `app/models/notification.py` — Notification

**Đặc biệt:** KHÔNG kế thừa `BaseModel`. Thiết kế đơn giản hơn vì notification không cần soft delete hay updated_at.

```python
class Notification:
    def __init__(self, user_id, user_type, title, message):
        self.id = str(uuid.uuid4())
        self.user_id = user_id              # ID member hoặc trainer
        self.user_type = user_type          # "member" hoặc "trainer"
        self.title = title
        self.message = message
        self.is_read = False
        self.created_at = datetime.now()

    def mark_read(self):
        self.is_read = True
```

| Field | Kiểu | Mô tả |
|-------|------|-------|
| `user_id` | str | ID của member hoặc trainer |
| `user_type` | str | `"member"` hoặc `"trainer"` |
| `title` | str | Tiêu đề thông báo |
| `message` | str | Nội dung chi tiết |
| `is_read` | bool | Trạng thái đã đọc |

---

#### 3.2.7 `app/models/trainer_assignment.py` — TrainerAssignment

**Mục đích:** Mô hình hóa mối quan hệ HLV ↔ hội viên, liên kết với subscription.

```python
class TrainerAssignment(BaseModel):
    def __init__(self, member_id, trainer_id, subscription_id=None,
                 start_date=None, notes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_id = member_id
        self.trainer_id = trainer_id
        self.subscription_id = subscription_id
        self.start_date = start_date or datetime.now()
        self.end_date = None                    # None = đang active
        self.status = "active"                  # active/ended
        self.notes = notes
```

| Field | Kiểu | Mô tả |
|-------|------|-------|
| `member_id` | str (FK) | Hội viên được gán |
| `trainer_id` | str (FK) | HLV phụ trách |
| `subscription_id` | str/None (FK) | Gói tập liên kết |
| `start_date` | datetime | Ngày bắt đầu |
| `end_date` | datetime/None | Ngày kết thúc (None = đang active) |
| `status` | str | `"active"` hoặc `"ended"` |
| `notes` | str/None | Ghi chú về học viên |

---

#### 3.2.8 `app/models/training_session.py` — TrainingSession

**Mục đích:** Đại diện cho một buổi tập cụ thể do HLV lên lịch.

```python
class TrainingSession(BaseModel):
    def __init__(self, trainer_id, member_id, session_date,
                 start_time, end_time, content=None,
                 assignment_id=None, notes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trainer_id = trainer_id
        self.member_id = member_id
        self.session_date = session_date        # "YYYY-MM-DD" (string)
        self.start_time = start_time            # "HH:MM"
        self.end_time = end_time                # "HH:MM"
        self.content = content                  # Nội dung buổi tập
        self.assignment_id = assignment_id
        self.status = "scheduled"               # scheduled/completed/cancelled
        self.notes = notes
```

**Lưu ý:** `session_date` lưu dạng string `"YYYY-MM-DD"`, khác với `TrainerAssignment.start_date` lưu datetime. Đây là sự không nhất quán đã được ghi nhận trong báo cáo kiểm tra.

---

#### 3.2.9 `app/models/attendance.py` — Attendance

**Mục đích:** Ghi nhận điểm danh hội viên (check-in/check-out).

```python
class Attendance(BaseModel):
    def __init__(self, member_id, method="face_id", confidence=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_id = member_id
        self.check_in = datetime.now()          # Thời điểm check-in
        self.check_out = None                   # Thời điểm check-out (nullable)
        self.method = method                    # "face_id" / "manual" / "qr_code"
        self.confidence = confidence            # Độ tin cậy nhận diện (0.0-1.0)
```

| Field | Kiểu | Mô tả |
|-------|------|-------|
| `member_id` | str (FK) | Hội viên điểm danh |
| `check_in` | datetime | Thời điểm vào |
| `check_out` | datetime/None | Thời điểm ra (null = chưa check-out) |
| `method` | str | Phương thức: face_id, manual, qr_code |
| `confidence` | float/None | Độ tin cậy nhận diện Face ID (0.0-1.0) |

---

#### 3.2.10 `app/models/transaction.py` — Transaction

**Mục đích:** Ghi nhận giao dịch thanh toán.

```python
class Transaction(BaseModel):
    def __init__(self, member_id, amount, subscription_id=None,
                 payment_method=None, note=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_id = member_id
        self.amount = amount                    # Số tiền (VND)
        self.subscription_id = subscription_id  # Gói tập liên kết (nullable)
        self.payment_method = payment_method    # "cash" / "transfer" / "card"
        self.note = note
```

---

### 3.3 Repositories Layer

**Pattern chung:** Mỗi repository file chứa:
1. `_row_to_model(row)` — chuyển `sqlite3.Row` → Model object (Hydration pattern, dùng `__new__`)
2. `create(model)` — INSERT
3. `get_by_id(id)` — SELECT WHERE id
4. `get_all(active_only)` — SELECT (có filter soft delete)
5. `update(model)` — UPDATE
6. `delete(id)` — Soft delete hoặc hard delete

#### 3.3.1 `app/repositories/member_repo.py`

##### Hàm `_row_to_member(row)` — Hydration pattern

```python
def _row_to_member(row) -> Member:
    m = Member.__new__(Member)    # Tạo instance MÀ KHÔNG gọi __init__
    m.id = row["id"]
    m.name = row["name"]
    # ... (gán tất cả fields bao gồm pin, face_registered, member_code, photo_path)
    m.created_at = datetime.fromisoformat(row["created_at"])
    m.is_active = bool(row["is_active"])
    return m
```

**Tại sao dùng `__new__`?** Bypass `__init__` → giữ nguyên id và timestamps từ DB.

##### Hàm `delete()` — Soft Delete + Cascade (cập nhật 2026-04-04)

```python
def delete(member_id: str):
    with get_db() as conn:
        # Soft delete member
        conn.execute("UPDATE members SET is_active = 0 WHERE id = ?", (member_id,))
        # Cascade: hủy subscriptions, assignments, sessions, notifications
        conn.execute("UPDATE subscriptions SET is_active = 0 WHERE member_id = ?", (member_id,))
        conn.execute("UPDATE trainer_assignments SET is_active = 0 WHERE member_id = ?", (member_id,))
        conn.execute("UPDATE training_sessions SET is_active = 0 WHERE member_id = ?", (member_id,))
        conn.execute("DELETE FROM notifications WHERE user_id = ? AND user_type = 'member'", (member_id,))
```

**Bảo mật:** Tất cả query dùng `?` placeholder → an toàn SQL injection.

---

#### 3.3.2 `app/repositories/membership_repo.py`

File lớn nhất trong repo layer, quản lý cả Plans lẫn Subscriptions.

**Hàm đặc biệt:** `get_expiring_soon(days=7)`, `expire_old_subscriptions()`.

---

#### 3.3.3 `app/repositories/equipment_repo.py`

Thêm `get_by_status()`, `get_by_category()`. Index `idx_equipment_status` tăng tốc filter.

---

#### 3.3.4 `app/repositories/trainer_repo.py`

Tuân thủ cùng pattern, thêm `get_by_phone()` cho đăng nhập user app. Soft delete + cascade tới assignments, sessions, notifications.

---

#### 3.3.5 `app/repositories/notification_repo.py` (MỚI)

```python
def create(notification) → None          # INSERT thông báo
def get_by_user(user_id, user_type) → list  # Lấy theo user (mới nhất trước)
def get_unread_count(user_id, user_type) → int  # Đếm chưa đọc
def mark_read(notification_id) → None    # Đánh dấu đã đọc
def mark_all_read(user_id, user_type)    # Đánh dấu tất cả đã đọc
def has_notification_today(user_id, title) → bool  # Chống trùng lặp
```

**`has_notification_today()`**: Kiểm tra xem đã có thông báo cùng title cho user hôm nay chưa → tránh tạo thông báo hết hạn trùng lặp mỗi lần đăng nhập.

---

#### 3.3.6 `app/repositories/trainer_assignment_repo.py` (MỚI)

```python
def create(assignment) → None
def get_by_id(id) → TrainerAssignment
def get_by_trainer(trainer_id, active_only=True) → list
def get_by_member(member_id, active_only=True) → list
def get_by_subscription(subscription_id) → TrainerAssignment
def update(assignment) → None
def end_assignment(id) → None             # Set status='ended', end_date=now()
def check_duplicate(member_id, trainer_id) → bool  # Tránh gán trùng
```

---

#### 3.3.7 `app/repositories/training_session_repo.py` (MỚI)

```python
def create(session) → None
def get_by_id(id) → TrainingSession
def get_by_trainer_and_week(trainer_id, week_start, week_end) → list
def get_by_member_and_week(member_id, week_start, week_end) → list
def count_by_trainer_month(trainer_id, year, month) → int
def update(session) → None
def delete(id) → None                      # Soft delete (is_active=0)
```

---

#### 3.3.8 `app/repositories/attendance_repo.py` (MỚI)

```python
def create(attendance) → None
def get_today(member_id=None) → list       # Điểm danh hôm nay
def has_checked_in_today(member_id) → bool # Đã check-in chưa
def check_out(attendance_id) → None        # Ghi nhận check-out
def get_history(member_id, limit=50) → list # Lịch sử
def get_by_date_range(from_date, to_date, member_id=None) → list
def count_today() → int                    # Tổng check-in hôm nay
```

---

#### 3.3.9 `app/repositories/transaction_repo.py` (MỚI)

```python
def create(transaction) → None
def get_by_member(member_id, limit=50) → list
def get_all(limit=100) → list
def get_revenue_today() → float            # SUM(amount) hôm nay
def get_revenue_by_range(from_date, to_date) → float
```

---

### 3.4 Services Layer

**Pattern chung:** Service nhận raw input từ GUI → validate → gọi repository → trả model.

#### 3.4.1 `app/services/member_svc.py`

*(Giữ nguyên nội dung từ bản trước)*

Validation regex: phone `[0-9+\-\s]{7,15}`, email `[^@]+@[^@]+\.[^@]+`.

---

#### 3.4.2 `app/services/membership_svc.py`

*(Giữ nguyên nội dung từ bản trước)*

`subscribe_member()`, `get_monthly_revenue()`, `auto_expire_subscriptions()`.

**Cập nhật:** Khi subscribe, nếu có trainer_id trong gói → tự động gán HLV qua `assignment_svc` (bọc trong try/except).

---

#### 3.4.3 `app/services/equipment_svc.py`

*(Giữ nguyên nội dung từ bản trước)*

---

#### 3.4.4 `app/services/trainer_svc.py`

*(Giữ nguyên nội dung từ bản trước)*

`register_trainer()`, `update_trainer()`, `reset_pin()`, `get_trainer_members()`.

---

#### 3.4.5 `app/services/auth_svc.py` (MỚI)

**Mục đích:** Xác thực đăng nhập cho user app (hội viên & HLV).

```python
def login_member(phone: str, pin: str) -> Member:
    """Đăng nhập hội viên bằng SĐT + PIN"""
    if not phone or not phone.strip():
        raise ValueError("Vui lòng nhập số điện thoại")
    if not pin or not pin.strip():
        raise ValueError("Vui lòng nhập PIN")
    phone = phone.strip()
    pin = pin.strip()
    member = member_repo.get_by_phone(phone)
    if not member:
        raise ValueError("Số điện thoại không tồn tại")
    if member.pin != pin:                    # So sánh plaintext (MVP)
        raise ValueError("PIN không đúng")
    return member

def login_trainer(phone: str, pin: str) -> Trainer:
    """Đăng nhập HLV bằng SĐT + PIN"""
    # ... (tương tự login_member, dùng trainer_repo.get_by_phone)

def change_pin(user_type: str, user_id: str, old_pin: str, new_pin: str):
    """Đổi PIN cho member hoặc trainer"""
    if not new_pin or len(new_pin) != 6 or not new_pin.isdigit():
        raise ValueError("PIN mới phải gồm đúng 6 chữ số")
    # Lấy user → kiểm tra old_pin → cập nhật new_pin → save
```

| Hàm | Validate đầu vào | Thiếu |
|-----|-------------------|-------|
| `login_member()` | Rỗng, strip | Định dạng phone, định dạng PIN |
| `login_trainer()` | Rỗng, strip | Tương tự login_member |
| `change_pin()` | new_pin: 6 số, isdigit, khác old | old_pin: không validate định dạng |

---

#### 3.4.6 `app/services/notification_svc.py` (MỚI)

**Mục đích:** Quản lý thông báo + tự động tạo thông báo khi gói tập sắp hết hạn.

```python
def create_notification(user_id, user_type, title, message) → Notification
def get_notifications(user_id, user_type) → list[Notification]
def get_unread_count(user_id, user_type) → int
def mark_read(notification_id) → None
def mark_all_read(user_id, user_type) → None

def check_expiring_subscriptions(member_id):
    """Tự động tạo thông báo khi gói tập sắp hết hạn (≤7 ngày)"""
    subs = membership_repo.get_subscriptions_by_member(member_id)
    for sub in subs:
        if sub.status == "active" and sub.days_remaining() <= 7:
            # Kiểm tra đã có thông báo hôm nay chưa (chống trùng)
            if not notification_repo.has_notification_today(member_id, "Goi tap sap het han!"):
                create_notification(member_id, "member",
                    "Goi tap sap het han!",
                    f"Goi tap cua ban con {sub.days_remaining()} ngay")

def check_trainer_notifications(trainer_id):
    """Tạo thông báo cho HLV khi gói tập học viên sắp hết hạn"""
```

**Trigger:** `check_expiring_subscriptions()` được gọi khi member đăng nhập user app (trong `user_login.py`).

---

#### 3.4.7 `app/services/assignment_svc.py` (MỚI)

**Mục đích:** Quản lý việc gán HLV cho hội viên.

```python
def assign_trainer(member_id, trainer_id, subscription_id=None, notes=None):
    """Gán HLV cho hội viên — kiểm tra trùng lặp trước"""
    if trainer_assignment_repo.check_duplicate(member_id, trainer_id):
        raise ValueError("Hội viên đã được gán cho HLV này")
    assignment = TrainerAssignment(member_id, trainer_id, subscription_id, notes=notes)
    return trainer_assignment_repo.create(assignment)

def end_assignment(assignment_id):
    """Kết thúc assignment — set status='ended', end_date=now()"""

def get_trainer_students(trainer_id) → list
def get_member_trainers(member_id) → list
def update_assignment_notes(assignment_id, notes) → None

def auto_end_expired_assignments():
    """Tự động kết thúc assignments khi subscription hết hạn"""
    # ⚠️ Gọi get_db() trực tiếp — phá vỡ layered architecture
```

**Vấn đề đã ghi nhận:** `auto_end_expired_assignments()` gọi `get_db()` trực tiếp thay vì qua repository — cần refactor.

---

#### 3.4.8 `app/services/schedule_svc.py` (MỚI)

**Mục đích:** Quản lý lịch tập (buổi tập) do HLV lên.

```python
def _validate_date(date_str):     # Validate format YYYY-MM-DD
def _validate_time(time_str):     # Validate format HH:MM, range 0-23:0-59
def _validate_time_range(start, end):  # start < end

def create_session(trainer_id, member_id, session_date, start_time, end_time,
                   content=None, notes=None):
    """Tạo buổi tập mới — validate date/time trước"""
    _validate_date(session_date)
    _validate_time(start_time)
    _validate_time(end_time)
    _validate_time_range(start_time, end_time)
    # ... tạo TrainingSession và lưu

def get_week_sessions(trainer_id, week_start_date) → list
def get_member_week_sessions(member_id, week_start_date) → list
def count_sessions_this_month(trainer_id) → int
def get_week_start(reference_date) → date   # Tính thứ Hai của tuần
```

**Validation chặt chẽ:** Date phải đúng format `YYYY-MM-DD`, time phải `HH:MM` trong khoảng hợp lệ, start_time < end_time.

**Vấn đề:** Không validate ngày trong quá khứ — có thể tạo buổi tập cho ngày đã qua.

---

#### 3.4.9 `app/services/attendance_svc.py` (MỚI)

**Mục đích:** Quản lý điểm danh, tích hợp Face ID.

```python
CHECKIN_COOLDOWN = 30  # Chờ 30 giây giữa 2 lần check-in cùng người

def check_in(member_id, method="face_id", confidence=None):
    """Check-in hội viên — kiểm tra cooldown + subscription active"""
    # 1. Kiểm tra member tồn tại
    # 2. Kiểm tra có subscription active không
    # 3. Kiểm tra cooldown (chống spam)
    # 4. Tạo Attendance record
    attendance = Attendance(member_id, method=method, confidence=confidence)
    attendance_repo.create(attendance)
    return attendance

def check_in_by_face(name_or_id, confidence):
    """Check-in từ kết quả nhận diện khuôn mặt"""
    # Tìm member theo name hoặc id → gọi check_in()

def check_out(member_id):
    """Ghi nhận check-out — cập nhật attendance record gần nhất"""

def get_today_attendance() → list
def get_member_attendance(member_id, limit=50) → list
def get_attendance_by_range(from_date, to_date) → list
def count_today() → int
def get_attendance_stats() → dict
```

**Anti-spam cooldown:** Ngăn check-in trùng lặp trong 30 giây — tránh Face ID nhận diện liên tục ghi nhiều record.

---

#### 3.4.10 `app/services/face_svc.py` (MỚI)

**Mục đích:** Service layer điều phối Face ID — kết nối GUI với module nhận diện.

```python
def _get_recognition_system():    # Singleton FaceRecognitionSystem
def _get_registration_system():   # Singleton FaceRegistration

def register_face(member_id, num_photos=5, camera_id=0):
    """Đăng ký khuôn mặt qua camera — chụp + encode + lưu"""
    reg = _get_registration_system()
    result = reg.register_member(member_id, num_photos, camera_id)
    # Cập nhật member.face_registered = 1

def register_face_from_images(member_id, image_paths):
    """Đăng ký từ ảnh có sẵn (không cần camera)"""

def recognize_frame(frame):
    """Nhận diện khuôn mặt trong frame camera"""
    system = _get_recognition_system()
    return system.recognize_frame(frame)
    # Trả về: [{"name": "member_id", "confidence": 0.85, "bbox": (t,r,b,l)}]

def reload_encodings():
    """Tải lại file encodings sau khi đăng ký mới"""

def remove_face(member_id):
    """Xóa face data của member"""

def get_registration_status(member_id) → bool
def get_registered_count() → int
def encode_all():
    """Rebuild toàn bộ encodings từ ảnh trong data/dataset/"""
```

**Singleton pattern:** `_get_recognition_system()` và `_get_registration_system()` tạo instance một lần, tái sử dụng cho performance (tránh load encodings file mỗi lần gọi).

---

### 3.5 Face ID Layer

**Mục đích tổng thể:** Nhận diện khuôn mặt theo 3 bước: Detection → Encoding → Matching.

#### 3.5.1 `app/face_id/face_encoder.py` — Mã hóa khuôn mặt

```python
class FaceEncoder:
    def __init__(self, model_type="hog"):
        self.model_type = model_type    # "hog" (CPU, nhanh) hoặc "cnn" (GPU, chính xác)

    def encode_face(self, image_path) -> list:
        """Đọc 1 ảnh → trả về vector 128 chiều (face embedding)"""
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        return encodings[0] if encodings else None

    def encode_all_members(self, dataset_dir) -> dict:
        """Duyệt toàn bộ data/dataset/ → encode tất cả ảnh → dict {name: [encodings]}"""

    def save_encodings(self, data, file_path):
        """Lưu encodings ra file pickle (nhị phân, nhanh khi load)"""
        with open(file_path, "wb") as f:
            pickle.dump(data, f)

    @staticmethod
    def load_encodings(file_path) -> dict:
        """Đọc file pickle đã lưu"""
```

**Face Embedding 128 chiều:** Mỗi khuôn mặt được biểu diễn bằng vector 128 số thực. Hai khuôn mặt cùng người có khoảng cách Euclidean nhỏ (<0.6 mặc định).

---

#### 3.5.2 `app/face_id/face_recognizer.py` — Nhận diện real-time

```python
class FaceDetector:
    def detect(self, frame) -> list:
        """Tìm vị trí khuôn mặt trong frame (bounding boxes)"""

    def detect_and_encode(self, frame) -> tuple:
        """Vừa detect vừa encode — tối ưu hơn gọi riêng"""

class FaceRecognitionSystem:
    def __init__(self, tolerance=0.5, model_type="hog"):
        self.tolerance = tolerance      # Ngưỡng (càng nhỏ càng nghiêm ngặt)
        self._load_known_encodings()    # Load từ file pickle

    def recognize_frame(self, frame) -> list[dict]:
        """Nhận diện khuôn mặt → trả về [{name, confidence, bbox}]"""
        # 1. Resize frame 50% (tối ưu hiệu năng)
        # 2. Detect + encode khuôn mặt trong frame
        # 3. So sánh với known encodings bằng Euclidean distance
        # 4. Nếu distance < tolerance → match
        # 5. Confidence = 1 - distance (càng cao càng chắc chắn)

    def reload_encodings(self):
        """Tải lại known faces sau khi đăng ký mới"""
```

**Tối ưu hiệu năng:**
- Resize frame 50% trước khi xử lý
- Xử lý mỗi 2-3 frame (không phải mọi frame)
- Dùng model "hog" cho CPU (nhanh) thay vì "cnn" (cần GPU)

---

#### 3.5.3 `app/face_id/face_register.py` — Đăng ký khuôn mặt

```python
class FaceRegistration:
    def capture_faces(self, member_id, num_photos=5, camera_id=0):
        """Mở camera, chụp ảnh với giao diện HUD"""
        # SPACE = chụp thủ công
        # A = auto-capture (1.5s/lần)
        # Q = hoàn tất
        # Tự động crop khuôn mặt + padding 30%

    def register_member(self, member_id, num_photos=5, camera_id=0):
        """Quy trình đăng ký hoàn chỉnh: chụp → encode → cập nhật pickle"""

    def register_from_images(self, member_id, image_paths):
        """Đăng ký từ ảnh có sẵn (không cần camera)"""

    def remove_member(self, member_id):
        """Xóa member khỏi file encodings"""

    def list_members(self) -> list:
        """Liệt kê member đã đăng ký"""
```

**Lưu trữ dữ liệu Face ID:**
- `data/dataset/{member_id}/` — Ảnh gốc (5-10 ảnh mỗi member)
- `data/encodings/face_encodings.pkl` — Vector encodings (pickle, load nhanh)

---

#### 3.5.4 `app/face_id/image_processing.py` — Tiện ích xử lý ảnh

Hàm tiện ích: vẽ bounding box, resize frame, convert BGR↔RGB (OpenCV dùng BGR, face_recognition dùng RGB).

---

### 3.6 GUI Admin Layer

#### 3.6.1 `app/main.py` — Entry Point + Router (Admin)

*(Giữ nguyên pattern từ bản trước, cập nhật routes mới)*

```python
def navigate(route: str):
    page.overlay.clear()
    page.controls.clear()
    page.on_search_change = None
    if route == "login":
        from gui.admin.login import LoginScreen
        page.add(LoginScreen(page))
    elif route == "dashboard":
        from gui.admin.dashboard import DashboardScreen
        page.add(DashboardScreen(page))
    elif route == "attendance":                    # MỚI
        from gui.admin.attendance import AttendanceScreen
        page.add(AttendanceScreen(page))
    elif route == "face_register":                 # MỚI
        from gui.admin.face_register import FaceRegisterScreen
        page.add(FaceRegisterScreen(page))
    # ... các route khác
    page.update()
```

---

#### 3.6.2 `gui/theme.py` — Design System

*(Giữ nguyên nội dung từ bản trước)*

| Nhóm | Hằng số | Ví dụ | Ý nghĩa |
|------|---------|-------|---------|
| **Colors** | `ORANGE` | `#F97316` | Primary action, brand color |
| | `GREEN/GREEN_LIGHT` | `#22C55E / #DCFCE7` | Trạng thái tốt (active, working) |
| | `AMBER/AMBER_LIGHT` | `#F59E0B / #FEF3C7` | Cảnh báo (sắp hết hạn, bảo trì) |
| | `RED/RED_LIGHT` | `#EF4444 / #FEE2E2` | Nguy hiểm (hỏng, quá hạn, xóa) |
| | `SIDEBAR_BG` | `#1C1C2E` | Dark navy cho sidebar |
| **Typography** | `FONT_XS→FONT_3XL` | 11→28px | 7 cấp font size |
| **Spacing** | `PAD_XS→PAD_2XL` | 4→24px | 6 cấp padding |

---

#### 3.6.3 `gui/admin/components/sidebar.py` — Sidebar điều hướng

**Layout cập nhật (thêm 2 menu mới):**

```
┌──────────────────────┐
│ [P] GymAdmin         │  ← Logo section
│ MANAGEMENT SYSTEM    │
├──────────────────────┤  ← Divider
│ ◉ Dashboard          │  ← Nav items (8 items → thêm 2 mới)
│ ○ Members            │
│ ○ Gym Packages       │
│ ○ Equipment          │
│ ○ Trainers           │
│ ○ Attendance         │  ← MỚI (icon: FACT_CHECK)
│ ○ Face Register      │  ← MỚI (icon: FACE)
│ ○ Reports            │
│                      │
│ [+ Add Member]       │  ← Quick action button
└──────────────────────┘
```

---

#### 3.6.4 `gui/admin/attendance.py` — Điểm danh bằng Face ID (MỚI — 498 dòng)

**Layout:**

```
┌──────────┬──────────────────────────────────────────────────┐
│ SIDEBAR  │  Header                                          │
│          │  ──────────────────────────────────────────────── │
│          │  ┌──────────────────┐  ┌───────────────────────┐ │
│          │  │  Camera Feed     │  │  Kết quả nhận diện    │ │
│          │  │  (placeholder)   │  │  Tên: Nguyễn Văn A    │ │
│          │  │  [Mở Camera]     │  │  Confidence: 85%      │ │
│          │  │  [Đóng Camera]   │  │  Trạng thái: ✅       │ │
│          │  └──────────────────┘  └───────────────────────┘ │
│          │                                                   │
│          │  ┌──── Thống kê hôm nay ────────────────────────┐│
│          │  │ Check-in: 23  │  Face ID: 18  │  Thủ công: 5 ││
│          │  └──────────────────────────────────────────────┘│
│          │                                                   │
│          │  ┌──── Check-in thủ công ───────────────────────┐│
│          │  │ [Nhập SĐT hội viên]  [Check-in]             ││
│          │  └──────────────────────────────────────────────┘│
│          │                                                   │
│          │  ┌──── Bảng điểm danh hôm nay ─────────────────┐│
│          │  │ Hội viên │ Check-in │ Check-out │ Phương thức││
│          │  │ Tuấn     │ 08:30    │ 10:15     │ face_id    ││
│          │  │ Minh     │ 09:00    │ —         │ manual     ││
│          │  └──────────────────────────────────────────────┘│
└──────────┴──────────────────────────────────────────────────┘
```

**Kỹ thuật quan trọng:**

```python
async def listen_camera_results():
    """Async loop — poll bridge.get_result() mỗi 200ms"""
    while camera_running:
        result = bridge.get_result()
        if result:
            if result["type"] == "recognition":
                # Gọi attendance_svc.check_in_by_face()
                # Cập nhật UI hiển thị kết quả
            elif result["type"] == "unknown_face":
                # Hiện "Không nhận diện được"
        await asyncio.sleep(0.2)
```

**Camera chạy trong subprocess riêng** (qua `bridge.py`) → không block Flet event loop.

**Fallback thủ công:** Khi camera không hoạt động hoặc không nhận diện được, admin nhập SĐT hội viên → check-in method="manual".

---

#### 3.6.5 `gui/admin/face_register.py` — Đăng ký khuôn mặt (MỚI — 388 dòng)

**Layout:**

```
┌──────────┬──────────────────────────────────────────────────┐
│ SIDEBAR  │  Header                                          │
│          │  ──────────────────────────────────────────────── │
│          │  Đăng ký khuôn mặt                               │
│          │  ┌─────────────────┐  ┌────────────────────────┐ │
│          │  │ Danh sách HV    │  │  Thông tin hội viên    │ │
│          │  │ [🔍 Tìm kiếm]  │  │  Tên: Nguyễn Văn A    │ │
│          │  │ ✅ Tuấn (đã ĐK)│  │  SĐT: 0912345678      │ │
│          │  │ ❌ Minh (chưa) │  │  Face ID: Chưa đăng ký │ │
│          │  │ ❌ Lan  (chưa) │  │                        │ │
│          │  └─────────────────┘  │  [Camera Placeholder]  │ │
│          │                       │  ████████░░ 60%        │ │
│          │                       │                        │ │
│          │                       │  [Mở Camera] [Xóa FID] │ │
│          │                       └────────────────────────┘ │
└──────────┴──────────────────────────────────────────────────┘
```

**Flow đăng ký:**
1. Admin chọn member từ danh sách (filter: chưa đăng ký face)
2. Nhấn "Mở Camera" → bridge mở camera subprocess ở mode "register"
3. Camera hiển thị hướng dẫn đặt mặt trong khung oval
4. Chụp 5-10 ảnh (tự động hoặc thủ công)
5. Progress bar cập nhật theo `register_progress` messages
6. Hoàn thành → encode faces → lưu pickle → cập nhật `member.face_registered = 1`

---

#### 3.6.6-3.6.11 Các màn hình Admin khác

*(Giữ nguyên nội dung chi tiết từ bản trước cho: login.py, dashboard.py, members.py, memberships.py, equipment.py, trainers.py, reports.py)*

**Tóm tắt thay đổi so với bản trước:**
- `dashboard.py`: Thêm widget "Điểm danh hôm nay" (số lượng check-in)
- `sidebar.py`: Thêm 2 menu: "Attendance" và "Face Register"
- Các màn hình khác: Giữ nguyên chức năng

---

### 3.7 GUI User Layer

#### 3.7.1 `app/user_main.py` — Entry Point + Router (User App)

```python
def main(page: ft.Page):
    init_db()

    page.title = "GymFit Member App"
    page.window_width = 1100     # Nhỏ hơn admin (1280)
    page.window_height = 700     # Nhỏ hơn admin (800)
    page.bgcolor = "#F5F5F5"
    page.padding = 0

    # Auth state trên page object
    page.current_user = None     # Member hoặc Trainer object
    page.current_role = None     # "member" hoặc "trainer"

    def navigate(route: str):
        page.overlay.clear()
        page.controls.clear()
        if route == "login":
            page.current_user = None     # Reset auth state
            page.current_role = None
            from gui.user.user_login import LoginScreen
            page.add(LoginScreen(page))
        elif route == "dashboard":
            from gui.user.user_dashboard import DashboardScreen
            page.add(DashboardScreen(page))
        # ... 13 routes khác (xem Navigation Flow mục 2.3)
        page.update()

    page.navigate = navigate
    navigate("login")

ft.run(main)
```

**Khác biệt với Admin:**
- Window nhỏ hơn (1100x700 vs 1280x800)
- Có auth state (`current_user`, `current_role`) trên page object
- Logout reset auth state về None
- 14 routes (vs 9 routes admin)

---

#### 3.7.2 `gui/user/user_login.py` — Đăng nhập hội viên/HLV (227 dòng)

**Layout:**

```
┌─────────────────────────────────────────┐
│          (gradient background)          │
│                                         │
│         ┌─────────────────────┐         │
│         │      GymFit         │         │
│         │   MEMBER APP        │         │
│         │                     │         │
│         │  [Hội viên] [HLV]   │  ← Role toggle
│         │                     │         │
│         │  [📱 Số điện thoại] │  ← input_filter: digits only
│         │  [🔒 Mã PIN      ] │  ← max_length=6, digits only
│         │  (error message)    │         │
│         │  [  Đăng nhập  ]    │         │
│         └─────────────────────┘         │
│                                         │
└─────────────────────────────────────────┘
```

**Kỹ thuật quan trọng:**

```python
# Role toggle — 2 nút chuyển đổi
role = {"value": "member"}   # Default: hội viên

def toggle_role(new_role):
    role["value"] = new_role
    # Cập nhật visual: nút active = cam, nút inactive = xám

# Input validation tại GUI (cập nhật 2026-04-04)
phone_field = ft.TextField(
    input_filter=ft.InputFilter.digits_only,   # Chỉ cho phép số
    max_length=11,
)
pin_field = ft.TextField(
    input_filter=ft.InputFilter.digits_only,
    max_length=6,
    password=True,
    can_reveal_password=True,
)

def do_login(e):
    phone = phone_field.value.strip()
    pin = pin_field.value.strip()
    # Validate: phone 9-11 số, PIN đúng 6 số
    try:
        if role["value"] == "member":
            user = auth_svc.login_member(phone, pin)
            page.current_role = "member"
            # Trigger kiểm tra thông báo hết hạn
            notification_svc.check_expiring_subscriptions(user.id)
        else:
            user = auth_svc.login_trainer(phone, pin)
            page.current_role = "trainer"
            notification_svc.check_trainer_notifications(user.id)
        page.current_user = user
        page.navigate("dashboard" if role["value"] == "member" else "trainer")
    except ValueError as ex:
        error_text.value = str(ex)
```

**Guard clause trên mọi screen (cập nhật 2026-04-04):**

```python
def DashboardScreen(page):
    current_user = getattr(page, "current_user", None)
    navigate = getattr(page, "navigate", None)
    if not current_user:
        if navigate: navigate("login")
        return ft.Container()
    # ... render screen
```

---

#### 3.7.3 `gui/user/user_dashboard.py` — Dashboard hội viên (204 dòng)

**Layout:**

```
┌──────────────┬───────────────────────────────────────────┐
│  UserSidebar │  Chào mừng, Nguyễn Văn A!                │
│              │                                           │
│  ◉ Dashboard │  ┌── Gói tập hiện tại ─────────────────┐ │
│  ○ Hồ sơ    │  │ Gói 3 tháng        Còn 45 ngày      │ │
│  ○ Lịch tập │  │ ████████████████░░░ 50%              │ │
│  ○ Gói tập  │  └──────────────────────────────────────┘ │
│  ○ Lịch sử  │                                           │
│  ○ Điểm danh│  ┌── Điểm danh gần đây ────────────────┐ │
│  ○ Thông báo│  │ 08/04 — 08:30 (face_id, 92%)        │ │
│              │  │ 07/04 — 09:15 (manual)               │ │
│  [Đăng xuất]│  └──────────────────────────────────────┘ │
│              │                                           │
│              │  ┌── Thao tác nhanh ───────────────────┐ │
│              │  │ [Gói tập] [Lịch sử] [Hồ sơ]        │ │
│              │  └──────────────────────────────────────┘ │
└──────────────┴───────────────────────────────────────────┘
```

---

#### 3.7.4 `gui/user/components/user_sidebar.py` — Sidebar user (168 dòng)

**Menu động theo role:**

```python
def UserSidebar(page, active_route):
    role = getattr(page, "current_role", "member")

    if role == "member":
        nav_items = [
            ("dashboard", "Dashboard", ft.Icons.DASHBOARD),
            ("profile", "Hồ sơ", ft.Icons.PERSON),
            ("schedule", "Lịch tập", ft.Icons.CALENDAR_MONTH),
            ("membership", "Gói tập", ft.Icons.CARD_MEMBERSHIP),
            ("history", "Lịch sử", ft.Icons.HISTORY),
            ("attendance_history", "Điểm danh", ft.Icons.FACT_CHECK),
            ("notifications", "Thông báo", ft.Icons.NOTIFICATIONS),
        ]
    else:  # trainer
        nav_items = [
            ("trainer", "Dashboard", ft.Icons.DASHBOARD),
            ("trainer_students", "Học viên", ft.Icons.PEOPLE),
            ("trainer_schedule", "Lịch dạy", ft.Icons.CALENDAR_MONTH),
            ("trainer_profile", "Hồ sơ", ft.Icons.PERSON),
            ("trainer_notifications", "Thông báo", ft.Icons.NOTIFICATIONS),
        ]
```

**Badge thông báo:** Menu "Thông báo" hiện badge đỏ số thông báo chưa đọc.

**Đăng xuất:** Reset `page.current_user = None` + navigate("login").

---

#### 3.7.5 `gui/user/user_profile.py` — Hồ sơ cá nhân + Đổi PIN

**Chức năng:**
- Hiển thị thông tin cá nhân (tên, SĐT, email, giới tính)
- Form đổi PIN: PIN cũ → PIN mới → Xác nhận PIN mới
- Input filter digits only + validate 6 số trước khi gửi service

---

#### 3.7.6 `gui/user/user_membership.py` — Gói tập

**Chức năng:**
- Hiện gói tập đang active + days remaining
- Danh sách gói tập có thể đăng ký
- Nút đăng ký → gọi `membership_svc.subscribe_member()`

---

#### 3.7.7 `gui/user/user_schedule.py` — Lịch tập hội viên

**Chức năng:** Hiển thị lịch tập tuần (buổi tập được HLV lên lịch).

---

#### 3.7.8 `gui/user/user_history.py` — Lịch sử gói tập

**Chức năng:** Danh sách tất cả subscription (active/expired/cancelled) với tên gói, ngày, giá.

---

#### 3.7.9 `gui/user/user_attendance.py` — Lịch sử điểm danh

**Chức năng:** Bảng lịch sử check-in/check-out với phương thức (face_id/manual) và confidence.

---

#### 3.7.10 `gui/user/user_checkin.py` — Check-in bằng khuôn mặt

**Chức năng:** User tự check-in bằng camera Face ID — sử dụng bridge.py giống admin attendance.

---

#### 3.7.11 `gui/user/user_notifications.py` — Thông báo hội viên

**Chức năng:**
- Danh sách thông báo (mới nhất trước)
- Đánh dấu đã đọc (từng thông báo hoặc tất cả)
- Tự động tạo thông báo khi gói sắp hết hạn ≤7 ngày

---

#### 3.7.12 `gui/user/trainer_dashboard.py` — Dashboard HLV

**Chức năng:**
- Hiện thông tin cá nhân HLV (tên, SĐT, chuyên môn)
- Danh sách học viên active
- Thống kê: số học viên, số buổi tập tháng này

---

#### 3.7.13 `gui/user/trainer_schedule.py` — Lịch dạy HLV

**Chức năng:**
- Xem lịch dạy theo tuần (chuyển tuần trước/sau)
- Tạo buổi tập mới: chọn học viên, ngày, giờ bắt đầu/kết thúc, nội dung
- Sửa/xóa buổi tập
- Validate date/time chặt chẽ qua `schedule_svc`

**DAY_NAMES có dấu:** Thứ Hai, Thứ Ba, ... (đã sửa từ không dấu).

---

#### 3.7.14 `gui/user/trainer_students.py` — Danh sách học viên

**Chức năng:**
- Tìm kiếm học viên
- Xem thông tin chi tiết: tên, gói tập, ngày hết hạn
- Ghi chú cho từng học viên (max_length=500)

---

#### 3.7.15 `gui/user/trainer_profile.py` — Hồ sơ HLV + Đổi PIN

**Chức năng:** Tương tự user_profile nhưng cho trainer. Input filter digits only cho PIN.

---

#### 3.7.16 `gui/user/trainer_notifications.py` — Thông báo HLV

**Chức năng:** Tương tự user_notifications. HLV nhận thông báo khi gói tập học viên sắp hết hạn.

---

### 3.8 Bridge & Camera Module

#### 3.8.1 `bridge.py` — IPC Bridge (121 dòng)

**Mục đích:** Cầu nối giữa Flet (main process) và camera (subprocess) qua multiprocessing.Queue.

```python
from multiprocessing import Process, Queue

class CameraBridge:
    def __init__(self):
        self.command_queue = Queue()      # Flet → Camera (mở/đóng)
        self.result_queue = Queue()       # Camera → Flet (kết quả nhận diện)
        self.camera_process = None

    def open_camera(self, mode="recognize", **kwargs):
        """Spawn camera subprocess"""
        self._clear_queue(self.result_queue)
        self.camera_process = Process(
            target=camera_module.run_camera,
            args=(self.command_queue, self.result_queue, mode),
            kwargs=kwargs,
            daemon=True
        )
        self.camera_process.start()

    def close_camera(self):
        """Gửi lệnh đóng camera + terminate process nếu cần"""

    def get_result(self):
        """Non-blocking dequeue — trả None nếu queue rỗng"""
        try:
            return self.result_queue.get_nowait()
        except:
            return None

    def is_camera_running(self) -> bool:
        return self.camera_process and self.camera_process.is_alive()

# Singleton pattern
_bridge_instance = None
def get_bridge():
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = CameraBridge()
    return _bridge_instance
```

**Message Protocol (dict-based):**

| Type | Direction | Dữ liệu | Mô tả |
|------|-----------|----------|-------|
| `recognition` | Camera → Flet | `member_id`, `confidence` | Nhận diện thành công |
| `unknown_face` | Camera → Flet | — | Có mặt nhưng không nhận ra |
| `register_progress` | Camera → Flet | `current`, `total` | Tiến độ chụp ảnh |
| `register_complete` | Camera → Flet | `member_id`, `photos` | Đăng ký hoàn thành |
| `register_failed` | Camera → Flet | `captured` | Đăng ký thất bại |
| `camera_error` | Camera → Flet | `message` | Lỗi camera |
| `camera_closed` | Camera → Flet | — | Camera đã đóng |

---

#### 3.8.2 `camera_module.py` — CustomTkinter Camera Window

**Mục đích:** Cửa sổ camera chạy trong subprocess, xử lý face recognition/registration.

```python
import customtkinter as ctk
import cv2
import threading

class CameraWindow(ctk.CTk):
    def __init__(self, command_queue, result_queue, mode="recognize", **kwargs):
        super().__init__()
        self.mode = mode                 # "recognize" hoặc "register"
        self.result_queue = result_queue

    def draw_face_guide(self):
        """Vẽ khung oval hướng dẫn đặt mặt"""

    def is_face_in_guide_zone(self, face_location):
        """Kiểm tra khuôn mặt nằm trong khung hướng dẫn"""
```

**2 chế độ hoạt động:**
- **"recognize"**: Nhận diện liên tục → gửi kết quả qua result_queue
- **"register"**: Chụp N ảnh → gửi progress → hoàn thành/thất bại

**Threading:** Camera capture + face processing chạy trên thread riêng → GUI CustomTkinter vẫn responsive.

**Tại sao CustomTkinter mà không dùng Flet?**
- Flet không có native camera component — chỉ hiển thị ảnh static qua `ft.Image`.
- CustomTkinter + OpenCV có thể render video frame trực tiếp lên canvas.
- Chạy trong subprocess → không conflict với Flet event loop.

---

## 4. Phân tích luồng dữ liệu

### 4.1 Luồng "Thêm hội viên mới" (Admin)

```
1. User click "+ Thêm hội viên"
   │
2. open_add_dialog() → clear form → set dialog title → dialog.open = True
   │
3. User điền form → click "Lưu"
   │
4. save_member() → gọi member_svc.register_member(name, phone, ...)
   │
5. member_svc._validate(name, phone, email) → regex check
   │  ↓ Lỗi: raise ValueError → dialog_error.value = str(ex) → hiện lỗi
   │  ↓ OK: tiếp
6. Member(name, phone, ...) → tạo object với UUID mới, PIN mặc định "000000"
   │
7. member_repo.create(member) → INSERT INTO members VALUES (...)
   │
8. dialog.open = False → refresh_table() → đọc lại từ DB → render bảng mới
```

### 4.2 Luồng "Đăng nhập User App" (Hội viên)

```
1. User mở user app → hiện LoginScreen
   │
2. Chọn role "Hội viên" → nhập SĐT + PIN → nhấn "Đăng nhập"
   │
3. do_login() → validate GUI (9-11 số, PIN 6 số)
   │  ↓ Sai format: hiện lỗi tại GUI (không gọi service)
   │  ↓ OK: tiếp
4. auth_svc.login_member(phone, pin)
   │  ↓ SĐT không tồn tại: raise ValueError
   │  ↓ PIN sai: raise ValueError
   │  ↓ OK: trả Member object
5. page.current_user = member
   page.current_role = "member"
   │
6. notification_svc.check_expiring_subscriptions(member.id)
   │  → Nếu gói sắp hết hạn ≤7 ngày → tạo notification (chống trùng)
   │
7. page.navigate("dashboard") → hiện DashboardScreen
```

### 4.3 Luồng "Đăng ký khuôn mặt" (Admin)

```
1. Admin mở Face Register screen
   │
2. Chọn member chưa đăng ký face từ danh sách
   │
3. Nhấn "Mở Camera" → bridge.open_camera(mode="register", member_id=...)
   │
4. Camera subprocess khởi động:
   │  ├── Hiện cửa sổ CustomTkinter với khung oval hướng dẫn
   │  ├── Chờ khuôn mặt nằm trong khung
   │  └── Auto-capture mỗi 1.5s (hoặc SPACE thủ công)
   │
5. Mỗi ảnh chụp xong:
   │  ├── Crop khuôn mặt + padding 30%
   │  ├── Lưu vào data/dataset/{member_id}/
   │  └── result_queue.put({"type": "register_progress", "current": 3, "total": 5})
   │
6. Flet poll result_queue → cập nhật progress bar
   │
7. Đủ ảnh → encode tất cả → cập nhật face_encodings.pkl
   │  └── result_queue.put({"type": "register_complete", "member_id": "..."})
   │
8. Flet nhận complete → cập nhật member.face_registered = 1
   │                   → reload_encodings() cho recognition system
   │                   → refresh danh sách
```

### 4.4 Luồng "Điểm danh bằng Face ID" (Admin)

```
1. Admin mở Attendance screen → nhấn "Mở Camera"
   │
2. bridge.open_camera(mode="recognize") → spawn camera subprocess
   │
3. Camera subprocess:
   │  ├── OpenCV capture frame liên tục
   │  ├── Resize 50% → detect faces → encode → compare với known encodings
   │  ├── Match (distance < tolerance):
   │  │   └── result_queue.put({"type": "recognition", "member_id": "...", "confidence": 0.85})
   │  └── No match:
   │      └── result_queue.put({"type": "unknown_face"})
   │
4. Flet async listen_camera_results():
   │  ├── Nhận "recognition" → attendance_svc.check_in_by_face(member_id, confidence)
   │  │   ├── Kiểm tra subscription active
   │  │   ├── Kiểm tra cooldown (30s)
   │  │   ├── Tạo Attendance record (method="face_id")
   │  │   └── Hiện thông tin: tên, ảnh, trạng thái
   │  └── Nhận "unknown_face" → hiện "Không nhận diện được"
   │
5. Fallback: Admin nhập SĐT → check_in(member_id, method="manual")
```

### 4.5 Luồng "HLV tạo buổi tập"

```
1. HLV mở Trainer Schedule screen → nhấn "Thêm buổi tập"
   │
2. Chọn: học viên, ngày, giờ bắt đầu/kết thúc, nội dung
   │
3. save_session() → schedule_svc.create_session(trainer_id, member_id, ...)
   │
4. Validate:
   │  ├── _validate_date("2026-04-10") → OK
   │  ├── _validate_time("08:00") → OK
   │  ├── _validate_time("09:30") → OK
   │  └── _validate_time_range("08:00", "09:30") → OK (start < end)
   │
5. TrainingSession(trainer_id, member_id, ...) → tạo object
   │
6. training_session_repo.create(session) → INSERT INTO training_sessions
   │
7. Refresh lịch tuần → hiện buổi tập mới
```

### 4.6 Luồng "Auto-expire subscriptions"

```
1. User mở tab "Đăng ký" trên Memberships screen
   │
2. refresh_subs() gọi → membership_svc.auto_expire_subscriptions()
   │
3. membership_repo.expire_old_subscriptions()
   │
4. SQL: UPDATE subscriptions SET status='expired'
        WHERE status='active' AND end_date < NOW()
   │
5. Tất cả subscription quá hạn tự đổi thành "expired"
```

### 4.7 Luồng "Thông báo tự động khi gói sắp hết hạn"

```
1. Member đăng nhập user app thành công
   │
2. notification_svc.check_expiring_subscriptions(member_id)
   │
3. Lấy tất cả subscription active của member
   │
4. Với mỗi sub có days_remaining() ≤ 7:
   │  ├── Kiểm tra has_notification_today() → chống trùng
   │  └── Tạo notification: "Goi tap sap het han! Con X ngay"
   │
5. Member mở tab Thông báo → thấy thông báo mới
   │  ├── Đánh dấu đã đọc
   │  └── Badge đỏ trên sidebar giảm
```

---

## 5. Đánh giá kỹ thuật

### 5.1 Điểm mạnh

| # | Điểm mạnh | Chi tiết |
|---|-----------|---------|
| 1 | **Kiến trúc phân tầng rõ ràng** | Models → Repositories → Services → GUI. Mỗi tầng có trách nhiệm riêng, dễ maintain |
| 2 | **2 ứng dụng, 1 backend** | Admin + User app dùng chung services/repos/models, tránh duplicate code |
| 3 | **Face ID tích hợp hoàn chỉnh** | Detection → Encoding → Matching, với multiprocessing IPC cho camera |
| 4 | **Design System nhất quán** | `theme.py` tập trung tokens → UI đồng nhất cả Admin + User |
| 5 | **Soft Delete + Cascade** | Không mất dữ liệu khi xóa, cascade tới bảng liên quan |
| 6 | **SQL Injection safe** | Tất cả query dùng parameterized `?` placeholder |
| 7 | **Transaction safe** | Context manager `get_db()` đảm bảo commit/rollback |
| 8 | **Validation tập trung** | Service layer validate trước khi ghi DB |
| 9 | **Guard clause trên mọi screen** | User app kiểm tra current_user → redirect login nếu None |
| 10 | **Anti-spam cooldown** | Check-in Face ID có cooldown 30s chống ghi trùng |
| 11 | **Notification deduplication** | Không tạo thông báo trùng lặp cùng ngày |
| 12 | **Observer pattern cho search** | Header search → callback → active screen filter |

### 5.2 Điểm cần cải thiện

| # | Vấn đề | Mức độ | Gợi ý |
|---|--------|:------:|-------|
| 1 | **Plaintext password/PIN** | ⚠️ Nghiêm trọng | Dùng `bcrypt` hoặc `hashlib.pbkdf2_hmac` |
| 2 | **Credentials admin hardcoded** | ⚠️ Nghiêm trọng | Bắt buộc env var, không fallback yếu |
| 3 | **Không kiểm tra role** | ⚠️ Nghiêm trọng | Member có thể truy cập route trainer nếu biết tên |
| 4 | **Không có tests** | ⚠️ Cao | Cần ít nhất unit test cho services |
| 5 | **Không giới hạn đăng nhập sai** | Cao | Brute force PIN 6 số rất nhanh |
| 6 | **So sánh PIN không constant-time** | Cao | Dùng `hmac.compare_digest()` chống timing attack |
| 7 | **Không có pagination** | Trung bình | OK cho <500 records, cần khi data lớn |
| 8 | **Datetime vs String không nhất quán** | Trung bình | TrainingSession.session_date là string, khác datetime ở models khác |
| 9 | **assignment_svc gọi DB trực tiếp** | Trung bình | Phá vỡ layered architecture |
| 10 | **Thiếu max_length nhiều TextField** | Trung bình | Name, description không giới hạn |
| 11 | **Tiếng Việt không dấu** | Trung bình | Một số service/GUI dùng tiếng Việt không dấu |
| 12 | **Stub files chưa dọn** | Thấp | `payment_svc.py`, `app/api/` rỗng |
| 13 | **app_state.py không còn dùng** | Thấp | Nên xóa hoặc cập nhật |

### 5.3 Đánh giá theo tiêu chuẩn

| Tiêu chí | Đánh giá | Ghi chú |
|----------|:--------:|---------|
| **Separation of Concerns** | ★★★★★ | Rõ ràng: GUI / Service / Repo / Model / FaceID |
| **Consistent Design Tokens** | ★★★★★ | Tất cả dùng theme.py |
| **Component Reusability** | ★★★★☆ | Sidebar + Header reusable, guard clause nhất quán |
| **Error Handling** | ★★★★☆ | Service validate, GUI hiện lỗi; thiếu try/except một số nơi |
| **State Management** | ★★★☆☆ | Dict-based + page object — hoạt động nhưng không scale tốt |
| **AI Integration** | ★★★★☆ | Face ID hoạt động, multiprocessing IPC tốt |
| **Security** | ★★★☆☆ | SQL injection safe, plaintext PIN, thiếu rate limit |
| **Performance** | ★★★☆☆ | Camera tối ưu (resize, skip frame), DB cần pagination |
| **Testing** | ★☆☆☆☆ | Không có tests |
| **Documentation** | ★★★★★ | Comment tiếng Việt chi tiết, báo cáo kỹ thuật đầy đủ |

---

## 6. Lịch sử thay đổi & sửa lỗi

### 2026-04-04 — Cascade soft delete + Guard clause + Constraints

| # | Thay đổi | Files |
|---|----------|-------|
| 1 | ✅ Soft delete + cascade member | `member_repo.py` → subscriptions, assignments, sessions, notifications |
| 2 | ✅ Soft delete + cascade trainer | `trainer_repo.py` → assignments, sessions, notifications |
| 3 | ✅ Guard clause current_user trên 11 screen user | Tất cả `gui/user/` (trừ login) |
| 4 | ✅ CHECK constraint PIN (6 ký tự) | `database.py` — members + trainers |
| 5 | ✅ UNIQUE constraint phone | `database.py` — members + trainers (CREATE + migration) |
| 6 | ✅ Input filter digits only cho PIN | `user_login.py`, `user_profile.py`, `trainer_profile.py` |
| 7 | ✅ max_length=500 cho notes/content | `trainer_students.py`, `trainer_schedule.py` |

### 2026-03-26 — Search bar + Hard delete fix

| # | Thay đổi | Files |
|---|----------|-------|
| 1 | ✅ Chuyển sang `ft.SearchBar` chuẩn | `header.py`, `members.py` |
| 2 | ✅ Sửa xóa hội viên (hard → soft delete) | `member_repo.py` |

### 2026-03-22 — Comment tiếng Việt

| # | Thay đổi | Files |
|---|----------|-------|
| 1 | ✅ Thêm comment tiếng Việt chi tiết | 23 file source code |

### 2026-03-20 — MVP hoàn thành

| # | Thay đổi | Files |
|---|----------|-------|
| 1 | ✅ Tạo màn hình đăng nhập admin | `login.py`, `security.py`, `config.py` |
| 2 | ✅ Hoàn thành CRUD Members, Memberships, Equipment | Toàn bộ GUI admin |
| 3 | ✅ Dashboard với KPI, biểu đồ doanh thu | `dashboard.py` |
| 4 | ✅ Fix vấn đề từ Code Review (7 mục) | `database.py`, `main.py`, `member_svc.py`, `requirements.txt` |
| 5 | ✅ Thêm field photo (Member), location (Equipment) | Models + repos + GUI |
| 6 | ✅ Filter giới tính + subscription trên Members | `members.py` |
| 7 | ✅ Section sắp hết hạn trên Dashboard | `dashboard.py` |
| 8 | ✅ Nút hủy subscription + confirm dialog | `memberships.py` |

---

## 7. Tổng kết

### 7.1 Bảng tóm tắt file & dòng code

| Tầng | File | Dòng code (ước tính) | Trạng thái |
|------|------|:-------------------:|:----------:|
| **Core** | `config.py` | ~30 | ✅ |
| | `database.py` | ~300 | ✅ |
| | `security.py` | ~7 | ✅ (MVP) |
| **Models** | `base.py` | ~25 | ✅ |
| | `member.py` | ~25 | ✅ |
| | `membership.py` | ~63 | ✅ |
| | `equipment.py` | ~49 | ✅ |
| | `trainer.py` | ~18 | ✅ |
| | `notification.py` | ~54 | ✅ |
| | `trainer_assignment.py` | ~33 | ✅ |
| | `training_session.py` | ~33 | ✅ |
| | `attendance.py` | ~22 | ✅ |
| | `transaction.py` | ~22 | ✅ |
| **Repositories** | `member_repo.py` | ~100 | ✅ |
| | `membership_repo.py` | ~157 | ✅ |
| | `equipment_repo.py` | ~87 | ✅ |
| | `trainer_repo.py` | ~100 | ✅ |
| | `notification_repo.py` | ~97 | ✅ |
| | `trainer_assignment_repo.py` | ~141 | ✅ |
| | `training_session_repo.py` | ~115 | ✅ |
| | `attendance_repo.py` | ~119 | ✅ |
| | `transaction_repo.py` | ~79 | ✅ |
| **Services** | `member_svc.py` | ~58 | ✅ |
| | `membership_svc.py` | ~109 | ✅ |
| | `equipment_svc.py` | ~43 | ✅ |
| | `trainer_svc.py` | ~101 | ✅ |
| | `auth_svc.py` | ~93 | ✅ |
| | `notification_svc.py` | ~149 | ✅ |
| | `assignment_svc.py` | ~145 | ✅ |
| | `schedule_svc.py` | ~121 | ✅ |
| | `attendance_svc.py` | ~170 | ✅ |
| | `face_svc.py` | ~163 | ✅ |
| | `payment_svc.py` | ~0 | ❌ Stub trống |
| **Face ID** | `face_encoder.py` | ~128 | ✅ |
| | `face_recognizer.py` | ~128 | ✅ |
| | `face_register.py` | ~266 | ✅ |
| | `image_processing.py` | ~50 | ✅ |
| **GUI Admin** | `main.py` | ~80 | ✅ |
| | `login.py` | ~125 | ✅ |
| | `sidebar.py` | ~140 | ✅ |
| | `header.py` | ~102 | ✅ |
| | `dashboard.py` | ~650 | ✅ |
| | `members.py` | ~454 | ✅ |
| | `memberships.py` | ~390 | ✅ |
| | `equipment.py` | ~262 | ✅ |
| | `trainers.py` | ~302 | ✅ |
| | `attendance.py` | ~498 | ✅ |
| | `face_register.py` | ~388 | ✅ |
| | `reports.py` | ~178 | ✅ |
| **GUI User** | `user_main.py` | ~108 | ✅ |
| | `user_login.py` | ~227 | ✅ |
| | `user_sidebar.py` | ~168 | ✅ |
| | `user_dashboard.py` | ~204 | ✅ |
| | `user_profile.py` | ~150 | ✅ |
| | `user_membership.py` | ~180 | ✅ |
| | `user_schedule.py` | ~150 | ✅ |
| | `user_history.py` | ~120 | ✅ |
| | `user_attendance.py` | ~130 | ✅ |
| | `user_checkin.py` | ~200 | ✅ |
| | `user_notifications.py` | ~140 | ✅ |
| | `trainer_dashboard.py` | ~180 | ✅ |
| | `trainer_profile.py` | ~150 | ✅ |
| | `trainer_schedule.py` | ~300 | ✅ |
| | `trainer_students.py` | ~250 | ✅ |
| | `trainer_notifications.py` | ~140 | ✅ |
| **Bridge** | `bridge.py` | ~121 | ✅ |
| | `camera_module.py` | ~250 | ✅ |
| | `theme.py` | ~46 | ✅ |
| **Tổng** | **~56 files Python** | **~9,000+** | **Admin ~95%, User ~85%, Face ID ~90%** |

### 7.2 Thống kê tổng hợp

| Chỉ số | Giá trị |
|--------|---------|
| Tổng file Python (app + gui) | ~56 |
| Màn hình Admin | 9 |
| Màn hình User/Trainer | 16 |
| Services | 11 (1 stub) |
| Repositories | 9 |
| Models | 10 |
| Database tables | 10 |
| Database indexes | 18+ |
| Face ID modules | 4 |
| Dependencies | 7 |
| Tổng dòng code ước tính | ~9,000+ |

### 7.3 Tổng đánh giá

**FaceGym** là hệ thống quản lý phòng gym desktop toàn diện, tích hợp nhận diện khuôn mặt, bao gồm:

**2 ứng dụng riêng biệt:**
- **Admin App** (9 màn hình): Quản lý toàn bộ phòng gym — hội viên, gói tập, thiết bị, HLV, điểm danh Face ID, đăng ký khuôn mặt, báo cáo
- **User App** (16 màn hình): Hội viên xem thông tin cá nhân, gói tập, lịch tập, điểm danh, thông báo; HLV quản lý học viên, lịch dạy

**Điểm nổi bật:**
- Kiến trúc layered sạch: GUI → Service → Repository → Database
- Face ID hoạt động real-time qua multiprocessing IPC (Flet ↔ CustomTkinter)
- Database 10 bảng + 18 indexes, soft delete + cascade
- Guard clause, input validation, SQL injection prevention
- Comment tiếng Việt chi tiết cho toàn bộ codebase
- Notification tự động khi gói sắp hết hạn

**Cần hoàn thiện:**
- Testing (0% hiện tại)
- Password/PIN hashing (plaintext → bcrypt)
- Role guard cho user app routes
- Rate limiting đăng nhập
- Pagination cho data lớn
- Dọn dẹp stub files

---

*Báo cáo được tạo tự động bởi Claude Code — 2026-03-20, cập nhật lần cuối 2026-04-09*
*Tham khảo thêm: [BAO_CAO_KIEM_TRA_TOAN_BO.md](BAO_CAO_KIEM_TRA_TOAN_BO.md) | [BAO_CAO_USER_APP.md](BAO_CAO_USER_APP.md) | [KE_HOACH_GOP_DU_AN.md](../plans/KE_HOACH_GOP_DU_AN.md) | [HUONG_DI_PHAT_TRIEN.md](../plans/HUONG_DI_PHAT_TRIEN.md)*
