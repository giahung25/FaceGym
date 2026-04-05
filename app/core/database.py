# ============================================================================
# FILE: app/core/database.py
# MỤC ĐÍCH: Quản lý kết nối và khởi tạo database SQLite.
#            Cung cấp 2 thứ chính:
#              1. get_db()  — context manager để mở/đóng kết nối an toàn
#              2. init_db() — tạo các bảng (tables) nếu chưa tồn tại
# ============================================================================

import sqlite3                          # Thư viện SQLite có sẵn trong Python — database dạng file
from contextlib import contextmanager   # Decorator để tạo context manager (dùng với `with`)
from app.core.config import DB_PATH     # Đường dẫn tới file database (VD: data/gym_db.db)


@contextmanager  # ← Decorator biến hàm thành context manager (có thể dùng `with get_db() as conn:`)
def get_db():
    """Mở kết nối tới database và tự động đóng khi xong.

    Cách dùng:
        with get_db() as conn:
            conn.execute("SELECT * FROM members")
            # ... làm gì đó với database ...
        # ← Khi thoát khỏi `with`, kết nối tự động đóng

    Flow hoạt động:
        1. Mở kết nối tới file SQLite
        2. Bật foreign keys (ràng buộc khóa ngoại)
        3. `yield conn` — trả kết nối cho caller dùng
        4. Nếu KHÔNG có lỗi → commit (lưu thay đổi vào DB)
        5. Nếu CÓ lỗi → rollback (hủy thay đổi, quay về trạng thái trước)
        6. Cuối cùng (finally) → luôn đóng kết nối dù có lỗi hay không
    """
    # Bước 1: Mở kết nối tới file database
    conn = sqlite3.connect(DB_PATH)

    # Bước 2: Thiết lập row_factory = sqlite3.Row
    # → Khi query, kết quả trả về dạng dict-like (truy cập bằng tên cột)
    # VD: row["name"] thay vì row[1]
    conn.row_factory = sqlite3.Row

    # Bước 3: Bật ràng buộc khóa ngoại (foreign key)
    # SQLite mặc định TẮT foreign keys! Phải bật thủ công.
    # Khi bật: nếu insert subscription với member_id không tồn tại → sẽ báo lỗi
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn      # ← Trả kết nối cho caller (phần code trong `with`)
        conn.commit()   # ← Nếu không có lỗi → lưu thay đổi vào database
    except Exception:
        conn.rollback()  # ← Nếu có lỗi → hủy tất cả thay đổi chưa commit
        raise            # ← Ném lại lỗi để caller biết (không "nuốt" lỗi)
    finally:
        conn.close()     # ← LUÔN đóng kết nối, dù có lỗi hay không (tránh rò rỉ tài nguyên)


