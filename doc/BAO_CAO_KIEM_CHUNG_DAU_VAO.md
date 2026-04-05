# BAO CAO KIEM CHUNG DAU VAO - USER APP

> Ngay kiem tra: 2026-04-04
> Pham vi: Toan bo User App (`gui/user/`) va cac service lien quan
> Trang thai: CHO DUYET — Chua sua doi code

---

## TONG KET NHANH

| Muc do       | So luong | Mo ta                                                                              |
| ------------ | -------- | ---------------------------------------------------------------------------------- |
| NGHIEM TRONG | 3        | PIN khong kiem tra so, truong text khong gioi han do dai                           |
| CAO          | 3        | Phone khong kiem tra dinh dang, dropdown co the bi spoof, khong gioi han dang nhap |
| TRUNG BINH   | 2        | Tim kiem khong escape ky tu dac biet, old PIN khong validate                       |

**Tong: 8 van de can xu ly**

---

## CHI TIET THEO MAN HINH

### 1. MAN HINH DANG NHAP (`gui/user/user_login.py`)

#### 1.1 Truong SĐT (Phone)

- **Loai:** TextField (dong 77-85)
- **Hien tai:** Kiem tra rong + strip()
- **THIEU:**
  - Khong co `max_length` tren TextField
  - Khong kiem tra dinh dang so dien thoai (cho phep chu cai, ky tu dac biet)
  - Khong co regex (VD: `^0\d{9}$` cho so VN)
  - Khong co `input_filter` chi cho phep so
  - Nguoi dung co the nhap: `"abc !@#"` → van gui len service

#### 1.2 Truong PIN

- **Loai:** TextField password (dong 86-97)
- **Hien tai:** `max_length=6`, kiem tra rong
- **THIEU:**
  - Khong co `input_filter=ft.InputFilter.digits_only` → cho phep nhap chu cai
  - Khong kiem tra do dai toi thieu (co the gui 1-5 ky tu)
  - Nguoi dung co the nhap `"abcdef"` → gui len service, so sanh sai

---

### 2. MAN HINH HO SO HOI VIEN (`gui/user/user_profile.py`)

#### 2.1 Truong PIN cu (dong 47-50)

- **Hien tai:** `max_length=6`, kiem tra rong
- **THIEU:**
  - Khong co `input_filter` chi cho so
  - Khong kiem tra dung 6 chu so truoc khi gui

#### 2.2 Truong PIN moi (dong 51-54)

- **Hien tai:** `max_length=6`, kiem tra rong, so sanh voi xac nhan
- **THIEU:**
  - Khong co `input_filter` chi cho so
  - Service (`auth_svc.change_pin` dong 70) CO kiem tra `isdigit()` → nhung GUI van cho nhap sai roi moi bao loi
  - Nen chan tu GUI de trai nghiem tot hon

#### 2.3 Truong xac nhan PIN (dong 55-58)

- **THIEU:** Tuong tu PIN moi

> **Ghi chu:** Service `auth_svc.change_pin()` da validate PIN moi (6 so, isdigit) nhung KHONG validate PIN cu. GUI nen validate truoc de UX tot hon.

---

### 3. MAN HINH HO SO HLV (`gui/user/trainer_profile.py`)

#### 3.1-3.3 Ba truong PIN (dong 70-81)

- **Van de giong het** man hinh ho so hoi vien (muc 2 o tren)
- Thieu `input_filter` cho so
- Thieu kiem tra do dai toi thieu

---

### 4. MAN HINH HOC VIEN CUA HLV (`gui/user/trainer_students.py`)

#### 4.1 Truong Ghi chu (Notes) (dong 22-25)

- **Loai:** TextField multiline, `min_lines=3, max_lines=5`
- **Hien tai:** Khong co bat ky validation nao
- **THIEU:**
  - **Khong co `max_length`** → nguoi dung co the dan van ban cuc lon (100KB+)
  - Service `assignment_svc.update_assignment_notes()` khong kiem tra do dai
  - Repository dung parameterized query (an toan SQL injection) nhung khong gioi han kich thuoc
  - **De xuat:** Them `max_length=500`

#### 4.2 Truong Tim kiem (dong 225-232)

- **Loai:** TextField voi `on_change`
- **Hien tai:** `filter_students()` dung `.lower()` va `in` de so sanh
- **THIEU:**
  - Khong escape ky tu dac biet regex
  - Chuoi tim kiem qua dai co the anh huong hieu nang
  - **De xuat:** Them `max_length=50`

---

### 5. MAN HINH LICH DAY HLV (`gui/user/trainer_schedule.py`)

#### 5.1 Dropdown Hoc vien (dong 32)

- **Hien tai:** Options tu danh sach hoc vien duoc gan
- **THIEU:**
  - Service `schedule_svc.create_session()` chi kiem tra `if not member_id` (rong)
  - **Khong kiem tra member_id co ton tai trong DB** → co the luu ID gia
  - **De xuat:** Them kiem tra ton tai member trong service

#### 5.2 Dropdown Gio/Phut (dong 35-39)

