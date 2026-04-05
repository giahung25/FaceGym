# KE HOACH GOP 2 DU AN: GYM MANAGEMENT + FACE ID

> **Ngay tao:** 2026-04-04
> **Trang thai:** Chua bat dau
> **Muc tieu:** Gop du an quan ly phong gym (Flet) va du an diem danh khuon mat (face_recognition + OpenCV) thanh 1 he thong thong nhat.

---

## 1. TONG QUAN 2 DU AN HIEN TAI

### Du an 1: `gym_management/`
| Hang muc | Chi tiet |
|----------|----------|
| **GUI** | Flet 0.82.2 (desktop/web) |
| **Database** | SQLite - 8 bang (members, membership_plans, subscriptions, equipment, trainers, notifications, trainer_assignments, training_sessions) |
| **Kien truc** | GUI -> Service -> Repository -> Database |
| **Tinh nang** | Quan ly hoi vien, goi tap, thiet bi, huan luyen vien, thong bao, lich tap |
| **Trang thai** | Admin ~95%, User app ~70% |

### Du an 2: `Face_ID/`
| Hang muc | Chi tiet |
|----------|----------|
| **AI** | face_recognition (dlib) + OpenCV |
| **Database** | SQLite - 6 bang (members, packages, member_packages, attendance, transactions) rieng biet |
| **GUI** | Chua hoan thanh (chi co CLI scripts) |
| **Tinh nang** | Nhan dien khuon mat, dang ky khuon mat, diem danh tu dong |
| **Trang thai** | Core AI hoan thanh, GUI chua lam |

### Van de chinh khi gop:
1. **2 database schema khac nhau** - bang `members` trung lap nhung cot khac nhau
2. **GUI framework khac nhau** - Flet (gym) vs chua co (Face_ID)
3. **Du lieu hoi vien trung lap** - ca 2 deu quan ly member nhung field khac nhau
4. **Thu vien khac nhau** - Flet vs OpenCV/face_recognition

---

## 2. CHIEN LUOC GOP

> **Chien luoc:** Lay `gym_management` lam nen tang chinh (vi co GUI hoan chinh + kien truc tot), tich hop module AI/Face Recognition tu `Face_ID` vao.

### So do sau khi gop:

```
gym_face_id/                          # Du an gop
├── app/                              # Backend (tu gym_management)
│   ├── core/
│   │   ├── config.py                 # Config gop (them camera, face settings)
│   │   ├── database.py               # Database gop (them bang attendance, transactions)
│   │   └── security.py
│   ├── models/
│   │   ├── ... (giu nguyen cac model cu)
│   │   ├── attendance.py             # MOI - Model diem danh
│   │   └── transaction.py            # MOI - Model giao dich
│   ├── repositories/
│   │   ├── ... (giu nguyen cac repo cu)
│   │   ├── attendance_repo.py        # MOI
│   │   └── transaction_repo.py       # MOI
│   ├── services/
│   │   ├── ... (giu nguyen cac service cu)
│   │   ├── attendance_svc.py         # MOI - Logic diem danh
│   │   └── face_svc.py              # MOI - Dieu phoi face recognition
│   └── face_id/                      # MOI - Module AI tu Face_ID
│       ├── __init__.py
│       ├── face_encoder.py           # Tu Face_ID/core/ai/
│       ├── face_recognizer.py        # Tu Face_ID/core/ai/
│       ├── face_register.py          # Tu Face_ID/core/ai/
│       └── image_processing.py       # Tu Face_ID/utils/
├── gui/
│   ├── theme.py
│   ├── admin/
│   │   ├── ... (giu nguyen)
│   │   ├── attendance.py             # MOI - Man hinh diem danh (admin)
│   │   └── face_register.py          # MOI - Man hinh dang ky khuon mat
│   └── user/
│       ├── ... (giu nguyen)
│       └── user_checkin.py           # MOI - Man hinh check-in bang khuon mat
├── data/
│   ├── gym_db.db                     # Database gop
│   ├── dataset/                      # Tu Face_ID - anh khuon mat
│   ├── encodings/                    # Tu Face_ID - face embeddings
│   └── member_pics/                  # Tu Face_ID - anh dang ky
├── logs/
├── doc/
├── requirements.txt                  # Gop dependencies
└── CLAUDE.md
```

---

## 3. CAC BUOC THUC HIEN CHI TIET

### GIAI DOAN 1: CHUAN BI (1-2 ngay)

#### Buoc 1.1: Sao luu du an
- [ ] Tao branch/backup cho ca 2 du an
- [ ] Git init cho du an gop (neu chua co)

#### Buoc 1.2: Gop dependencies
- [ ] Gop `requirements.txt`:
  ```
  flet==0.82.2
  face_recognition
  opencv-python
  numpy
  ```
- [ ] Cai dat va kiem tra tat ca thu vien chay duoc cung nhau

