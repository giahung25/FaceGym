# BÁO CÁO TIẾN ĐỘ DỰ ÁN
# Hệ Thống Nhận Diện Khuôn Mặt — Quản Lý Phòng Gym

> **Ngày báo cáo:** 17/03/2026  
> **Dự án:** Face_ID — Gym Management with Face Recognition  
> **Ngôn ngữ:** Python 3.11  
> **Thư viện chính:** face_recognition, OpenCV, SQLite3, NumPy

---

## 1. TỔNG QUAN

Dự án xây dựng phần mềm quản lý phòng Gym tích hợp nhận diện khuôn mặt (Face ID) để:
- Tự động **đăng ký** khuôn mặt hội viên qua camera.
- **Nhận diện** và điểm danh hội viên thời gian thực.
- **Quản lý** thông tin hội viên, gói tập, giao dịch bằng SQLite.

---

## 2. CÁC MODULE ĐÃ HOÀN THÀNH

### 2.1. Module AI — Nhận diện khuôn mặt (`core/ai/`)

| File | Chức năng | Trạng thái |
|------|-----------|:----------:|
| `face_encoder.py` | Encode ảnh khuôn mặt → vector embedding 128 chiều | ✅ |
| `face_recognizer.py` | Nhận diện khuôn mặt real-time từ camera | ✅ |
| `face_register.py` | Đăng ký khuôn mặt hội viên mới (chụp + encode + lưu) | ✅ |
| `register_face.py` | Script CLI để chạy đăng ký | ✅ |
| `__init__.py` | Export API: FaceEncoder, FaceDetector, FaceRecognitionSystem, FaceRegistration | ✅ |

**Chi tiết:**

#### `face_encoder.py` — Class `FaceEncoder`
- `encode_face(image_path)` → Đọc 1 ảnh, trả về mảng 128 số (embedding).
- `encode_all_members(dataset_dir)` → Duyệt toàn bộ thư mục `data/dataset/`, encode tất cả ảnh.
- `save_encodings(data, path)` → Lưu embeddings ra file pickle.
- `load_encodings(path)` → Đọc file pickle đã lưu.

#### `face_recognizer.py` — Class `FaceDetector` & `FaceRecognitionSystem`
- `FaceDetector.detect(frame)` → Phát hiện vị trí khuôn mặt trong frame.
- `FaceDetector.detect_and_encode(frame)` → Vừa detect vừa encode (tối ưu).
- `FaceRecognitionSystem.recognize_frame(frame)` → Nhận diện khuôn mặt, trả về tên + confidence.
- `FaceRecognitionSystem.run_camera_loop()` → Vòng lặp camera chính (bấm Q thoát).
- Tối ưu hiệu năng: thu nhỏ frame 50%, xử lý mỗi 2 frame, hiển thị FPS.

#### `face_register.py` — Class `FaceRegistration`
- `capture_faces(name, num_photos)` → Mở camera, chụp ảnh với giao diện HUD:
  - Hiển thị tên, số ảnh, thanh tiến trình, trạng thái detect.
  - SPACE = chụp thủ công, A = auto-capture (1.5s/lần), Q = hoàn tất.
  - Tự động crop khuôn mặt + padding 30%.
- `register_member(name, num_photos)` → Quy trình đăng ký hoàn chỉnh (chụp + encode + lưu pickle).
- `register_from_images(name, image_paths)` → Đăng ký từ ảnh có sẵn (không cần camera).
- `remove_member(name)` → Xóa hội viên khỏi file encodings.
- `list_members()` → Liệt kê hội viên đã đăng ký.

---

### 2.2. Cấu hình hệ thống (`config/settings.py`)

