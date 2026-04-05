# ============================================================================
# FILE: app/repositories/member_repo.py
# MỤC ĐÍCH: Tầng REPOSITORY cho Member — chịu trách nhiệm ĐỌC/GHI dữ liệu
#            hội viên vào database SQLite.
#
# KIẾN TRÚC: GUI → Service → Repository → Database
#   - Repository CHỈ làm việc với database (SELECT, INSERT, UPDATE)
#   - KHÔNG chứa logic nghiệp vụ (validation, tính toán...) → đó là việc của Service
#
# CÁC HÀM CHÍNH (gọi là CRUD):
#   - Create: tạo mới    → create()
#   - Read:   đọc/tìm    → get_by_id(), get_all(), search()
#   - Update: cập nhật   → update()
#   - Delete: xóa (mềm) → delete()
# ============================================================================

from app.core.database import get_db    # Context manager để mở kết nối database
from app.models.member import Member    # Class Member (model)
from datetime import datetime


def _row_to_member(row) -> Member:
    """Chuyển đổi 1 dòng kết quả từ database (sqlite3.Row) thành đối tượng Member.

    Tại sao cần hàm này?
    - Database trả về dạng dict-like (row["name"], row["phone"]...)
    - Nhưng code Python cần dùng đối tượng Member (member.name, member.phone...)
    - Hàm này "dịch" từ dạng database → dạng Python object

    Tại sao dùng Member.__new__(Member) thay vì Member(...)?
    - Member(...) sẽ gọi __init__() → tạo ID MỚI + created_at MỚI
    - Nhưng ta muốn GIỮ NGUYÊN id, created_at từ database
    - __new__() chỉ tạo object rỗng, KHÔNG gọi __init__()
    - Sau đó ta tự gán từng thuộc tính từ database vào

    Tham số:
        row: 1 dòng kết quả từ database (sqlite3.Row)

    Trả về:
        Member: đối tượng Member với dữ liệu từ database
    """
    m = Member.__new__(Member)  # Tạo object Member rỗng (KHÔNG gọi __init__)

    # Gán từng thuộc tính từ database vào object
    m.id = row["id"]                    # ID (UUID dạng chuỗi)
    m.name = row["name"]                # Họ tên
    m.phone = row["phone"]              # Số điện thoại
    m.email = row["email"]              # Email (có thể None)
    m.gender = row["gender"]            # Giới tính
    m.date_of_birth = row["date_of_birth"]  # Ngày sinh
    m.address = row["address"]          # Địa chỉ
    m.emergency_contact = row["emergency_contact"]  # SĐT khẩn cấp
    m.photo = row["photo"]              # Đường dẫn ảnh
    m.pin = row["pin"]                  # PIN đăng nhập user app
    m.member_code = row["member_code"] if "member_code" in row.keys() else None
    m.face_registered = bool(row["face_registered"]) if "face_registered" in row.keys() else False
    m.photo_path = row["photo_path"] if "photo_path" in row.keys() else None

    # Chuyển chuỗi ISO → datetime object (VD: "2026-03-22T14:30:00" → datetime)
    m.created_at = datetime.fromisoformat(row["created_at"])
    m.updated_at = datetime.fromisoformat(row["updated_at"])

    # Database lưu is_active dạng INTEGER (0 hoặc 1)
    # bool() chuyển: 0 → False, 1 → True
    m.is_active = bool(row["is_active"])

    return m