#### Buoc 1.3: Gop config
- [ ] Them cac config cua Face_ID vao `app/core/config.py`:
  - `CAMERA_ID`, `FRAME_WIDTH`, `FRAME_HEIGHT`
  - `FACE_TOLERANCE`, `FACE_MODEL_TYPE` (hog/cnn)
  - `FRAME_RESIZE_SCALE`
  - `DATASET_PATH`, `ENCODINGS_FILE`
  - `CHECKIN_COOLDOWN_SECONDS`

---

### GIAI DOAN 2: GOP DATABASE (2-3 ngay)

#### Buoc 2.1: Mo rong bang `members`
Them cac cot tu Face_ID vao bang members cua gym_management:

```sql
ALTER TABLE members ADD COLUMN member_code TEXT UNIQUE;
ALTER TABLE members ADD COLUMN face_registered INTEGER DEFAULT 0;
ALTER TABLE members ADD COLUMN photo_path TEXT;
```

> **Luu y:** Giu nguyen cot `photo` (gym_management) va them `photo_path` (Face_ID) hoac gop thanh 1.

#### Buoc 2.2: Them bang `attendance`
```sql
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    check_in TEXT DEFAULT (datetime('now', 'localtime')),
    check_out TEXT,
    method TEXT DEFAULT 'face_id' CHECK(method IN ('face_id', 'manual', 'qr_code')),
    confidence REAL,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (member_id) REFERENCES members(id)
);
```

#### Buoc 2.3: Them bang `transactions`
```sql
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    subscription_id INTEGER,
    amount REAL NOT NULL,
    payment_method TEXT CHECK(payment_method IN ('cash', 'transfer', 'card')),
    note TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
);
```

#### Buoc 2.4: Cap nhat `database.py`
- [ ] Them CREATE TABLE cho 2 bang moi vao `init_db()`
- [ ] Them migration ALTER TABLE cho bang members
- [ ] Them index cho attendance (member_id, check_in)

---

### GIAI DOAN 3: TICH HOP MODULE FACE ID (3-4 ngay)

#### Buoc 3.1: Chuyen code AI vao du an gop
- [ ] Tao thu muc `app/face_id/`
- [ ] Copy va chinh sua tu `Face_ID/core/ai/`:
  - `face_encoder.py` - cap nhat import paths
  - `face_recognizer.py` - cap nhat import paths
  - `face_register.py` - **sua lai** de lam viec voi database gop (khong dung database rieng cua Face_ID nua)
- [ ] Copy `Face_ID/utils/image_processing.py` -> `app/face_id/image_processing.py`

#### Buoc 3.2: Tao model + repository moi
- [ ] `app/models/attendance.py` - Attendance model ke thua BaseModel
- [ ] `app/models/transaction.py` - Transaction model ke thua BaseModel
- [ ] `app/repositories/attendance_repo.py` - CRUD cho attendance
- [ ] `app/repositories/transaction_repo.py` - CRUD cho transactions

#### Buoc 3.3: Tao service layer
- [ ] `app/services/face_svc.py`:
  ```python
  class FaceService:
      def register_face(member_id, photos) -> bool
      def encode_all_faces() -> None
      def recognize_face(frame) -> (member_id, confidence)
      def load_encodings() -> dict
      def get_registration_status(member_id) -> bool
  ```
- [ ] `app/services/attendance_svc.py`:
  ```python
  class AttendanceService:
      def check_in(member_id, method, confidence) -> bool
      def check_out(member_id) -> bool
      def get_today_attendance() -> list
      def get_member_attendance(member_id, from_date, to_date) -> list
      def is_already_checked_in(member_id) -> bool
      def get_attendance_stats() -> dict
  ```

#### Buoc 3.4: Cap nhat member service
- [ ] Them `face_registered` field vao member operations
- [ ] Them `member_code` auto-generation (format: GYM-YYYYMMDD-XXX)
- [ ] Lien ket member voi face data khi dang ky khuon mat

---

### GIAI DOAN 4: XAY DUNG GUI (4-5 ngay)

#### Buoc 4.1: Man hinh diem danh (Admin) - `gui/admin/attendance.py` ✅
- [x] Hien thi camera feed trong Flet (dung `ft.Image` + threading)
- [x] Hien thi thong tin nguoi duoc nhan dien (ten, anh, goi tap)
- [x] Bang lich su diem danh hom nay
- [x] Nut check-in thu cong (fallback khi face ID khong nhan dien duoc)
- [x] Thong ke nhanh (so nguoi check-in hom nay)

**Giai phap ky thuat cho camera trong Flet:**
```python
import threading
import base64
import cv2
import flet as ft

class CameraFeed:
    """Chay camera tren thread rieng, gui frame qua base64 -> ft.Image"""
    def __init__(self, page, image_control):
        self.running = False
        self.page = page
        self.image_control = image_control

    def start(self):
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Face recognition processing here
                _, buffer = cv2.imencode('.jpg', frame)
                img_base64 = base64.b64encode(buffer).decode()
                self.image_control.src_base64 = img_base64
                self.page.update()
        cap.release()
```

#### Buoc 4.2: Man hinh dang ky khuon mat - `gui/admin/face_register.py` ✅
- [x] Chon member tu danh sach (nhung nguoi chua dang ky face)
- [x] Hien thi camera feed
- [x] Chup nhieu anh (5-10 anh) tu nhieu goc
- [x] Hien thi progress bar
- [x] Xac nhan dang ky thanh cong
- [x] Tu dong encode va luu face embeddings

