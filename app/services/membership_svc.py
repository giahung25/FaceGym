# ============================================================================
# FILE: app/services/membership_svc.py
# MỤC ĐÍCH: Tầng SERVICE cho gói tập và đăng ký gói tập.
#            Chứa logic nghiệp vụ: tạo gói, đăng ký, hủy, tính doanh thu...
# ============================================================================

from datetime import datetime
from app.models.membership import MembershipPlan, MembershipSubscription
from app.repositories import membership_repo


def create_plan(name: str, duration_days: int, price: float,
                description: str = None) -> MembershipPlan:
    """Tạo gói tập MỚI (VD: "Gói 1 tháng", 30 ngày, 500,000đ).

    Validation:
    - Tên không được trống
    - Số ngày phải > 0
    - Giá không được âm (cho phép 0 = miễn phí)

    Raises: ValueError nếu dữ liệu không hợp lệ
    """
    if not name or not name.strip():
        raise ValueError("Tên gói tập không được để trống")
    if duration_days <= 0:
        raise ValueError("Số ngày phải lớn hơn 0")
    if price < 0:
        raise ValueError("Giá không được âm")

    # Tạo đối tượng MembershipPlan (id, created_at tự động sinh)
    plan = MembershipPlan(
        name=name.strip(),
        duration_days=duration_days,
        price=price,
        description=description,
    )
    # Lưu vào database qua repository
    return membership_repo.create_plan(plan)


def update_plan(plan: MembershipPlan, name: str = None, duration_days: int = None,
                price: float = None, description: str = None) -> MembershipPlan:
    """Cập nhật thông tin gói tập.

    Chỉ cập nhật các field được truyền vào (không None).
    VD: update_plan(plan, name="Tên mới") → chỉ đổi tên, giữ nguyên giá và số ngày

    Tham số:
        plan: đối tượng MembershipPlan cần sửa
        name, duration_days, price, description: giá trị mới (None = không đổi)
    """
    # "is not None" kiểm tra xem tham số có được truyền vào không
    if name is not None:
        plan.name = name.strip()
    if duration_days is not None:
        plan.duration_days = duration_days
    if price is not None:
        plan.price = price
    if description is not None:
        plan.description = description
    return membership_repo.update_plan(plan)  # Ghi vào DB


def subscribe_member(member_id: str, plan_id: str,
                     price_paid: float = None, start_date: datetime = None,
                     trainer_id: str = None) -> MembershipSubscription:
    """Đăng ký gói tập cho hội viên.

    Flow:
    1. Tìm gói tập theo plan_id (phải tồn tại)
    2. Tạo MembershipSubscription với:
       - member_id: ai đăng ký
       - plan_id: đăng ký gói nào
       - duration_days: lấy từ plan
       - price_paid: số tiền thực trả (nếu không truyền → dùng giá gốc)
       - start_date: ngày bắt đầu (mặc định = hôm nay)
    3. Lưu vào database

    Tham số:
        member_id (str): UUID hội viên
        plan_id (str): UUID gói tập
        price_paid (float, optional): giá thực trả (None = giá gốc)
        start_date (datetime, optional): ngày bắt đầu (None = hôm nay)

    Raises: ValueError nếu không tìm thấy gói tập
    """
    # Bước 1: Tìm gói tập trong DB
    plan = membership_repo.get_plan_by_id(plan_id)
    if not plan:
        raise ValueError("Không tìm thấy gói tập")

    # Bước 2: Tạo đăng ký
    sub = MembershipSubscription(
        member_id=member_id,
        plan_id=plan_id,
        duration_days=plan.duration_days,                              # Lấy số ngày từ gói
        price_paid=price_paid if price_paid is not None else plan.price,  # Giá thực trả hoặc giá gốc
        start_date=start_date or datetime.now(),                       # Ngày bắt đầu hoặc hôm nay
        trainer_id=trainer_id,                                          # HLV (None = gói thường)
    )

    # Bước 3: Lưu vào DB
    sub = membership_repo.create_subscription(sub)

    # Bước 4: Nếu có HLV → tự động tạo assignment
    if trainer_id:
        from app.services import assignment_svc
        try:
            assignment_svc.assign_trainer(
                member_id=member_id,
                trainer_id=trainer_id,
                subscription_id=sub.id,
                notes=f"Gói tập: {plan.name}",
            )
        except ValueError:
            pass  # Bỏ qua nếu đã có assignment trùng

    return sub


def cancel_subscription(sub_id: str) -> MembershipSubscription:
    """Hủy đăng ký gói tập.

    Điều kiện:
    - Đăng ký phải tồn tại
    - Chỉ hủy được khi đang active (không hủy gói đã expired/cancelled)

    Tham số:
        sub_id (str): UUID đăng ký cần hủy

    Raises: ValueError nếu không tìm thấy hoặc không thể hủy
    """
    sub = membership_repo.get_subscription_by_id(sub_id)
    if not sub:
        raise ValueError("Không tìm thấy đăng ký gói tập")
    if sub.status != MembershipSubscription.STATUS_ACTIVE:
        raise ValueError("Chỉ có thể hủy gói tập đang active")

    sub.cancel()  # Đổi status → "cancelled", cập nhật updated_at
    return membership_repo.update_subscription(sub)  # Ghi vào DB