- **Hien tai:** Options co dinh (gio 05-22, phut buoc 5)
- **THIEU:**
  - Service `_validate_time()` DA validate HH:MM + range → **day la OK**
  - Dropdown la desktop app (Flet) → kho spoof hon web app
  - **Rui ro thap** cho desktop app

#### 5.3 Truong Noi dung buoi tap (dong 40)

- **Loai:** TextField
- **Hien tai:** `.strip()` (dong 82)
- **THIEU:**
  - **Khong co `max_length`** → tuong tu van de ghi chu
  - Service khong validate do dai
  - **De xuat:** Them `max_length=500`

#### 5.4 Truong Ngay (dong 33)

- **Hien tai:** `read_only=True` → nguoi dung khong the sua
- **Trang thai:** OK — khong can them validation

---

### 6. CAC MAN HINH CHI HIEN THI (Khong co dau vao)

| Man hinh           | File                       | Ket qua                           |
| ------------------ | -------------------------- | --------------------------------- |
| Dashboard hoi vien | `user_dashboard.py`        | OK — chi hien thi                 |
| Lich su            | `user_history.py`          | OK — chi hien thi                 |
| Thong bao hoi vien | `user_notifications.py`    | OK — chi hien thi                 |
| Dashboard HLV      | `trainer_dashboard.py`     | OK — chi hien thi                 |
| Thong bao HLV      | `trainer_notifications.py` | OK — chi hien thi                 |
| Goi tap            | `user_membership.py`       | OK — chi bam nut, khong nhap lieu |

---

## KIEM TRA TANG SERVICE

### `app/services/auth_svc.py`

| Ham               | Validate dung                    | Thieu                                                                |
| ----------------- | -------------------------------- | -------------------------------------------------------------------- |
| `login_member()`  | Rong, strip                      | Dinh dang phone, dinh dang PIN                                       |
| `login_trainer()` | Rong, strip                      | Tuong tu login_member                                                |
| `change_pin()`    | new_pin: 6 so, isdigit, khac old | old_pin: khong validate dinh dang; user_type: khong validate gia tri |

### `app/services/schedule_svc.py`

| Ham                      | Validate dung                       | Thieu                                                 |
| ------------------------ | ----------------------------------- | ----------------------------------------------------- |
| `create_session()`       | date, time, time_range, member rong | content khong gioi han, khong kiem tra member ton tai |
| `update_session()`       | date, time, time_range              | tuong tu create                                       |
| `_validate_date()`       | YYYY-MM-DD format                   | OK                                                    |
| `_validate_time()`       | HH:MM, gio 0-23, phut 0-59          | OK                                                    |
| `_validate_time_range()` | start < end                         | OK                                                    |

### `app/services/assignment_svc.py`

| Ham                         | Validate dung               | Thieu                       |
| --------------------------- | --------------------------- | --------------------------- |
| `update_assignment_notes()` | Kiem tra assignment ton tai | notes khong gioi han do dai |

### Bao mat SQL Injection

- **Tat ca repository deu dung parameterized query (`?`)** → AN TOAN
- Khong co rui ro SQL injection

---

## BANG TONG HOP DE XUAT SUA

| #   | Muc do       | File                  | Truong         | De xuat sua                                     |
| --- | ------------ | --------------------- | -------------- | ----------------------------------------------- |
| 1   | ✅ NGHIEM TRONG | `user_login.py`       | PIN            | Them `input_filter` chi so + validate 6 so      |
| 2   | ✅ NGHIEM TRONG | `user_login.py`       | Phone          | Them `input_filter` chi so, `max_length=11`, validate 9-11 so |
| 3   | ✅ NGHIEM TRONG | `trainer_students.py` | Notes          | Them `max_length=500`                           |
| 4   | ✅ CAO          | `trainer_schedule.py` | Content        | Them `max_length=500`                           |
| 5   | ✅ CAO          | `user_profile.py`     | 3 truong PIN   | Them `input_filter` chi so + validate 6 so      |
| 6   | ✅ CAO          | `trainer_profile.py`  | 3 truong PIN   | Them `input_filter` chi so + validate 6 so      |
| 7   | TRUNG BINH   | `trainer_students.py` | Search         | Them `max_length=50`                            |
| 8   | TRUNG BINH   | `auth_svc.py`         | `change_pin()` | Validate dinh dang old_pin (6 so)               |

---

## GHI CHU

- **SQL Injection:** An toan — tat ca repo dung parameterized query
- **XSS:** Rui ro thap vi la desktop app (Flet render native, khong phai web browser)
- **Dropdown spoof:** Rui ro thap vi la desktop app (khong co DevTools nhu web)
- **PIN plaintext:** Hien tai PIN luu plaintext trong DB — day la van de bao mat rieng, khong thuoc pham vi bao cao nay
- **Rate limiting:** Ly tuong nen co nhung phu thuoc vao yeu cau bao mat cua du an

---

_Da sua 6/8 van de (3 NGHIEM TRONG + 3 CAO). Con lai 2 van de TRUNG BINH._
