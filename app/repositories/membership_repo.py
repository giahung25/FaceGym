# ============================================================================
# FILE: app/repositories/membership_repo.py
# MỤC ĐÍCH: Tầng REPOSITORY cho MembershipPlan và MembershipSubscription.
#            Đọc/ghi dữ liệu gói tập và đăng ký gói tập vào database.
#
# FILE NÀY QUẢN LÝ 2 BẢNG:
#   1. membership_plans   — danh sách gói tập (CRUD)
#   2. subscriptions      — đăng ký gói tập (CRUD + query đặc biệt)
# ============================================================================

from app.core.database import get_db
from app.models.membership import MembershipPlan, MembershipSubscription
from datetime import datetime, timedelta


# ══════════════════════════════════════════════════════════════════════════════
# HÀM CHUYỂN ĐỔI: database row → Python object
# ══════════════════════════════════════════════════════════════════════════════

def _row_to_plan(row) -> MembershipPlan:
    """Chuyển 1 dòng database thành đối tượng MembershipPlan.

    Dùng __new__() thay vì __init__() để KHÔNG tạo id mới
    (giữ nguyên id từ database).
    """
    p = MembershipPlan.__new__(MembershipPlan)  # Tạo object rỗng
    p.id = row["id"]
    p.name = row["name"]                        # Tên gói (VD: "Gói 1 tháng")
    p.duration_days = row["duration_days"]      # Số ngày
    p.price = row["price"]                      # Giá (VND)
    p.description = row["description"]          # Mô tả
    p.created_at = datetime.fromisoformat(row["created_at"])  # Chuỗi ISO → datetime
    p.updated_at = datetime.fromisoformat(row["updated_at"])
    p.is_active = bool(row["is_active"])         # 0/1 → False/True
    return p


def _row_to_sub(row) -> MembershipSubscription:
    """Chuyển 1 dòng database thành đối tượng MembershipSubscription.

    Tương tự _row_to_plan nhưng cho bảng subscriptions.
    """
    s = MembershipSubscription.__new__(MembershipSubscription)
    s.id = row["id"]
    s.member_id = row["member_id"]       # ID hội viên
    s.plan_id = row["plan_id"]           # ID gói tập
    s.price_paid = row["price_paid"]     # Giá đã thanh toán
    s.start_date = datetime.fromisoformat(row["start_date"])  # Ngày bắt đầu
    s.end_date = datetime.fromisoformat(row["end_date"])      # Ngày hết hạn
    s.trainer_id = row["trainer_id"] if "trainer_id" in row.keys() else None
    s.status = row["status"]             # 'active', 'expired', hoặc 'cancelled'
    s.created_at = datetime.fromisoformat(row["created_at"])
    s.updated_at = datetime.fromisoformat(row["updated_at"])
    s.is_active = bool(row["is_active"])
    return s


# ══════════════════════════════════════════════════════════════════════════════
# CRUD CHO BẢNG: membership_plans (Gói tập)
# ══════════════════════════════════════════════════════════════════════════════

def create_plan(plan: MembershipPlan) -> MembershipPlan:
    """Thêm gói tập mới vào database (INSERT).

    VD: Tạo gói "1 tháng" 30 ngày giá 500,000đ
    """
    with get_db() as conn:
        conn.execute(
            """INSERT INTO membership_plans (id, name, duration_days, price, description,
               created_at, updated_at, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (plan.id, plan.name, plan.duration_days, plan.price, plan.description,
             plan.created_at.isoformat(), plan.updated_at.isoformat(), int(plan.is_active))
        )
    return plan


def get_plan_by_id(id: str) -> MembershipPlan | None:
    """Tìm gói tập theo ID. Trả về MembershipPlan hoặc None."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM membership_plans WHERE id = ?", (id,)).fetchone()
    return _row_to_plan(row) if row else None


def get_all_plans(active_only: bool = True) -> list[MembershipPlan]:
    """Lấy danh sách tất cả gói tập, sắp xếp theo giá từ thấp → cao.

    active_only=True: chỉ lấy gói đang active (chưa bị xóa)
    """
    with get_db() as conn:
        if active_only:
            rows = conn.execute("SELECT * FROM membership_plans WHERE is_active = 1 ORDER BY price").fetchall()
        else:
            rows = conn.execute("SELECT * FROM membership_plans ORDER BY price").fetchall()
    return [_row_to_plan(r) for r in rows]


def update_plan(plan: MembershipPlan) -> MembershipPlan:
    """Cập nhật thông tin gói tập (UPDATE)."""
    plan.update()  # Cập nhật updated_at
    with get_db() as conn:
        conn.execute(
            """UPDATE membership_plans SET name=?, duration_days=?, price=?, description=?,
               updated_at=?, is_active=? WHERE id=?""",
            (plan.name, plan.duration_days, plan.price, plan.description,
             plan.updated_at.isoformat(), int(plan.is_active), plan.id)
        )
    return plan


def delete_plan(id: str):
    """Xóa mềm gói tập (soft delete): is_active = 0."""
    with get_db() as conn:
        conn.execute(
            "UPDATE membership_plans SET is_active = 0, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), id)
        )


