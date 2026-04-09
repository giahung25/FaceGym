import os
import pytest
import numpy as np
from app.face_id.face_encoder import FaceEncoder

@pytest.fixture
def encoder():
    return FaceEncoder(model_type="hog")

def test_encode_face_file_not_found(encoder, mocker):
    mocker.patch("os.path.isfile", return_value=False)
    result = encoder.encode_face("dummy_path.jpg")
    assert result is None

def test_encode_face_no_face_detected(encoder, mocker):
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("face_recognition.load_image_file", return_value="dummy_img")
    mocker.patch("face_recognition.face_locations", return_value=[])
    
    result = encoder.encode_face("dummy_path.jpg")
    assert result is None

def test_encode_face_multiple_faces(encoder, mocker):
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("face_recognition.load_image_file", return_value="dummy_img")
    mocker.patch("face_recognition.face_locations", return_value=[(10,20,30,40), (50,60,70,80)])
    
    dummy_encoding = np.array([0.1, 0.2])
    mocker.patch("face_recognition.face_encodings", return_value=[dummy_encoding, np.array([0.3, 0.4])])
    
    result = encoder.encode_face("dummy_path.jpg")
    # Kiểm tra xem hệ thống có lấy đúng khuôn mặt đầu tiên hay không
    assert np.array_equal(result, dummy_encoding)

def test_encode_face_no_encoding(encoder, mocker):
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("face_recognition.load_image_file", return_value="dummy_img")
    mocker.patch("face_recognition.face_locations", return_value=[(10,20,30,40)])
    mocker.patch("face_recognition.face_encodings", return_value=[])
    
    result = encoder.encode_face("dummy_path.jpg")
    assert result is None

def test_encode_all_members_dir_not_found(encoder, mocker):
    mocker.patch("os.path.isdir", return_value=False)
    result = encoder.encode_all_members("dummy_dir")
    assert result == {"names": [], "encodings": []}

def test_encode_all_members_success(encoder, mocker):
    # Mock logic hệ thống kiểm tra thư mục
    def mock_isdir(path):
        if path == "dummy_dir": return True
        if path.endswith("member1") or path.endswith("member2"): return True
        return False
    mocker.patch("os.path.isdir", side_effect=mock_isdir)
    
    # Lần 1: Lấy danh sách thư mục hội viên, Lần 2 & 3: Lấy danh sách ảnh
    mocker.patch("os.listdir", side_effect=[
        ["member1", "member2", "file.txt"],    # Trong dataset_dir
        ["img1.jpg", "img2.png", "doc.txt"],   # Trong member1
        ["img3.jpg"]                           # Trong member2
    ])
    
    dummy_encoding = np.array([0.1, 0.2])
    # Encode face mock trả về dữ liệu ảo
    mocker.patch.object(encoder, "encode_face", return_value=dummy_encoding)
    
    result = encoder.encode_all_members("dummy_dir")
    
    assert len(result["names"]) == 3
    assert result["names"] == ["member1", "member1", "member2"]
    assert len(result["encodings"]) == 3
    assert np.array_equal(result["encodings"][0], dummy_encoding)

def test_save_and_load_encodings(encoder, tmp_path):
    """Sử dụng tmp_path để test tạo và đọc file pickle thực sự nhưng chỉ lưu tạm."""
    encodings_data = {
        "names": ["member1", "member2"],
        "encodings": [np.array([0.1]), np.array([0.2])]
    }
    
    file_path = tmp_path / "test_encodings.pkl"
    
    # Test Save
    encoder.save_encodings(encodings_data, str(file_path))
    assert file_path.exists()
    
    # Test Load
    loaded_data = FaceEncoder.load_encodings(str(file_path))
    assert loaded_data["names"] == ["member1", "member2"]
    assert np.array_equal(loaded_data["encodings"][0], np.array([0.1]))

def test_load_encodings_file_not_found(tmp_path):
    file_path = tmp_path / "not_exist.pkl"
    loaded_data = FaceEncoder.load_encodings(str(file_path))
    assert loaded_data == {"names": [], "encodings": []}
