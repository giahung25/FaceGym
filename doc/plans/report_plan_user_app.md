# Kế hoạch triển khai — GymFit Member App (User App)

**Ngày tạo:** 2026-04-01
**Cập nhật lần cuối:** 2026-04-01
**Dự án:** Gym Management System — Phần User App
**Trạng thái:** Hoàn tất dự án User App ✅ (Tất cả các Bước đã hoàn thành)
**Tài liệu thiết kế:** `doc/BAO_CAO_USER_APP.md`

---

## 1. Tổng quan tiến độ

### 1.1 Kiến trúc sau tái cấu trúc (mục tiêu)

```
gym_management/
├── app/
│   ├── main.py              ✅ Hiện có (admin entry point — đã cập nhật import)
│   ├── user_main.py         ❌ Chưa tạo (user entry point)
│   ├── core/
│   │   ├── config.py        ✅ Hiện có
│   │   ├── database.py      ✅ Hiện có (cần cập nhật: thêm bảng + cột)
│   │   └── security.py      ✅ Hiện có
│   ├── models/
│   │   ├── base.py          ✅ Hiện có
│   │   ├── member.py        ✅ Hiện có
│   │   ├── membership.py    ✅ Hiện có
│   │   ├── equipment.py     ✅ Hiện có
│   │   ├── trainer.py       ❌ Chưa tạo
│   │   └── notification.py  ❌ Chưa tạo
│   ├── repositories/
│   │   ├── member_repo.py       ✅ Hiện có
│   │   ├── membership_repo.py   ✅ Hiện có
│   │   ├── equipment_repo.py    ✅ Hiện có
│   │   ├── trainer_repo.py      ❌ Chưa tạo
│   │   └── notification_repo.py ❌ Chưa tạo
│   └── services/
│       ├── member_svc.py        ✅ Hiện có
│       ├── membership_svc.py    ✅ Hiện có
│       ├── equipment_svc.py     ✅ Hiện có
│       ├── payment_svc.py       ⚠️ Stub trống
│       ├── trainer_svc.py       ⚠️ Stub trống (cần implement)
│       ├── auth_svc.py          ❌ Chưa tạo
│       └── notification_svc.py  ❌ Chưa tạo
├── gui/
│   ├── theme.py                 ✅ Hiện có (dùng chung)
│   ├── admin/                   ✅ Hoàn thành
│   │   ├── login.py             ✅ Di chuyển + cập nhật import
│   │   ├── dashboard.py         ✅ Di chuyển + cập nhật import
│   │   ├── members.py           ✅ Di chuyển + cập nhật import
│   │   ├── memberships.py       ✅ Di chuyển + cập nhật import
│   │   ├── equipment.py         ✅ Di chuyển + cập nhật import
│   │   ├── reports.py           ✅ Di chuyển + cập nhật import
│   │   └── components/
│   │       ├── sidebar.py       ✅ Di chuyển + cập nhật import
│   │       └── header.py        ✅ Di chuyển + cập nhật import
│   └── user/                    ❌ Chưa tạo
│       ├── user_login.py
│       ├── user_dashboard.py
│       ├── user_profile.py
│       ├── user_membership.py
│       ├── user_history.py
│       ├── user_notifications.py
│       ├── trainer_dashboard.py
│       └── components/
│           └── user_sidebar.py
└── data/
    └── gym_db.db                ✅ Hiện có (dùng chung)
```

### 1.2 Bảng tóm tắt trạng thái

| Layer | Module | Trạng thái | Ghi chú |
|-------|--------|:----------:|---------|
| **Restructure** | Di chuyển admin GUI | ✅ Xong | `gui/admin/` — 6 screens + 2 components |
| **Restructure** | Cập nhật imports admin | ✅ Xong | `app/main.py` + 5 admin screens đã cập nhật |
| **Database** | Thêm bảng `trainers` | ✅ Xong | CREATE TABLE trong `database.py` |
| **Database** | Thêm bảng `notifications` | ✅ Xong | CREATE TABLE trong `database.py` |
| **Database** | Thêm cột `pin` cho `members` | ✅ Xong | CREATE TABLE + ALTER TABLE migration cho DB cũ |
| **Models** | `trainer.py` | ✅ Xong | Kế thừa BaseModel, fields: name, phone, email, specialization, pin |
| **Models** | `notification.py` | ✅ Xong | Không kế thừa BaseModel — chỉ có id, user_id, user_type, title, message, is_read, created_at |
| **Repositories** | `trainer_repo.py` | ✅ Xong | CRUD + get_by_phone |
| **Repositories** | `notification_repo.py` | ✅ Xong | CRUD + get_by_user + get_unread_count + has_notification_today |
| **Services** | `auth_svc.py` | ✅ Xong | login_member, login_trainer, change_pin |
| **Services** | `trainer_svc.py` | ✅ Xong | register, update, get_by_id, get_all, get_trainer_members |
| **Services** | `notification_svc.py` | ✅ Xong | create, get, mark_read, check_expiring_subscriptions |
| **GUI User** | `user_sidebar.py` | ✅ Xong | Sidebar menu theo role member/trainer |
| **GUI User** | `user_login.py` | ✅ Xong | Toggle member/trainer, SĐT + PIN |
| **GUI User** | `user_dashboard.py` | ✅ Xong | Thông tin + gói tập active + shortcuts |
| **GUI User** | `user_profile.py` | ✅ Xong | Xem thông tin + đổi PIN |
| **GUI User** | `user_membership.py` | ✅ Xong | Tab gói hiện tại + tab đăng ký mới |
| **GUI User** | `user_history.py` | ✅ Xong | Bảng lịch sử + filter tháng/năm |
| **GUI User** | `user_notifications.py` | ✅ Xong | Danh sách + đánh dấu đã đọc |
| **GUI User** | `trainer_dashboard.py` | ✅ Xong | Thông tin HLV + danh sách học viên |
| **Entry** | `user_main.py` | ✅ Xong | Entry point user app |

