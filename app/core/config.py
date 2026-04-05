# ============================================================================
# FILE: app/core/config.py
# MỤC ĐÍCH: Lưu trữ các HẰNG SỐ CẤU HÌNH cho toàn bộ ứng dụng.
#            Các file khác sẽ import từ đây để dùng, giúp quản lý tập trung.
# ============================================================================

import os  # Thư viện chuẩn của Python — dùng để làm việc với file/thư mục/biến môi trường

# ── Đường dẫn thư mục gốc của dự án ──────────────────────────────────────────
# __file__         = đường dẫn tới file config.py (VD: E:/gym_management/app/core/config.py)
# abspath(__file__) = đường dẫn tuyệt đối (đầy đủ) của file này
# dirname()        = lấy thư mục cha. Gọi 3 lần để đi từ config.py → core/ → app/ → gym_management/
#   Lần 1: E:/gym_management/app/core/
#   Lần 2: E:/gym_management/app/
#   Lần 3: E:/gym_management/          ← đây là thư mục gốc dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Đường dẫn tới file database SQLite ────────────────────────────────────────
# os.path.join() nối các phần đường dẫn lại: BASE_DIR + "data" + "gym_db.db"
# Kết quả VD: E:/gym_management/data/gym_db.db
DB_PATH = os.path.join(BASE_DIR, "data", "gym_db.db")

# ── Tiêu đề và kích thước cửa sổ ứng dụng ────────────────────────────────────
APP_TITLE = "Hệ thống quản lý GymAdmin"  # Tên hiển thị trên thanh tiêu đề cửa sổ
WINDOW_WIDTH = 1280   # Chiều rộng cửa sổ tính bằng pixel
WINDOW_HEIGHT = 800   # Chiều cao cửa sổ tính bằng pixel

# ── Thông tin đăng nhập mặc định ──────────────────────────────────────────────
# os.environ.get("TÊN_BIẾN", "giá_trị_mặc_định"):
#   - Nếu biến môi trường "GYM_USERNAME" tồn tại → dùng giá trị đó
#   - Nếu KHÔNG tồn tại → dùng giá trị mặc định "admin"
# Cách này cho phép thay đổi username/password mà KHÔNG cần sửa code
ADMIN_USERNAME = os.environ.get("GYM_USERNAME", "admin")       # Mặc định: "admin"
ADMIN_PASSWORD = os.environ.get("GYM_PASSWORD", "admin123")    # Mặc định: "admin123"

# ── Cấu hình Camera ─────────────────────────────────────────────────────────
CAMERA_ID = 0              # ID camera (0 = webcam mặc định)
FRAME_WIDTH = 640          # Chiều rộng frame camera (pixel)
FRAME_HEIGHT = 480         # Chiều cao frame camera (pixel)
FPS_DISPLAY = True         # Hiển thị FPS trên màn hình camera

# ── Cấu hình nhận diện khuôn mặt ────────────────────────────────────────────
FACE_TOLERANCE = 0.5       # Ngưỡng nhận diện (càng nhỏ càng nghiêm ngặt, 0.0 - 1.0)
FACE_MODEL_TYPE = "hog"    # "hog" (CPU nhanh) hoặc "cnn" (GPU chính xác hơn)
FRAME_RESIZE_SCALE = 0.5   # Thu nhỏ frame để xử lý nhanh hơn (0.5 = 50%)
CHECKIN_COOLDOWN = 30      # Thời gian chờ giữa 2 lần check-in (giây)

# ── Đường dẫn dữ liệu Face ID ───────────────────────────────────────────────
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_PATH = os.path.join(DATA_DIR, "dataset")             # Ảnh gốc hội viên (mỗi người 1 folder)
MEMBER_PICS_PATH = os.path.join(DATA_DIR, "member_pics")     # Ảnh chụp từ camera khi đăng ký
ENCODINGS_PATH = os.path.join(DATA_DIR, "encodings")         # Thư mục chứa file pickle encodings
ENCODINGS_FILE = os.path.join(ENCODINGS_PATH, "face_encodings.pkl")  # File encoding chính
EMBEDDINGS_PATH = os.path.join(DATA_DIR, "embeddings")       # File embeddings dạng numpy

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "system.log")
LOG_LEVEL = "INFO"

# ── Tự động tạo các thư mục cần thiết nếu chưa tồn tại ─────────────────────
# exist_ok=True: nếu thư mục đã có rồi thì bỏ qua, không báo lỗi
for _dir in [DATA_DIR, DATASET_PATH, MEMBER_PICS_PATH, ENCODINGS_PATH, EMBEDDINGS_PATH, LOG_DIR]:
    os.makedirs(_dir, exist_ok=True)
