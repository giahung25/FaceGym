# Hướng Dẫn Sử Dụng Hệ Thống Nhận Diện Khuôn Mặt

> ⚠️ **QUAN TRỌNG**: Luôn chạy lệnh từ thư mục gốc `Face_ID/`, KHÔNG chạy từ bên trong `core/ai/`.
> ```powershell
> cd d:\tai_lieu_hk2_nam_2\python\Face_ID
> .\venv\Scripts\activate
> ```

---

## 📌 Chức năng 1: ĐĂNG KÝ KHUÔN MẶT (Face Registration)

### Mục đích
Chụp ảnh khuôn mặt hội viên qua camera → mã hóa thành dữ liệu số → lưu vào hệ thống để sau này nhận diện được.

### Các bước hoạt động

```
Bước 1                Bước 2              Bước 3               Bước 4
┌─────────┐     ┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│ Mở      │     │ Chụp ảnh     │    │ Encode ảnh    │    │ Lưu vào file │
│ Camera  │ ──► │ khuôn mặt    │──► │ → vector 128D │──► │ pickle       │
│         │     │ (crop mặt)   │    │               │    │              │
└─────────┘     └──────────────┘    └───────────────┘    └──────────────┘
```

**Bước 1 — Mở Camera:**
- Hệ thống mở webcam (camera ID = 0).
- Hiển thị giao diện HUD gồm: tên hội viên, số ảnh đã chụp, thanh tiến trình.

**Bước 2 — Chụp ảnh khuôn mặt:**
- Phát hiện khuôn mặt trong frame bằng thư viện `face_recognition`.
- Vẽ khung xanh quanh khuôn mặt khi phát hiện được.
- Người dùng chụp bằng 2 cách:
  - **Thủ công**: Bấm `SPACE` để chụp.
  - **Tự động**: Bấm `A` để bật — hệ thống tự chụp mỗi 1.5 giây.
- Ảnh được **crop** (cắt) vùng khuôn mặt + thêm viền padding 30%.
- Ảnh lưu vào: `data/dataset/{TenHoiVien}/`

**Bước 3 — Encode (Mã hóa):**
- Mỗi ảnh khuôn mặt được chuyển thành 1 mảng gồm **128 con số** (gọi là "embedding").
- Mảng 128 số này là "dấu vân tay kỹ thuật số" của khuôn mặt — mỗi người có mảng số khác nhau.
- Thư viện `face_recognition` (sử dụng mô hình deep learning `dlib`) thực hiện việc này.

**Bước 4 — Lưu trữ:**
- Tất cả embeddings được lưu vào file: `data/encodings/face_encodings.pkl`
- Cấu trúc dữ liệu: `{"names": ["A", "A", "B", ...], "encodings": [array_128D, ...]}`
- Nếu file đã tồn tại → dữ liệu mới được **thêm vào** (không ghi đè).

### Cách chạy

```powershell
# Từ thư mục gốc Face_ID/
python register_face.py --name "Nguyen Van A" --photos 5
```

| Phím | Chức năng |
|------|-----------|
| `SPACE` | Chụp 1 ảnh |
| `A` | Bật/tắt Auto-capture |
| `Q` | Hoàn tất và thoát |

### Các lệnh khác

```powershell
# Xem danh sách hội viên đã đăng ký
python register_face.py --list

# Xóa hội viên
python register_face.py --remove "Nguyen Van A"
```

---

## 📌 Chức năng 2: NHẬN DIỆN KHUÔN MẶT (Face Recognition)

### Mục đích
Mở camera → phát hiện khuôn mặt → so sánh với dữ liệu đã đăng ký → hiển thị tên + độ tin cậy.

### Các bước hoạt động

```
Bước 1            Bước 2              Bước 3              Bước 4             Bước 5
┌────────┐   ┌────────────┐    ┌──────────────┐    ┌─────────────┐    ┌────────────┐
│ Load   │   │ Đọc frame  │    │ Detect +     │    │ So sánh     │    │ Vẽ khung + │
│ pickle │──►│ từ camera  │───►│ Encode       │───►│ khoảng cách │───►│ hiển thị   │
│ file   │   │            │    │ khuôn mặt    │    │ Euclidean   │    │ tên/Unknown│
└────────┘   └────────────┘    └──────────────┘    └─────────────┘    └────────────┘
                   ▲                                                        │
                   └────────────────── Lặp lại ◄────────────────────────────┘
```