---

## 2. Bảng kế hoạch chi tiết

### Ưu tiên 0 — TÁI CẤU TRÚC THƯ MỤC (làm đầu tiên, trước mọi thứ)

> **Mục tiêu:** Tách `gui/admin/` và `gui/user/` để 2 app không lẫn code GUI. Admin app phải vẫn chạy bình thường sau khi di chuyển.

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 0.1 | **Tạo thư mục `gui/admin/`** | `gui/admin/__init__.py` | ✅ XONG | Tạo package `gui.admin` |
| 0.2 | **Tạo thư mục `gui/admin/components/`** | `gui/admin/components/__init__.py` | ✅ XONG | Tạo package `gui.admin.components` |
| 0.3 | **Di chuyển admin screens** | `gui/login.py` → `gui/admin/login.py`, tương tự cho dashboard, members, memberships, equipment, reports | ✅ XONG | Di chuyển 6 file screen |
| 0.4 | **Di chuyển admin components** | `gui/components/sidebar.py` → `gui/admin/components/sidebar.py`, tương tự header.py | ✅ XONG | Di chuyển 2 file component |
| 0.5 | **Cập nhật import trong `app/main.py`** | `app/main.py` | ✅ XONG | `from gui.login` → `from gui.admin.login`, v.v. (6 import) |
| 0.6 | **Cập nhật import nội bộ admin screens** | Tất cả file trong `gui/admin/` | ✅ XONG | `from gui.components.sidebar` → `from gui.admin.components.sidebar` |
| 0.7 | **Xóa file cũ ở `gui/`** | `gui/login.py`, `gui/dashboard.py`, v.v. | ✅ XONG | Xóa 6 screens + `gui/components/`, giữ `theme.py` và `__init__.py` |
| 0.8 | **Kiểm tra admin app** | — | ✅ XONG | Tất cả import OK: `python -c "from gui.admin.login import LoginScreen ..."` |

**Điều kiện hoàn thành:** ✅ Tất cả imports resolve đúng. `python app/main.py` chạy bình thường.

---

### Ưu tiên 1 — DATABASE & MODELS (nền tảng dữ liệu)

> **Mục tiêu:** Mở rộng database schema và tạo models mới cho trainer + notification.

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 1.1 | **Thêm cột `pin` vào bảng `members`** | `app/core/database.py` | ✅ XONG | CREATE TABLE + ALTER TABLE migration — DB cũ tự migrate |
| 1.2 | **Tạo bảng `trainers`** | `app/core/database.py` | ✅ XONG | id, name, phone, email, specialization, pin, created_at, updated_at, is_active |
| 1.3 | **Tạo bảng `notifications`** | `app/core/database.py` | ✅ XONG | id, user_id, user_type, title, message, is_read, created_at |
| 1.4 | **Tạo model `Trainer`** | `app/models/trainer.py` | ✅ XONG | Kế thừa BaseModel, fields: name, phone, email, specialization, pin |
| 1.5 | **Tạo model `Notification`** | `app/models/notification.py` | ✅ XONG | Không kế thừa BaseModel (không cần updated_at/is_active), có mark_read() |
| 1.6 | **Cập nhật model `Member`** | `app/models/member.py` | ✅ XONG | Thêm `pin="000000"` vào `__init__` |

**Điều kiện hoàn thành:** ✅ `init_db()` tạo đủ 6 bảng, models import và khởi tạo đúng.

---

### Ưu tiên 2 — REPOSITORIES & SERVICES (logic nghiệp vụ)