| Hằng số | Giá trị | Mô tả |
|---------|---------|-------|
| `CAMERA_ID` | 0 | ID webcam |
| `FRAME_WIDTH / HEIGHT` | 640 × 480 | Kích thước frame |
| `TOLERANCE` | 0.5 | Ngưỡng nhận diện (càng nhỏ càng nghiêm ngặt) |
| `MODEL_TYPE` | "hog" | Mô hình detect: "hog" (CPU) / "cnn" (GPU) |
| `FRAME_RESIZE_SCALE` | 0.5 | Tỷ lệ thu nhỏ frame khi xử lý |
| `DATASET_PATH` | `data/dataset/` | Ảnh gốc hội viên |
| `ENCODINGS_FILE` | `data/encodings/face_encodings.pkl` | File encoding chính |
| `DB_PATH` | `database/gym_gym.db` | File database SQLite |

---

### 2.3. Database SQLite (`database/`)

| File | Chức năng | Trạng thái |
|------|-----------|:----------:|
| `models.py` | Định nghĩa 5 bảng + khởi tạo database | ✅ |
| `crud_members.py` | CRUD hội viên (thêm/sửa/xóa/tìm) | ✅ |
| `crud_billing.py` | Gói tập, điểm danh, giao dịch | ✅ |

**Sơ đồ quan hệ các bảng:**

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│   members    │       │ member_packages  │       │   packages   │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │◄──┐   │ id (PK)          │   ┌──►│ id (PK)      │
│ member_code  │   ├───│ member_id (FK)   │   │   │ package_name │
│ full_name    │   │   │ package_id (FK)──│───┘   │ duration_days│
│ phone        │   │   │ start_date       │       │ price        │
│ email        │   │   │ end_date         │       │ description  │
│ gender       │   │   │ status           │       │ is_active    │
│ date_of_birth│   │   └──────────────────┘       └──────────────┘
│ photo_path   │   │
│face_registered│   │   ┌──────────────┐          ┌──────────────┐
│ status       │   │   │  attendance  │          │ transactions │
│ created_at   │   │   ├──────────────┤          ├──────────────┤
└──────────────┘   │   │ id (PK)      │          │ id (PK)      │
                   ├───│ member_id(FK)│          │ member_id(FK)│───┐
                   │   │ check_in     │      ┌───│ package_id(FK│   │
                   │   │ check_out    │      │   │ amount       │   │
                   │   │ method       │      │   │payment_method│   │
                   │   │ confidence   │      │   │ note         │   │
                   │   └──────────────┘      │   └──────────────┘   │
                   │                         │                      │
                   └─────────────────────────┴──────────────────────┘
```

**Các hàm CRUD chính:**

| Hàm | Mô tả |
|-----|-------|
| `add_member(name, phone, ...)` | Thêm hội viên, tự tạo mã `GYM-YYYYMMDD-XXX` |
| `get_member_by_id/code/name()` | Tìm kiếm hội viên |
| `update_member(id, **kwargs)` | Cập nhật thông tin |
| `update_face_status(id)` | Đánh dấu đã đăng ký Face ID |
| `delete_member(id)` | Xóa hội viên (CASCADE) |
| `add_package(name, days, price)` | Thêm gói tập |
| `register_package(member_id, pkg_id)` | Đăng ký gói cho hội viên |
| `check_in(member_id, method)` | Ghi nhận điểm danh |
| `check_out(attendance_id)` | Ghi nhận check-out |
| `add_transaction(member_id, amount)` | Ghi giao dịch thanh toán |
| `get_revenue_today()` | Thống kê doanh thu hôm nay |

---

### 2.4. Tiện ích (`utils/`)

| File | Chức năng | Trạng thái |
|------|-----------|:----------:|
| `image_processing.py` | Vẽ bbox, resize frame, convert BGR↔RGB | ✅ |
| `logger.py` | Logger ghi ra console + file `logs/system.log` | ✅ |

---

### 2.5. Hệ thống điểm danh (`core/attendance.py`)

| File | Chức năng | Trạng thái |
|------|-----------|:----------:|
| `core/attendance.py` | Class `AttendanceSystem` — Điểm danh tự động bằng Face ID | ✅ |
| `run_attendance.py` | Script CLI chạy hệ thống điểm danh | ✅ |

**Quy trình hoạt động:**

```
Camera → Nhận diện khuôn mặt → Tìm member_id trong DB → Kiểm tra hạn thẻ → Ghi check-in → Thông báo
```

**Chi tiết class `AttendanceSystem`:**
- `run(camera_id)` → Vòng lặp camera điểm danh chính (Q=thoát, R=reload).
- `_recognize_and_checkin(frame)` → Nhận diện + tự động ghi check-in vào bảng `attendance`.
- `_process_checkin(name, confidence)` → Xử lý logic check-in:
  - 🟢 **success** — Ghi DB thành công.
  - 🟡 **already** — Đã điểm danh hôm nay (không ghi trùng).
  - 🔴 **expired** — Gói tập hết hạn.
  - 🟠 **not_found** — Khuôn mặt khớp nhưng chưa có trong DB.
  - ⏱️ **cooldown** — Chờ 30 giây giữa 2 lần check-in cùng người.
- Hiển thị HUD: đồng hồ, FPS, thông báo auto-hide sau 3 giây.

---

### 2.6. File tài liệu

| File | Nội dung |
|------|----------|
| `cau_truc_thu_muc.md` | Sơ đồ cấu trúc thư mục dự án (đã cập nhật) |
| `huong_dan_su_dung.md` | Hướng dẫn từng bước 2 chức năng chính |
| `note.md` | Tài liệu phân tích yêu cầu tổng quan |
| `bao_cao.md` | File báo cáo này |

---

## 3. CÁC MODULE CHƯA HOÀN THÀNH

| Module | Mô tả | Trạng thái |
|--------|-------|:----------:|
| `core/membership.py` | Logic quản lý thẻ (đăng ký, gia hạn) | ⏳ Chưa implement |
| `gui/app.py` | Giao diện chính (Dashboard) | ⏳ Chưa implement |
| `gui/views/register_view.py` | Cửa sổ đăng ký hội viên (GUI) | ⏳ Chưa implement |
| `gui/views/member_view.py` | Cửa sổ quản lý danh sách hội viên | ⏳ Chưa implement |
| `gui/views/setting_view.py` | Cửa sổ cài đặt hệ thống | ⏳ Chưa implement |
| `gui/components/camera_thread.py` | Luồng camera riêng cho GUI | ⏳ Chưa implement |
| `main.py` | Entry point khởi chạy ứng dụng GUI | ⏳ Chưa implement |

---

## 4. KẾT QUẢ KIỂM THỬ

| Test | Kết quả |
|------|:-------:|
| Import `core.ai` (FaceEncoder, FaceDetector, FaceRecognitionSystem, FaceRegistration) | ✅ Pass |
| Khởi tạo FaceEncoder (model="hog") | ✅ Pass |
| Khởi tạo FaceRegistration | ✅ Pass |
| CLI `register_face.py --list` | ✅ Pass |
| Mở camera + nhận diện real-time + bấm Q thoát | ✅ Pass |
| Init database (tạo 5 bảng) | ✅ Pass |
| Add member → Query → Delete | ✅ Pass |
| Logger ghi ra console + file | ✅ Pass |
| Import `AttendanceSystem` + khởi tạo | ✅ Pass |
| AttendanceSystem load encodings (2 hội viên) | ✅ Pass |

---

## 5. HƯỚNG PHÁT TRIỂN TIẾP THEO

1. **Implement `core/membership.py`** — Logic gia hạn, kiểm tra hết hạn thẻ.
2. **Xây dựng GUI** bằng PyQt5/CustomTkinter — Dashboard chính với camera live.
3. **Tích hợp toàn bộ** vào `main.py` — Entry point khởi chạy ứng dụng hoàn chỉnh.