**Bước 1 — Load dữ liệu đã đăng ký:**
- Đọc file `data/encodings/face_encodings.pkl`.
- Lấy ra danh sách tên (`names`) và danh sách embeddings (`encodings`) đã lưu trước đó.

**Bước 2 — Đọc frame từ camera:**
- Mở webcam, đọc từng frame liên tục.
- Frame được **thu nhỏ 50%** trước khi xử lý (để tăng tốc).
- Chuyển đổi BGR (OpenCV) → RGB (face_recognition).

**Bước 3 — Detect + Encode:**
- Phát hiện vị trí khuôn mặt trong frame (tọa độ top, right, bottom, left).
- Trích xuất embedding 128D cho mỗi khuôn mặt phát hiện được.
- Chỉ xử lý nhận diện mỗi **2 frame** (tối ưu hiệu năng).

**Bước 4 — So sánh (Matching):**
- Tính **khoảng cách Euclidean** giữa embedding vừa trích xuất với TẤT CẢ embeddings đã đăng ký.
- Tìm khoảng cách NHỎ NHẤT (best match).
- Nếu khoảng cách ≤ **ngưỡng tolerance (0.5)**:
  - → Nhận diện thành công! Trả về tên hội viên.
  - → Độ tin cậy (confidence) = `1.0 - khoảng cách` (ví dụ: distance 0.3 → confidence 70%).
- Nếu khoảng cách > tolerance:
  - → Đánh dấu "Unknown" (người lạ).

**Bước 5 — Hiển thị:**
- Vẽ khung bao (bounding box) quanh khuôn mặt:
  - 🟢 **Xanh** nếu nhận ra + hiển thị tên và % tin cậy.
  - 🔴 **Đỏ** nếu "Unknown".
- Hiển thị FPS (số frame/giây) ở góc trên.
- Bấm `Q` để thoát.

### Cách chạy

```python
# Tạo file run_recognition.py tại thư mục gốc Face_ID/
from core.ai import FaceRecognitionSystem

system = FaceRecognitionSystem()
system.run_camera_loop()  # Bấm Q để thoát
```

---

## 📂 Sơ đồ file liên quan

```
Face_ID/
├── register_face.py          ← Chạy file này để ĐĂNG KÝ
├── config/
│   └── settings.py           ← Cấu hình: tolerance, camera, đường dẫn
├── core/
│   └── ai/
│       ├── face_encoder.py   ← Encode ảnh → embedding 128D
│       ├── face_recognizer.py← Nhận diện real-time từ camera
│       ├── face_register.py  ← Logic đăng ký khuôn mặt
│       └── __init__.py       ← Export API
├── utils/
│   ├── image_processing.py   ← Vẽ bbox, resize, convert màu
│   └── logger.py             ← Ghi log hệ thống
└── data/
    ├── dataset/              ← Ảnh gốc hội viên (mỗi người 1 folder)
    └── encodings/            ← File pickle chứa embeddings
        └── face_encodings.pkl
```

---

## ❓ Giải thích thuật ngữ

| Thuật ngữ | Giải thích |
|---|---|
| **Embedding (128D)** | Mảng 128 con số đại diện cho 1 khuôn mặt. Giống "mã vạch" của mặt — mỗi người có mã khác nhau. |
| **Euclidean Distance** | Cách đo "khoảng cách" giữa 2 embedding. Khoảng cách càng NHỎ → 2 khuôn mặt càng GIỐNG nhau. |
| **Tolerance (ngưỡng)** | Giá trị 0.5 — nếu khoảng cách ≤ 0.5 thì coi là khớp. Giảm xuống 0.4 sẽ nghiêm ngặt hơn. |
| **HOG** | Mô hình phát hiện khuôn mặt chạy trên CPU, nhanh nhưng kém chính xác hơn CNN. |
| **CNN** | Mô hình phát hiện khuôn mặt chạy trên GPU, chính xác hơn nhưng chậm hơn HOG. |
| **Pickle (.pkl)** | Định dạng file Python để lưu dữ liệu (dict, list, array) ra ổ cứng. |