#### Buoc 4.3: Man hinh check-in (User) - `gui/user/user_checkin.py` ✅
- [x] Hien thi camera full screen
- [x] Tu dong nhan dien va hien thi ket qua
- [x] Hien thi thong tin hoi vien khi nhan dien thanh cong
- [x] Thong bao khi goi tap het han

#### Buoc 4.4: Cap nhat Dashboard ✅
- [x] **Admin dashboard:** Them widget "Diem danh hom nay" (so luong, bieu do)
- [x] **User dashboard:** Them lich su diem danh cua member
- [ ] **Trainer dashboard:** Them thong tin diem danh cua hoc vien

#### Buoc 4.5: Cap nhat Sidebar ✅
- [x] **Admin sidebar:** Them menu "Diem danh" va "Dang ky khuon mat"
- [x] **User sidebar:** Them menu "Check-in"

#### Buoc 4.6: Cap nhat Reports
- [ ] Them bao cao diem danh (theo ngay/tuan/thang)
- [ ] Thong ke tan suat tap luyen cua hoi vien
- [ ] Bieu do gio cao diem

---

### GIAI DOAN 5: KIEM TRA VA HOAN THIEN (2-3 ngay)

#### Buoc 5.1: Kiem tra tich hop
- [ ] Dang ky member moi -> dang ky khuon mat -> diem danh bang face ID
- [ ] Kiem tra khi goi tap het han -> tu choi check-in
- [ ] Kiem tra chong check-in trung (cooldown 30 giay)
- [ ] Kiem tra fall back: check-in thu cong khi camera hong

#### Buoc 5.2: Xu ly loi
- [ ] Camera khong ket noi duoc -> hien thi thong bao
- [ ] Khong nhan dien duoc -> cho phep check-in thu cong
- [ ] Face encoding file bi loi -> tu dong rebuild

#### Buoc 5.3: Toi uu hieu suat
- [ ] Xu ly face recognition tren background thread
- [ ] Resize frame truoc khi xu ly (50%)
- [ ] Chi xu ly moi frame thu 3
- [ ] Cache ket qua nhan dien

#### Buoc 5.4: Di chuyen du lieu cu
- [ ] Script migration face data tu `Face_ID/data/` sang du an gop
- [ ] Dong bo member giua 2 database (neu co du lieu cu)

---

## 4. THU TU UU TIEN

| STT | Cong viec | Do uu tien | Giai doan |
|-----|-----------|------------|-----------|
| 1 | Gop config + dependencies | **Cao** | 1 |
| 2 | Mo rong database schema | **Cao** | 2 |
| 3 | Chuyen module AI vao du an | **Cao** | 3 |
| 4 | Tao attendance service | **Cao** | 3 |
| 5 | Man hinh diem danh (Admin) | **Cao** | 4 |
| 6 | Man hinh dang ky khuon mat | **Cao** | 4 |
| 7 | Man hinh check-in (User) | Trung binh | 4 |
| 8 | Cap nhat dashboard + reports | Trung binh | 4 |
| 9 | Kiem tra tich hop | **Cao** | 5 |
| 10 | Toi uu hieu suat | Thap | 5 |

---

## 5. RUI RO VA GIAI PHAP

| Rui ro | Muc do | Giai phap |
|--------|--------|-----------|
| Camera feed trong Flet cham/lag | Cao | Dung threading + base64 encoding, resize frame, giam FPS |
| Thu vien face_recognition kho cai tren Windows | Trung binh | Dung pre-built wheel hoac conda install |
| 2 database conflict khi merge | Trung binh | Lay gym_management lam chinh, chi them bang/cot moi |
| Face recognition khong chinh xac | Thap | Dieu chinh tolerance, chup nhieu anh khi dang ky |
| Hieu suat giam khi chay AI + GUI cung luc | Trung binh | Tach AI processing sang thread rieng, xu ly async |

---

## 6. KET QUA MONG DOI SAU KHI GOP

1. **1 ung dung duy nhat** voi 2 entry point (Admin + User)
2. **Diem danh tu dong** bang nhan dien khuon mat tich hop truc tiep trong GUI
3. **Quan ly toan dien:** hoi vien, goi tap, thiet bi, HLV, lich tap, diem danh, thanh toan
4. **1 database duy nhat** chua tat ca du lieu
5. **Kien truc sach:** GUI -> Service -> Repository/FaceID -> Database
6. **Fall back:** Khi camera/face ID khong hoat dong, van co the check-in thu cong

---

## 7. TIMELINE DU KIEN

```
Tuan 1: Giai doan 1 + 2 (Chuan bi + Gop database)
Tuan 2: Giai doan 3 (Tich hop Face ID module)
Tuan 3: Giai doan 4 (Xay dung GUI)
Tuan 4: Giai doan 5 (Kiem tra + Hoan thien)
```

> **Tong thoi gian du kien:** 3-4 tuan lam viec
