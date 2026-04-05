# ============================================================================
# FILE: app/services/equipment_svc.py
# MỤC ĐÍCH: Tầng SERVICE cho thiết bị — chứa logic nghiệp vụ:
#            thêm/sửa thiết bị, thống kê tình trạng thiết bị.
# ============================================================================

from app.models.equipment import Equipment
from app.repositories import equipment_repo


def add_equipment(name: str, category: str, quantity: int = 1,
                  purchase_date=None, notes: str = None, location: str = None) -> Equipment:
    """Thêm thiết bị mới vào hệ thống.

    Validation:
    - Tên thiết bị không được trống
    - Loại thiết bị không được trống

    Tham số:
        name (str): Tên thiết bị (VD: "Máy chạy bộ TechnoGym")
        category (str): Loại (VD: "Cardio", "Tạ tự do")
        quantity (int): Số lượng — mặc định 1
        purchase_date: Ngày mua (tùy chọn)
        notes (str): Ghi chú (tùy chọn)
        location (str): Vị trí (tùy chọn)

    Trả về: Equipment đã tạo và lưu vào DB
    Raises: ValueError nếu tên hoặc loại trống
    """
    if not name or not name.strip():
        raise ValueError("Tên thiết bị không được để trống")
    if not category or not category.strip():
        raise ValueError("Loại thiết bị không được để trống")

    # Tạo đối tượng Equipment
    eq = Equipment(
        name=name.strip(),
        category=category.strip(),
        quantity=quantity,
        purchase_date=purchase_date,
        notes=notes,
    )
    # Equipment.__init__ không nhận location → phải gán riêng
    eq.location = location

    # Lưu vào database
    return equipment_repo.create(eq)


def update_equipment(eq: Equipment, **kwargs) -> Equipment:
    """Cập nhật thông tin thiết bị.

    Dùng **kwargs để nhận BẤT KỲ thuộc tính nào cần sửa.

    **kwargs là gì?
    - ** = "keyword arguments" — nhận tất cả tham số tên=giá_trị thành dict
    - VD: update_equipment(eq, name="Tên mới", status="broken")
          → kwargs = {"name": "Tên mới", "status": "broken"}

    setattr(object, name, value):
    - Gán thuộc tính cho object: eq.name = "Tên mới"
    - Tương đương: eq.name = value, nhưng tên thuộc tính là BIẾN (linh hoạt)

    Tham số:
        eq (Equipment): đối tượng cần sửa
        **kwargs: các thuộc tính cần thay đổi (VD: name="X", status="broken")

    Trả về: Equipment đã cập nhật
    """
    for k, v in kwargs.items():      # Duyệt qua từng cặp (tên thuộc tính, giá trị mới)
        setattr(eq, k, v)            # Gán: eq.<k> = v
    return equipment_repo.update(eq)  # Ghi vào DB


def get_equipment_summary() -> dict:
    """Tính thống kê tổng quan về thiết bị.

    Trả về dict:
    {
        "total": 20,           # Tổng số thiết bị
        "working": 15,         # Đang hoạt động
        "broken": 2,           # Đang hỏng
        "maintenance": 3,      # Đang bảo trì
        "categories": {        # Số lượng theo loại
            "Cardio": 8,
            "Tạ tự do": 5,
            "Máy lực": 7,
        }
    }

    Dùng ở Dashboard và Reports.
    """
    all_eq = equipment_repo.get_all(active_only=True)  # Lấy thiết bị đang active

    # sum(1 for e in list if điều_kiện) = đếm số phần tử thỏa điều kiện
    # (cách khác: len([e for e in list if điều_kiện]) — nhưng tốn bộ nhớ hơn)
    working = sum(1 for e in all_eq if e.status == Equipment.STATUS_WORKING)
    broken = sum(1 for e in all_eq if e.status == Equipment.STATUS_BROKEN)
    maintenance = sum(1 for e in all_eq if e.status == Equipment.STATUS_MAINTENANCE)

    # Đếm số thiết bị theo từng category
    categories = {}
    for e in all_eq:
        # dict.get(key, default): lấy giá trị hiện tại, nếu chưa có → trả default (0)
        # + 1: tăng đếm lên 1
        categories[e.category] = categories.get(e.category, 0) + 1

    return {
        "total": len(all_eq),
        "working": working,
        "broken": broken,
        "maintenance": maintenance,
        "categories": categories,
    }
