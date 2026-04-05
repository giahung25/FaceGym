from app.core.database import get_db
from app.models.transaction import Transaction
from datetime import datetime


def _row_to_transaction(row) -> Transaction:
    """Chuyển 1 dòng database thành đối tượng Transaction."""
    t = Transaction.__new__(Transaction)
    t.id = row["id"]
    t.member_id = row["member_id"]
    t.subscription_id = row["subscription_id"]
    t.amount = row["amount"]
    t.payment_method = row["payment_method"]
    t.note = row["note"]
    t.created_at = datetime.fromisoformat(row["created_at"])
    t.is_active = bool(row["is_active"])
    return t


def create(transaction: Transaction) -> Transaction:
    """Tạo giao dịch mới."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO transactions (id, member_id, subscription_id, amount,
               payment_method, note, created_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (transaction.id, transaction.member_id, transaction.subscription_id,
             transaction.amount, transaction.payment_method, transaction.note,
             transaction.created_at.isoformat(), int(transaction.is_active))
        )
    return transaction


def get_by_member(member_id: str, limit: int = 50) -> list[Transaction]:
    """Lấy lịch sử giao dịch của hội viên."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM transactions
               WHERE member_id = ? AND is_active = 1
               ORDER BY created_at DESC LIMIT ?""",
            (member_id, limit)
        ).fetchall()
    return [_row_to_transaction(r) for r in rows]


def get_all(limit: int = 50) -> list[Transaction]:
    """Lấy tất cả giao dịch."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM transactions
               WHERE is_active = 1
               ORDER BY created_at DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    return [_row_to_transaction(r) for r in rows]


def get_revenue_today() -> float:
    """Tổng doanh thu hôm nay."""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        row = conn.execute(
            """SELECT COALESCE(SUM(amount), 0) as total FROM transactions
               WHERE DATE(created_at) = ? AND is_active = 1""",
            (today,)
        ).fetchone()
    return row["total"]


def get_revenue_by_range(from_date: str, to_date: str) -> float:
    """Tổng doanh thu theo khoảng thời gian."""
    with get_db() as conn:
        row = conn.execute(
            """SELECT COALESCE(SUM(amount), 0) as total FROM transactions
               WHERE DATE(created_at) BETWEEN ? AND ? AND is_active = 1""",
            (from_date, to_date)
        ).fetchone()
    return row["total"]