> **Mục tiêu:** Xây dựng tầng data access và business logic cho trainer, notification, authentication.

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 2.1 | **Tạo `trainer_repo.py`** | `app/repositories/trainer_repo.py` | ✅ XONG | CRUD: create, get_by_id, get_by_phone, get_all, update, delete |
| 2.2 | **Tạo `notification_repo.py`** | `app/repositories/notification_repo.py` | ✅ XONG | create, get_by_user, mark_read, mark_all_read, get_unread_count, has_notification_today |
| 2.3 | **Tạo `auth_svc.py`** | `app/services/auth_svc.py` | ✅ XONG | login_member, login_trainer, change_pin (validate 6 chữ số) |
| 2.4 | **Implement `trainer_svc.py`** | `app/services/trainer_svc.py` | ✅ XONG | register_trainer, update_trainer, get_trainer_by_id, get_all_trainers, get_trainer_members |
| 2.5 | **Tạo `notification_svc.py`** | `app/services/notification_svc.py` | ✅ XONG | create_notification, check_expiring_subscriptions (1 lần/ngày, ≤7 ngày hoặc hết hạn) |
| 2.6 | **Cập nhật `member_repo.py`** | `app/repositories/member_repo.py` | ✅ XONG | Thêm pin vào _row_to_member/create/update, thêm get_by_phone() |

**Điều kiện hoàn thành:** ✅ Tất cả service methods hoạt động đúng — test end-to-end passed.

---

### Ưu tiên 3 — GUI USER: Components & Login (khung giao diện)

> **Mục tiêu:** Tạo khung giao diện user app — sidebar, login screen, và entry point.

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 3.1 | **Tạo `user_sidebar.py`** | `gui/user/components/user_sidebar.py` | ✅ Xong | Menu theo role: member (Trang chủ, Thông tin, Gói tập, Lịch sử, Thông báo, Đăng xuất) / trainer (Trang chủ, Học viên, Đăng xuất) |
| 3.2 | **Tạo `user_login.py`** | `gui/user/user_login.py` | ✅ Xong | Toggle Hội viên/HLV, input SĐT + PIN (6 số, password mode), nút Đăng nhập, gọi `auth_svc` |
| 3.3 | **Tạo `user_main.py`** | `app/user_main.py` | ✅ Xong | Entry point: `ft.app(target=main)`, window 1100x700, navigate function cho user screens |
| 3.4 | **Kiểm tra login flow** | — | ✅ Xong | Đăng nhập member + trainer, PIN sai → hiện lỗi, PIN đúng → vào dashboard |

**Điều kiện hoàn thành:** `python app/user_main.py` mở được cửa sổ, đăng nhập thành công.

---

### Ưu tiên 4 — GUI USER: Các màn hình Member (chức năng chính)

> **Mục tiêu:** Hoàn thành toàn bộ giao diện cho hội viên.

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 4.1 | **Tạo `user_dashboard.py`** | `gui/user/user_dashboard.py` | ✅ Xong | Hiển thị: tên + SĐT, gói tập active + progress bar + ngày còn lại, 3 shortcut buttons |
| 4.2 | **Tạo `user_profile.py`** | `gui/user/user_profile.py` | ✅ Xong | Thông tin cá nhân (read-only) + form đổi PIN (PIN cũ, PIN mới, xác nhận) |
| 4.3 | **Tạo `user_membership.py`** | `gui/user/user_membership.py` | ✅ Xong | Tab 1: gói hiện tại (progress, ngày, giá). Tab 2: danh sách gói + nút đăng ký → tạo subscription "pending" |
| 4.4 | **Tạo `user_history.py`** | `gui/user/user_history.py` | ✅ Xong | Bảng lịch sử tất cả subscriptions, filter theo năm/tháng, badge trạng thái |
| 4.5 | **Tạo `user_notifications.py`** | `gui/user/user_notifications.py` | ✅ Xong | Danh sách thông báo (mới → cũ), badge đỏ chưa đọc, nút "Đánh dấu tất cả đã đọc" |

**Điều kiện hoàn thành:** Hội viên đăng nhập → xem dashboard → xem/đổi thông tin → đăng ký gói → xem lịch sử → xem thông báo.

---

### Ưu tiên 5 — GUI USER: Màn hình Trainer + Tích hợp

> **Mục tiêu:** Hoàn thành dashboard HLV và tích hợp toàn bộ luồng.

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 5.1 | **Tạo `trainer_dashboard.py`** | `gui/user/trainer_dashboard.py` | ✅ Xong | Thông tin HLV (tên, chuyên môn, SĐT) + bảng danh sách học viên (tên, SĐT, gói tập) |
| 5.2 | **Tích hợp thông báo tự động** | `auth_svc.py`, `notification_svc.py` | ✅ Xong | Khi member đăng nhập → check gói sắp hết hạn → tự tạo notification |
| 5.3 | **Badge thông báo trên sidebar** | `gui/user/components/user_sidebar.py` | ✅ Xong | Hiển thị số thông báo chưa đọc bên cạnh menu "Thông báo" |
| 5.4 | **Test toàn bộ luồng** | — | ✅ Xong | Test end-to-end: login → navigate tất cả screens → đăng ký gói → xem thông báo |
| 5.5 | **Đảm bảo admin app không bị ảnh hưởng** | — | ✅ Xong | Chạy `python app/main.py` kiểm tra lại toàn bộ admin |

