# Cấu Trúc Thư Mục Dự Án Phần Mềm Quản Lý Phòng Gym (Tích hợp Face ID)

Để đảm bảo dự án dễ quản lý, bảo trì và mở rộng sau này, mã nguồn được chia thành các thư mục với chức năng biệt lập như sau:

```text
Face_ID/
│
├── main.py                     # Điểm khởi đầu của ứng dụng (Run file này)
├── test.py                     # File test nhanh các chức năng
├── config.py                   # (Legacy) File config gốc
│
├── config/                     # Cấu hình hệ thống
│   ├── __init__.py
│   └── settings.py             # Hằng số: Camera, Tolerance, đường dẫn, logging
│
├── core/                       # Logic nghiệp vụ & Xử lý AI
│   ├── __init__.py
│   ├── ai/                     # ★ Module chuyên xử lý Face ID
│   │   ├── __init__.py         # Export: FaceEncoder, FaceDetector, FaceRecognitionSystem, FaceRegistration
│   │   ├── face_encoder.py     # Chuyển ảnh khuôn mặt → vector embedding 128D
│   │   ├── face_recognizer.py  # Nhận diện khuôn mặt real-time từ Camera
│   │   ├── face_register.py    # Đăng ký khuôn mặt hội viên mới (chụp + encode + lưu)
│   │   └── register_face.py    # Script CLI để chạy đăng ký (python core/ai/register_face.py)
│   ├── attendance.py           # Logic điểm danh (kiểm tra hạn thẻ, ghi log)
│   ├── membership.py           # Logic quản lý thẻ (đăng ký, gia hạn, hết hạn)
│   └── utils.py                # Các tiện ích hỗ trợ nghiệp vụ
│
├── database/                   # Quản lý dữ liệu (Chia nhỏ theo nghiệp vụ)
│   ├── __init__.py
│   ├── models.py               # Định nghĩa các bảng (Member, Package, Attendance, ...)
│   ├── crud_members.py         # Các hàm thêm/sửa/xóa/đọc thông tin Hội viên
│   └── crud_billing.py         # Các hàm xử lý giao dịch, hóa đơn, gói tập
│
├── gui/                        # Giao diện người dùng (CustomTkinter / PyQt)
│   ├── __init__.py
│   ├── app.py                  # Main Dashboard (Thống kê, hiển thị camera chính)
│   ├── views/                  # Các cửa sổ chức năng độc lập
│   │   ├── __init__.py
│   │   ├── register_view.py    # Cửa sổ đăng ký hội viên mới (nhập info, chụp ảnh)
│   │   ├── member_view.py      # Cửa sổ quản lý danh sách hội viên
│   │   └── setting_view.py     # Cửa sổ cài đặt hệ thống
│   └── components/             # Các UI con tái sử dụng
│       ├── __init__.py
│       └── camera_thread.py    # Luồng camera riêng (QThread) tránh UI bị freeze
│
├── data/                       # Nơi lưu trữ tài nguyên động phát sinh trong lúc chạy
│   ├── dataset/                # Ảnh gốc hội viên (mỗi người 1 subfolder)
│   ├── member_pics/            # Ảnh chụp từ camera khi đăng ký
│   ├── encodings/              # File pickle chứa embeddings đã mã hóa
│   │   └── face_encodings.pkl  # File encoding chính của hệ thống
│   └── embeddings/             # File embeddings dạng numpy (dự phòng)
│
├── assets/                     # Tài nguyên tĩnh cấu hình UI
│   ├── icons/                  # Biểu tượng, logo phần mềm
│   └── styles.json             # Cấu hình màu sắc, theme
│
├── utils/                      # Các tiện ích chung
│   ├── __init__.py
│   ├── image_processing.py     # Vẽ bbox, resize frame, convert BGR↔RGB
│   └── logger.py               # Logger ghi ra console + file log
│
├── logs/                       # Nơi lưu file log hệ thống
│   └── system.log              # File log chính
│
├── models/                     # Thư mục chứa model AI (nếu dùng model custom)
├── test/                       # Thư mục chứa các file Test
│
├── note.md                     # File tài liệu phân tích tổng quan
├── cau_truc_thu_muc.md         # File giải thích sơ đồ kiến trúc này
├── huong_dan_su_dung.md        # Hướng dẫn sử dụng 2 chức năng chính
├── .gitignore                  # Cấu hình bỏ qua file (chống rò rỉ dữ liệu)
└── venv/                       # Môi trường ảo Python (không push lên Git)
```