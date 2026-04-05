# Báo cáo Kế hoạch & Việc cần làm — Gym Management System

**Ngày tạo:** 2026-03-19
**Cập nhật lần cuối:** 2026-03-20
**Dự án:** Gym Management System
**Trạng thái:** Đang phát triển

---

## 1. Tổng quan tiến độ hiện tại

### 1.1 Kiến trúc tổng thể

```
gym_management/
├── app/
│   ├── core/
│   │   ├── config.py          ✅ Hoàn thành
│   │   ├── database.py        ✅ Hoàn thành (đã fix executescript + thêm indexes)
│   │   └── security.py        ✅ Hoàn thành (check_login)
│   ├── models/                ✅ Hoàn thành
│   ├── repositories/          ✅ Hoàn thành
│   ├── services/
│   │   ├── member_svc.py      ✅ Hoàn thành
│   │   ├── membership_svc.py  ✅ Hoàn thành
│   │   ├── equipment_svc.py   ✅ Hoàn thành
│   │   ├── payment_svc.py     ❌ Stub trống
│   │   └── trainer_svc.py     ❌ Stub trống
│   └── api/                   ❌ Stub trống (không dùng)
├── gui/
│   ├── login.py               ✅ Hoàn thành (đã fix responsive)
│   ├── dashboard.py           ✅ Hoàn thành (kết nối DB thật)
│   ├── members.py             ✅ Hoàn thành
│   ├── memberships.py         ✅ Hoàn thành
│   ├── equipment.py           ✅ Hoàn thành
│   └── reports.py             ✅ Hoàn thành
└── tests/                     ❌ Chưa có
```

### 1.2 Bảng tóm tắt trạng thái

| Layer | Module | Trạng thái | Ghi chú |
|-------|--------|:----------:|---------|
| **Core** | `config.py` | ✅ Xong | Settings, env var override cho credentials |
| **Core** | `database.py` | ✅ Xong | SQLite3 + 4 bảng schema + 6 indexes, FK chuẩn |
| **Core** | `security.py` | ✅ Xong | `check_login()` so sánh với config |
| **Models** | `base.py` | ✅ Xong | UUID, created_at, updated_at, is_active |
| **Models** | `member.py` | ✅ Xong | Đầy đủ fields kể cả `photo` |
| **Models** | `membership.py` | ✅ Xong | MembershipPlan + MembershipSubscription |
| **Models** | `equipment.py` | ✅ Xong | Đầy đủ fields kể cả `location` |
| **Repositories** | `member_repo.py` | ✅ Xong | Full CRUD + search |
| **Repositories** | `membership_repo.py` | ✅ Xong | Full CRUD + expiring_soon |
| **Repositories** | `equipment_repo.py` | ✅ Xong | Full CRUD + filter by status/category |
| **Services** | `member_svc.py` | ✅ Xong | Validate, CRUD, stats — đã đơn giản hóa `update_member()` |
| **Services** | `membership_svc.py` | ✅ Xong | Validate, subscribe, revenue stats, monthly revenue, plan stats |
| **Services** | `equipment_svc.py` | ✅ Xong | Validate, CRUD, summary |
| **Services** | `payment_svc.py` | ❌ Stub | Trống — chưa implement |
| **Services** | `trainer_svc.py` | ❌ Stub | Trống — chưa implement |
| **GUI** | `theme.py` | ✅ Xong | Design tokens: màu, font, spacing |
| **GUI** | `sidebar.py` | ✅ Xong | Navigation hoạt động đầy đủ |
| **GUI** | `header.py` | ✅ Xong | Search bar + avatar (search chưa có chức năng) |
| **GUI** | `login.py` | ✅ Xong | Form đăng nhập, responsive, enter-to-submit |
| **GUI** | `dashboard.py` | ✅ Xong | KPI, charts, packages, equipment — dữ liệu thật |
| **GUI** | `members.py` | ✅ Xong | CRUD đầy đủ, search realtime |
| **GUI** | `memberships.py` | ✅ Xong | Gói tập + đăng ký (2 tabs) |
| **GUI** | `equipment.py` | ✅ Xong | CRUD + filter trạng thái |
| **GUI** | `reports.py` | ✅ Xong | KPI, thiết bị, gói sắp hết hạn |
| **Tests** | `tests/` | ❌ Chưa làm | Không có test nào |

