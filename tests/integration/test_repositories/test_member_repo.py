import pytest
from app.models.member import Member
from app.repositories import member_repo

def test_create_and_get_member(db):
    """Kiểm tra chức năng thêm mới và lấy thông tin theo ID."""
    # Tạo đối tượng hội viên mới
    new_member = Member(name="Nguyen Van A", phone="0901234567")
    
    # 1. Gọi hàm Create
    created = member_repo.create(new_member)
    assert created.id == new_member.id
    
    # 2. Gọi hàm Get By ID
    fetched = member_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Nguyen Van A"
    assert fetched.phone == "0901234567"
    assert fetched.is_active is True

def test_get_all_members(db):
    """Kiểm tra chức năng lấy danh sách hội viên (sắp xếp theo tên)."""
    m1 = Member(name="Alice", phone="0911111111")
    m2 = Member(name="Bob", phone="0922222222")
    m3 = Member(name="Charlie", phone="0933333333")
    
    member_repo.create(m2)
    member_repo.create(m1)
    member_repo.create(m3)
    
    # Xóa mềm m3 để test `active_only`
    member_repo.delete(m3.id)
    
    # Lấy danh sách hội viên (chỉ lấy active)
    active_members = member_repo.get_all(active_only=True)
    assert len(active_members) == 2
    assert active_members[0].name == "Alice"  # Kiểm tra sắp xếp A->Z
    assert active_members[1].name == "Bob"

    # Lấy toàn bộ (cả active và không active)
    all_members = member_repo.get_all(active_only=False)
    assert len(all_members) == 3

def test_search_members(db):
    """Kiểm tra tìm kiếm hội viên theo Tên, SĐT, Email."""
    m1 = Member(name="Alice Nguyen", phone="0911111111")
    m2 = Member(name="Bob Tran", phone="0922222222", email="bob@gmail.com")
    
    member_repo.create(m1)
    member_repo.create(m2)
    
    # Tìm kiếm theo tên
    res_name = member_repo.search("Nguyen")
    assert len(res_name) == 1
    assert res_name[0].name == "Alice Nguyen"
    
    # Tìm kiếm theo email
    res_email = member_repo.search("gmail.com")
    assert len(res_email) == 1
    assert res_email[0].name == "Bob Tran"
    
    # Tìm kiếm theo số điện thoại
    res_phone = member_repo.search("091")
    assert len(res_phone) == 1
    assert res_phone[0].name == "Alice Nguyen"

def test_update_member(db):
    """Kiểm tra chức năng cập nhật thông tin hội viên."""
    m = Member(name="Old Name", phone="0999999999")
    member_repo.create(m)
    
    # Thay đổi thông tin
    m.name = "New Name"
    m.email = "new@mail.com"
    member_repo.update(m)
    
    # Kiểm tra lại thông tin sau update
    fetched = member_repo.get_by_id(m.id)
    assert fetched.name == "New Name"
    assert fetched.email == "new@mail.com"

def test_get_by_phone(db):
    """Kiểm tra chức năng tìm hội viên theo SĐT để đăng nhập."""
    m = Member(name="Jane", phone="0888777666")
    member_repo.create(m)
    
    fetched = member_repo.get_by_phone("0888777666")
    assert fetched is not None
    assert fetched.name == "Jane"
    
    # Tìm số không tồn tại
    assert member_repo.get_by_phone("0000000000") is None