def auto_expire_subscriptions():
    """Tự động chuyển tất cả gói quá hạn thành 'expired'.

    Được gọi khi mở trang Subscriptions để cập nhật trạng thái.
    Delegate (ủy quyền) cho repository xử lý bằng 1 câu SQL UPDATE.
    """
    membership_repo.expire_old_subscriptions()


def get_monthly_revenue(months: int = 6) -> list[tuple[str, float]]:
    """Tính doanh thu theo từng tháng (mặc định 6 tháng gần nhất).

    Trả về:
        list[tuple[str, float]]: VD [("T10", 5000000), ("T11", 6000000), ...]
        - Phần tử đầu: label tháng (VD: "T3" = tháng 3)
        - Phần tử sau: tổng doanh thu tháng đó

    Logic:
    - Lấy TẤT CẢ subscriptions
    - Duyệt 6 tháng gần nhất (từ xa → gần)
    - Với mỗi tháng: tính tổng price_paid của các subscription được tạo trong tháng đó
    """
    subs = membership_repo.get_all_subscriptions()  # Lấy tất cả đăng ký
    now = datetime.now()
    result = []

    # Duyệt từ (months-1) tháng trước → tháng hiện tại
    # VD: months=6, i = 5,4,3,2,1,0 → 5 tháng trước, 4 tháng trước, ..., tháng này
    for i in range(months - 1, -1, -1):
        month = now.month - i   # Tính tháng (có thể ra số <= 0)
        year = now.year

        # Xử lý trường hợp tháng <= 0 (lùi sang năm trước)
        # VD: tháng hiện tại = 3, i = 5 → month = 3-5 = -2
        #     → month = -2+12 = 10, year = year-1 (tháng 10 năm trước)
        while month <= 0:
            month += 12
            year -= 1

        # Tính tổng doanh thu tháng đó
        # sum() cộng tất cả price_paid của subscription có created_at trong tháng/năm tương ứng
        total = sum(
            s.price_paid for s in subs
            if s.created_at.year == year and s.created_at.month == month
        )
        result.append((f"T{month}", total))  # VD: ("T3", 5000000)

    return result


def get_plan_subscription_stats() -> list[tuple[str, int]]:
    """Thống kê số lượng đăng ký active theo từng gói tập.

    Trả về top 3 gói phổ biến nhất.

    VD: [("Gói 1 tháng", 45), ("Gói 6 tháng", 30), ("Gói 1 năm", 12)]

    Dùng ở Dashboard: biểu đồ "Active Growth".
    """
    plans = membership_repo.get_all_plans(active_only=True)   # Lấy danh sách gói tập
    subs = membership_repo.get_all_subscriptions()             # Lấy tất cả đăng ký

    # Lọc chỉ đăng ký đang active
    active_subs = [s for s in subs if s.status == MembershipSubscription.STATUS_ACTIVE]

    # Đếm số đăng ký active cho mỗi plan_id
    # sub_counts = {"plan_id_1": 10, "plan_id_2": 5, ...}
    sub_counts: dict[str, int] = {}
    for s in active_subs:
        # dict.get(key, default) = lấy giá trị, nếu không có → trả default
        sub_counts[s.plan_id] = sub_counts.get(s.plan_id, 0) + 1

    # Ghép tên gói + số lượng
    stats = [(p.name, sub_counts.get(p.id, 0)) for p in plans]

    # Sắp xếp giảm dần theo số lượng, lấy top 3
    # key=lambda x: x[1] = sắp xếp theo phần tử thứ 2 (count)
    # reverse=True = giảm dần (nhiều nhất trước)
    stats.sort(key=lambda x: x[1], reverse=True)
    return stats[:3]  # Lấy 3 phần tử đầu tiên (top 3)


def get_revenue_stats() -> dict:
    """Tính thống kê doanh thu tổng hợp.

    Trả về dict:
    {
        "monthly": 5000000,    # Doanh thu tháng này
        "yearly": 45000000,    # Doanh thu năm nay
        "total": 120000000,    # Tổng doanh thu toàn bộ
    }

    Dùng ở Dashboard và Reports.
    """
    subs = membership_repo.get_all_subscriptions()
    now = datetime.now()

    # sum() với generator expression:
    # sum(s.price_paid for s in subs if điều_kiện)
    # = cộng price_paid của tất cả subscription thỏa điều kiện

    # Doanh thu tháng này: đăng ký có created_at trong tháng + năm hiện tại
    monthly = sum(
        s.price_paid for s in subs
        if s.created_at.year == now.year and s.created_at.month == now.month
    )

    # Doanh thu năm nay: đăng ký có created_at trong năm hiện tại
    yearly = sum(s.price_paid for s in subs if s.created_at.year == now.year)

    # Tổng doanh thu: cộng tất cả (không lọc)
    total = sum(s.price_paid for s in subs)

    return {
        "monthly": monthly,
        "yearly": yearly,
        "total": total,
    }