def init_db():
    """Tạo tất cả các bảng (tables) trong database nếu chưa tồn tại.

    Hàm này được gọi MỘT LẦN khi app khởi động (trong main.py).
    "CREATE TABLE IF NOT EXISTS" nghĩa là: chỉ tạo nếu bảng chưa có,
    nếu đã có rồi thì bỏ qua (không ghi đè dữ liệu cũ).

    LƯU Ý: Không dùng get_db() context manager ở đây vì executescript()
    tự commit ngầm — không tương thích với cơ chế commit/rollback của get_db().
    """
    # Mở kết nối trực tiếp (không qua get_db)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # Bật foreign key

    try:
        # ── BẢNG 1: members (Hội viên) ───────────────────────────────────────
        # Lưu thông tin cá nhân của từng hội viên phòng gym
        conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id TEXT PRIMARY KEY,           -- UUID duy nhất cho mỗi hội viên (VD: "a1b2c3...")
                name TEXT NOT NULL,            -- Họ tên (bắt buộc, NOT NULL = không được để trống)
                phone TEXT NOT NULL UNIQUE,    -- Số điện thoại (bắt buộc, duy nhất — dùng đăng nhập)
                email TEXT,                    -- Email (tùy chọn, có thể NULL)
                gender TEXT,                   -- Giới tính: 'male', 'female', 'other'
                date_of_birth TEXT,            -- Ngày sinh dạng text (VD: "2000-01-15")
                address TEXT,                  -- Địa chỉ
                emergency_contact TEXT,        -- Số liên hệ khẩn cấp
                photo TEXT,                    -- Đường dẫn ảnh đại diện
                pin TEXT NOT NULL DEFAULT '000000' CHECK(LENGTH(pin) = 6),  -- PIN đúng 6 ký tự
                created_at TEXT NOT NULL,      -- Thời điểm tạo (ISO format: "2026-03-22T10:30:00")
                updated_at TEXT NOT NULL,      -- Thời điểm cập nhật gần nhất
                is_active INTEGER NOT NULL DEFAULT 1  -- 1 = đang hoạt động, 0 = đã xóa (soft delete)
            )
        """)

        # ── BẢNG 2: membership_plans (Gói tập) ───────────────────────────────
        # Định nghĩa các loại gói tập mà gym cung cấp (VD: Gói 1 tháng, 6 tháng, 1 năm)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS membership_plans (
                id TEXT PRIMARY KEY,           -- UUID duy nhất
                name TEXT NOT NULL,            -- Tên gói (VD: "Gói 1 tháng")
                duration_days INTEGER NOT NULL, -- Thời hạn tính bằng ngày (VD: 30, 180, 365)
                price REAL NOT NULL,           -- Giá gói (REAL = số thập phân, VD: 500000.0)
                description TEXT,              -- Mô tả chi tiết
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)

        # ── BẢNG 3: subscriptions (Đăng ký gói tập) ──────────────────────────
        # Lưu việc hội viên X đăng ký gói tập Y vào ngày nào, hết hạn khi nào
        # Đây là bảng LIÊN KẾT giữa members và membership_plans (quan hệ nhiều-nhiều)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,        -- ID hội viên (khóa ngoại → members.id)
                plan_id TEXT NOT NULL,           -- ID gói tập (khóa ngoại → membership_plans.id)
                price_paid REAL NOT NULL,        -- Số tiền thực tế đã thanh toán
                start_date TEXT NOT NULL,        -- Ngày bắt đầu gói tập
                end_date TEXT NOT NULL,          -- Ngày hết hạn gói tập
                status TEXT NOT NULL DEFAULT 'active',  -- Trạng thái: 'active', 'expired', 'cancelled'
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (member_id) REFERENCES members(id),          -- Ràng buộc: member_id phải tồn tại trong bảng members
                FOREIGN KEY (plan_id) REFERENCES membership_plans(id)    -- Ràng buộc: plan_id phải tồn tại trong bảng membership_plans
            )
        """)

        # ── BẢNG 4: equipment (Thiết bị) ─────────────────────────────────────
        # Quản lý máy móc, thiết bị trong phòng gym
        conn.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,             -- Tên thiết bị (VD: "Máy chạy bộ")
                category TEXT NOT NULL,         -- Phân loại (VD: "Cardio", "Tạ tự do")
                quantity INTEGER NOT NULL DEFAULT 1,  -- Số lượng
                status TEXT NOT NULL DEFAULT 'working',  -- 'working' | 'broken' | 'maintenance'
                purchase_date TEXT,             -- Ngày mua
                location TEXT,                  -- Vị trí (VD: "Tầng 1", "Khu Cardio")
                notes TEXT,                     -- Ghi chú bảo trì
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)

        # ── BẢNG 5: trainers (Huấn luyện viên) ──────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trainers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,            -- Họ tên HLV
                phone TEXT NOT NULL UNIQUE,    -- SĐT (dùng để đăng nhập user app, duy nhất)
                email TEXT,
                specialization TEXT,           -- Chuyên môn (VD: "Yoga", "Gym", "Boxing")
                pin TEXT NOT NULL DEFAULT '000000' CHECK(LENGTH(pin) = 6),  -- PIN đúng 6 ký tự
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)

        # ── BẢNG 6: notifications (Thông báo) ────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,         -- ID hội viên hoặc HLV nhận thông báo
                user_type TEXT NOT NULL,       -- 'member' hoặc 'trainer'
                title TEXT NOT NULL,           -- Tiêu đề thông báo
                message TEXT NOT NULL,         -- Nội dung chi tiết
                is_read INTEGER NOT NULL DEFAULT 0,  -- 0 = chưa đọc, 1 = đã đọc
                created_at TEXT NOT NULL
            )
        """)

        # ── BẢNG 7: trainer_assignments (Liên kết HLV ↔ Hội viên) ───────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trainer_assignments (
                id              TEXT PRIMARY KEY,
                member_id       TEXT NOT NULL,
                trainer_id      TEXT NOT NULL,
                subscription_id TEXT,
                start_date      TEXT NOT NULL,
                end_date        TEXT,
                status          TEXT NOT NULL DEFAULT 'active',
                notes           TEXT,
                created_at      TEXT NOT NULL,
                updated_at      TEXT NOT NULL,
                is_active       INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (member_id) REFERENCES members(id),
                FOREIGN KEY (trainer_id) REFERENCES trainers(id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
            )
        """)

        # ── BẢNG 8: training_sessions (Buổi tập HLV-Học viên) ────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                id              TEXT PRIMARY KEY,
                trainer_id      TEXT NOT NULL,
                member_id       TEXT NOT NULL,
                assignment_id   TEXT,
                session_date    TEXT NOT NULL,
                start_time      TEXT NOT NULL,
                end_time        TEXT,
                content         TEXT,
                status          TEXT NOT NULL DEFAULT 'scheduled',
                notes           TEXT,
                created_at      TEXT NOT NULL,
                updated_at      TEXT NOT NULL,
                is_active       INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (trainer_id) REFERENCES trainers(id),
                FOREIGN KEY (member_id) REFERENCES members(id),
                FOREIGN KEY (assignment_id) REFERENCES trainer_assignments(id)
            )
        """)

        # ── BẢNG 9: attendance (Điểm danh) ─────────────────────────────────
        # Lưu lịch sử check-in/check-out bằng Face ID hoặc thủ công
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,            -- ID hội viên (khóa ngoại → members.id)
                check_in TEXT NOT NULL,             -- Thời gian check-in (ISO format)
                check_out TEXT,                     -- Thời gian check-out (NULL nếu chưa checkout)
                method TEXT NOT NULL DEFAULT 'face_id',  -- 'face_id', 'manual', 'qr_code'
                confidence REAL,                    -- Độ tin cậy nhận diện (0.0 → 1.0, NULL nếu manual)
                created_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)

        # ── BẢNG 10: transactions (Giao dịch thanh toán) ────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,
                subscription_id TEXT,               -- Liên kết với subscription (tùy chọn)
                amount REAL NOT NULL,               -- Số tiền (VND)
                payment_method TEXT NOT NULL DEFAULT 'cash',  -- 'cash', 'transfer', 'card'
                note TEXT,
                created_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (member_id) REFERENCES members(id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
            )
        """)

        # ── INDEXES (Chỉ mục) ────────────────────────────────────────────────
        # Index giúp database TÌM KIẾM NHANH HƠN trên các cột hay query.
        # Giống như mục lục sách — thay vì đọc từng trang, tra mục lục sẽ nhanh hơn.
        # Trade-off: tốn thêm dung lượng lưu trữ, nhưng query nhanh hơn rất nhiều.
        conn.execute("CREATE INDEX IF NOT EXISTS idx_members_phone ON members(phone)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_members_is_active ON members(is_active)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subs_member_id ON subscriptions(member_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subs_plan_id ON subscriptions(plan_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subs_status ON subscriptions(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trainers_phone ON trainers(phone)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, user_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ta_member ON trainer_assignments(member_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ta_trainer ON trainer_assignments(trainer_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ta_status ON trainer_assignments(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ts_trainer ON training_sessions(trainer_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ts_date ON training_sessions(session_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_member ON attendance(member_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_checkin ON attendance(check_in)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_method ON attendance(method)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_member ON transactions(member_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_created ON transactions(created_at)")

        # ── MIGRATION: thêm cột pin vào bảng members nếu chưa có ─────────────
        # Dành cho DB cũ đã tồn tại trước khi có cột pin.
        # Nếu cột đã tồn tại → SQLite báo lỗi "duplicate column name" → bỏ qua (pass).
        try:
            conn.execute("ALTER TABLE members ADD COLUMN pin TEXT NOT NULL DEFAULT '000000'")
        except Exception:
            pass  # Cột đã tồn tại — bỏ qua

        # ── MIGRATION: thêm cột trainer_id vào bảng subscriptions ────────────
        try:
            conn.execute("ALTER TABLE subscriptions ADD COLUMN trainer_id TEXT REFERENCES trainers(id)")
        except Exception:
            pass  # Cột đã tồn tại — bỏ qua

        # ── MIGRATION: thêm UNIQUE index cho phone (DB cũ chưa có UNIQUE) ───
        # CREATE TABLE mới đã có UNIQUE, nhưng DB cũ cần thêm index.
        # Nếu DB cũ có phone trùng → index sẽ lỗi, cần xử lý trước.
        try:
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_members_phone_unique ON members(phone)")
        except Exception:
            pass  # Có phone trùng trong DB cũ — bỏ qua, xử lý ở application layer
        try:
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_trainers_phone_unique ON trainers(phone)")
        except Exception:
            pass  # Tương tự

        # ── MIGRATION: thêm cột Face ID vào bảng members ────────────────
        try:
            conn.execute("ALTER TABLE members ADD COLUMN member_code TEXT")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE members ADD COLUMN face_registered INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE members ADD COLUMN photo_path TEXT")
        except Exception:
            pass

        conn.commit()  # Lưu tất cả thay đổi vào database
    except Exception:
        conn.rollback()  # Có lỗi → hủy tất cả
        raise
    finally:
        conn.close()     # Luôn đóng kết nối
