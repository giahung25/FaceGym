# Walkthrough — Hệ Thống Đăng Ký Khuôn Mặt

## Files đã tạo/sửa

| File | Mô tả |
|---|---|
| [face_register.py](file:///d:/tai_lieu_hk2_nam_2/python/Face_ID/core/ai/face_register.py) | **FaceRegistration** class — toàn bộ logic đăng ký |
| [register_face.py](file:///d:/tai_lieu_hk2_nam_2/python/Face_ID/register_face.py) | CLI entry point |
| [\_\_init\_\_.py](file:///d:/tai_lieu_hk2_nam_2/python/Face_ID/core/ai/__init__.py) | Thêm export [FaceRegistration](file:///d:/tai_lieu_hk2_nam_2/python/Face_ID/core/ai/face_register.py#33-471) |

## Tính năng chính

### Camera HUD khi đăng ký
- Hiển thị tên hội viên, số ảnh đã chụp, thanh tiến trình
- Trạng thái phát hiện khuôn mặt real-time (xanh = OK, đỏ = không thấy)
- Chế độ **MANUAL** (SPACE chụp) hoặc **AUTO** (bấm A, tự chụp 1.5s/lần)
- Flash effect khi chụp ảnh

### Quy trình đăng ký
```mermaid
graph LR
    A[Mở Camera] --> B[Chụp ảnh khuôn mặt]
    B --> C[Crop + Lưu vào dataset/]
    C --> D[Encode → embedding 128D]
    D --> E[Cập nhật file pickle]
```

## Cách sử dụng

### CLI
```powershell
# Đăng ký (nhập tên từ bàn phím)
python register_face.py

# Đăng ký với tên + số ảnh
python register_face.py --name "Nguyen Van A" --photos 10

# Xem danh sách hội viên
python register_face.py --list

# Xóa hội viên
python register_face.py --remove "Nguyen Van A"
```

### Python API
```python
from core.ai import FaceRegistration

reg = FaceRegistration()
result = reg.register_member("Nguyen Van A", num_photos=5)
# → {"success": True, "photos": 5, "encodings": 5}
```

## Kết quả kiểm thử
- ✅ Import [FaceRegistration](file:///d:/tai_lieu_hk2_nam_2/python/Face_ID/core/ai/face_register.py#33-471) — OK
- ✅ Instantiate — OK  
- ✅ CLI `--list` — OK (hiển thị "Chưa có hội viên nào")
- ⏳ Camera capture — cần test thủ công
