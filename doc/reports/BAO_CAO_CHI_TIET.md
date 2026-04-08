# BÁO CÁO KỸ THUẬT CHI TIẾT — Gym Management System

**Ngày tạo:** 2026-03-20 21:40
**Cập nhật lần cuối:** 2026-04-04
**Người viết:** Claude Code (AI Assistant)
**Phạm vi:** Toàn bộ hệ thống — `app/`, `gui/`, `data/`
**Trạng thái dự án:** Đang phát triển (MVP hoàn thiện ~85%)

---

## MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Sơ đồ kiến trúc tổng thể](#2-sơ-đồ-kiến-trúc-tổng-thể)
3. [Phân tích chi tiết từng tầng (Layer)](#3-phân-tích-chi-tiết-từng-tầng)
   - 3.1 [Core Layer — Cấu hình, Database, Bảo mật](#31-core-layer)
   - 3.2 [Models Layer — Cấu trúc dữ liệu](#32-models-layer)
   - 3.3 [Repositories Layer — Data Access](#33-repositories-layer)
   - 3.4 [Services Layer — Business Logic](#34-services-layer)
   - 3.5 [GUI Layer — Giao diện người dùng](#35-gui-layer)
4. [Phân tích luồng dữ liệu (Data Flow)](#4-phân-tích-luồng-dữ-liệu)
5. [Đánh giá kỹ thuật](#5-đánh-giá-kỹ-thuật)
6. [Tổng kết](#6-tổng-kết)

---

## 1. Tổng quan hệ thống

### 1.1 Mục đích

Gym Management System là ứng dụng desktop quản lý phòng gym, cho phép:
- **Quản lý hội viên** (CRUD, tìm kiếm, lọc theo giới tính / trạng thái gói tập)
- **Quản lý gói tập** (tạo gói, đăng ký hội viên, hủy, tự động hết hạn)
- **Quản lý thiết bị** (CRUD, lọc theo trạng thái hoạt động / bảo trì / hỏng)
- **Dashboard tổng quan** (KPI, biểu đồ doanh thu, cảnh báo sắp hết hạn)
- **Báo cáo** (thống kê hội viên, doanh thu, thiết bị)

### 1.2 Stack công nghệ

| Thành phần | Công nghệ | Phiên bản | Vai trò |
|-----------|-----------|-----------|---------|
| Ngôn ngữ | Python | 3.10+ | Ngôn ngữ chính, không dùng ORM |
| GUI Framework | Flet | 0.82.2 (pinned) | Render giao diện desktop |
| Database | SQLite3 | Built-in | Lưu trữ dữ liệu cục bộ |
| Auth | Plaintext compare | — | MVP, chưa có password hashing |

### 1.3 Cấu trúc thư mục tổng thể

```
gym_management/
├── app/                          # Backend: core + models + repos + services
│   ├── main.py                   # Entry point: ft.run(main)
│   ├── core/
│   │   ├── config.py             # Biến cấu hình (DB path, credentials)
│   │   ├── database.py           # SQLite3 connection + schema init
│   │   └── security.py           # check_login()
│   ├── models/
│   │   ├── base.py               # BaseModel (UUID, timestamps, soft delete)
│   │   ├── member.py             # Member
│   │   ├── membership.py         # MembershipPlan + MembershipSubscription
│   │   └── equipment.py          # Equipment
│   ├── repositories/
│   │   ├── member_repo.py        # CRUD + search Members
│   │   ├── membership_repo.py    # CRUD Plans + Subscriptions + expiring_soon
│   │   └── equipment_repo.py     # CRUD + filter by status/category
│   ├── services/
│   │   ├── member_svc.py         # Validate + CRUD + stats
│   │   ├── membership_svc.py     # Plans + Subscriptions + revenue + auto-expire
│   │   ├── equipment_svc.py      # Validate + CRUD + summary
│   │   └── trainer_svc.py        # Validate + CRUD HLV + reset PIN
│   ├── api/                      # ❌ Stub trống (không sử dụng)
│   └── utils/                    # ❌ Stub trống
├── gui/                          # Frontend: Flet screens + components
│   ├── theme.py                  # Design tokens (màu, font, spacing)
│   ├── admin/                    # GUI Admin
│   │   ├── login.py              # Màn hình đăng nhập
│   │   ├── dashboard.py          # Dashboard tổng quan
│   │   ├── members.py            # Quản lý hội viên
│   │   ├── memberships.py        # Gói tập & Đăng ký
│   │   ├── equipment.py          # Quản lý thiết bị
│   │   ├── trainers.py           # Quản lý huấn luyện viên (MỚI)
│   │   ├── reports.py            # Báo cáo thống kê
│   │   └── components/
│   │       ├── sidebar.py        # Sidebar điều hướng (reusable)
│   │       └── header.py         # Header + search bar (reusable)
│   └── user/                     # GUI User (đang phát triển)
├── data/
│   └── gym_db.db                 # SQLite database file
├── doc/                          # Tài liệu dự án
│   ├── note.txt                  # Yêu cầu ban đầu
│   ├── report_plan.md            # Kế hoạch & tiến độ
│   ├── AI_REPORT.md              # Nhật ký thay đổi
│   └── UI_REVIEW.md              # Review giao diện
└── requirements.txt              # Dependencies (flet==0.82.2)
```

---

## 2. Sơ đồ kiến trúc tổng thể

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GUI Layer (Flet)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌───────────────┐  │
│  │ login.py │ │dashboard │ │  members.py  │ │memberships.py │  │
│  └──────────┘ └──────────┘ └──────────────┘ └───────────────┘  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ equipment.py │ │ trainers.py  │ │  reports.py  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ components/: sidebar.py + header.py + theme.py       │       │
│  └──────────────────────────────────────────────────────┘       │
├─────────────────────────────────────────────────────────────────┤
│                      Services Layer                             │
│  ┌─────────────┐ ┌────────────────┐ ┌───────────────┐          │
│  │member_svc.py│ │membership_svc.py│ │equipment_svc.py│         │
│  └─────────────┘ └────────────────┘ └───────────────┘          │
│  ┌──────────────┐                                               │
│  │trainer_svc.py│                                               │
│  └──────────────┘                                               │
│  Validation → Business Logic → Gọi Repository                  │
├─────────────────────────────────────────────────────────────────┤
│                    Repositories Layer                            │
│  ┌─────────────┐ ┌────────────────┐ ┌───────────────┐          │
│  │member_repo  │ │membership_repo │ │equipment_repo │          │
│  └─────────────┘ └────────────────┘ └───────────────┘          │
│  ┌──────────────┐                                               │
│  │trainer_repo  │                                               │
│  └──────────────┘                                               │
│  SQL thuần (INSERT/SELECT/UPDATE) → Model objects               │
├─────────────────────────────────────────────────────────────────┤
│                      Models Layer                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ ┌───────────┐  │
│  │ BaseModel│ │ Member   │ │MembershipPlan    │ │ Equipment │  │
│  │          │ │          │ │MembershipSubscr. │ │           │  │
│  └──────────┘ └──────────┘ └──────────────────┘ └───────────┘  │
│  ┌──────────┐                                                   │
│  │ Trainer  │                                                   │
│  └──────────┘                                                   │
├─────────────────────────────────────────────────────────────────┤
│                       Core Layer                                │
│  ┌──────────┐ ┌────────────┐ ┌──────────────┐                  │
│  │ config.py│ │ database.py│ │ security.py  │                  │
│  └──────────┘ └────────────┘ └──────────────┘                  │
│  Settings     SQLite3 conn     check_login()                    │
├─────────────────────────────────────────────────────────────────┤
│                     SQLite3 Database                            │
│  ┌──────────┐ ┌────────────────┐ ┌──────────────┐ ┌──────────┐│
│  │ members  │ │membership_plans│ │subscriptions │ │equipment ││
│  └──────────┘ └────────────────┘ └──────────────┘ └──────────┘│
│  ┌──────────┐                                                  │
│  │ trainers │                                                  │
│  └──────────┘                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Navigation Flow

```
ft.run(main)
    │
    ├── init_db()                    # Tạo bảng nếu chưa có
    ├── page.navigate = navigate     # Inject router function
    └── navigate("login")
         │
         ├── LoginScreen ──[đăng nhập thành công]──→ DashboardScreen
         │                                                │
         │         Sidebar điều hướng: ←──────────────────┘
         │         ├── "dashboard" → DashboardScreen
         │         ├── "members"   → MembersScreen
         │         ├── "packages"  → MembershipsScreen
         │         ├── "equipment" → EquipmentScreen
         │         ├── "trainers"  → TrainersScreen
         │         └── "reports"   → ReportsScreen
         │
         └── Mỗi lần navigate():
              page.overlay.clear()      # Xóa dialog cũ
              page.controls.clear()     # Xóa UI cũ
              page.on_search_change = None  # Reset search callback
              page.add(NewScreen(page))
              page.update()
```

---

## 3. Phân tích chi tiết từng tầng

---

### 3.1 Core Layer

#### 3.1.1 `app/core/config.py` — Cấu hình hệ thống

**Mục đích:** Tập trung toàn bộ hằng số cấu hình, tránh hardcode rải rác.

```python
# Dòng 4: Tính đường dẫn gốc dự án
# os.path.abspath(__file__) → E:/gym_management/app/core/config.py
# dirname x3 → E:/gym_management/
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
| `WINDOW_WIDTH` | `1280` | ❌ | Chiều rộng cửa sổ |
| `WINDOW_HEIGHT` | `800` | ❌ | Chiều cao cửa sổ |
| `ADMIN_USERNAME` | `"admin"` | ✅ `GYM_USERNAME` | Tên đăng nhập |
| `ADMIN_PASSWORD` | `"admin123"` | ✅ `GYM_PASSWORD` | Mật khẩu |

**Liên kết:** `database.py` import `DB_PATH`, `security.py` import `ADMIN_USERNAME/PASSWORD`, `main.py` import `APP_TITLE/WIDTH/HEIGHT`.

---

#### 3.1.2 `app/core/database.py` — Kết nối SQLite3

**Mục đích:** Quản lý kết nối database và khởi tạo schema (4 bảng + 6 indexes).

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

**`PRAGMA foreign_keys = ON`**: SQLite mặc định TẮT kiểm tra FK. Dòng này bật lên để đảm bảo `subscriptions.member_id` phải tồn tại trong `members.id`.

##### Khối 2: `init_db()` — Tạo schema

```python
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        # 4 bảng: members, membership_plans, subscriptions, equipment
        conn.execute("CREATE TABLE IF NOT EXISTS members (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS membership_plans (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS subscriptions (...)")
        conn.execute("CREATE TABLE IF NOT EXISTS equipment (...)")

        # 6 indexes tăng tốc query
        conn.execute("CREATE INDEX IF NOT EXISTS idx_members_phone ON members(phone)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_members_is_active ON members(is_active)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subs_member_id ON subscriptions(member_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subs_plan_id ON subscriptions(plan_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subs_status ON subscriptions(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status)")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

**Tại sao không dùng `get_db()` cho `init_db()`?**
Ban đầu code dùng `executescript()` — hàm này tự commit ngầm, không tương thích với context manager. Sau khi fix sang `execute()` từng lệnh, pattern vẫn được giữ để tường minh hơn.

**`CREATE TABLE IF NOT EXISTS`**: Idempotent — chạy nhiều lần không lỗi, chỉ tạo bảng nếu chưa tồn tại.

##### Database Schema

| Bảng | Cột | Kiểu | Ràng buộc | Mô tả |
|------|-----|------|-----------|-------|
| **members** | `id` | TEXT | PK | UUID4 |
| | `name` | TEXT | NOT NULL | Họ tên |
| | `phone` | TEXT | NOT NULL | SĐT |
| | `email` | TEXT | — | Email |
| | `gender` | TEXT | — | male/female/other |
| | `date_of_birth` | TEXT | — | YYYY-MM-DD |
| | `address` | TEXT | — | Địa chỉ |
| | `emergency_contact` | TEXT | — | Liên hệ khẩn cấp |
| | `photo` | TEXT | — | Đường dẫn ảnh |
| | `created_at` | TEXT | NOT NULL | ISO datetime |
| | `updated_at` | TEXT | NOT NULL | ISO datetime |
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
| | `phone` | TEXT | NOT NULL | SĐT (dùng để đăng nhập user app) |
| | `email` | TEXT | — | Email |
| | `specialization` | TEXT | — | Chuyên môn: "Yoga", "Boxing", "Gym"... |
| | `pin` | TEXT | NOT NULL DEFAULT '000000' | PIN 6 chữ số (đăng nhập user app) |
| | `created_at/updated_at/is_active` | — | — | (giống members) |

**Quan hệ giữa các bảng:**

```
members ──1:N──→ subscriptions ←──N:1── membership_plans
                   (member_id FK)         (plan_id FK)

equipment: bảng độc lập, không có FK
trainers: bảng độc lập, không có FK
```

---

#### 3.1.3 `app/core/security.py` — Xác thực

**Mục đích:** Kiểm tra thông tin đăng nhập.

```python
from app.core.config import ADMIN_USERNAME, ADMIN_PASSWORD

def check_login(username: str, password: str) -> bool:
    """Kiểm tra thông tin đăng nhập. Trả về True nếu hợp lệ."""
    return username.strip() == ADMIN_USERNAME and password == ADMIN_PASSWORD
```

- `username.strip()`: Bỏ khoảng trắng đầu/cuối → người dùng gõ thừa space vẫn đăng nhập được.
- `password` **không strip**: Mật khẩu có thể chứa space ở đầu/cuối theo ý người dùng.
- So sánh plaintext — **chấp nhận cho MVP**, cần chuyển sang bcrypt/hashlib cho production.

**Liên kết:** `gui/login.py` gọi `check_login()` khi user nhấn nút đăng nhập.

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

**Tại sao `*args, **kwargs` trong `__init__`?**
- Cho phép subclass truyền thêm tham số mà không gây lỗi. Tuy nhiên, BaseModel bản thân không dùng chúng.

```python
    def update(self):
        """Cập nhật updated_at mỗi khi dữ liệu thay đổi"""
        self.updated_at = datetime.now()
```

> **Lưu ý quan trọng:** `update()` KHÔNG nhận kwargs. Muốn cập nhật field, caller phải set thủ công rồi gọi `update()`:
> ```python
> member.name = "Tên mới"
> member.update()  # Chỉ cập nhật updated_at
> ```

```python
    def delete(self):
        """Xóa ảo (soft delete) — đánh dấu is_active = False"""
        self.is_active = False
        self.update()   # Cũng cập nhật updated_at
```

**Soft Delete pattern:** Không xóa record khỏi database, chỉ đánh dấu `is_active = 0`. Lợi ích:
- Giữ lịch sử dữ liệu (audit trail)
- Có thể khôi phục nếu xóa nhầm
- Không phá vỡ FK ở bảng `subscriptions`

```python
    def to_dict(self):
        """Chuyển object → dict, datetime → ISO string"""
        return {
            k: v.isoformat() if isinstance(v, datetime) else v
            for k, v in self.__dict__.items()
        }
```

**Dict comprehension** duyệt tất cả attributes, tự chuyển `datetime` → string ISO. Hữu ích khi cần serialize JSON.

---

#### 3.2.2 `app/models/member.py` — Member

```python
class Member(BaseModel):
    def __init__(self, name, phone, email=None, gender=None,
                 date_of_birth=None, address=None, emergency_contact=None,
                 photo=None, *args, **kwargs):
        super().__init__(*args, **kwargs)   # Gọi BaseModel.__init__ → tạo id, timestamps
        self.name = name
        self.phone = phone
        self.email = email
        self.gender = gender                        # 'male' | 'female' | 'other'
        self.date_of_birth = date_of_birth          # datetime.date
        self.address = address
        self.emergency_contact = emergency_contact  # số điện thoại khẩn cấp
        self.photo = photo                          # đường dẫn file ảnh
```

| Field | Kiểu | Bắt buộc | Mô tả |
|-------|------|:--------:|-------|
| `name` | str | ✅ | Họ tên — validate ở service |
| `phone` | str | ✅ | SĐT — validate regex ở service |
| `email` | str/None | ❌ | Email — validate regex ở service |
| `gender` | str/None | ❌ | `male`/`female`/`other` |
| `date_of_birth` | str/None | ❌ | Dạng `YYYY-MM-DD` |
| `address` | str/None | ❌ | Địa chỉ |
| `emergency_contact` | str/None | ❌ | Liên hệ khẩn cấp |
| `photo` | str/None | ❌ | Đường dẫn ảnh (chưa implement upload) |

---

#### 3.2.3 `app/models/membership.py` — MembershipPlan + MembershipSubscription

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
    # Status constants — định nghĩa trên class để dùng chung
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, member_id, plan_id, duration_days, price_paid,
                 start_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_id = member_id      # FK → Member.id
        self.plan_id = plan_id          # FK → MembershipPlan.id
        self.price_paid = price_paid    # Giá thực tế (có thể khác giá gốc)

        # Chuẩn hóa start_date — phòng khi caller truyền date thuần
        if start_date is None:
            start_date = datetime.now()
        elif isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        self.start_date = start_date
        self.end_date = self.start_date + timedelta(days=duration_days)  # Tự tính
        self.status = self.STATUS_ACTIVE
```

**Tại sao cần chuẩn hóa `start_date`?**
- `datetime` là subclass của `date` trong Python → `isinstance(dt, date)` trả về `True` cho cả hai.
- Kiểm tra `isinstance(start_date, date) and not isinstance(start_date, datetime)` để chỉ convert `date` thuần.
- `datetime.combine(date_obj, datetime.min.time())` → `date(2026,3,20)` thành `datetime(2026,3,20,0,0,0)`.
- Tránh lỗi `TypeError: '>' not supported between instances of 'datetime' and 'date'` khi so sánh.

**Methods quan trọng:**

```python
    def is_expired(self):
        return datetime.now() > self.end_date

    def days_remaining(self):
        remaining = (self.end_date - datetime.now()).days
        return max(remaining, 0)    # Không trả số âm

    def cancel(self):
        self.status = self.STATUS_CANCELLED
        self.update()               # Gọi BaseModel.update() → cập nhật updated_at

    def refresh_status(self):
        """Tự cập nhật status nếu đã quá hạn (chỉ với active)"""
        if self.status == self.STATUS_ACTIVE and self.is_expired():
            self.status = self.STATUS_EXPIRED
            self.update()
```

---

#### 3.2.4 `app/models/equipment.py` — Equipment

```python
class Equipment(BaseModel):
    STATUS_WORKING = "working"          # Hoạt động tốt
    STATUS_BROKEN = "broken"            # Hỏng
    STATUS_MAINTENANCE = "maintenance"  # Đang bảo trì

    def __init__(self, name, category, quantity=1,
                 purchase_date=None, location=None, notes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.category = category        # "Cardio", "Tạ tự do", "Máy lực"
        self.quantity = quantity
        self.status = self.STATUS_WORKING
        self.purchase_date = purchase_date
        self.location = location        # "Tầng 1", "Khu Cardio"
        self.notes = notes
```

**State machine cho status:**

```
                  mark_maintenance()
    WORKING ←──────────────→ MAINTENANCE
       ↑                          │
       │  mark_working()          │
       │                          │
       ├──── mark_broken() ──→ BROKEN
       │                          │
       └───── mark_working() ─────┘
```

Mỗi method `mark_*()` có thể nhận `notes` tùy chọn (trừ `mark_working()`), cho phép ghi lý do.

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

**So sánh với Member:** Trainer đơn giản hơn Member (không có gender, DOB, address, emergency_contact, photo). Cả hai đều kế thừa `BaseModel` → có id, created_at, updated_at, is_active.

---

### 3.3 Repositories Layer

**Pattern chung:** Mỗi repository file chứa:
1. `_row_to_model(row)` — chuyển `sqlite3.Row` → Model object
2. `create(model)` — INSERT
3. `get_by_id(id)` — SELECT WHERE id
4. `get_all(active_only)` — SELECT (có filter soft delete)
5. `update(model)` — UPDATE
6. `delete(id)` — Soft delete (UPDATE is_active = 0)

#### 3.3.1 `app/repositories/member_repo.py`

##### Hàm `_row_to_member(row)` — Hydration pattern

```python
def _row_to_member(row) -> Member:
    m = Member.__new__(Member)    # Tạo instance MÀ KHÔNG gọi __init__
    m.id = row["id"]              # Gán trực tiếp từ DB
    m.name = row["name"]
    # ... (gán tất cả fields)
    m.created_at = datetime.fromisoformat(row["created_at"])  # Parse ISO string → datetime
    m.is_active = bool(row["is_active"])   # SQLite lưu 0/1 → Python True/False
    return m
```

**Tại sao dùng `__new__` thay vì `Member(name, phone)`?**
- `__new__` tạo instance rỗng, bypass `__init__` (không tạo UUID mới, không set `created_at = now()`).
- Khi đọc từ DB, ta muốn GIỮ nguyên `id` và `created_at` gốc, không tạo mới.
- Đây là pattern phổ biến cho Data Mapper / ORM-free mapping.

##### Hàm `search(keyword)`

```python
def search(keyword: str) -> list[Member]:
    with get_db() as conn:
        like = f"%{keyword}%"   # Wildcard SQL LIKE
        rows = conn.execute(
            """SELECT * FROM members WHERE is_active = 1
               AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)
               ORDER BY name""",
            (like, like, like)   # Parameterized query → chống SQL injection
        ).fetchall()
    return [_row_to_member(r) for r in rows]
```

**Bảo mật:** Dùng `?` placeholder thay vì string interpolation → an toàn SQL injection.

---

#### 3.3.2 `app/repositories/membership_repo.py`

File lớn nhất trong repo layer, quản lý cả Plans lẫn Subscriptions.

**Hàm đặc biệt — `get_expiring_soon(days=7)`:**

```python
def get_expiring_soon(days: int = 7) -> list[MembershipSubscription]:
    cutoff = (datetime.now() + timedelta(days=days)).isoformat()   # 7 ngày nữa
    now = datetime.now().isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM subscriptions WHERE status = 'active'
               AND end_date <= ? AND end_date >= ? ORDER BY end_date""",
            (cutoff, now)    # Giữa hôm nay và 7 ngày tới
        ).fetchall()
    return [_row_to_sub(r) for r in rows]
```

**Logic:** Tìm subscription có `end_date` nằm trong khoảng `[now, now+7days]` VÀ đang `active`. Dùng cho Dashboard "Sắp hết hạn" và Reports.

**Hàm `expire_old_subscriptions()`:**

```python
def expire_old_subscriptions():
    now = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE subscriptions SET status='expired', updated_at=? "
            "WHERE status='active' AND end_date < ?",
            (now, now)
        )
```

**Bulk update** — đổi tất cả subscription đã quá hạn sang `expired` trong 1 câu SQL, hiệu quả hơn lặp từng record.

---

#### 3.3.3 `app/repositories/equipment_repo.py`

Tương tự member_repo, thêm hai hàm filter:

```python
def get_by_status(status: str) -> list[Equipment]:
    # SELECT WHERE status = ? AND is_active = 1

def get_by_category(category: str) -> list[Equipment]:
    # SELECT WHERE category = ? AND is_active = 1
```

Index `idx_equipment_status` tăng tốc `get_by_status()`.

---

#### 3.3.4 `app/repositories/trainer_repo.py`

Tuân thủ cùng pattern với member_repo:

##### Hàm `_row_to_trainer(row)` — Hydration

```python
def _row_to_trainer(row) -> Trainer:
    t = Trainer.__new__(Trainer)   # Tạo instance không gọi __init__
    t.id = row["id"]
    t.name = row["name"]
    t.phone = row["phone"]
    t.email = row["email"]
    t.specialization = row["specialization"]
    t.pin = row["pin"]
    t.created_at = datetime.fromisoformat(row["created_at"])
    t.updated_at = datetime.fromisoformat(row["updated_at"])
    t.is_active = bool(row["is_active"])
    return t
```

**Giống `_row_to_member()`**: Dùng `__new__()` để giữ nguyên id và timestamps từ database.

##### CRUD Functions

| Hàm | SQL | Mô tả |
|-----|-----|-------|
| `create(trainer)` | `INSERT INTO trainers` | Thêm HLV mới |
| `get_by_id(id)` | `SELECT * WHERE id = ?` | Tìm theo ID |
| `get_by_phone(phone)` | `SELECT * WHERE phone = ? AND is_active = 1` | Tìm theo SĐT (đăng nhập) |
| `get_all(active_only)` | `SELECT * ORDER BY name` | Lấy danh sách |
| `update(trainer)` | `UPDATE trainers SET ... WHERE id = ?` | Cập nhật thông tin |
| `delete(id)` | `DELETE FROM trainers WHERE id = ?` | Xóa (hard delete) |

**`get_by_phone()`** — hàm đặc biệt so với các repo khác: dùng cho đăng nhập user app, chỉ tìm HLV active (`is_active = 1`).

Index `idx_trainers_phone` tăng tốc `get_by_phone()`.

---

### 3.4 Services Layer

**Pattern chung:** Service nhận raw input từ GUI → validate → gọi repository → trả model.

#### 3.4.1 `app/services/member_svc.py`

##### Validation

```python
def _validate(name: str, phone: str, email: str = None):
    if not name or not name.strip():
        raise ValueError("Tên hội viên không được để trống")
    if not phone or not phone.strip():
        raise ValueError("Số điện thoại không được để trống")
    if not re.fullmatch(r"[0-9+\-\s]{7,15}", phone.strip()):
        raise ValueError("Số điện thoại không hợp lệ")
    if email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email.strip()):
        raise ValueError("Email không hợp lệ")
```

| Regex | Ý nghĩa | Ví dụ hợp lệ |
|-------|---------|--------------|
| `[0-9+\-\s]{7,15}` | 7-15 ký tự: số, +, -, space | `0912345678`, `+84-912-345-678` |
| `[^@]+@[^@]+\.[^@]+` | Basic email format | `user@example.com` |

**`re.fullmatch`** kiểm tra TOÀN BỘ chuỗi khớp pattern (khác `re.match` chỉ kiểm tra đầu chuỗi).

##### `register_member()` vs `update_member()`

```python
def register_member(name, phone, email=None, ...):
    _validate(name, phone, email)
    member = Member(name=name.strip(), phone=phone.strip(), ...)
    return member_repo.create(member)    # INSERT mới

def update_member(member: Member):
    """Caller tự mutate member rồi truyền vào, service chỉ validate + save."""
    _validate(member.name, member.phone, member.email)
    return member_repo.update(member)    # UPDATE existing
```

**Design decision:** `update_member()` nhận object đã mutate — đơn giản hơn nhận kwargs rồi merge.

##### `get_member_stats()`

```python
def get_member_stats() -> dict:
    all_members = member_repo.get_all(active_only=False)  # Cả đã xóa
    active = [m for m in all_members if m.is_active]
    now = datetime.now()
    new_this_month = [
        m for m in active
        if m.created_at.year == now.year and m.created_at.month == now.month
    ]
    return {"total": len(all_members), "active": len(active), "new_this_month": len(new_this_month)}
```

Dùng cho Dashboard KPI và trang Members.

---

#### 3.4.2 `app/services/membership_svc.py`

**File phức tạp nhất**, cung cấp:
- CRUD Plans + Subscriptions
- Tính doanh thu theo tháng
- Thống kê số lượng subscription theo gói
- Auto-expire hàng loạt

##### `subscribe_member()` — Đăng ký gói tập

```python
def subscribe_member(member_id, plan_id, price_paid=None, start_date=None):
    plan = membership_repo.get_plan_by_id(plan_id)
    if not plan:
        raise ValueError("Không tìm thấy gói tập")
    sub = MembershipSubscription(
        member_id=member_id,
        plan_id=plan_id,
        duration_days=plan.duration_days,
        price_paid=price_paid if price_paid is not None else plan.price,
        # ↑ Nếu không truyền giá, lấy giá gốc của plan
        start_date=start_date or datetime.now(),
    )
    return membership_repo.create_subscription(sub)
```

**`price_paid if price_paid is not None`**: Kiểm tra `is not None` thay vì `if price_paid` vì giá 0 (`0.0`) vẫn hợp lệ nhưng falsy trong Python.

##### `get_monthly_revenue(months=6)` — Doanh thu 6 tháng gần nhất

```python
def get_monthly_revenue(months: int = 6) -> list[tuple[str, float]]:
    subs = membership_repo.get_all_subscriptions()
    now = datetime.now()
    result = []
    for i in range(months - 1, -1, -1):    # Lùi từ 5 tháng trước đến hiện tại
        month = now.month - i
        year = now.year
        while month <= 0:                    # Xử lý quay năm
            month += 12
            year -= 1
        total = sum(
            s.price_paid for s in subs
            if s.created_at.year == year and s.created_at.month == month
        )
        result.append((f"T{month}", total))
    return result
```

Trả về list `[("T10", 50000000), ("T11", 35000000), ...]` → dùng cho Revenue Chart trên Dashboard.

---

#### 3.4.3 `app/services/equipment_svc.py`

```python
def add_equipment(name, category, quantity=1, purchase_date=None,
                  notes=None, location=None):
    if not name or not name.strip():
        raise ValueError("Tên thiết bị không được để trống")
    if not category or not category.strip():
        raise ValueError("Loại thiết bị không được để trống")
    eq = Equipment(name=name.strip(), category=category.strip(),
                   quantity=quantity, purchase_date=purchase_date, notes=notes)
    eq.location = location    # Set sau vì Equipment.__init__ nhận location
    return equipment_repo.create(eq)

def update_equipment(eq, **kwargs):
    for k, v in kwargs.items():
        setattr(eq, k, v)     # Dynamic field update
    return equipment_repo.update(eq)
```

**`setattr(eq, k, v)`**: Pattern cho phép update bất kỳ field nào mà không cần liệt kê từng field. GUI gọi: `equipment_svc.update_equipment(eq, name="...", status="broken")`.

---

#### 3.4.4 `app/services/trainer_svc.py` — Quản lý HLV

##### Validation

```python
def _validate(name: str, phone: str, email: str = None):
    if not name or not name.strip():
        raise ValueError("Ten HLV khong duoc de trong")
    if not phone or not phone.strip():
        raise ValueError("So dien thoai khong duoc de trong")
    if not re.fullmatch(r"[0-9+\-\s]{7,15}", phone.strip()):
        raise ValueError("So dien thoai khong hop le")
    if email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email.strip()):
        raise ValueError("Email khong hop le")
```

**Giống `member_svc._validate()`**: Cùng pattern regex cho phone và email. Tái sử dụng logic, đảm bảo nhất quán.

##### CRUD Functions

```python
def register_trainer(name, phone, email=None, specialization=None) -> Trainer:
    _validate(name, phone, email)
    trainer = Trainer(name=name.strip(), phone=phone.strip(),
                      email=email.strip() if email else None,
                      specialization=specialization.strip() if specialization else None)
    return trainer_repo.create(trainer)

def update_trainer(trainer: Trainer) -> Trainer:
    _validate(trainer.name, trainer.phone, trainer.email)
    return trainer_repo.update(trainer)
```

**Design decision:** Giống `member_svc` — `update_trainer()` nhận object đã mutate, chỉ validate rồi save.

##### `reset_pin()` — Reset PIN HLV

```python
def reset_pin(trainer_id: str, new_pin: str) -> Trainer:
    if not re.fullmatch(r"\d{6}", new_pin):
        raise ValueError("PIN phải gồm đúng 6 chữ số")
    trainer = trainer_repo.get_by_id(trainer_id)
    if not trainer:
        raise ValueError("Không tìm thấy HLV")
    trainer.pin = new_pin
    return trainer_repo.update(trainer)
```

**Regex `\d{6}`**: Chính xác 6 chữ số (0-9). Đơn giản hơn phone regex vì PIN là format cố định.

**Use case:** Admin reset PIN cho HLV khi HLV quên — gọi từ GUI admin `trainers.py`.

##### `get_trainer_members()` — Danh sách học viên

```python
def get_trainer_members(trainer_id: str) -> list:
    members = member_repo.get_all(active_only=True)
    result = []
    for member in members:
        subs = membership_repo.get_subscriptions_by_member(member.id)
        active_subs = [s for s in subs if s.status == "active"]
        if active_subs:
            result.append({"member": member, "subscription": active_subs[0]})
    return result
```

**Hạn chế hiện tại:** Chưa có bảng liên kết `trainer_members` trong database, nên trả về tất cả member có gói tập active. Khi có bảng liên kết, sẽ filter theo `trainer_id`.

---

### 3.5 GUI Layer

#### 3.5.1 `app/main.py` — Entry Point + Router

##### Khối khởi tạo

```python
import sys, os
# Thêm thư mục gốc vào sys.path để import gui/ từ app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from app.core.config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from app.core.database import init_db

def main(page: ft.Page):
    # Khởi tạo database
    try:
        init_db()
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo database: {e}")
        raise

    page.title = APP_TITLE
    page.window_width = WINDOW_WIDTH
    page.window_height = WINDOW_HEIGHT
    page.bgcolor = "#F5F5F5"
    page.padding = 0
```

**`sys.path.insert(0, ...)`**: Thêm thư mục gốc dự án vào đầu module search path. Cần thiết vì `main.py` nằm trong `app/` nhưng cần import `gui/` (đồng cấp).

##### Router Pattern

```python
    def navigate(route: str):
        page.overlay.clear()          # Xóa tất cả dialog cũ
        page.controls.clear()         # Xóa UI cũ hoàn toàn
        page.on_search_change = None  # Reset callback header search
        if route == "login":
            from gui.login import LoginScreen
            page.add(LoginScreen(page))
        elif route == "dashboard":
            from gui.dashboard import DashboardScreen
            page.add(DashboardScreen(page))
        # ... các route khác
        page.update()

    page.navigate = navigate  # Inject vào page object
    navigate("login")         # Khởi động tại login

ft.run(main)
```

**Tại sao `page.overlay.clear()`?**
Mỗi màn hình thêm dialog vào `page.overlay`. Nếu không clear, dialog bị tích lũy qua mỗi lần navigate → memory leak + UI bug.

**Tại sao Lazy import (`from gui.xxx import ...` bên trong function)?**
- Tránh circular import (gui import services, services import repos, repos import database).
- Chỉ load module khi thực sự cần → startup nhanh hơn.

**`page.navigate = navigate`** — Monkey-patching: gắn function tùy chỉnh lên page object. Mọi screen có thể gọi `page.navigate("route")` để chuyển trang. Đây là pattern thay thế cho routing framework.

---

#### 3.5.2 `gui/theme.py` — Design System

**Mục đích:** Tập trung toàn bộ design tokens, đảm bảo UI nhất quán.

| Nhóm | Hằng số | Ví dụ | Ý nghĩa |
|------|---------|-------|---------|
| **Colors** | `ORANGE` | `#F97316` | Primary action, brand color |
| | `GREEN/GREEN_LIGHT` | `#22C55E / #DCFCE7` | Trạng thái tốt (active, working) |
| | `AMBER/AMBER_LIGHT` | `#F59E0B / #FEF3C7` | Cảnh báo (sắp hết hạn, bảo trì) |
| | `RED/RED_LIGHT` | `#EF4444 / #FEE2E2` | Nguy hiểm (hỏng, quá hạn, xóa) |
| | `SIDEBAR_BG` | `#1C1C2E` | Dark navy cho sidebar |
| **Typography** | `FONT_XS→FONT_3XL` | 11→28px | 7 cấp font size |
| **Spacing** | `PAD_XS→PAD_2XL` | 4→24px | 6 cấp padding |
| **Sizing** | `SIDEBAR_WIDTH` | 220px | Chiều rộng sidebar cố định |
| | `HEADER_HEIGHT` | 64px | Chiều cao header |
| | `CARD_RADIUS` | 12px | Bo góc card |
| | `BUTTON_RADIUS` | 8px | Bo góc button |
| | `BADGE_RADIUS` | 20px | Bo góc badge (pill shape) |

**Palette tuân theo Semantic Color principle:**
- Xanh lá = tích cực (active, working, tăng trưởng)
- Vàng = cảnh báo (sắp hết hạn, maintenance)
- Đỏ = nguy hiểm (hỏng, expired, xóa)
- Cam = brand identity + primary action

---

#### 3.5.3 `gui/components/sidebar.py` — Sidebar điều hướng

**Layout:**

```
┌──────────────────────┐
│ [P] GymAdmin         │  ← Logo section
│ MANAGEMENT SYSTEM    │
├──────────────────────┤  ← Divider
│ ◉ Dashboard          │  ← Nav items (6 items)
│ ○ Members            │     Active = nền cam, text trắng
│ ○ Gym Packages       │     Inactive = text xám
│ ○ Equipment          │
│ ○ Trainers           │  ← MỚI (icon: SPORTS_ROUNDED)
│ ○ Reports            │
│                      │
│ [+ Add Member]       │  ← Quick action button
└──────────────────────┘
```

**Kỹ thuật quan trọng — Closure trong `make_nav_item()`:**

```python
def make_nav_item(route: str) -> ft.Container:
    is_active = route == active_route

    def on_click(e, r=route):   # Default argument giữ giá trị tại thời điểm tạo
        if navigate:
            navigate(r)

    return ft.Container(
        bgcolor=theme.ORANGE if is_active else "transparent",
        on_click=on_click,
        ink=True,    # Hiệu ứng ripple khi click
        ...
    )
```

**`r=route` trong lambda/function**: Python closure giữ tham chiếu, không giá trị. Nếu viết `def on_click(e): navigate(route)` thì tất cả 5 item sẽ dùng cùng một `route` (item cuối cùng). Default argument `r=route` capture giá trị hiện tại.

---

#### 3.5.4 `gui/components/header.py` — Header + Search

```
┌─────────────────────────────────────────────────────────┐
│ [🔍 Search members, packages...]     [🔔]  [A] Admin ▼ │
└─────────────────────────────────────────────────────────┘
```

**Search bar kết nối với màn hình active:**

```python
def _on_search(e):
    cb = getattr(page, "on_search_change", None)
    if callable(cb):
        cb(e.control.value)
```

**Pattern Observer/Callback:**
- Header không biết đang ở màn hình nào.
- Mỗi screen tự đăng ký: `page.on_search_change = my_handler`.
- Khi navigate, `main.py` reset: `page.on_search_change = None`.
- Header chỉ gọi callback nếu tồn tại → loose coupling.

---

#### 3.5.5 `gui/login.py` — Màn hình đăng nhập

**Layout:**

```
┌─────────────────────────────────────────┐
│          (gradient background)          │
│                                         │
│         ┌─────────────────────┐         │
│         │      [G] Logo       │         │
│         │     GymAdmin        │         │
│         │  MANAGEMENT SYSTEM  │         │
│         │                     │         │
│         │  Đăng nhập          │         │
│         │  [👤 Tên đăng nhập] │         │
│         │  [🔒 Mật khẩu    ] │         │
│         │  (error message)    │         │
│         │  [  Đăng nhập  ]    │         │
│         └─────────────────────┘         │
│                                         │
└─────────────────────────────────────────┘
```

**Kỹ thuật quan trọng:**

```python
# Enter-to-submit: gán on_submit cho password field
password_field.on_submit = do_login

# Gradient background
gradient=ft.LinearGradient(
    begin=ft.Alignment.TOP_CENTER,
    end=ft.Alignment.BOTTOM_CENTER,
    colors=["#FFF0E6", theme.BG],    # Cam nhạt → xám
    stops=[0.0, 0.4],                 # Gradient kết thúc sớm (40%)
)

# Card shadow tạo chiều sâu
shadow=ft.BoxShadow(blur_radius=24, color="#00000018", offset=ft.Offset(0, 4))
```

**Flow đăng nhập:**
1. User nhập username/password → nhấn Enter hoặc click nút
2. `do_login()` kiểm tra rỗng → hiện lỗi nếu thiếu
3. `check_login()` so sánh credentials
4. Thành công → `page.navigate("dashboard")`
5. Thất bại → hiện lỗi + xóa password field

---

#### 3.5.6 `gui/dashboard.py` — Dashboard tổng quan

**File lớn nhất (632 dòng)**, gồm nhiều widget con:

##### Widget `stat_card()` — 4 KPI cards

```python
def stat_card(icon, label, value, badge_text, badge_color, badge_text_color):
    """
    Tạo card KPI với:
    - Icon trong hộp cam (brand consistency)
    - Badge trạng thái (xanh/vàng/đỏ)
    - Số lớn (FONT_3XL = 28px)
    - Label nhỏ phía dưới
    """
```

| Card | Icon | Value | Badge |
|------|------|-------|-------|
| Tổng hội viên | PEOPLE_ALT | Số active | +N tháng này (xanh) |
| Sắp hết hạn | SCHEDULE | Count | 7 ngày tới (vàng) |
| Doanh thu tháng | ATTACH_MONEY | Xđ | Năm: Yđ (xanh) |
| Cần bảo trì | BUILD | broken + maintenance | Thiết bị (đỏ) |

##### Widget `revenue_chart()` — Biểu đồ doanh thu

```python
def revenue_chart(monthly_data):
    max_h = 120    # Chiều cao tối đa bar (px)
    max_val = max(v for _, v in monthly_data)  # Tìm giá trị lớn nhất

    for i, (label, val) in enumerate(monthly_data):
        bar_h = int((val / max_val) * max_h)   # Tỷ lệ chiều cao
        # Bar cuối cùng (tháng hiện tại) = cam đậm, còn lại = cam nhạt
        bgcolor = theme.ORANGE if i == len(monthly_data) - 1 else "#FED7AA"
```

**Custom bar chart** bằng `ft.Container` thay vì dùng thư viện chart bên ngoài. Lý do: Flet chưa có chart component built-in, và tránh thêm dependency.

##### Widget `active_growth_chart()` — Biểu đồ tăng trưởng

Dùng `ft.ProgressBar` horizontal cho từng loại gói tập. Màu xoay vòng: Cam → Xanh dương → Xanh lá.

##### Section "Sắp hết hạn" (Feature 2.2)

```python
expiring_subs = membership_repo.get_expiring_soon(days=7)
for s in expiring_subs:
    remaining = s.days_remaining()
    badge_color = theme.RED_LIGHT if remaining <= 3 else theme.AMBER_LIGHT
    # ≤3 ngày: badge đỏ (urgent)
    # >3 ngày: badge vàng (warning)
```

---

#### 3.5.7 `gui/members.py` — Quản lý hội viên

**File phức tạp thứ 2 (454 dòng)**, bao gồm:

##### State management bằng dict

```python
search_query = {"value": ""}
selected_member = {"obj": None}
filter_gender = {"value": None}
filter_sub_status = {"value": None}
```

**Tại sao dùng dict thay vì biến thường?**
Python closure không cho phép gán lại biến nonlocal một cách trực tiếp trong nested function (trừ khi dùng `nonlocal` keyword). Dict mutable → cập nhật `d["key"]` thay vì `d = ...`.

##### Dialog Add/Edit — Form hội viên

```python
member_dialog = ft.AlertDialog(
    modal=True,
    title=dialog_title,     # Dynamic: "Thêm mới" hoặc "Chỉnh sửa"
    content=ft.Column([
        ft.Row([f_name, f_phone]),      # Row 1: Tên + SĐT
        ft.Row([f_email, f_gender]),    # Row 2: Email + Giới tính (Dropdown)
        ft.Row([f_dob, f_emergency]),   # Row 3: Ngày sinh + Liên hệ khẩn cấp
        f_address,                       # Row 4: Địa chỉ (full width)
        dialog_error,                    # Hiện lỗi validation
    ]),
    actions=[cancel_btn, save_btn],
)
```

**Reuse dialog:** Cùng 1 dialog cho cả Add và Edit, phân biệt bằng `selected_member["obj"]`:
- `None` → mode Add → gọi `register_member()`
- Có giá trị → mode Edit → gọi `update_member()`

##### Filter nâng cao (Feature 2.3)

```python
gender_filter = ft.Dropdown(
    label="Giới tính",
    border=ft.InputBorder.UNDERLINE,
    enable_filter=True,         # Cho phép filter options
    editable=True,              # Cho phép gõ tìm
    leading_icon=ft.Icons.SEARCH,
    options=[
        ft.dropdown.Option("", "Tất cả"),
        ft.dropdown.Option("male", "Nam"),
        ft.dropdown.Option("female", "Nữ"),
        ft.dropdown.Option("other", "Khác"),
    ],
)

def on_gender_change(e):
    filter_gender.update({"value": e.control.value or None})
    refresh_table()

gender_filter.on_change = on_gender_change
```

**Tại sao tách `on_change` ra khỏi constructor?**
- Tránh lỗi khi Flet render dropdown — một số phiên bản Flet crash khi callback phức tạp nằm trong constructor.
- Code dễ đọc hơn: define control → define handler → connect.

##### `refresh_table()` — Filter pipeline

```python
def refresh_table():
    kw = search_query["value"].strip()
    members = member_repo.search(kw) if kw else member_repo.get_all()

    # Filter 1: Giới tính
    gf = filter_gender["value"]
    if gf:
        members = [m for m in members if m.gender == gf]

    # Filter 2: Trạng thái subscription
    sf = filter_sub_status["value"]
    if sf:
        active_ids = {
            s.member_id
            for s in membership_repo.get_all_subscriptions()
            if s.status == "active"
        }
        if sf == "active":
            members = [m for m in members if m.id in active_ids]
        else:
            members = [m for m in members if m.id not in active_ids]

    table_body.controls = [_make_row(m) for m in members]
    page.update()
```

**Pipeline pattern:** Search → filter giới tính → filter trạng thái → render. Mỗi bước thu hẹp tập kết quả.

##### Lambda closure đúng cách trong bảng

```python
on_click=lambda e, member=m: open_edit_dialog(member)
#                  ↑ Capture giá trị m hiện tại
```

Nếu viết `lambda e: open_edit_dialog(m)` → tất cả button sẽ mở dialog cho member cuối cùng trong danh sách (do closure giữ tham chiếu, không giá trị).

---

#### 3.5.8 `gui/memberships.py` — Gói tập & Đăng ký

**2 tabs:** "Gói tập" (CRUD plans) + "Đăng ký" (subscribe/cancel)

##### Tab switching

```python
def on_tab_change(e):
    if e.control.selected_index == 0:
        refresh_plans()      # Tab 1: load plans
    else:
        refresh_subs()       # Tab 2: load subscriptions

tabs = ft.Tabs(
    selected_index=0,
    on_change=on_tab_change,
    content=ft.Column([
        ft.TabBar(tabs=[ft.Tab(label="Gói tập"), ft.Tab(label="Đăng ký")]),
        ft.TabBarView(controls=[plans_tab_content, subs_tab_content]),
    ]),
)
```

##### Cancel subscription (Feature 2.4)

```python
# Nút Hủy chỉ hiện khi subscription đang active
cancel_btn = ft.Container(
    content=ft.Text("Hủy", ...),
    on_click=lambda e, sid=s.id: open_cancel_confirm(sid),
) if s.status == MembershipSubscription.STATUS_ACTIVE else ft.Container(width=46)
```

**Ternary expression** tạo nút Hủy hoặc spacer rỗng cùng chiều rộng (46px) → giữ layout đều.

---

#### 3.5.9 `gui/equipment.py` — Quản lý thiết bị

**Filter buttons** (không dùng Dropdown):

```python
filter_buttons_row = ft.Row([
    ft.ElevatedButton("Tất cả", on_click=lambda e: _set_filter(None),
                      bgcolor=theme.ORANGE, color=theme.WHITE),
    ft.OutlinedButton("Hoạt động", on_click=lambda e: _set_filter("working")),
    ft.OutlinedButton("Bảo trì", on_click=lambda e: _set_filter("maintenance")),
    ft.OutlinedButton("Hỏng", on_click=lambda e: _set_filter("broken")),
])
```

**`ElevatedButton` vs `OutlinedButton`:** Button "Tất cả" (default) nổi bật hơn với background cam, còn lại chỉ có viền. *Hạn chế:* Active state không thay đổi visual khi click filter khác.

---

#### 3.5.10 `gui/admin/trainers.py` — Quản lý huấn luyện viên

**File mới (302 dòng)**, cung cấp CRUD đầy đủ cho HLV.

##### Layout

```
┌──────────┬─────────────────────────────────────────────────┐
│ SIDEBAR  │  Header                                        │
│          │  ───────────────────────────────────────────    │
│          │  Huấn luyện viên    [🔍 Tìm kiếm] [+ Thêm]   │
│          │  Tổng: 5 HLV  •  Hiển thị: 5                  │
│          │  ┌─────────────────────────────────────────┐   │
│          │  │ HLV | Email | Chuyên môn | Hành động    │   │
│          │  │ Tuấn| t@..  | [Boxing]  | Sửa Reset Xóa│   │
│          │  │ Minh| m@..  | [Yoga]    | Sửa Reset Xóa│   │
│          │  └─────────────────────────────────────────┘   │
└──────────┴─────────────────────────────────────────────────┘
```

##### State management

```python
search_query = {"value": ""}       # Từ khóa tìm kiếm
selected_trainer = {"obj": None}   # HLV đang sửa (None = thêm mới)
```

Giống pattern members.py — dùng dict trong closure.

##### 3 Dialog riêng biệt

| Dialog | Mục đích | Trigger | Service call |
|--------|----------|---------|-------------|
| `trainer_dialog` | Thêm / Sửa HLV | Nút "Thêm HLV" hoặc "Sửa" | `register_trainer()` / `update_trainer()` |
| `pin_dialog` | Reset PIN | Nút "Reset PIN" | `reset_pin(trainer_id, new_pin)` |
| `confirm_dlg` | Xác nhận xóa | Nút "Xóa" | `trainer.delete()` + `update_trainer()` |

**Tại sao 3 dialog thay vì 1?**
- Dialog Thêm/Sửa: 4 fields (tên, SĐT, email, chuyên môn) — form dài
- Dialog Reset PIN: 1 field (PIN mới) — form ngắn, tách riêng để UX rõ ràng
- Dialog xác nhận xóa: chỉ có text + 2 nút — pattern chung cho delete confirmation

##### Dialog Thêm/Sửa HLV

```python
trainer_dialog = ft.AlertDialog(
    modal=True,
    title=dialog_title,     # Dynamic: "Thêm huấn luyện viên mới" hoặc "Chỉnh sửa"
    content=ft.Column([
        ft.Row([f_name, f_phone]),          # Row 1: Tên + SĐT
        ft.Row([f_email, f_specialization]),# Row 2: Email + Chuyên môn
        dialog_error,                        # Hiện lỗi validation
    ]),
    actions=[cancel_btn, save_btn],
)
```

**Reuse dialog:** Phân biệt mode bằng `selected_trainer["obj"]`:
- `None` → mode Add → gọi `trainer_svc.register_trainer()`
- Có giá trị → mode Edit → mutate object rồi gọi `trainer_svc.update_trainer()`

##### Dialog Reset PIN

```python
f_new_pin = ft.TextField(
    label="PIN mới (6 chữ số)",
    password=True,              # Ẩn nội dung
    can_reveal_password=True,   # Nút toggle hiện/ẩn
    max_length=6,
)
```

**UX:** PIN mặc định ẩn (password mode) nhưng admin có thể bấm icon mắt để kiểm tra. `max_length=6` ngăn nhập quá 6 ký tự.

**Validation ở service:** `re.fullmatch(r"\d{6}", new_pin)` — chỉ chấp nhận đúng 6 chữ số.

##### Xóa HLV — Soft Delete

```python
def do_delete(e):
    t = delete_target["obj"]
    t.delete()                     # BaseModel.delete() → is_active = False
    trainer_svc.update_trainer(t)  # Lưu thay đổi vào DB
```

**Soft delete pattern:** Không xóa record khỏi DB, chỉ set `is_active = 0`. Khi `refresh_table()` gọi `get_all_trainers(active_only=True)` → HLV đã xóa không hiện.

##### Bảng danh sách — `_make_row(t)`

```python
# Avatar tròn với chữ cái đầu, màu dựa trên hash(id)
initials = "".join(w[0].upper() for w in t.name.split()[:2])
colors = ["#8B5CF6", "#3B82F6", "#EC4899", "#10B981", "#F59E0B"]
avatar_color = colors[hash(t.id) % len(colors)]
```

| Cột | Nội dung | Chi tiết |
|-----|----------|---------|
| 1 | Avatar + Tên + SĐT | Avatar tròn 36px, 5 màu xoay vòng |
| 2 | Email | Text xám, hiện "—" nếu null |
| 3 | Chuyên môn | Badge xanh dương (BLUE_LIGHT bg), hiện "—" nếu null |
| 4 | Hành động | 3 nút: Sửa (cam) / Reset PIN (xanh) / Xóa (đỏ) |

**Badge chuyên môn:** Dùng `ft.Container` với `bgcolor=theme.BLUE_LIGHT` và text `color=theme.BLUE` → tạo hiệu ứng "pill badge" nổi bật. Nếu HLV chưa có chuyên môn → hiện "—" trên nền trong suốt.

##### Tìm kiếm — `refresh_table()`

```python
def refresh_table():
    q = search_query["value"].lower()
    all_trainers = trainer_svc.get_all_trainers(active_only=True)
    if q:
        filtered = [
            t for t in all_trainers
            if q in t.name.lower()
            or q in t.phone.lower()
            or q in (t.specialization or "").lower()
        ]
    else:
        filtered = all_trainers
    # ...render table_body...
```

**Tìm kiếm 3 trường:** Tên, SĐT, chuyên môn — case-insensitive. Dùng `(t.specialization or "").lower()` để tránh lỗi khi specialization là `None`.

**Empty state:** Khi không có kết quả, hiện text "Không tìm thấy huấn luyện viên nào." (có tìm kiếm) hoặc "Chưa có huấn luyện viên." (chưa thêm).

---

#### 3.5.11 `gui/reports.py` — Báo cáo thống kê

**Pattern đặc biệt — `build_content()` + `refresh()`:**

```python
def build_content():
    # Fetch tất cả data từ services
    # Tạo toàn bộ UI tree
    return ft.Column([kpi_row, eq_section, expiring_section, ...])

content_area = ft.Container(expand=True)

def refresh():
    content_area.content = build_content()  # Rebuild hoàn toàn
    page.update()

content_area.content = build_content()  # Initial render
```

**Tại sao rebuild toàn bộ thay vì update từng field?**
- Reports là read-only, không có form/dialog cần giữ state.
- Rebuild đơn giản hơn track từng widget cần update.
- Performance chấp nhận được vì data nhỏ (vài trăm record).

---

## 4. Phân tích luồng dữ liệu

### 4.1 Luồng "Thêm hội viên mới"

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
6. Member(name, phone, ...) → tạo object với UUID mới
   │
7. member_repo.create(member) → INSERT INTO members VALUES (...)
   │
8. dialog.open = False → refresh_table() → đọc lại từ DB → render bảng mới
```

### 4.2 Luồng "Đăng ký gói tập"

```
1. Memberships screen → Tab "Đăng ký" → "+ Đăng ký mới"
   │
2. open_add_sub() → load danh sách members + plans → populate dropdowns
   │
3. User chọn member, plan, (optional: giá, ngày bắt đầu) → "Đăng ký"
   │
4. save_sub() → membership_svc.subscribe_member(member_id, plan_id, ...)
   │
5. Service → get plan → tạo MembershipSubscription (auto-calc end_date)
   │
6. membership_repo.create_subscription(sub) → INSERT INTO subscriptions
   │
7. refresh_subs() → auto_expire → đọc lại subscriptions → render bảng
```

### 4.3 Luồng "Thêm huấn luyện viên mới"

```
1. User click "Thêm HLV" trên Trainers screen
   │
2. open_add_dialog() → clear form → dialog_title = "Thêm huấn luyện viên mới"
   │                  → trainer_dialog.open = True
   │
3. User điền form (tên, SĐT, email, chuyên môn) → click "Lưu"
   │
4. save_trainer() → gọi trainer_svc.register_trainer(name, phone, ...)
   │
5. trainer_svc._validate(name, phone, email) → regex check
   │  ↓ Lỗi: raise ValueError → dialog_error.value = str(ex) → hiện lỗi
   │  ↓ OK: tiếp
6. Trainer(name, phone, ...) → tạo object với UUID mới, PIN mặc định "000000"
   │
7. trainer_repo.create(trainer) → INSERT INTO trainers VALUES (...)
   │
8. dialog.open = False → refresh_table() → đọc lại từ DB → render bảng mới
```

### 4.4 Luồng "Reset PIN huấn luyện viên"

```
1. Admin click "Reset PIN" trên dòng HLV trong bảng
   │
2. open_pin_dialog(trainer) → set pin_target id/name → clear form
   │                        → pin_dialog_title = "Reset PIN — Tên HLV"
   │
3. Admin nhập PIN mới (6 chữ số) → click "Đặt PIN"
   │
4. do_reset_pin() → gọi trainer_svc.reset_pin(trainer_id, new_pin)
   │
5. reset_pin() validate: re.fullmatch(r"\d{6}", new_pin)
   │  ↓ Sai format: raise ValueError("PIN phải gồm đúng 6 chữ số")
   │  ↓ OK: trainer_repo.get_by_id(id) → set trainer.pin = new_pin
   │
6. trainer_repo.update(trainer) → UPDATE trainers SET pin=? WHERE id=?
   │
7. pin_dialog.open = False → refresh_table()
```

### 4.5 Luồng "Auto-expire subscriptions"

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

---

## 5. Đánh giá kỹ thuật

### 5.1 Điểm mạnh

| # | Điểm mạnh | Chi tiết |
|---|-----------|---------|
| 1 | **Kiến trúc phân tầng rõ ràng** | Models → Repositories → Services → GUI. Mỗi tầng có trách nhiệm riêng, dễ maintain |
| 2 | **Design System nhất quán** | `theme.py` tập trung tokens → UI đồng nhất, dễ đổi theme |
| 3 | **Soft Delete pattern** | Không mất dữ liệu khi xóa, giữ audit trail |
| 4 | **SQL Injection safe** | Tất cả query dùng parameterized `?` placeholder |
| 5 | **Transaction safe** | Context manager `get_db()` đảm bảo commit/rollback |
| 6 | **Validation tập trung** | Service layer validate trước khi ghi DB |
| 7 | **Loose coupling GUI ↔ Logic** | GUI gọi service, không trực tiếp SQL |
| 8 | **Observer pattern cho search** | Header search → callback → active screen filter |

### 5.2 Điểm cần cải thiện

| # | Vấn đề | Mức độ | Gợi ý |
|---|--------|:------:|-------|
| 1 | **Plaintext password** | ⚠️ | Dùng `bcrypt` hoặc `hashlib.pbkdf2_hmac` |
| 2 | **Không có pagination** | Trung bình | Khi data lớn, `get_all()` load toàn bộ vào RAM |
| 3 | **Filter subscription N+1 query** | Trung bình | `refresh_table()` gọi `get_all_subscriptions()` mỗi lần filter → nên cache hoặc JOIN |
| 4 | **Thiếu loading state** | Thấp | Không có spinner khi fetch data |
| 5 | **Thiếu tests** | ⚠️ | Không có test nào — cần ít nhất unit test cho services |
| 6 | **Equipment filter visual** | Thấp | Nút filter không đổi visual khi active |
| 7 | **Stub files chưa dọn** | Thấp | `payment_svc.py`, `api/` rỗng |

### 5.3 Đánh giá theo tiêu chuẩn Web Design Guidelines

| Tiêu chí | Đánh giá | Ghi chú |
|----------|:--------:|---------|
| **Separation of Concerns** | ★★★★★ | Rõ ràng: GUI / Service / Repo / Model |
| **Consistent Design Tokens** | ★★★★★ | Tất cả dùng theme.py |
| **Component Reusability** | ★★★★☆ | Sidebar + Header reusable, nhưng stat_card chỉ dùng ở dashboard |
| **Error Handling** | ★★★★☆ | Service validate, GUI hiện lỗi; thiếu global error boundary |
| **State Management** | ★★★☆☆ | Dict-based state hoạt động nhưng không scale tốt |
| **Accessibility** | ★★☆☆☆ | Thiếu tooltip, aria labels (hạn chế của Flet) |
| **Performance** | ★★★☆☆ | OK cho ~100-500 records, cần pagination cho data lớn |
| **Security** | ★★★☆☆ | SQL injection safe nhưng plaintext password |
| **Testing** | ★☆☆☆☆ | Không có tests |

---

## 6. Tổng kết

### 6.1 Bảng tóm tắt file & dòng code

| Tầng | File | Dòng code | Trạng thái |
|------|------|:---------:|:----------:|
| Core | `config.py` | 14 | ✅ |
| Core | `database.py` | 99 | ✅ |
| Core | `security.py` | 7 | ✅ (MVP) |
| Models | `base.py` | 25 | ✅ |
| Models | `member.py` | 19 | ✅ |
| Models | `membership.py` | 63 | ✅ |
| Models | `equipment.py` | 49 | ✅ |
| Models | `trainer.py` | 18 | ✅ |
| Repos | `member_repo.py` | 80 | ✅ |
| Repos | `membership_repo.py` | 157 | ✅ |
| Repos | `equipment_repo.py` | 87 | ✅ |
| Repos | `trainer_repo.py` | 93 | ✅ |
| Services | `member_svc.py` | 58 | ✅ |
| Services | `membership_svc.py` | 109 | ✅ |
| Services | `equipment_svc.py` | 43 | ✅ |
| Services | `trainer_svc.py` | 101 | ✅ |
| GUI | `main.py` | 64 | ✅ |
| GUI | `theme.py` | 46 | ✅ |
| GUI Admin | `login.py` | 125 | ✅ |
| GUI Admin | `sidebar.py` | 124 | ✅ |
| GUI Admin | `header.py` | 102 | ✅ |
| GUI Admin | `dashboard.py` | 632 | ✅ |
| GUI Admin | `members.py` | 454 | ✅ |
| GUI Admin | `memberships.py` | 390 | ✅ |
| GUI Admin | `equipment.py` | 262 | ✅ |
| GUI Admin | `trainers.py` | 302 | ✅ |
| GUI Admin | `reports.py` | 178 | ✅ |
| **Tổng** | **27 files** | **~3,744** | **85% hoàn thiện** |

### 6.2 Tổng đánh giá

**Gym Management System** là một ứng dụng desktop MVP hoàn chỉnh với kiến trúc phân tầng rõ ràng. Hệ thống có đầy đủ 5 module chính (Members, Memberships, Equipment, **Trainers**, Reports), giao diện nhất quán dựa trên design system, và kết nối database thật qua SQLite3.

**Điểm nổi bật:** Kiến trúc sạch, code có cấu trúc, UI/UX đẹp và nhất quán, CRUD hoàn chỉnh cho tất cả module, router navigation đơn giản hiệu quả. Module Trainers mới bổ sung thêm khả năng quản lý HLV với reset PIN — chuẩn bị sẵn cho user app.

**Cần hoàn thiện:** Testing, password hashing, pagination, user app (gui/user/), và dọn dẹp stub files.

---

*Báo cáo được tạo tự động bởi Claude Code — 2026-03-20 21:40, cập nhật lần cuối 2026-04-04*
*Tham khảo thêm: [doc/report_plan.md](report_plan.md) | [doc/UI_REVIEW.md](UI_REVIEW.md) | [doc/AI_REPORT.md](../doc/AI_REPORT.md)*
