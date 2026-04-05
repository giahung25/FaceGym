## Hoạt động: Sửa thanh tìm kiếm — chuyển sang ft.SearchBar chuẩn (header + members)

**Thời gian:** 2026-03-26 21:52
**Files tác động:**
- `gui/members.py`
- `gui/components/header.py`

**Tóm tắt thay đổi:**
- Thanh tìm kiếm ở cả Header và Members trước đây dùng custom layout (Container > Row > Icon + TextField), gây lỗi chữ bị lệch so với icon.
- Đã thay bằng `ft.SearchBar` — component chuẩn của Flet, sử dụng các thuộc tính `bar_leading`, `bar_hint_text`, `bar_bgcolor`, `bar_border_side`, `bar_text_style`, `bar_hint_text_style` để styling.
- Header: width=320, Members: width=260. Cả hai dùng cùng pattern styling.

**Trạng thái Test:** Chưa có automated test.

---

## Hoạt động: Sửa lỗi xóa hội viên — đổi sang hard delete

**Thời gian:** 2026-03-26 20:52
**Files tác động:**
- `app/repositories/member_repo.py`

**Tóm tắt thay đổi:**
- Hàm `delete()` trước đây dùng soft delete (chỉ set `is_active = 0`), khiến record vẫn còn trong DB.
- Đã đổi sang hard delete: `DELETE FROM members WHERE id = ?` — xóa hẳn dòng khỏi database.

**Trạng thái Test:** Chưa có automated test.

---

## Hoạt động: Thêm comment chi tiết tiếng Việt vào toàn bộ codebase

**Thời gian:** 2026-03-22 19:44
**Files tác động:**
- `app/core/config.py`, `app/core/database.py`, `app/core/security.py`
- `app/models/base.py`, `app/models/member.py`, `app/models/membership.py`, `app/models/equipment.py`
- `app/repositories/member_repo.py`, `app/repositories/membership_repo.py`, `app/repositories/equipment_repo.py`
- `app/services/member_svc.py`, `app/services/membership_svc.py`, `app/services/equipment_svc.py`
- `app/main.py`
- `gui/theme.py`, `gui/login.py`, `gui/dashboard.py`, `gui/members.py`, `gui/memberships.py`, `gui/equipment.py`, `gui/reports.py`
- `gui/components/header.py`, `gui/components/sidebar.py`