---

## 2. Bảng kế hoạch việc cần làm

### Ưu tiên 1 — CAO (làm ngay)

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 1.1 | **Kết nối Dashboard với dữ liệu thật** | `gui/dashboard.py`, `membership_svc.py` | ✅ XONG | Revenue chart, active growth, packages, equipment dùng dữ liệu DB thật |
| 1.2 | **Màn hình Login + responsive** | `gui/login.py`, `app/main.py` | ✅ XONG | Form username/password, gradient BG, enter-to-submit, fix co dãn nút |
| 1.3 | **Implement security.py** | `app/core/security.py`, `config.py` | ✅ XONG | `check_login()` + env var override credentials |
| 1.4 | **Thêm field `photo` vào Member** | `app/models/member.py` | ✅ XONG | Thêm `photo=None` vào `__init__`, repo đọc/ghi đúng cột `photo` |
| 1.5 | **Thêm field `location` vào Equipment** | `app/models/equipment.py` | ✅ XONG | Thêm `location=None` vào `__init__`, bỏ toàn bộ `getattr()` workaround |

---

### Ưu tiên 2 — TRUNG BÌNH (làm sau khi xong priority 1)

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 2.1 | **Chi tiết hội viên — lịch sử gói tập** | `gui/members.py` | ✅ XONG | Dialog hiển thị toàn bộ subscription history: tên gói, ngày, trạng thái, giá |
| 2.2 | **Widget "Sắp hết hạn" trên Dashboard** | `gui/dashboard.py` | ✅ XONG | Section bảng danh sách chi tiết sau stat_cards, badge đỏ ≤3 ngày |
| 2.3 | **Filter nâng cao trang Members** | `gui/members.py` | ✅ XONG | Dropdown giới tính + dropdown trạng thái gói, kết hợp với search |
| 2.4 | **Hủy đăng ký gói tập (Cancel)** | `gui/memberships.py`, `membership_svc.py` | ✅ XONG | Nút "Hủy" chỉ hiện với active subs, confirm dialog, `cancel_subscription()` trong service |
| 2.5 | **Thống kê doanh thu theo tháng trên Reports** | `gui/reports.py` | ❌ Chưa | Biểu đồ doanh thu 6 tháng (hiện chỉ có tổng) |
| 2.6 | **Header search bar có chức năng** | `gui/components/header.py` | ❌ Chưa | Search hiện chỉ là UI trang trí — cần kết nối với màn hình đang active |

---

### Ưu tiên 3 — THẤP (cải tiến & hoàn thiện)

| # | Việc cần làm | File liên quan | Trạng thái | Mô tả chi tiết |
|---|---|---|:---:|---|
| 3.1 | **Xuất báo cáo CSV** | `gui/reports.py` | ❌ Chưa | Nút "Xuất CSV" export hội viên, doanh thu — dùng module `csv` |
| 3.2 | **Viết Tests** | `tests/` | ❌ Chưa | Tối thiểu: `test_member_svc.py`, `test_membership_svc.py`, `test_equipment_svc.py` |
| 3.3 | **Dọn dẹp stub không dùng** | `payment_svc.py`, `trainer_svc.py`, `api/` | ❌ Chưa | Xóa file stub trống để tránh nhầm lẫn kiến trúc |
| 3.4 | **Thông báo Toast / Snackbar** | Tất cả GUI screens | ❌ Chưa | Thêm `page.snack_bar` thông báo sau khi lưu/xóa dữ liệu |
| 3.5 | **Upload ảnh hội viên** | `gui/members.py` | ❌ Chưa | Sau khi thêm field `photo`, dùng `ft.FilePicker` để chọn ảnh |
| 3.6 | **Pagination cho bảng danh sách** | `members.py`, `memberships.py`, `equipment.py` | ❌ Chưa | Phân trang hoặc lazy load khi dữ liệu lớn |
| 3.7 | **Filter active state visual trên Equipment** | `gui/equipment.py` | ❌ Chưa | Nút filter không hiện rõ đang chọn filter nào |

