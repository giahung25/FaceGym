import os
import pytest
from app.core import config
from app.core.database import init_db, get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Thiết lập môi trường test chung nếu cần."""
    os.environ["TESTING"] = "1"
    yield
    os.environ.pop("TESTING", None)

@pytest.fixture
def test_db_path(tmp_path):
    """Tạo một đường dẫn file DB tạm thời cho MỖI test case."""
    db_file = tmp_path / "test_gym_db.db"
    return str(db_file)

@pytest.fixture
def db(monkeypatch, test_db_path):
    """
    Mock cấu hình DB_PATH để trỏ vào database tạm thời.
    Khởi tạo bảng (schema) sạch sẽ trước mỗi test case.
    """
    # 1. Ghi đè đường dẫn database trong module database
    import app.core.database as database
    monkeypatch.setattr(database, "DB_PATH", test_db_path)
    
    # 2. Khởi tạo schema (tạo bảng)
    init_db()
    
    # 3. Trả về session connection để test sử dụng nếu cần
    with get_db() as conn:
        yield conn
    
    # 4. Teardown: File test_db_path sẽ tự động bị xóa bởi tmp_path của pytest