**Tóm tắt thay đổi:**
- Thêm comment tiếng Việt chi tiết vào toàn bộ 23 file source code
- Giải thích từng khái niệm Python: class, inheritance, super(), UUID, datetime, contextmanager, regex, lambda, closure, dict comprehension, setattr, *args/**kwargs
- Giải thích kiến trúc 3-layer: GUI → Service → Repository → Database
- Giải thích SQLite3: PRAGMA foreign_keys, row_factory, soft delete, SQL injection prevention
- Giải thích Flet GUI: ft.Page, ft.Container, ft.Row, ft.Column, ft.AlertDialog, ft.Stack, page.overlay, monkey patching
- Mục tiêu: sinh viên học lập trình có thể đọc và hiểu toàn bộ hệ thống

**Trạng thái Test:** Chưa có test suite.

---

## Hoạt động: Tạo file PowerPoint thuyết trình 10 slides

**Thời gian:** 2026-03-20 22:03
**Files tác động:**
- `presentation/` — tạo mới thư mục
- `presentation/create_pptx.py` — script Python tạo PPTX
- `presentation/GymAdmin_Presentation.pptx` — file kết quả (51KB)

**Tóm tắt thay đổi:**
- Tạo thư mục `presentation/` độc lập trong dự án
- Dùng thư viện `python-pptx` để tạo 10 slides với design theo theme.py (màu ORANGE #F97316, SIDEBAR #1C1C2E)
- Nội dung 10 slides: Trang bìa → Tổng quan → Kiến trúc → DB Schema → Models → GUI/Navigation → Dashboard → Members/Memberships → Equipment/Reports → Đánh giá & Roadmap

**Trạng thái Test:** Chạy thành công, file 51KB

---

## Hoạt động: Viết báo cáo kỹ thuật chi tiết toàn hệ thống

**Thời gian:** 2026-03-20 21:40
**Files tác động:**
- `doc/BAO_CAO_CHI_TIET.md` — tạo mới

**Tóm tắt thay đổi:**
- Đọc và phân tích toàn bộ 23 file source code trong hệ thống
- Viết báo cáo ~3200 dòng bao gồm: tổng quan kiến trúc, sơ đồ khối, phân tích chi tiết từng tầng (Core → Models → Repositories → Services → GUI), giải thích từng khối code quan trọng, luồng dữ liệu, và đánh giá kỹ thuật
- Báo cáo tuân theo cấu trúc yêu cầu trong `sub_prompt.txt`

**Trạng thái Test:** Không áp dụng (báo cáo tĩnh)

---

## Hoạt động: Fix vấn đề kỹ thuật — start_date type & header search

**Thời gian:** 2026-03-20 20:49
**Files tác động:**
- `app/models/membership.py` — chuẩn hóa `start_date` về `datetime`
- `gui/components/header.py` — thêm `on_change` gọi `page.on_search_change`
- `app/main.py` — reset `page.on_search_change = None` khi navigate
- `gui/members.py` — đăng ký `page.on_search_change` callback

**Tóm tắt thay đổi:**
- `MembershipSubscription.__init__` kiểm tra nếu `start_date` là `date` thuần thì convert sang `datetime` bằng `datetime.combine()` — tránh lỗi so sánh `datetime > date`
- Header search TextField có `on_change` gọi `page.on_search_change` nếu callback tồn tại
- `navigate()` reset `page.on_search_change = None` mỗi lần đổi màn hình — tránh callback stale
- `MembersScreen` đăng ký `page.on_search_change` → header search giờ filter bảng hội viên realtime

**Trạng thái Test:** Chưa có test suite.

---

## Hoạt động: Hoàn thành Ưu tiên 2 (2.1 → 2.4)

**Thời gian:** 2026-03-20 20:41
**Files tác động:**
- `app/services/membership_svc.py` — thêm `cancel_subscription()`
- `gui/memberships.py` — thêm nút Hủy + confirm dialog (2.4)
- `gui/members.py` — thêm dialog Chi tiết + filter giới tính/subscription (2.1, 2.3)
- `gui/dashboard.py` — thêm section "Sắp hết hạn" (2.2)

**Tóm tắt thay đổi:**
- [2.1] Dialog "Lịch sử gói tập" cho từng hội viên: hiển thị toàn bộ subscription history với tên gói, ngày, trạng thái, giá
- [2.2] Section "Gói tập sắp hết hạn" trên Dashboard: bảng danh sách chi tiết (tên hội viên, gói, ngày hết hạn, đếm ngược), badge đỏ nếu ≤3 ngày
- [2.3] Filter trên trang Members: dropdown giới tính (Nam/Nữ/Khác) + dropdown trạng thái gói (Đang active/Không active), kết hợp được với search
- [2.4] Nút "Hủy" cho subscription đang active trong tab Đăng ký; confirm dialog trước khi hủy; `cancel_subscription()` trong service validate và persist

**Trạng thái Test:** Chưa có test suite.

---

## Hoạt động: Hoàn thành Ưu tiên 1 — field photo & location

**Thời gian:** 2026-03-20 20:32
**Files tác động:**
- `app/models/member.py` — thêm field `photo`
- `app/models/equipment.py` — thêm field `location`
- `app/repositories/member_repo.py` — map `photo` đầy đủ (read/create/update)
- `app/repositories/equipment_repo.py` — bỏ `getattr()` workaround, dùng `equipment.location`
- `gui/equipment.py` — bỏ `getattr(eq, "location", "")`, dùng `eq.location`

**Tóm tắt thay đổi:**
- [1.4] `Member.__init__` thêm param `photo=None`; `member_repo` đọc/ghi đúng cột `photo` thay vì hardcode `None`
- [1.5] `Equipment.__init__` thêm param `location=None`; `equipment_repo` bỏ toàn bộ `getattr()` workaround; GUI equipment bỏ `getattr` tương tự
- Tất cả Ưu tiên 1 (1.1 → 1.5) đã hoàn thành

**Trạng thái Test:** Chưa có test suite.

---

## Hoạt động: Tạo màn hình đăng nhập

**Thời gian:** 2026-03-20 20:15
**Files tác động:**
- `gui/login.py` — tạo mới
- `app/core/security.py` — implement
- `app/core/config.py` — thêm ADMIN_USERNAME / ADMIN_PASSWORD
- `app/main.py` — đổi route khởi động từ `dashboard` → `login`

**Tóm tắt thay đổi:**
- `LoginScreen`: form username/password, gradient background, logo, nút đăng nhập, hiển thị lỗi inline, hỗ trợ nhấn Enter để submit
- `check_login()` trong `security.py`: so sánh credentials với config (có thể override qua env var `GYM_USERNAME` / `GYM_PASSWORD`)
- `navigate("login")` được thêm vào router trong `main.py`; app khởi động tại login thay vì dashboard
- Default credentials: `admin` / `admin123`

**Trạng thái Test:** Chưa có test cho login flow.

---

## Hoạt động: Fix các vấn đề từ Code Review

**Thời gian:** 2026-03-20 18:55
**Files tác động:**
- `app/core/database.py` — sửa
- `app/main.py` — sửa
- `app/services/member_svc.py` — sửa
- `requirements.txt` — sửa

**Tóm tắt thay đổi:**

| # | Vấn đề | Fix |
|---|--------|-----|
| 1 | `executescript()` bypass transaction context manager | Thay bằng `conn.execute()` từng lệnh + explicit `commit/rollback` |
| 2 | FK dùng inline `REFERENCES` không nhất quán | Chuyển sang `FOREIGN KEY(...) REFERENCES(...)` chuẩn |
| 3 | Thiếu indexes trên các cột query thường xuyên | Thêm 6 indexes: `phone`, `is_active`, `member_id`, `plan_id`, `status` (subs), `status` (equipment) |
| 4 | `page.overlay` tích lũy dialogs mỗi lần navigate | Thêm `page.overlay.clear()` trước `page.controls.clear()` |
| 5 | `init_db()` không có error handling | Bọc trong `try/except`, in lỗi rõ ràng rồi re-raise |
| 6 | `update_member()` signature nhận `name/phone/email/kwargs` gây nhầm lẫn | Đơn giản hóa: chỉ nhận `member` đã mutate, thêm docstring |
| 7 | `requirements.txt` không pin version | Đổi `>=0.20.0` → `==0.82.2` (version đang dùng) |

**Trạng thái Test:** Chưa có test suite — cần thêm.

---

## Hoạt động: Review UI toàn bộ

**Thời gian:** 2026-03-20 18:48
**File tác động:** `doc/UI_REVIEW.md` (tạo mới)
**Tóm tắt:** Review toàn bộ 5 màn hình + 2 components trong `gui/`. Phân tích design system, chức năng từng màn hình, vấn đề và đề xuất cải thiện.
**Trạng thái Test:** Không áp dụng (báo cáo tĩnh)

---

# Báo cáo chi tiết: Tầng Models — Gym Management System

**Ngày tạo:** 2026-03-18
**Cập nhật lần cuối:** 2026-03-19
**Phạm vi:** `app/models/` + `gui/`
**Dự án:** Gym Management System

---

## 1. Tổng quan dự án

| Mục | Chi tiết |
|-----|----------|
| Tên dự án | Gym Management System |
| Ngôn ngữ | Python (thuần, không dùng ORM) |
| Database | SQLite3 |
| GUI Framework | Flet |
| Phạm vi báo cáo | `app/models/` + `gui/` |

---

## 2. Cấu trúc tầng Models

```
app/
└── models/
    ├── __init__.py          # Export tất cả models
    ├── base.py              # BaseModel — lớp nền chung
    ├── member.py            # Member — hội viên
    ├── membership.py        # MembershipPlan + MembershipSubscription
    └── equipment.py         # Equipment — thiết bị
```

---

## 3. Chi tiết từng file

### 3.1 `app/models/base.py` — BaseModel

**Mô tả:** Lớp nền (base class) mà tất cả các model khác kế thừa. Cung cấp các field chung và method cơ bản.

#### Bug đã phát hiện và sửa
- **Lỗi:** Các method `update()`, `delete()`, `to_dict()` bị định nghĩa **lồng bên trong `__init__()`** thay vì ở cấp class → các method này không thể gọi từ bên ngoài như instance method bình thường.
- **Sửa:** Đưa toàn bộ method ra cấp class đúng chuẩn Python.
- **Lỗi thứ hai:** Tên field `is_activate` (sai) → đổi thành `is_active` để nhất quán với Python convention và các model con.

#### Fields

| Field | Kiểu | Mô tả |
|-------|------|--------|
| `id` | `str` (UUID4) | Khóa chính, tự sinh khi tạo |
| `created_at` | `datetime` | Thời điểm tạo bản ghi |
| `updated_at` | `datetime` | Thời điểm cập nhật gần nhất |
| `is_active` | `bool` | Trạng thái hoạt động (mặc định `True`) |

#### Methods

| Method | Tham số | Trả về | Mô tả |
|--------|---------|--------|--------|
| `__init__()` | — | — | Khởi tạo id (UUID), created_at, updated_at, is_active |
| `update(**kwargs)` | `**kwargs` | `None` | Cập nhật các field được truyền vào, tự cập nhật `updated_at` |
| `delete()` | — | `None` | Soft delete: đặt `is_active = False`, cập nhật `updated_at` |
| `to_dict()` | — | `dict` | Chuyển object sang dict; các field `datetime` được chuyển sang ISO string |

#### Code tham khảo

```python
class BaseModel:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def delete(self):
        self.is_active = False
        self.updated_at = datetime.now()

    def to_dict(self):
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
```

---

### 3.2 `app/models/member.py` — Member

**Mô tả:** Đại diện cho một hội viên của phòng gym. Kế thừa `BaseModel`.

#### Fields bổ sung so với phiên bản gốc
Ban đầu model chỉ có `name` và `phone`. Đã bổ sung thêm các field:
- `email`
- `gender`
- `date_of_birth`
- `address`
- `emergency_contact`

#### Fields đầy đủ

| Field | Kiểu | Mặc định | Mô tả |
|-------|------|----------|--------|
| `id` | `str` | UUID4 (từ BaseModel) | Khóa chính |
| `name` | `str` | — | Họ tên hội viên |
| `phone` | `str` | — | Số điện thoại |
| `email` | `str` | `""` | Địa chỉ email |
| `gender` | `str` | `""` | Giới tính (`male` / `female` / `other`) |
| `date_of_birth` | `str` | `""` | Ngày sinh (ISO format) |
| `address` | `str` | `""` | Địa chỉ |
| `emergency_contact` | `str` | `""` | Liên hệ khẩn cấp |
| `created_at` | `datetime` | now() (từ BaseModel) | Ngày tạo |
| `updated_at` | `datetime` | now() (từ BaseModel) | Ngày cập nhật |
| `is_active` | `bool` | `True` (từ BaseModel) | Trạng thái hoạt động |

#### Code tham khảo

```python
class Member(BaseModel):
    def __init__(self, name: str, phone: str, email: str = "",
                 gender: str = "", date_of_birth: str = "",
                 address: str = "", emergency_contact: str = ""):
        super().__init__()
        self.name = name
        self.phone = phone
        self.email = email
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.address = address
        self.emergency_contact = emergency_contact
```

---

### 3.3 `app/models/membership.py` — MembershipPlan & MembershipSubscription

**Mô tả:** Gồm hai class liên quan đến gói tập và đăng ký của hội viên.

---

#### 3.3.1 MembershipPlan

Đại diện cho một gói tập (ví dụ: "Gói 1 tháng", "Gói 3 tháng").

| Field | Kiểu | Mô tả |
|-------|------|--------|
| `id` | `str` | UUID4 (từ BaseModel) |
| `name` | `str` | Tên gói tập |
| `duration_days` | `int` | Số ngày hiệu lực |
| `price` | `float` | Giá gói tập |
| `description` | `str` | Mô tả (tùy chọn) |

```python
class MembershipPlan(BaseModel):
    def __init__(self, name: str, duration_days: int,
                 price: float, description: str = ""):
        super().__init__()
        self.name = name
        self.duration_days = duration_days
        self.price = price
        self.description = description
```

---

#### 3.3.2 MembershipSubscription

Đại diện cho một lần đăng ký gói tập của hội viên. Kế thừa `BaseModel`.

| Field | Kiểu | Mô tả |
|-------|------|--------|
| `id` | `str` | UUID4 (từ BaseModel) |
| `member_id` | `str` | FK → Member.id |
| `plan_id` | `str` | FK → MembershipPlan.id |
| `price_paid` | `float` | Giá thực tế đã trả |
| `start_date` | `date` | Ngày bắt đầu |
| `end_date` | `date` | Ngày kết thúc (tự tính từ plan) |
| `status` | `str` | `active` / `expired` / `cancelled` |

#### Status Constants

```python
STATUS_ACTIVE    = "active"
STATUS_EXPIRED   = "expired"
STATUS_CANCELLED = "cancelled"
```

#### Methods

| Method | Tham số | Trả về | Mô tả |
|--------|---------|--------|--------|
| `is_expired()` | — | `bool` | Trả về `True` nếu `end_date < today` |
| `days_remaining()` | — | `int` | Số ngày còn lại (0 nếu đã hết hạn) |
| `cancel()` | — | `None` | Đặt status = `cancelled`, cập nhật `updated_at` |
| `refresh_status()` | — | `None` | Tự động cập nhật status dựa trên ngày hiện tại |

```python
class MembershipSubscription(BaseModel):
    def __init__(self, member_id: str, plan_id: str,
                 price_paid: float, start_date: date,
                 duration_days: int):
        super().__init__()
        self.member_id = member_id
        self.plan_id = plan_id
        self.price_paid = price_paid
        self.start_date = start_date
        self.end_date = start_date + timedelta(days=duration_days)
        self.status = STATUS_ACTIVE

    def is_expired(self) -> bool:
        return date.today() > self.end_date

    def days_remaining(self) -> int:
        delta = self.end_date - date.today()
        return max(0, delta.days)

    def cancel(self):
        self.status = STATUS_CANCELLED
        self.updated_at = datetime.now()

    def refresh_status(self):
        if self.status != STATUS_CANCELLED:
            if self.is_expired():
                self.status = STATUS_EXPIRED
            else:
                self.status = STATUS_ACTIVE
```

---

### 3.4 `app/models/equipment.py` — Equipment

**Mô tả:** Đại diện cho một thiết bị trong phòng gym. Kế thừa `BaseModel`.

#### Fields

| Field | Kiểu | Mặc định | Mô tả |
|-------|------|----------|--------|
| `id` | `str` | UUID4 (từ BaseModel) | Khóa chính |
| `name` | `str` | — | Tên thiết bị |
| `category` | `str` | `""` | Danh mục (ví dụ: cardio, strength) |
| `quantity` | `int` | `1` | Số lượng |
| `status` | `str` | `working` | Trạng thái thiết bị |
| `purchase_date` | `str` | `""` | Ngày mua (ISO format) |
| `notes` | `str` | `""` | Ghi chú |

#### Status Constants

```python
STATUS_WORKING     = "working"
STATUS_BROKEN      = "broken"
STATUS_MAINTENANCE = "maintenance"
```

#### Methods

| Method | Tham số | Trả về | Mô tả |
|--------|---------|--------|--------|
| `mark_broken()` | — | `None` | Đặt status = `broken`, cập nhật `updated_at` |
| `mark_maintenance()` | — | `None` | Đặt status = `maintenance`, cập nhật `updated_at` |
| `mark_working()` | — | `None` | Đặt status = `working`, cập nhật `updated_at` |
| `is_available()` | — | `bool` | Trả về `True` nếu status == `working` |

```python
class Equipment(BaseModel):
    def __init__(self, name: str, category: str = "",
                 quantity: int = 1, purchase_date: str = "",
                 notes: str = ""):
        super().__init__()
        self.name = name
        self.category = category
        self.quantity = quantity
        self.status = STATUS_WORKING
        self.purchase_date = purchase_date
        self.notes = notes

    def mark_broken(self):
        self.status = STATUS_BROKEN
        self.updated_at = datetime.now()

    def mark_maintenance(self):
        self.status = STATUS_MAINTENANCE
        self.updated_at = datetime.now()

    def mark_working(self):
        self.status = STATUS_WORKING
        self.updated_at = datetime.now()

    def is_available(self) -> bool:
        return self.status == STATUS_WORKING
```

---

### 3.5 `app/models/__init__.py` — Export

**Mô tả:** File export tập trung để các module khác import model qua `app.models`.

```python
from app.models.base import BaseModel
from app.models.member import Member
from app.models.membership import MembershipPlan, MembershipSubscription
from app.models.equipment import Equipment

__all__ = [
    "BaseModel",
    "Member",
    "MembershipPlan",
    "MembershipSubscription",
    "Equipment",
]
```

---

---

## 4. Tầng GUI — `gui/` (hoàn thành 2026-03-19)

### Cấu trúc

```
gui/
├── __init__.py
├── theme.py                  # Màu sắc, font size, spacing constants
├── dashboard.py              # Dashboard screen chính
└── components/
    ├── __init__.py
    ├── sidebar.py            # Sidebar navigation (reusable)
    └── header.py             # Top bar (reusable)

app/
└── main.py                   # Entry point: ft.app(target=main)
```

### `gui/theme.py`

Định nghĩa toàn bộ design tokens dùng chung:

| Nhóm | Hằng số tiêu biểu |
|------|-------------------|
| Màu sắc | `ORANGE`, `SIDEBAR_BG`, `GREEN`, `AMBER`, `RED`, `GRAY`, `BG`, `CARD_BG` |
| Typography | `FONT_XS`(11) → `FONT_3XL`(28) |
| Spacing | `PAD_XS`(4) → `PAD_2XL`(24) |
| Sizing | `SIDEBAR_WIDTH`(220), `HEADER_HEIGHT`(64), `CARD_RADIUS`(12) |

### `gui/components/sidebar.py`

- `Sidebar(page, active_route)` → `ft.Container`
- Logo "GymAdmin / MANAGEMENT SYSTEM"
- 5 nav items: Dashboard, Members, Gym Packages, Equipment, Reports
- Item active: nền cam (`#F97316`), text trắng; item thường: text xám
- Nút "+ Add Member" cuối sidebar (nền cam, bo góc)

### `gui/components/header.py`

- `Header(page)` → `ft.Container`
- Search bar (placeholder: "Search members, packages...")
- Icon chuông với badge cam (thông báo chưa đọc)
- Avatar hình tròn + tên "Admin User / Super Manager"

### `gui/dashboard.py`

Các widget con:

| Widget | Mô tả |
|--------|--------|
| `stat_card(icon, label, value, badge_text, badge_color)` | 4 KPI cards: Total Members, Expiring Soon, Monthly Revenue, Maintenance Needed |
| `member_row(name, initials, avatar_color, status, joined)` | 1 dòng bảng Recent Member Activity (badge Active/Expired/Pending) |
| `revenue_chart()` | Bar chart 6 tháng dùng `ft.Container` custom |
| `active_growth_chart()` | 3 `ft.ProgressBar` nằm ngang theo loại membership |
| `package_card(name, price, period, member_count, duration_label, is_popular)` | Card gói tập; gói "Elite Annual" có badge POPULAR |
| `equipment_card(name, wear_pct, purchased, status)` | Card thiết bị với `ft.ProgressBar` wear level |

### `app/main.py`

```python
import flet as ft
from gui.dashboard import DashboardScreen

def main(page: ft.Page):
    page.title = "GymAdmin Management System"
    page.window_width = 1280
    page.window_height = 800
    page.bgcolor = "#F5F5F5"
    page.padding = 0
    page.add(DashboardScreen(page))

ft.app(target=main)
```

### Chạy ứng dụng

```bash
cd E:/gym_management
python app/main.py
```

---

## 5. Điểm còn thiếu ở tầng Models so với `note.txt`

| Field / File thiếu | Lý do | Ưu tiên |
|---------------------|-------|---------|
| `member.photo` | Field ảnh hội viên có trong yêu cầu `note.txt` nhưng chưa được thêm | Trung bình |
| `equipment.location` | Field vị trí thiết bị có trong yêu cầu `note.txt` nhưng chưa được thêm | Thấp |
| `app/core/database.py` | SQLite3 schema và kết nối chưa được xây dựng | **Cao** |
| Validation | Chưa có kiểm tra định dạng số điện thoại, ngày tháng, email | Trung bình |

---

## 6. Phần chưa làm (ngoài phạm vi hiện tại)

| Module | Mô tả | Ưu tiên |
|--------|--------|---------|
| `app/core/database.py` | Tạo kết nối SQLite3, định nghĩa schema các bảng (`members`, `membership_plans`, `subscriptions`, `equipment`) | **Cao** |
| `app/services/` | Business logic: tìm kiếm, lọc, thống kê, xử lý nghiệp vụ | **Cao** |
| `app/api/` hoặc `app/repositories/` | Data access layer — CRUD với SQLite3 | **Cao** |
| GUI ↔ Data binding | Kết nối `gui/dashboard.py` với dữ liệu thật từ DB (hiện tại dùng mock data) | Trung bình |
| Các màn hình GUI còn lại | Members, Gym Packages, Equipment, Reports screens | Trung bình |
| `member.photo` | Field ảnh hội viên theo `note.txt` | Thấp |
| `equipment.location` | Field vị trí thiết bị theo `note.txt` | Thấp |

---

## 7. Tóm tắt tiến độ

### Tầng Models

| File | Class(es) | Trạng thái |
|------|-----------|------------|
| `app/models/base.py` | `BaseModel` | Hoàn thành (đã sửa bug indent + is_active) |
| `app/models/member.py` | `Member` | Hoàn thành (thiếu `photo`) |
| `app/models/membership.py` | `MembershipPlan`, `MembershipSubscription` | Hoàn thành |
| `app/models/equipment.py` | `Equipment` | Hoàn thành (thiếu `location`) |
| `app/models/__init__.py` | — | Hoàn thành |

### Tầng GUI

| File | Mô tả | Trạng thái |
|------|--------|------------|
| `gui/theme.py` | Design tokens (màu, font, spacing) | Hoàn thành |
| `gui/components/sidebar.py` | Sidebar navigation | Hoàn thành |
| `gui/components/header.py` | Top bar | Hoàn thành |
| `gui/dashboard.py` | Dashboard screen (mock data) | Hoàn thành |
| `app/main.py` | Entry point Flet | Hoàn thành |

### Tầng Core / Services / Data (chưa làm)

| File | Trạng thái |
|------|------------|
| `app/core/database.py` | Chưa làm |
| `app/services/*.py` | Stub rỗng |
| `app/api/*.py` | Stub rỗng |