def create(member: Member) -> Member:
    """Thêm hội viên MỚI vào database (INSERT).

    Tham số:
        member (Member): đối tượng Member đã được tạo (có id, name, phone...)

    Trả về:
        Member: chính đối tượng đã truyền vào (đã được lưu vào DB)

    SQL dùng dấu ? (placeholder) thay vì nối chuỗi trực tiếp:
    → Để TRÁNH SQL Injection (tấn công bảo mật qua input)
    VD: Nếu nối chuỗi: f"INSERT ... VALUES ('{name}')" → hacker có thể input: "'; DROP TABLE--"
        Dùng ?: INSERT ... VALUES (?) + (name,) → an toàn 100%
    """
    with get_db() as conn:  # Mở kết nối DB, tự động commit/rollback/close
        conn.execute(
            """INSERT INTO members (id, name, phone, email, gender, date_of_birth,
               address, emergency_contact, photo, pin, member_code, face_registered,
               photo_path, created_at, updated_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (member.id, member.name, member.phone, member.email, member.gender,
             member.date_of_birth, member.address, member.emergency_contact, member.photo,
             member.pin, member.member_code, int(member.face_registered),
             member.photo_path,
             member.created_at.isoformat(),
             member.updated_at.isoformat(),
             int(member.is_active))
        )
    return member


def get_by_id(id: str) -> Member | None:
    """Tìm hội viên theo ID (UUID).

    Tham số:
        id (str): UUID của hội viên cần tìm

    Trả về:
        Member: nếu tìm thấy
        None: nếu không tìm thấy

    LƯU Ý: (id,) phải có dấu PHẨY để Python hiểu đây là tuple, không phải nhóm ngoặc.
            (id) = chỉ là id bọc trong ngoặc
            (id,) = tuple chứa 1 phần tử
    """
    with get_db() as conn:
        # fetchone() = lấy 1 dòng kết quả đầu tiên (hoặc None nếu không có)
        row = conn.execute("SELECT * FROM members WHERE id = ?", (id,)).fetchone()
    # Nếu row tồn tại → chuyển thành Member, nếu None → trả None
    return _row_to_member(row) if row else None


def get_all(active_only: bool = True) -> list[Member]:
    """Lấy DANH SÁCH tất cả hội viên.

    Tham số:
        active_only (bool): True = chỉ lấy hội viên đang hoạt động (mặc định)
                            False = lấy cả hội viên đã bị xóa (soft delete)

    Trả về:
        list[Member]: danh sách các đối tượng Member, sắp xếp theo tên (A→Z)
    """
    with get_db() as conn:
        if active_only:
            # Chỉ lấy hội viên có is_active = 1 (đang hoạt động)
            rows = conn.execute("SELECT * FROM members WHERE is_active = 1 ORDER BY name").fetchall()
        else:
            # Lấy tất cả, kể cả đã xóa mềm
            rows = conn.execute("SELECT * FROM members ORDER BY name").fetchall()

    # List comprehension: chuyển từng row thành Member object
    # [f(x) for x in list] = áp dụng hàm f lên từng phần tử x
    return [_row_to_member(r) for r in rows]


def search(keyword: str) -> list[Member]:
    """Tìm kiếm hội viên theo từ khóa (tìm trong tên, SĐT, email).

    Tham số:
        keyword (str): từ khóa tìm kiếm (VD: "Nguyễn", "0901", "gmail")

    Trả về:
        list[Member]: danh sách hội viên khớp với từ khóa

    SQL LIKE với %keyword%:
    - % = đại diện cho BẤT KỲ ký tự nào (0 hoặc nhiều)
    - %Nguyễn% sẽ khớp: "Nguyễn Văn A", "Trần Nguyễn B", "nguyễn"
    - Tìm trong 3 cột: name, phone, email (dùng OR = khớp 1 trong 3 là được)
    """
    with get_db() as conn:
        like = f"%{keyword}%"  # Thêm % hai đầu để tìm kiếm "chứa" từ khóa
        rows = conn.execute(
            "SELECT * FROM members WHERE is_active = 1 AND (name LIKE ? OR phone LIKE ? OR email LIKE ?) ORDER BY name",
            (like, like, like)  # 3 dấu ? → truyền 3 lần cùng giá trị like
        ).fetchall()
    return [_row_to_member(r) for r in rows]


def update(member: Member) -> Member:
    """Cập nhật thông tin hội viên trong database (UPDATE).

    Tham số:
        member (Member): đối tượng Member ĐÃ ĐƯỢC SỬA các thuộc tính trước khi gọi hàm

    Flow:
        1. Caller sửa: member.name = "Tên mới"
        2. Gọi: member_repo.update(member)
        3. Hàm này gọi member.update() → cập nhật updated_at
        4. Ghi vào database

    Trả về:
        Member: đối tượng đã cập nhật
    """
    member.update()  # Gọi BaseModel.update() → cập nhật updated_at = datetime.now()
    with get_db() as conn:
        conn.execute(
            """UPDATE members SET name=?, phone=?, email=?, gender=?, date_of_birth=?,
               address=?, emergency_contact=?, photo=?, pin=?, member_code=?,
               face_registered=?, photo_path=?, updated_at=?, is_active=?
               WHERE id=?""",
            (member.name, member.phone, member.email, member.gender, member.date_of_birth,
             member.address, member.emergency_contact, member.photo, member.pin,
             member.member_code, int(member.face_registered), member.photo_path,
             member.updated_at.isoformat(), int(member.is_active), member.id)
        )
    return member


def get_by_phone(phone: str) -> Member | None:
    """Tìm hội viên theo số điện thoại (dùng cho đăng nhập user app).

    Tham số:
        phone (str): Số điện thoại cần tìm

    Trả về:
        Member nếu tìm thấy (active), None nếu không có
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM members WHERE phone = ? AND is_active = 1", (phone,)
        ).fetchone()
    return _row_to_member(row) if row else None


def delete(id: str):
    """Xóa mềm hội viên và cascade tới các bảng liên quan.

    Soft delete (is_active=0) thay vì hard delete để:
    - Tránh lỗi FK constraint (subscriptions, trainer_assignments, training_sessions tham chiếu members)
    - Giữ lại dữ liệu lịch sử cho báo cáo
    - C�� thể khôi phục nếu xóa nhầm

    Cascade: đồng thời vô hiệu hóa subscriptions, assignments, sessions, notifications
    của hội viên này.

    Tham số:
        id (str): UUID của hội viên cần xóa
    """
    now = datetime.now().isoformat()
    with get_db() as conn:
        # 1. Soft delete hội viên
        conn.execute(
            "UPDATE members SET is_active = 0, updated_at = ? WHERE id = ?",
            (now, id)
        )
        # 2. Cascade: vô hiệu hóa subscriptions
        conn.execute(
            "UPDATE subscriptions SET is_active = 0, status = 'cancelled', updated_at = ? WHERE member_id = ? AND is_active = 1",
            (now, id)
        )
        # 3. Cascade: kết thúc trainer_assignments
        conn.execute(
            "UPDATE trainer_assignments SET is_active = 0, status = 'ended', end_date = ?, updated_at = ? WHERE member_id = ? AND status = 'active'",
            (now, now, id)
        )
        # 4. Cascade: vô hiệu hóa training_sessions chưa hoàn thành
        conn.execute(
            "UPDATE training_sessions SET is_active = 0, status = 'cancelled', updated_at = ? WHERE member_id = ? AND status = 'scheduled'",
            (now, id)
        )
        # 5. Xóa thông báo (hard delete vì notifications không có is_active)
        conn.execute(
            "DELETE FROM notifications WHERE user_id = ? AND user_type = 'member'",
            (id,)
        )