**Điều kiện hoàn thành:** Cả 2 app (`main.py` + `user_main.py`) chạy song song, dùng chung database.

---

## 3. Thứ tự thực hiện

```
Bước 1 — Tái cấu trúc thư mục ✅ HOÀN THÀNH
├── [0.1] Tạo gui/admin/ + gui/admin/components/          ✅
├── [0.2] Di chuyển 6 admin screens + 2 components        ✅
├── [0.3] Cập nhật tất cả import (main.py + nội bộ screens) ✅
├── [0.4] Xóa file cũ ở gui/ (giữ theme.py, __init__.py)  ✅
└── [0.5] Kiểm tra: python app/main.py — all imports OK   ✅

Bước 2 — Database & Models ✅ HOÀN THÀNH
├── [1.1] Cập nhật database.py (bảng trainers, notifications, cột pin)  ✅
├── [1.2] Tạo trainer.py model                                           ✅
├── [1.3] Tạo notification.py model                                      ✅
└── [1.4] Cập nhật member.py (thêm pin)                                  ✅

Bước 3 — Repositories & Services ✅ HOÀN THÀNH
├── [2.1] trainer_repo.py                                     ✅
├── [2.2] notification_repo.py                                ✅
├── [2.3] auth_svc.py                                         ✅
├── [2.4] Implement trainer_svc.py                            ✅
├── [2.5] notification_svc.py                                 ✅
└── [2.6] Cập nhật member_repo.py (pin, get_by_phone)        ✅

Bước 4 — GUI User cơ bản ✅ HOÀN THÀNH
├── [3.1] user_sidebar.py (component) ✅
├── [3.2] user_login.py (đăng nhập) ✅
├── [3.3] user_main.py (entry point) ✅
└── [3.4] Kiểm tra login flow ✅

Bước 5 — GUI User đầy đủ ✅ HOÀN THÀNH
├── [4.1] user_dashboard.py ✅
├── [4.2] user_profile.py ✅
├── [4.3] user_membership.py ✅
├── [4.4] user_history.py ✅
└── [4.5] user_notifications.py ✅

Bước 6 — Trainer + Tích hợp ✅ HOÀN THÀNH
├── [5.1] trainer_dashboard.py ✅
├── [5.2] Tích hợp thông báo tự động ✅
├── [5.3] Badge thông báo sidebar ✅
├── [5.4] Test toàn bộ luồng ✅
└── [5.5] Kiểm tra admin app ✅
```

---

## 4. Vấn đề kỹ thuật cần lưu ý

| Vấn đề | Chi tiết | Giải pháp |
|--------|----------|-----------|
| **Import path thay đổi khi di chuyển admin** | Tất cả `from gui.xxx` phải đổi thành `from gui.admin.xxx` | Cập nhật từng file, kiểm tra bằng cách chạy app |
| **Cột `pin` cho members hiện có** | Bảng `members` đã có dữ liệu, thêm cột cần ALTER TABLE | Dùng `ALTER TABLE members ADD COLUMN pin TEXT NOT NULL DEFAULT '000000'` |
| **`theme.py` dùng chung** | Cả admin và user đều import `from gui import theme` | Giữ `theme.py` tại `gui/theme.py`, không di chuyển |
| **2 entry point song song** | `main.py` (admin) và `user_main.py` (user) chạy độc lập | Mỗi app có navigate riêng, dùng chung DB + services |
| **PIN security** | PIN hiện lưu plaintext (giống password admin) | Chấp nhận cho MVP, có thể hash sau |
| **Thông báo tự động timing** | Tạo notification mỗi lần đăng nhập có thể bị trùng | Kiểm tra: chỉ tạo nếu chưa có thông báo cùng loại trong ngày |

---

## 5. Hướng dẫn chạy sau khi hoàn thành

```bash
# App Admin (quản trị viên)
python app/main.py

# App User (hội viên / HLV)
python app/user_main.py
```

**Tài khoản test:**
- Hội viên: SĐT đã có trong DB + PIN mặc định `000000`
- HLV: Tạo qua admin hoặc trực tiếp DB + PIN mặc định `000000`

---

*Cập nhật lần cuối: 2026-04-01 — Khởi tạo kế hoạch, chưa bắt đầu triển khai.*
