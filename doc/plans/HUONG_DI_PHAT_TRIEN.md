# Hướng đi phát triển — Gym Management System

**Ngày tạo:** 2026-04-04
**Người viết:** Claude Code (AI Assistant)
**Phạm vi:** Toàn bộ hệ thống — Admin App + User App
**Trạng thái hiện tại:** Admin App ~95% | User App ~70% | Tests 0%

---

## MỤC LỤC

1. [Đánh giá hiện trạng](#1-đánh-giá-hiện-trạng)
2. [Các hướng phát triển](#2-các-hướng-phát-triển)
3. [Chi tiết từng hướng](#3-chi-tiết-từng-hướng)
4. [Bảng tổng hợp & lộ trình gợi ý](#4-bảng-tổng-hợp--lộ-trình-gợi-ý)

---

## 1. Đánh giá hiện trạng

### 1.1 Những gì đã hoàn thành

```
Admin App (app/main.py)
├── ✅ Login — đăng nhập admin (username + password)
├── ✅ Dashboard — KPI, biểu đồ doanh thu, sắp hết hạn, gói tập
├── ✅ Members — CRUD hội viên, tìm kiếm, lọc giới tính/gói tập, lịch sử gói
├── ✅ Memberships — CRUD gói tập, đăng ký/hủy subscription
├── ✅ Equipment — CRUD thiết bị, lọc theo trạng thái
├── ✅ Trainers — CRUD huấn luyện viên, reset PIN (MỚI)
└── ✅ Reports — thống kê hội viên, thiết bị, gói sắp hết hạn

User App (app/user_main.py)
├── ✅ Login — đăng nhập member/trainer bằng SĐT + PIN
├── ✅ Dashboard — thông tin cá nhân, gói tập active, progress bar
├── ✅ Profile — xem thông tin cá nhân + đổi PIN
├── ✅ Membership — gói hiện tại + đăng ký gói mới
├── ✅ History — lịch sử gói tập
├── ✅ Notifications — thông báo (hết hạn, gia hạn)
└── ✅ Trainer Dashboard — thông tin HLV + danh sách học viên

Backend
├── ✅ 6 models (base, member, membership, equipment, trainer, notification)
├── ✅ 5 repositories (member, membership, equipment, trainer, notification)
├── ✅ 7 services (member, membership, equipment, trainer, auth, notification, payment_stub)
└── ✅ 6 bảng database + indexes
```

### 1.2 Những gì còn thiếu / yếu

| # | Vấn đề | Mức độ | Ảnh hưởng |
|---|--------|:------:|-----------|
| 1 | **Không có tests** | 🔴 Cao | Không thể xác minh logic đúng, refactor nguy hiểm |
| 2 | **User App chưa test kỹ** | 🔴 Cao | Nhiều bug tiềm ẩn từ session trước (login crash, sidebar) |
| 3 | **Plaintext password/PIN** | 🟡 Trung bình | Bảo mật yếu, không phù hợp production |
| 4 | **Dashboard admin chưa có thống kê HLV** | 🟡 Trung bình | Thêm Trainers nhưng Dashboard chưa phản ánh |
| 5 | **Admin chưa gửi được thông báo** | 🟡 Trung bình | Notification chỉ tự động, admin không chủ động gửi |
| 6 | **Header search bar chưa hoạt động** | 🟢 Thấp | Search trên header chỉ là UI trang trí |
| 7 | **Không có pagination** | 🟢 Thấp | OK cho <500 records, cần khi data lớn |
| 8 | **Không có export CSV/PDF** | 🟢 Thấp | Báo cáo chỉ xem trên app, không xuất file |
| 9 | **Stub files chưa dọn** | 🟢 Thấp | `payment_svc.py`, `api/` rỗng gây nhầm lẫn |

---

## 2. Các hướng phát triển

### Hướng A — Ổn định & Chất lượng (Testing + Bug Fix)
> *"Làm cho cái đã có hoạt động đúng 100%"*

Ưu tiên viết tests, sửa bug user app, đảm bảo hệ thống hiện tại chạy ổn định.

**Phù hợp khi:** Chuẩn bị nộp bài, demo, hoặc trước khi thêm tính năng mới.

### Hướng B — Hoàn thiện tính năng Admin
> *"Admin app mạnh hơn, thông minh hơn"*

Bổ sung các tính năng còn thiếu cho admin: dashboard thống kê HLV, header search, gửi thông báo, export báo cáo.

**Phù hợp khi:** Muốn admin app hoàn chỉnh 100% trước khi chuyển sang user app.

### Hướng C — Nâng cấp User App
> *"Trải nghiệm người dùng tốt hơn"*

Sửa bug, thêm tính năng: toast/snackbar thông báo, upload ảnh, cải thiện UX sidebar.

**Phù hợp khi:** User app là trọng tâm, muốn demo được cả hai app.

### Hướng D — Bảo mật & Production-ready
> *"Chuẩn bị cho triển khai thật"*

Thêm password hashing, giới hạn đăng nhập sai, log audit trail, backup database.

**Phù hợp khi:** Muốn nâng cấp từ MVP lên bản có thể dùng thực tế.

---

## 3. Chi tiết từng hướng

---

### Hướng A — Ổn định & Chất lượng

#### A1. Viết Unit Tests cho Services

| Test file | Test cases | Service |
|-----------|-----------|---------|
| `tests/test_member_svc.py` | Tên trống, SĐT sai format, email sai, đăng ký thành công, cập nhật | `member_svc` |
| `tests/test_membership_svc.py` | Tạo gói, đăng ký subscription, auto-expire, tính doanh thu | `membership_svc` |
| `tests/test_equipment_svc.py` | Tên trống, category trống, thay đổi status, summary | `equipment_svc` |
| `tests/test_trainer_svc.py` | Tên trống, SĐT sai, đăng ký HLV, reset PIN (6 số, sai format) | `trainer_svc` |
| `tests/test_auth_svc.py` | Login member đúng/sai, login trainer đúng/sai, đổi PIN | `auth_svc` |

**Công cụ cần cài:** `pip install pytest`

**Pattern test:**
```python
import pytest
from app.services import trainer_svc

def test_register_trainer_success():
    t = trainer_svc.register_trainer("Nguyễn Huấn", "0901234567")
    assert t.name == "Nguyễn Huấn"
    assert t.pin == "000000"  # PIN mặc định

def test_reset_pin_invalid():
    with pytest.raises(ValueError, match="PIN phải gồm đúng 6 chữ số"):
        trainer_svc.reset_pin("fake-id", "abc")
```

**Ước lượng:** ~5 files, ~50 test cases

#### A2. Kiểm tra & sửa bug User App

Chạy `python app/user_main.py` và kiểm tra từng luồng:

| Luồng | Kiểm tra | Trạng thái |
|-------|----------|:----------:|
| Login member | Nhập SĐT + PIN → vào dashboard | ❓ Cần test |
| Login trainer | Nhập SĐT + PIN → vào trainer dashboard | ❓ Cần test |
| Login sai | SĐT sai / PIN sai → hiện lỗi | ❓ Cần test |
| Dashboard | Hiện thông tin cá nhân + gói active | ❓ Cần test |
| Profile | Xem thông tin + đổi PIN | ❓ Cần test |
| Membership | Xem gói hiện tại + đăng ký gói mới | ❓ Cần test |
| History | Xem lịch sử gói tập | ❓ Cần test |
| Notifications | Xem thông báo, đánh dấu đã đọc | ❓ Cần test |
| Sidebar | Chuyển tab hoạt động mượt, animation đúng | ❓ Cần test |
| Đăng xuất | Quay về login, xóa session | ❓ Cần test |

---

### Hướng B — Hoàn thiện tính năng Admin

#### B1. Dashboard thống kê HLV

Thêm vào `gui/admin/dashboard.py`:
- **Card KPI mới:** "Tổng HLV" (icon: SPORTS_ROUNDED, badge: "+N tháng này")
- **Section:** "Huấn luyện viên" — bảng danh sách HLV với chuyên môn

```
Hiện tại:
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Hội viên │ │ Sắp hạn  │ │ Doanh thu│ │ Bảo trì  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

Sau khi thêm:
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Hội viên │ │ Sắp hạn  │ │ Doanh thu│ │ Bảo trì  │ │ HLV (5)  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

**Files:** `gui/admin/dashboard.py`, `app/services/trainer_svc.py`

#### B2. Header Search hoạt động

Kết nối search bar trên `header.py` với màn hình active thông qua callback pattern:

```python
# Mỗi screen tự đăng ký callback:
page.on_search_change = lambda keyword: refresh_table_with_search(keyword)

# Header gọi callback khi user gõ:
def _on_search(e):
    cb = getattr(page, "on_search_change", None)
    if callable(cb):
        cb(e.control.value)
```

**Files:** `gui/admin/components/header.py`, tất cả admin screens

#### B3. Admin gửi thông báo cho member

Thêm tính năng trong admin:
- Nút "Gửi thông báo" trên trang Members (cho từng member hoặc broadcast)
- Dialog: nhập tiêu đề + nội dung → `notification_svc.create_notification()`
- Member mở user app → thấy thông báo mới

**Files:** `gui/admin/members.py`, `app/services/notification_svc.py`

#### B4. Export báo cáo CSV

Thêm nút "Xuất CSV" trên trang Reports:
- Export danh sách hội viên
- Export doanh thu theo tháng
- Export danh sách thiết bị

**Dùng module `csv` built-in + `ft.FilePicker` để chọn nơi lưu.**

**Files:** `gui/admin/reports.py`

#### B5. Thống kê doanh thu theo tháng trên Reports

Thêm biểu đồ bar chart doanh thu 6 tháng gần nhất (tương tự dashboard nhưng chi tiết hơn).

**Files:** `gui/admin/reports.py`, `app/services/membership_svc.py` (hàm `get_monthly_revenue()` đã có)

---

### Hướng C — Nâng cấp User App

#### C1. Toast / Snackbar thông báo

Thêm `page.snack_bar` sau các hành động quan trọng:
- Đổi PIN thành công → "PIN đã được cập nhật"
- Đăng ký gói tập → "Đăng ký thành công, chờ admin xác nhận"
- Lỗi → snackbar đỏ với nội dung lỗi

**Files:** Tất cả `gui/user/*.py`

#### C2. Upload ảnh hội viên

Thêm vào `gui/admin/members.py`:
- Nút "Chọn ảnh" trong dialog Thêm/Sửa → `ft.FilePicker`
- Lưu ảnh vào `data/photos/` + cập nhật field `member.photo`
- Hiển thị ảnh thật trong avatar thay vì chữ cái

**Files:** `gui/admin/members.py`, `app/services/member_svc.py`

#### C3. Cải thiện UX Sidebar User App

- Animation chuyển tab mượt hơn (giống admin sidebar)
- Hiện badge đỏ số thông báo chưa đọc trên menu "Thông báo"
- Hiện tên + avatar user đang đăng nhập

**Files:** `gui/user/components/user_sidebar.py`

---

### Hướng D — Bảo mật & Production-ready

#### D1. Password/PIN Hashing

Chuyển từ plaintext sang hash:

```python
import hashlib

def hash_pin(pin: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', pin.encode(), b'gym_salt', 100000).hex()

def verify_pin(pin: str, hashed: str) -> bool:
    return hash_pin(pin) == hashed
```

**Ảnh hưởng:** `security.py`, `auth_svc.py`, `trainer_svc.py` (reset_pin), database migration cho PIN cũ.

#### D2. Giới hạn đăng nhập sai

- Sau 5 lần sai → khóa tài khoản 15 phút
- Cần thêm cột `login_attempts` + `locked_until` vào `members` và `trainers`

**Files:** `auth_svc.py`, `database.py`

#### D3. Backup Database tự động

Thêm hàm backup khi app khởi động:

```python
import shutil
from datetime import datetime

def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(DB_PATH, f"data/backup/gym_db_{timestamp}.db")
```

**Files:** `app/core/database.py`, `app/main.py`

#### D4. Dọn dẹp stub files

- Xóa `app/services/payment_svc.py` (trống, không dùng)
- Xóa `app/api/` (thư mục trống)
- Xóa `app/utils/` (thư mục trống)

---

## 4. Bảng tổng hợp & Lộ trình gợi ý

### 4.1 Ma trận ưu tiên

| Hướng | Tác vụ | Độ khó | Ưu tiên | Thời gian ước tính |
|-------|--------|:------:|:-------:|:------------------:|
| **A1** | Viết Unit Tests | ★★☆ | 🔴 Cao | 2-3 sessions |
| **A2** | Sửa bug User App | ★★☆ | 🔴 Cao | 1-2 sessions |
| **B1** | Dashboard thống kê HLV | ★☆☆ | 🟡 TB | 1 session |
| **B2** | Header Search hoạt động | ★★☆ | 🟡 TB | 1 session |
| **B3** | Admin gửi thông báo | ★★☆ | 🟡 TB | 1 session |
| **B4** | Export CSV | ★☆☆ | 🟡 TB | 1 session |
| **B5** | Thống kê doanh thu Reports | ★☆☆ | 🟡 TB | 1 session |
| **C1** | Toast / Snackbar | ★☆☆ | 🟢 Thấp | 1 session |
| **C2** | Upload ảnh hội viên | ★★☆ | 🟢 Thấp | 1 session |
| **C3** | Cải thiện Sidebar UX | ★☆☆ | 🟢 Thấp | 1 session |
| **D1** | Password hashing | ★★★ | 🟡 TB | 1-2 sessions |
| **D2** | Giới hạn login sai | ★★☆ | 🟢 Thấp | 1 session |
| **D3** | Backup DB tự động | ★☆☆ | 🟢 Thấp | < 1 session |
| **D4** | Dọn stub files | ★☆☆ | 🟢 Thấp | < 1 session |

### 4.2 Lộ trình gợi ý (theo thứ tự)

```
Phase 1 — Ổn định (ưu tiên cao nhất)
├── [A2] Kiểm tra & sửa bug User App
├── [A1] Viết Unit Tests (ít nhất services layer)
└── [D4] Dọn dẹp stub files

Phase 2 — Hoàn thiện Admin
├── [B1] Dashboard thống kê HLV
├── [B5] Thống kê doanh thu theo tháng trên Reports
├── [B2] Header Search hoạt động
└── [B4] Export CSV

Phase 3 — Tích hợp Admin ↔ User
├── [B3] Admin gửi thông báo cho member
├── [C1] Toast / Snackbar cho User App
└── [C3] Cải thiện Sidebar UX

Phase 4 — Nâng cấp (nếu còn thời gian)
├── [D1] Password/PIN hashing
├── [D3] Backup DB tự động
├── [C2] Upload ảnh hội viên
└── [D2] Giới hạn đăng nhập sai
```

---

*Báo cáo hướng đi được tạo bởi Claude Code — 2026-04-04*
*Tham khảo thêm: [report_plan.md](report_plan.md) | [report_plan_user_app.md](report_plan_user_app.md) | [BAO_CAO_CHI_TIET.md](BAO_CAO_CHI_TIET.md)*
