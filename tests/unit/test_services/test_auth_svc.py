import pytest
from app.services import auth_svc

def test_login_member_success(mocker):
    mock_member = mocker.MagicMock()
    mock_member.pin = "123456"
    mocker.patch("app.services.auth_svc.member_repo.get_by_phone", return_value=mock_member)
    result = auth_svc.login_member("0901234567", "123456")
    assert result == mock_member

def test_login_member_empty_input():
    assert auth_svc.login_member(None, "123456") is None
    assert auth_svc.login_member("0901234567", None) is None

def test_login_member_fail_wrong_pin(mocker):
    mock_member = mocker.MagicMock()
    mock_member.pin = "123456"
    mocker.patch("app.services.auth_svc.member_repo.get_by_phone", return_value=mock_member)
    result = auth_svc.login_member("0901234567", "000000")
    assert result is None

def test_login_member_fail_not_found(mocker):
    mocker.patch("app.services.auth_svc.member_repo.get_by_phone", return_value=None)
    result = auth_svc.login_member("0901234567", "123456")
    assert result is None

def test_login_trainer_success(mocker):
    mock_trainer = mocker.MagicMock()
    mock_trainer.pin = "654321"
    mocker.patch("app.services.auth_svc.trainer_repo.get_by_phone", return_value=mock_trainer)
    result = auth_svc.login_trainer("0888888888", "654321")
    assert result == mock_trainer

def test_login_trainer_empty_input():
    assert auth_svc.login_trainer("", "654321") is None
    assert auth_svc.login_trainer("0888888888", "") is None

def test_login_trainer_fail(mocker):
    mock_trainer = mocker.MagicMock()
    mock_trainer.pin = "654321"
    mocker.patch("app.services.auth_svc.trainer_repo.get_by_phone", return_value=mock_trainer)
    assert auth_svc.login_trainer("0888888888", "000000") is None
    
    mocker.patch("app.services.auth_svc.trainer_repo.get_by_phone", return_value=None)
    assert auth_svc.login_trainer("0888888888", "654321") is None

def test_change_pin_success_member(mocker):
    mock_member = mocker.MagicMock()
    mock_member.pin = "123456"
    mocker.patch("app.services.auth_svc.member_repo.get_by_id", return_value=mock_member)
    mock_update = mocker.patch("app.services.auth_svc.member_repo.update")
    result = auth_svc.change_pin("member", "mock-id", "123456", "111111")
    assert result is True
    assert mock_member.pin == "111111"
    mock_update.assert_called_once_with(mock_member)

def test_change_pin_success_trainer(mocker):
    mock_trainer = mocker.MagicMock()
    mock_trainer.pin = "654321"
    mocker.patch("app.services.auth_svc.trainer_repo.get_by_id", return_value=mock_trainer)
    mock_update = mocker.patch("app.services.auth_svc.trainer_repo.update")
    result = auth_svc.change_pin("trainer", "mock-id", "654321", "111111")
    assert result is True
    assert mock_trainer.pin == "111111"
    mock_update.assert_called_once_with(mock_trainer)

def test_change_pin_fail_invalid_format():
    with pytest.raises(ValueError, match="PIN mới phải là 6 chữ số"):
        auth_svc.change_pin("member", "id", "123456", "123")
    with pytest.raises(ValueError, match="PIN mới phải là 6 chữ số"):
        auth_svc.change_pin("member", "id", "123456", "abcdef")

def test_change_pin_fail_same_pin():
    with pytest.raises(ValueError, match="PIN mới phải khác PIN cũ"):
        auth_svc.change_pin("member", "id", "123456", "123456")

def test_change_pin_fail_wrong_old_pin(mocker):
    mock_member = mocker.MagicMock()
    mock_member.pin = "123456"
    mocker.patch("app.services.auth_svc.member_repo.get_by_id", return_value=mock_member)
    result = auth_svc.change_pin("member", "id", "000000", "654321")
    assert result is False
    
    mock_trainer = mocker.MagicMock()
    mock_trainer.pin = "654321"
    mocker.patch("app.services.auth_svc.trainer_repo.get_by_id", return_value=mock_trainer)
    assert auth_svc.change_pin("trainer", "id", "000000", "111111") is False

def test_change_pin_invalid_user_type():
    assert auth_svc.change_pin("admin", "id", "123456", "654321") is False

def test_change_pin_user_not_found(mocker):
    mocker.patch("app.services.auth_svc.member_repo.get_by_id", return_value=None)
    assert auth_svc.change_pin("member", "id", "123456", "654321") is False
