# ============================================================================
# FILE: app/services/auth_svc.py
# MỤC ĐÍCH: Xác thực đăng nhập cho USER APP (hội viên + HLV).
#            Khác với security.py (xác thực admin bằng username/password),
#            auth_svc xác thực bằng SĐT + PIN.
#
# KIẾN TRÚC: GUI (user_login.py) → auth_svc → member_repo / trainer_repo
# ============================================================================

from app.repositories import member_repo, trainer_repo


def login_member(phone: str, pin: str):
    """Đăng nhập hội viên bằng SĐT + PIN.

    Tham số:
        phone (str): Số điện thoại
        pin (str):   Mã PIN 6 số

    Trả về:
        Member: nếu đăng nhập thành công
        None:   nếu SĐT không tồn tại hoặc PIN sai
    """
    if not phone or not pin:
        return None

    member = member_repo.get_by_phone(phone.strip())
    if member and member.pin == pin:
        return member
    return None


def login_trainer(phone: str, pin: str):
    """Đăng nhập HLV bằng SĐT + PIN.

    Tham số:
        phone (str): Số điện thoại
        pin (str):   Mã PIN 6 số

    Trả về:
        Trainer: nếu đăng nhập thành công
        None:    nếu SĐT không tồn tại hoặc PIN sai
    """
    if not phone or not pin:
        return None

    trainer = trainer_repo.get_by_phone(phone.strip())
    if trainer and trainer.pin == pin:
        return trainer
    return None


def change_pin(user_type: str, user_id: str, old_pin: str, new_pin: str) -> bool:
    """Đổi PIN đăng nhập cho hội viên hoặc HLV.

    Tham số:
        user_type (str): 'member' hoặc 'trainer'
        user_id (str):   ID của user
        old_pin (str):   PIN hiện tại (để xác nhận)
        new_pin (str):   PIN mới

    Trả về:
        True:  đổi PIN thành công
        False: PIN cũ sai, PIN mới không hợp lệ, hoặc user không tồn tại

    Raises:
        ValueError: nếu PIN mới không đúng định dạng (6 chữ số)
    """
    # Validate PIN mới
    if not new_pin or len(new_pin) != 6 or not new_pin.isdigit():
        raise ValueError("PIN mới phải là 6 chữ số")

    if new_pin == old_pin:
        raise ValueError("PIN mới phải khác PIN cũ")

    if user_type == "member":
        user = member_repo.get_by_id(user_id)
        if not user or user.pin != old_pin:
            return False
        user.pin = new_pin
        member_repo.update(user)
        return True

    elif user_type == "trainer":
        user = trainer_repo.get_by_id(user_id)
        if not user or user.pin != old_pin:
            return False
        user.pin = new_pin
        trainer_repo.update(user)
        return True

    return False