---

## 3. Thứ tự thực hiện gợi ý

```
Tuần 1 — Đã hoàn thành ✅
├── [1.1] Kết nối Dashboard với dữ liệu thật
├── [1.2] Màn hình Login + fix responsive
└── [1.3] security.py (check_login)

Tuần 2 — Đã hoàn thành ✅
├── [1.4] Thêm field photo vào Member model
└── [1.5] Thêm field location vào Equipment model

Tuần 3 — Đã hoàn thành ✅
├── [2.1] Chi tiết hội viên — lịch sử gói tập
├── [2.2] Widget "Sắp hết hạn" trên Dashboard
├── [2.3] Filter nâng cao Members
└── [2.4] Hủy đăng ký gói tập

Tuần 4
├── [2.3] Filter nâng cao Members
├── [2.5] Thống kê doanh thu theo tháng
├── [2.6] Header search bar có chức năng
└── [3.4] Thông báo Toast / Snackbar

Tuần 5+
├── [3.2] Viết Tests
├── [3.1] Xuất báo cáo CSV
├── [3.5] Upload ảnh hội viên
├── [3.6] Pagination
├── [3.7] Equipment filter visual
└── [3.3] Dọn dẹp stub
```

---

## 4. Vấn đề kỹ thuật cần lưu ý

| Vấn đề | Chi tiết | Trạng thái |
|--------|----------|-----------|
| ~~Dashboard mock data~~ | ~~Hardcode số liệu~~ | ✅ Đã fix |
| ~~`executescript()` bypass transaction~~ | ~~Không tương thích với context manager~~ | ✅ Đã fix |
| ~~Overlay dialog tích lũy~~ | ~~`page.overlay` không được clear khi navigate~~ | ✅ Đã fix |
| ~~`update_member()` signature nhầm lẫn~~ | ~~Nhận cả object lẫn kwargs~~ | ✅ Đã fix |
| ~~`Equipment.location` thiếu trong model~~ | ~~`equipment_repo.py` dùng `getattr()` tạm~~ | ✅ Đã fix |
| ~~`Member.photo` hardcode `None`~~ | ~~`member_repo.py` luôn truyền `None` cho cột `photo`~~ | ✅ Đã fix |
| **`security.py` chưa có password hashing** | Credentials so sánh plaintext | ⚠️ Chấp nhận cho MVP |
| ~~**Subscription `start_date` kiểu dữ liệu**~~ | ~~`membership_svc` nhận `datetime`, model dùng `date`~~ | ✅ Đã fix — chuẩn hóa trong `__init__` |
| ~~**Header search không hoạt động**~~ | ~~Chỉ là UI trang trí~~ | ✅ Đã fix — inject `page.on_search_change`, Members đăng ký callback |

---

## 5. Stack công nghệ

| Thành phần | Công nghệ | Trạng thái |
|-----------|-----------|:---:|
| Ngôn ngữ | Python 3.10+ | ✅ |
| GUI | Flet 0.82.2 (pinned) | ✅ |
| Database | SQLite3 (không ORM) | ✅ |
| Auth | Plaintext compare (MVP) | ⚠️ |
| Password hashing | `bcrypt` hoặc `hashlib` | ❌ Chưa |
| Testing | `pytest` | ❌ Chưa |
| Export CSV | `csv` (built-in) | ❌ Chưa |

---

*Cập nhật lần cuối: 2026-03-20 — phản ánh login screen hoàn thành và các bug fix từ code review.*
