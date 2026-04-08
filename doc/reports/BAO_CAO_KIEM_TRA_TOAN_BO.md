# BÁO CÁO KIỂM TRA TOÀN BỘ HỆ THỐNG GYM MANAGEMENT

> Ngày kiểm tra: 2026-04-04
> Cập nhật lần cuối: 2026-04-04 20:00
> Phạm vi: Toàn bộ dự án — Core, Models, Repositories, Services, GUI Admin, GUI User

---

## TỔNG KẾT NHANH

| Mức độ       | Tổng | Đã sửa | Còn lại | Mô tả chính                                              |
| ------------ | ---- | ------ | ------- | --------------------------------------------------------- |
| NGHIÊM TRỌNG | 6    | 3      | 3       | Credentials, PIN plaintext, role guard chưa sửa           |
| CAO          | 25   | 6      | 19      | Thiếu validate, datetime, exception handling              |
| TRUNG BÌNH   | 20   | 0      | 20      | Thiếu constraint DB, validate yếu, tiếng Việt không dấu  |
| THẤP         | 10   | 0      | 10      | Thiếu index, UX nhỏ, hardcoded config                    |

**Tổng: 61 vấn đề — Đã sửa 9, Còn lại 52**

---

## MỤC LỤC

1. [Bảo mật (Security)](#1-bảo-mật)
2. [Database & Schema](#2-database--schema)
3. [Models](#3-models)
4. [Services](#4-services)
5. [Repositories](#5-repositories)
6. [GUI Admin](#6-gui-admin)
7. [GUI User](#7-gui-user)
8. [Entry Points & Architecture](#8-entry-points--architecture)

---

## 1. BẢO MẬT

### 1.1 NGHIÊM TRỌNG — Credentials admin hardcoded
- **File:** `app/core/config.py` (dòng 33-34)
- **Hiện tại:** `ADMIN_USERNAME="admin"`, `ADMIN_PASSWORD="admin123"` — hardcoded, rất yếu
- **Rủi ro:** Ai có mã nguồn đều biết mật khẩu admin; "admin123" nằm trong top 100 mật khẩu phổ biến
- **Đề xuất:** Bắt buộc dùng env var, không có fallback mặc định yếu

### 1.2 NGHIÊM TRỌNG — PIN lưu plaintext
- **File:** `app/services/auth_svc.py` (dòng 28, 48), `app/core/database.py`
- **Hiện tại:** PIN lưu trực tiếp trong DB dạng text, so sánh bằng `==`
- **Rủi ro:** Ai truy cập DB file (`gym_db.db`) đều thấy PIN của tất cả hội viên/HLV
- **Đề xuất:** Hash PIN bằng bcrypt hoặc argon2

### 1.3 CAO — Không giới hạn số lần đăng nhập sai
- **File:** `app/services/auth_svc.py` (dòng 13-50)
- **Hiện tại:** Không có rate limiting hay lockout
- **Rủi ro:** Brute force 6 chữ số PIN (1 triệu tổ hợp) có thể thử hết nhanh chóng
- **Đề xuất:** Khóa tài khoản sau 5 lần sai, hoặc tăng delay mỗi lần sai

### 1.4 CAO — So sánh mật khẩu/PIN không constant-time
- **File:** `app/core/security.py` (dòng 26), `app/services/auth_svc.py` (dòng 28, 48)
- **Hiện tại:** Dùng `==` để so sánh
- **Đề xuất:** Dùng `hmac.compare_digest()` để chống timing attack

---

## 2. DATABASE & SCHEMA

### ✅ 2.1 ĐÃ SỬA — Cascade delete khi xóa member/trainer
- **File:** `app/repositories/member_repo.py`, `app/repositories/trainer_repo.py`
- **Đã sửa:** Chuyển từ hard DELETE sang soft delete (is_active=0) + cascade tới subscriptions, trainer_assignments, training_sessions, notifications
- **Ngày sửa:** 2026-04-04

### ✅ 2.2 ĐÃ SỬA — CHECK constraint cho PIN
- **File:** `app/core/database.py`
- **Đã sửa:** Thêm `CHECK(LENGTH(pin) = 6)` vào cột pin trong CREATE TABLE members và trainers
- **Ghi chú:** DB mới áp dụng ngay; DB cũ dựa vào input_filter ở GUI (đã sửa ở session trước)
- **Ngày sửa:** 2026-04-04

### ✅ 2.3 ĐÃ SỬA — UNIQUE constraint cho phone
- **File:** `app/core/database.py`
- **Đã sửa:** Thêm `UNIQUE` vào cột phone trong CREATE TABLE + migration `CREATE UNIQUE INDEX` cho DB cũ
- **Ghi chú:** Nếu DB cũ có phone trùng, migration bỏ qua — cần xử lý thủ công
- **Ngày sửa:** 2026-04-04

### 2.4 CAO — init_db() bắt mọi exception rồi bỏ qua
- **File:** `app/core/database.py` (dòng 235-244)
- **Hiện tại:** `except Exception: pass` — bỏ qua TẤT CẢ lỗi, kể cả lỗi nghiêm trọng
- **Rủi ro:** Lỗi SQL syntax, lỗi permission bị nuốt im lặng
- **Đề xuất:** Chỉ bắt `sqlite3.OperationalError` và kiểm tra "duplicate column"

### 2.5 CAO — Không có schema versioning
- **File:** `app/core/database.py`
- **Hiện tại:** Dùng ALTER TABLE + try/except để migrate — rất mong manh
- **Đề xuất:** Thêm bảng `schema_version` để quản lý migration

### 2.6 TRUNG BÌNH — FK constraint cho trainer_id trong subscriptions yếu
- **File:** `app/core/database.py` (dòng 242)
- **Hiện tại:** ALTER TABLE thêm cột với REFERENCES nhưng SQLite có giới hạn
- **Đề xuất:** Tạo lại bảng hoặc enforce ở application layer

### 2.7 TRUNG BÌNH — Timestamp xử lý không nhất quán
- **File:** Nhiều file
- **Hiện tại:** Model lưu datetime object, DB lưu ISO string, repo convert lại
- **Rủi ro:** Nếu 1 repo quên `fromisoformat()` → so sánh datetime với string sẽ lỗi

### 2.8 THẤP — Thiếu index cho email, trainer_id trong subscriptions
- **File:** `app/core/database.py`
- **Đề xuất:** Thêm index nếu cần search theo email hoặc trainer_id

---

## 3. MODELS

### 3.1 CAO — Datetime vs String không nhất quán trong training data
- **File:** `app/models/training_session.py` (dòng 24-25)
- **Hiện tại:** `session_date` là string "YYYY-MM-DD", nhưng `TrainerAssignment.start_date` là datetime
- **Rủi ro:** So sánh ngày giữa 2 model sẽ lỗi type mismatch

### 3.2 TRUNG BÌNH — Model không validate dữ liệu trong __init__
- **File:** Tất cả models
- **Hiện tại:** Không validate name rỗng, phone sai format, quantity âm, price âm, duration_days <= 0
- **Rủi ro:** Dữ liệu xấu lọt vào DB nếu service quên validate
- **Đề xuất:** Thêm validation cơ bản trong __init__ hoặc dùng @property

### 3.3 TRUNG BÌNH — TrainerAssignment.end_date có thể None khi status='ended'
- **File:** `app/models/trainer_assignment.py` (dòng 26)
- **Rủi ro:** Trạng thái logic không nhất quán

### 3.4 TRUNG BÌNH — Notification không kế thừa BaseModel
- **File:** `app/models/notification.py` (dòng 16)
- **Hiện tại:** Thiết kế có chủ đích nhưng gây không nhất quán với các model khác

---

## 4. SERVICES

### 4.1 CAO — auth_svc.change_pin() không validate old_pin
- **File:** `app/services/auth_svc.py`
- **Hiện tại:** Validate new_pin (6 số, isdigit) nhưng KHÔNG validate format old_pin
- **Đề xuất:** Validate cả old_pin trước khi truy vấn DB

### 4.2 CAO — notification_svc dùng magic string thay vì constant
- **File:** `app/services/notification_svc.py` (dòng 70, 123)
- **Hiện tại:** `!= "active"` thay vì `!= MembershipSubscription.STATUS_ACTIVE`
- **Rủi ro:** Typo sẽ không bị phát hiện

### 4.3 CAO — assignment_svc.auto_end chạy SQL trực tiếp không qua repo
- **File:** `app/services/assignment_svc.py` (dòng 127-144)
- **Hiện tại:** Service gọi `get_db()` trực tiếp, phá vỡ kiến trúc layered
- **Đề xuất:** Chuyển query vào repo

### 4.4 CAO — membership_svc nuốt lỗi assignment khi subscribe
- **File:** `app/services/membership_svc.py`
- **Hiện tại:** `except ValueError: pass` — nếu assign trainer thất bại, không ai biết
- **Đề xuất:** Log lỗi hoặc thông báo cho user

### 4.5 TRUNG BÌNH — trainer_svc dùng tiếng Việt không dấu trong thông báo lỗi
- **File:** `app/services/trainer_svc.py` (dòng 16-25)
- **Hiện tại:** "Ten HLV khong duoc de trong" thay vì "Tên HLV không được để trống"

### 4.6 TRUNG BÌNH — notification_svc dùng tiếng Việt không dấu
- **File:** `app/services/notification_svc.py`
- **Hiện tại:** "Goi tap da het han!" thay vì "Gói tập đã hết hạn!"

### 4.7 TRUNG BÌNH — schedule_svc không validate ngày trong quá khứ
- **File:** `app/services/schedule_svc.py`
- **Hiện tại:** Có thể tạo buổi tập cho ngày đã qua

### 4.8 TRUNG BÌNH — Hardcoded ngưỡng 7 ngày trong notification_svc
- **File:** `app/services/notification_svc.py` (dòng 97, 136)
- **Đề xuất:** Định nghĩa constant ở đầu module

---

## 5. REPOSITORIES

### ✅ 5.1 ĐÃ SỬA — member_repo soft delete + cascade
- **File:** `app/repositories/member_repo.py`
- **Đã sửa:** Chuyển từ hard DELETE sang soft delete + cascade tới 4 bảng liên quan
- **Ngày sửa:** 2026-04-04

### ✅ 5.2 ĐÃ SỬA — trainer_repo soft delete + cascade
- **File:** `app/repositories/trainer_repo.py`
- **Đã sửa:** Tương tự member_repo
- **Ngày sửa:** 2026-04-04

### 5.3 CAO — notification_repo không có phân trang
- **File:** `app/repositories/notification_repo.py`
- **Hiện tại:** Lấy TẤT CẢ thông báo vào memory
- **Rủi ro:** Nếu 1 user có hàng ngàn thông báo → chậm, tốn RAM
- **Đề xuất:** Thêm LIMIT/OFFSET

### 5.4 CAO — notification_repo dùng LIKE để so sánh ngày
- **File:** `app/repositories/notification_repo.py` (dòng 84-96)
- **Hiện tại:** `created_at LIKE "%Y-%m-%d%"` — chậm và mong manh
- **Đề xuất:** Dùng `DATE(created_at) = DATE('now')`

### 5.5 CAO — equipment_repo thiếu hàm search()
- **File:** `app/repositories/equipment_repo.py`
- **Hiện tại:** Không có search(), trong khi member_repo và trainer_repo có
- **Đề xuất:** Thêm search() cho nhất quán

### 5.6 TRUNG BÌNH — membership_repo.get_all_subscriptions() load tất cả vào memory
- **File:** `app/repositories/membership_repo.py`
- **Đề xuất:** Thêm aggregation query (SUM, COUNT) thay vì load rồi tính

### 5.7 TRUNG BÌNH — Không có cleanup cho thông báo cũ
- **File:** `app/repositories/notification_repo.py`
- **Đề xuất:** Thêm hàm xóa thông báo quá 90 ngày

---

## 6. GUI ADMIN

### 6.1 CAO — members.py: Thiếu validate phone, email, date khi tạo/sửa hội viên
- **File:** `gui/admin/members.py` (dòng 101-109)
- **Hiện tại:** Gửi trực tiếp giá trị từ TextField lên service, không validate format
- **Rủi ro:** Phone = "abc", email = "xyz", date = "ngày mai" — đều lọt qua

### 6.2 CAO — memberships.py: Dropdown có thể None khi tạo subscription
- **File:** `gui/admin/memberships.py` (dòng 217-218)
- **Hiện tại:** `fs_member.value` và `fs_plan.value` không kiểm tra None
- **Rủi ro:** Crash khi user chưa chọn hội viên/gói tập

### 6.3 CAO — memberships.py: Thiếu validate duration_days > 0 và price > 0
- **File:** `gui/admin/memberships.py` (dòng 56-57)
- **Hiện tại:** `int(fp_days.value or 0)` cho phép 0 hoặc âm
- **Rủi ro:** Tạo gói tập 0 ngày, giá âm

### 6.4 CAO — trainers.py: Thiếu null check cho subscription khi hiện học viên
- **File:** `gui/admin/trainers.py` (dòng 240-243)
- **Hiện tại:** `sub.end_date.strftime(...)` mà không check sub có thể None
- **Rủi ro:** AttributeError crash dialog chi tiết

### 6.5 CAO — Lambda trả về list trong nút xóa (nhiều file)
- **File:** `memberships.py` (dòng 126), `equipment.py` (dòng 154), `trainers.py` (dòng 222)
- **Hiện tại:** `on_click=lambda e: [repo.delete(...), ...]`
- **Rủi ro:** Không bắt lỗi nếu delete thất bại (FK constraint)

### 6.6 TRUNG BÌNH — Thiếu max_length cho TextField ở nhiều form
- **File:** `members.py`, `memberships.py`, `equipment.py`
- **Hiện tại:** Name, description, notes không giới hạn độ dài

### 6.7 TRUNG BÌNH — dashboard.py: Có thể crash nếu subscription lookup thất bại
- **File:** `gui/admin/dashboard.py` (dòng 489-495)
- **Đề xuất:** Wrap trong try/except

### 6.8 THẤP — login.py: Không trim username/password
- **File:** `gui/admin/login.py` (dòng 84)
- **Đề xuất:** Thêm `.strip()` trước khi check

### 6.9 THẤP — header.py: Thông tin user hardcoded "Admin User"
- **File:** `gui/admin/components/header.py` (dòng 102-104)
- **Đề xuất:** Hiển thị thông tin thực từ session

---

## 7. GUI USER

### ✅ 7.1 ĐÃ SỬA — Guard clause current_user None cho 11 screen
- **File:** Tất cả 11 screen trong `gui/user/` (trừ user_login.py)
- **Đã sửa:** Thêm guard clause ở đầu mỗi screen:
  ```python
  if not current_user:
      if navigate: navigate("login")
      return ft.Container()
  ```
- **Ngày sửa:** 2026-04-04

### 7.2 NGHIÊM TRỌNG — Không kiểm tra role trước khi hiện screen
- **File:** Tất cả screen trong `gui/user/`
- **Hiện tại:** Member có thể truy cập route "trainer_schedule" nếu biết tên route
- **Rủi ro:** Hội viên xem/sửa lịch dạy của HLV
- **Đề xuất:** Thêm role guard trong navigate() hoặc đầu mỗi screen

### 7.3 CAO — trainer_dashboard.py: name[0] crash nếu name rỗng
- **File:** `gui/user/trainer_dashboard.py` (dòng 89), `trainer_students.py` (dòng 119)
- **Hiện tại:** `member_obj.name[0]` — IndexError nếu name = ""
- **Đề xuất:** `name[0] if name else "?"`

### 7.4 CAO — Nhiều screen không wrap service call trong try/except
- **File:** `user_membership.py`, `user_notifications.py`, `trainer_schedule.py`, `trainer_students.py`
- **Hiện tại:** Service gọi thất bại → crash không có feedback
- **Đề xuất:** Wrap trong try/except, hiện thông báo lỗi

### 7.5 CAO — membership_repo.get_plan_by_id() có thể trả None
- **File:** `user_dashboard.py` (dòng 74), `user_history.py` (dòng 35), `user_membership.py` (dòng 74)
- **Hiện tại:** `plan = get_plan_by_id(sub.plan_id)` rồi dùng `plan.name` không check None
- **Rủi ro:** AttributeError nếu plan bị xóa

### 7.6 CAO — trainer_students.py: sub.end_date.strftime() có thể crash
- **File:** `gui/user/trainer_students.py` (dòng 91-93)
- **Hiện tại:** Giả định sub.end_date luôn là datetime, nhưng có thể là string hoặc None
- **Đề xuất:** Check type trước khi gọi strftime()

### 7.7 TRUNG BÌNH — Tiếng Việt không dấu trong một số file
- **File:**
  - `trainer_notifications.py` — "Ban khong co thong bao nao", "Thong bao", "Danh dau da doc tat ca"
  - `trainer_students.py` — "Không tìm thay hoc vien nao", "Chua co hoc vien nao"
- **Đề xuất:** Sửa tất cả về tiếng Việt có dấu
- **Ghi chú:** `trainer_schedule.py` đã được sửa DAY_NAMES có dấu

### 7.8 THẤP — app_state.py không còn sử dụng
- **File:** `gui/user/app_state.py`
- **Hiện tại:** File tồn tại nhưng comment ghi "không còn sử dụng" — state chuyển sang page object
- **Đề xuất:** Xóa file hoặc cập nhật

---

## 8. ENTRY POINTS & ARCHITECTURE

### 8.1 CAO — navigate() không catch lỗi import
- **File:** `app/main.py` (dòng 81-105), `app/user_main.py` (dòng 56-90)
- **Hiện tại:** `from gui.admin.xxx import Screen` — nếu file lỗi syntax → crash cả app
- **Đề xuất:** Wrap mỗi import trong try/except, hiện dialog lỗi

### 8.2 CAO — Auth state không reset khi logout (user app)
- **File:** `app/user_main.py` (dòng 41-42)
- **Hiện tại:** Logout chỉ navigate về login, nhưng `page.current_user` vẫn giữ giá trị cũ
- **Ghi chú:** Sidebar có reset (`page.current_user = None`), nhưng nếu logout từ nơi khác thì không
- **Đề xuất:** Đảm bảo navigate("login") luôn reset auth state

### 8.3 TRUNG BÌNH — Không validate route parameter
- **File:** `app/main.py`, `app/user_main.py`
- **Hiện tại:** navigate(None) hoặc navigate(123) sẽ rơi vào else → hiện login
- **Đề xuất:** Validate type trước

### 8.4 THẤP — Window size hardcoded khác nhau
- **File:** `app/core/config.py` (1280x800), `app/user_main.py` (1100x700)
- **Đề xuất:** Thống nhất hoặc ghi rõ lý do khác biệt

---

## BẢNG TỔNG HỢP ƯU TIÊN SỬA

### NGHIÊM TRỌNG (Còn 3 vấn đề chưa sửa)

| # | Mục | Vấn đề | Trạng thái |
|---|------|--------|------------|
| 1 | 1.1 | Credentials admin hardcoded | ⚠️ Chưa sửa |
| 2 | 1.2 | PIN lưu plaintext | ⚠️ Chưa sửa |
| 3 | 2.1 | Cascade delete member/trainer | ✅ Đã sửa 2026-04-04 |
| 4 | 7.1 | 11 screen không check current_user None | ✅ Đã sửa 2026-04-04 |
| 5 | 7.2 | Không kiểm tra role | ⚠️ Chưa sửa |

### CAO (Còn 19 vấn đề chưa sửa)

| # | Mục | Vấn đề | Trạng thái |
|---|------|--------|------------|
| 6 | 1.3 | Không rate limit đăng nhập | ⚠️ Chưa sửa |
| 7 | 1.4 | So sánh không constant-time | ⚠️ Chưa sửa |
| 8 | 2.2 | Thiếu CHECK constraint PIN | ✅ Đã sửa 2026-04-04 |
| 9 | 2.3 | Thiếu UNIQUE phone | ✅ Đã sửa 2026-04-04 |
| 10 | 2.4 | init_db() nuốt mọi exception | ⚠️ Chưa sửa |
| 11 | 2.5 | Không có schema versioning | ⚠️ Chưa sửa |
| 12 | 3.1 | Datetime vs string không nhất quán | ⚠️ Chưa sửa |
| 13 | 4.1 | change_pin() không validate old_pin | ⚠️ Chưa sửa |
| 14 | 4.2 | Magic string thay vì constant | ⚠️ Chưa sửa |
| 15 | 4.3 | assignment_svc gọi SQL trực tiếp | ⚠️ Chưa sửa |
| 16 | 4.4 | Nuốt lỗi assignment khi subscribe | ⚠️ Chưa sửa |
| 17 | 5.1 | member_repo hard delete | ✅ Đã sửa 2026-04-04 |
| 18 | 5.2 | trainer_repo hard delete | ✅ Đã sửa 2026-04-04 |
| 19 | 5.3 | notification_repo không phân trang | ⚠️ Chưa sửa |
| 20 | 5.4 | Dùng LIKE so sánh ngày | ⚠️ Chưa sửa |
| 21 | 5.5 | equipment_repo thiếu search() | ⚠️ Chưa sửa |
| 22 | 6.1 | members.py thiếu validate input | ⚠️ Chưa sửa |
| 23 | 6.2 | memberships.py dropdown None | ⚠️ Chưa sửa |
| 24 | 6.3 | memberships.py duration/price <= 0 | ⚠️ Chưa sửa |
| 25 | 6.4 | trainers.py null check subscription | ⚠️ Chưa sửa |
| 26 | 6.5 | Lambda xóa không bắt lỗi | ⚠️ Chưa sửa |
| 27 | 7.3 | name[0] crash nếu rỗng | ⚠️ Chưa sửa |
| 28 | 7.4 | Service call không try/except | ⚠️ Chưa sửa |
| 29 | 7.5 | get_plan_by_id() trả None | ⚠️ Chưa sửa |
| 30 | 8.1 | navigate() không catch lỗi import | ⚠️ Chưa sửa |

---

## LỊCH SỬ SỬA LỖI

### 2026-04-04 — Session trước (Kiểm chứng đầu vào)
- ✅ `user_login.py`: Input filter + validate cho Phone (9-11 số) và PIN (6 số)
- ✅ `user_profile.py`: Input filter + validate cho 3 trường PIN
- ✅ `trainer_profile.py`: Input filter + validate cho 3 trường PIN
- ✅ `trainer_students.py`: max_length=500 cho trường Ghi chú
- ✅ `trainer_schedule.py`: max_length=500 cho trường Nội dung buổi tập

### 2026-04-04 19:53 — Cascade soft delete
- ✅ `member_repo.py`: Soft delete + cascade tới subscriptions, assignments, sessions, notifications
- ✅ `trainer_repo.py`: Soft delete + cascade tới assignments, sessions, notifications

### 2026-04-04 20:00 — Guard clause current_user
- ✅ 11 file GUI User: Thêm guard clause redirect login nếu current_user là None

### 2026-04-04 20:11 — CHECK constraint PIN + UNIQUE phone
- ✅ `database.py`: Thêm `CHECK(LENGTH(pin) = 6)` cho cột pin trong members và trainers
- ✅ `database.py`: Thêm `UNIQUE` cho cột phone trong members và trainers (CREATE TABLE + migration UNIQUE INDEX cho DB cũ)

---

## GHI CHÚ

- SQL Injection: **AN TOÀN** — tất cả repo dùng parameterized query.
- XSS: **Rủi ro thấp** — desktop app Flet, không phải web browser.
- `trainer_schedule.py` DAY_NAMES đã được sửa có dấu tiếng Việt.

---

_Báo cáo tạo bởi AI — 2026-04-04 19:32 | Cập nhật lần cuối: 2026-04-04 20:00_
