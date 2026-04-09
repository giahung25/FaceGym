# GymFit / GymAdmin - Hệ thống Quản lý Phòng Gym tích hợp Face ID

Dự án **GymFit/GymAdmin** là một hệ thống quản lý phòng tập thể hình toàn diện, được phát triển bằng Python với giao diện Desktop (Flet). Điểm nhấn của hệ thống là tính năng **nhận diện khuôn mặt (Face ID)** để tự động hóa quy trình điểm danh (check-in/check-out) nhanh chóng và chính xác.

## 🌟 Tính năng Nổi bật

Hệ thống bao gồm 2 ứng dụng độc lập dành cho các đối tượng người dùng khác nhau:

### 1. Ứng dụng Quản lý (Admin App - `app/main.py`)

Dành cho Chủ phòng tập và Lễ tân:

- **Quản lý Hội viên:** Thêm mới, chỉnh sửa thông tin, chụp ảnh và đăng ký khuôn mặt trực tiếp từ Camera.
- **Quản lý Gói tập (Memberships):** Tạo gói tập, đăng ký gia hạn cho hội viên.
- **Điểm danh tự động (Face ID):** Quét khuôn mặt bằng Camera để check-in/check-out, ghi nhận lịch sử.
- **Quản lý Thiết bị & Huấn luyện viên:** Theo dõi tình trạng máy móc, phân công HLV cho hội viên.
- **Báo cáo Thống kê:** Theo dõi doanh thu, số lượng người tập trong ngày.

### 2. Ứng dụng Người dùng (User App - `app/user_main.py`)

Dành cho Hội viên và Huấn luyện viên (HLV):

- **Hội viên:** Xem thông tin cá nhân, kiểm tra thời hạn gói tập, xem lịch tập, lịch sử check-in và nhận thông báo.
- **Huấn luyện viên:** Xem danh sách học viên đang quản lý, lịch dạy, lên lịch buổi tập mới.

---

## 🚀 Cài đặt & Hướng dẫn Chạy

### 1. Yêu cầu Hệ thống (Prerequisites)

- Python 3.8 trở lên
- Trình quản lý gói `pip`
- (Khuyến nghị) Sử dụng môi trường ảo (Virtual Environment)

### 2. Cài đặt Thư viện

Mở Terminal/Command Prompt tại thư mục dự án và chạy:

```bash
pip install -r requirements.txt
```

_Lưu ý:_ Thư viện `face_recognition` có thể yêu cầu cài đặt CMake và C++ Build Tools (trên Windows) để biên dịch `dlib`.

### 3. Khởi động Ứng dụng

- **Mở App Quản trị (Admin):**
  ```bash
  python app/main.py
  ```
- **Mở App Người dùng (User/Trainer):**
  ```bash
  python app/user_main.py
  ```
- _(Chỉ trên Windows)_ Chạy nhanh bằng file batch (nếu có):
  ```bash
  run.bat
  ```

---

## 🏗️ Cấu trúc Thư mục

Dự án áp dụng mô hình kiến trúc đa tầng (Service-Repository Pattern):

```text
E:\FaceGym\
├── app/
│   ├── api/            # (Mở rộng) Endpoint API
│   ├── core/           # Cấu hình chung (config.py, database.py, security.py)
│   ├── face_id/        # Logic nhận diện khuôn mặt (Encoder, Recognizer, Camera)
│   ├── models/         # Định nghĩa các bảng Database (Member, Trainer, Attendance...)
│   ├── repositories/   # Tầng tương tác Database SQLite (CRUD)
│   ├── services/       # Tầng xử lý nghiệp vụ (Business Logic)
│   ├── main.py         # Entry point cho App Quản trị
│   └── user_main.py    # Entry point cho App Người dùng
├── data/               # Nơi lưu trữ Database (.db) và ảnh khuôn mặt (dataset)
├── doc/                # Tài liệu hướng dẫn sử dụng, báo cáo, UML
├── gui/                # Tầng giao diện người dùng bằng thư viện Flet
│   ├── admin/          # Các màn hình của Admin App
│   └── user/           # Các màn hình của User App
└── tests/              # Mã nguồn kiểm thử (Pytest)
```

---

## 🧪 Kiểm thử (Testing)

Dự án có bộ kiểm thử tự động sử dụng `pytest` bao phủ các logic quan trọng (Services, Repositories, Face ID).

Để chạy bộ kiểm thử và xem báo cáo độ phủ mã nguồn (coverage):

```bash
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 🛠️ Công nghệ Sử dụng

- **Giao diện (UI):** [Flet](https://flet.dev/) (Flutter for Python)
- **Cơ sở dữ liệu:** SQLite (với cấu trúc Repository pattern)
- **Computer Vision:** `opencv-python`, `face_recognition` (dlib)
- **Kiểm thử:** `pytest`, `pytest-mock`, `pytest-cov`

---

## 📚 Tài liệu Tham khảo thêm

- [Hướng dẫn sử dụng chi tiết](doc/manuals/huong_dan_su_dung.md)
- [Báo cáo Cấu trúc Thư mục](doc/manuals/cau_truc_thu_muc.md)
- [Ghi chú kỹ thuật về Face ID](doc/notes/face_id_note.md)
- [Tài liệu Thiết kế UI / SDK](doc/technical/sdk)
