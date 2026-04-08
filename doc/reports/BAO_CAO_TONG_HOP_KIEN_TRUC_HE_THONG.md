# 📘 BÁO CÁO PHÂN TÍCH KIẾN TRÚC HỆ THỐNG GYMFIT (FACE ID)
*Dành cho sinh viên IT nghiên cứu về kiến trúc phần mềm và AI*

---

## 1. TỔNG QUAN HỆ THỐNG
Hệ thống **GymFit** là một giải pháp quản lý phòng gym toàn diện, kết hợp giữa quản lý nghiệp vụ truyền thống và công nghệ nhận diện khuôn mặt để tự động hóa quy trình điểm danh.

### 🎯 Mục tiêu kỹ thuật:
- Triển khai kiến trúc **Layered Architecture** (Phân tầng) để tách biệt UI và Logic.
- Áp dụng **Service-Repository Pattern** để quản lý dữ liệu hiệu quả.
- Tích hợp **Deep Learning** (Face Embeddings) vào ứng dụng Desktop thực tế.

---

## 2. KIẾN TRÚC PHẦN MỀM (ARCHITECTURE)

Hệ thống được chia thành 4 tầng chính, mỗi tầng chỉ giao tiếp với tầng trực tiếp bên dưới nó:

### 🧱 2.1. Tầng Giao diện (GUI Layer - Flet)
- **Công nghệ:** Sử dụng **Flet** (Flutter for Python).
- **Cơ chế:** Hoạt động dựa trên các `View` (màn hình) độc lập.
- **Navigation:** Sử dụng kỹ thuật *Monkey-patching* để gắn hàm `navigate` vào đối tượng `page`, cho phép chuyển trang linh hoạt mà không bị dính lỗi tham chiếu vòng.

### 🧠 2.2. Tầng Nghiệp vụ (Service Layer)
- **Vị trí:** `app/services/`
- **Chức năng:** Chứa toàn bộ "Logic nghiệp vụ". Đây là nơi thực hiện các ràng buộc (Validation), tính toán doanh thu, kiểm tra hạn gói tập.
- **Tại sao cần nó?** Để GUI không phải lo về logic. Nếu sau này bạn đổi từ Flet sang Web, bạn chỉ cần giữ nguyên tầng Service.

### 🗄️ 2.3. Tầng Truy xuất dữ liệu (Repository Layer)
- **Vị trí:** `app/repositories/`
- **Chức năng:** Thực hiện các câu lệnh SQL thuần túy (INSERT, SELECT, UPDATE).
- **Mẫu thiết kế:** Sử dụng **Hydration Pattern** (Hàm `_row_to_model` chuyển đổi kết quả từ SQL thành đối tượng Python để dễ xử lý).

### 📐 2.4. Tầng Dữ liệu (Model Layer)
- **Vị trí:** `app/models/`
- **Chức năng:** Định nghĩa cấu trúc dữ liệu dưới dạng Class. Các Class này kế thừa từ `BaseModel` để tự động có các thuộc tính như `id` (UUID), `created_at`, `updated_at`.

---

## 3. CƠ CHẾ NHẬN DIỆN KHUÔN MẶT (FACE ID CORE)

Hệ thống Face ID trong dự án này không chỉ đơn thuần là so sánh ảnh, mà là so sánh các **Vector toán học**.

### 🧬 Quy trình 3 bước:
1.  **Face Detection (Phát hiện):** Sử dụng OpenCV để tìm tọa độ khuôn mặt trong khung hình.
2.  **Face Encoding (Mã hóa):** Chuyển khuôn mặt thành một vector 128 chiều (Face Embeddings) thông qua mô hình Deep Learning. (File: `app/face_id/face_encoder.py`)
3.  **Face Matching (Đối chiếu):** Sử dụng khoảng cách **Euclidean**. Nếu khoảng cách giữa vector mới và vector trong DB < 0.6 (Tolerance), đó là cùng một người.

### 📁 Lưu trữ dữ liệu AI:
- `data/dataset/`: Lưu ảnh gốc để đối chiếu khi cần.
- `data/encodings/face_encodings.pkl`: Lưu trữ các vector đã tính toán xong dưới dạng nhị phân để nhận diện siêu nhanh (Real-time).

---

## 4. PHÂN TÍCH CÁC HÀM & LỚP QUAN TRỌNG

### 🛠️ Lớp `BaseModel` (`app/models/base.py`)
Đây là lớp cha của mọi dữ liệu. Nó giải quyết vấn đề:
- Tự tạo **UUID4** thay vì ID số tự tăng (giúp tránh xung đột dữ liệu khi gộp DB).
- Hỗ trợ **Soft Delete** (`is_active`): Khi xóa một hội viên, ta không xóa hẳn khỏi DB mà chỉ đánh dấu ẩn đi để giữ lại lịch sử điểm danh.

### 🛡️ Lớp `Database` (`app/core/database.py`)
Sử dụng **Context Manager** (`with get_db() as conn:`):
- Đảm bảo kết nối luôn được đóng dù code có bị lỗi.
- Tránh lỗi phổ biến nhất trong SQLite: `Database is locked`.

### ⚡ Service Điểm danh (`app/services/attendance_svc.py`)
Hàm quan trọng nhất: `check_in_by_face(face_id)`.
Luồng xử lý:
1. Nhận ID từ module nhận diện.
2. Gọi `MemberRepository` lấy thông tin hội viên.
3. Kiểm tra gói tập còn hạn không qua `MembershipService`.
4. Nếu OK, gọi `AttendanceRepository` để ghi log vào DB.

---

## 5. LUỒNG DỮ LIỆU THỰC TẾ (DATA FLOW)

**Khi một hội viên mới đăng ký:**
1. **GUI:** User nhập tên, SĐT -> Nhấn nút "Chụp ảnh".
2. **Face ID:** Camera mở -> Chụp -> `face_register.py` lưu ảnh -> `face_encoder.py` tạo vector.
3. **Service:** `member_svc.py` nhận thông tin + vector -> Kiểm tra tính hợp lệ.
4. **Repo:** `member_repo.py` lưu thông tin vào bảng `members`.
5. **DB:** Dữ liệu nằm an toàn trong `gym_db.db`.

---

## 6. LỜI KHUYÊN CHO SINH VIÊN NGHIÊN CỨU
Để làm chủ hệ thống này, bạn nên thực hiện các bài tập nhỏ sau:
1. **Trace Code:** Thử đặt một lệnh `print()` trong tầng Repository và xem nó được gọi từ Service nào.
2. **Mở rộng Model:** Thử thêm trường `Email` vào `Member` và cập nhật từ Model đến GUI.
3. **Tối ưu AI:** Thử thay đổi thông số `TOLERANCE` trong `config` để xem độ nhạy của Face ID thay đổi như thế nào.

---
*Báo cáo được tổng hợp tự động bởi Gemini CLI - Hệ thống hỗ trợ lập trình thông minh.*