# ══════════════════════════════════════════════════════════════════════════════
# CRUD CHO BẢNG: subscriptions (Đăng ký gói tập)
# ══════════════════════════════════════════════════════════════════════════════

def create_subscription(sub: MembershipSubscription) -> MembershipSubscription:
    """Lưu đăng ký gói tập mới vào database.

    VD: Hội viên A đăng ký Gói 1 tháng, trả 500,000đ, từ 01/03 đến 31/03
    """
    with get_db() as conn:
        conn.execute(
            """INSERT INTO subscriptions (id, member_id, plan_id, price_paid,
               start_date, end_date, status, trainer_id, created_at, updated_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sub.id, sub.member_id, sub.plan_id, sub.price_paid,
             sub.start_date.isoformat(), sub.end_date.isoformat(), sub.status,
             getattr(sub, 'trainer_id', None),
             sub.created_at.isoformat(), sub.updated_at.isoformat(), int(sub.is_active))
        )
    return sub


def get_subscription_by_id(id: str) -> MembershipSubscription | None:
    """Tìm đăng ký gói tập theo ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM subscriptions WHERE id = ?", (id,)).fetchone()
    return _row_to_sub(row) if row else None


def get_all_subscriptions() -> list[MembershipSubscription]:
    """Lấy TẤT CẢ đăng ký gói tập, sắp xếp theo ngày bắt đầu (mới nhất trước).

    ORDER BY start_date DESC: DESC = giảm dần (mới nhất ở đầu)
    """
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM subscriptions ORDER BY start_date DESC").fetchall()
    return [_row_to_sub(r) for r in rows]


def get_subscriptions_by_member(member_id: str) -> list[MembershipSubscription]:
    """Lấy tất cả đăng ký của 1 hội viên cụ thể (theo member_id).

    VD: Xem lịch sử gói tập của hội viên A → gọi get_subscriptions_by_member(a.id)
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM subscriptions WHERE member_id = ? ORDER BY start_date DESC", (member_id,)
        ).fetchall()
    return [_row_to_sub(r) for r in rows]


def get_active_subscriptions_by_member(member_id: str) -> list[MembershipSubscription]:
    """Lấy chỉ các đăng ký ĐANG ACTIVE của 1 hội viên.

    Khác với get_subscriptions_by_member: hàm trên lấy TẤT CẢ (kể cả expired/cancelled),
    hàm này chỉ lấy status = 'active'.
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM subscriptions WHERE member_id = ? AND status = 'active' ORDER BY end_date",
            (member_id,)
        ).fetchall()
    return [_row_to_sub(r) for r in rows]


def get_expiring_soon(days: int = 7) -> list[MembershipSubscription]:
    """Lấy danh sách đăng ký SẮP HẾT HẠN trong N ngày tới.

    Mặc định: 7 ngày tới.

    Logic SQL:
    - status = 'active': chỉ lấy gói đang active
    - end_date <= cutoff: hết hạn TRƯỚC hoặc đúng ngày cutoff
    - end_date >= now: chưa hết hạn (vẫn còn hiệu lực)
    → Kết hợp: gói active mà sẽ hết hạn trong khoảng [hôm nay, hôm nay + 7 ngày]

    VD: Hôm nay 22/03, days=7 → tìm gói hết hạn từ 22/03 đến 29/03
    """
    cutoff = (datetime.now() + timedelta(days=days)).isoformat()  # Ngày giới hạn trên
    now = datetime.now().isoformat()                               # Ngày hiện tại
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM subscriptions WHERE status = 'active'
               AND end_date <= ? AND end_date >= ? ORDER BY end_date""",
            (cutoff, now)
        ).fetchall()
    return [_row_to_sub(r) for r in rows]


def update_subscription(sub: MembershipSubscription) -> MembershipSubscription:
    """Cập nhật đăng ký gói tập (VD: đổi status, giá...)."""
    sub.update()  # Cập nhật updated_at
    with get_db() as conn:
        conn.execute(
            """UPDATE subscriptions SET status=?, price_paid=?, start_date=?, end_date=?,
               trainer_id=?, updated_at=?, is_active=? WHERE id=?""",
            (sub.status, sub.price_paid, sub.start_date.isoformat(), sub.end_date.isoformat(),
             getattr(sub, 'trainer_id', None),
             sub.updated_at.isoformat(), int(sub.is_active), sub.id)
        )
    return sub


def expire_old_subscriptions():
    """TỰ ĐỘNG chuyển các gói tập đã quá hạn từ 'active' → 'expired'.

    Hàm này được gọi khi mở trang đăng ký gói tập (refresh_subs).
    Thay vì kiểm tra từng gói trong Python, dùng 1 câu SQL UPDATE hàng loạt:
    → Tất cả gói có status='active' VÀ end_date < hiện tại → đổi thành 'expired'
    """
    now = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE subscriptions SET status='expired', updated_at=? WHERE status='active' AND end_date < ?",
            (now, now)
        )
