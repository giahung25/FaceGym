"""
Module trích xuất đặc trưng khuôn mặt (Face Encoding).

Chức năng:
    - Đọc ảnh khuôn mặt và chuyển thành vector embedding 128 chiều.
    - Encode hàng loạt ảnh hội viên từ thư mục dataset.
    - Lưu / Đọc file encodings (pickle) để tái sử dụng.
"""

import os
import pickle
import logging
import face_recognition
import numpy as np

logger = logging.getLogger("FaceEncoder")


class FaceEncoder:
    """Mã hóa ảnh khuôn mặt thành embedding vector 128D."""

    def __init__(self, model_type="hog"):
        self.model_type = model_type
        logger.info(f"FaceEncoder khởi tạo với model: {model_type}")

    def encode_face(self, image_path):
        """Đọc 1 ảnh và trích xuất embedding khuôn mặt.

        Returns: numpy array 128D nếu tìm thấy khuôn mặt, None nếu không.
        """
        if not os.path.isfile(image_path):
            logger.warning(f"File ảnh không tồn tại: {image_path}")
            return None

        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image, model=self.model_type)

        if len(face_locations) == 0:
            logger.warning(f"Không phát hiện khuôn mặt trong: {image_path}")
            return None

        if len(face_locations) > 1:
            logger.warning(
                f"Phát hiện {len(face_locations)} khuôn mặt trong {image_path}, "
                f"chỉ lấy khuôn mặt đầu tiên."
            )

        encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)

        if len(encodings) == 0:
            logger.warning(f"Không thể trích xuất encoding từ: {image_path}")
            return None

        logger.info(f"Encode thành công: {os.path.basename(image_path)}")
        return encodings[0]

    def encode_all_members(self, dataset_dir):
        """Duyệt thư mục dataset và encode tất cả ảnh hội viên.

        Cấu trúc: dataset/{member_id_or_name}/img1.jpg, img2.jpg...

        Returns: dict {"names": [str], "encodings": [ndarray]}
        """
        known_names = []
        known_encodings = []

        if not os.path.isdir(dataset_dir):
            logger.error(f"Thư mục dataset không tồn tại: {dataset_dir}")
            return {"names": known_names, "encodings": known_encodings}

        member_dirs = sorted(os.listdir(dataset_dir))

        for member_name in member_dirs:
            member_path = os.path.join(dataset_dir, member_name)
            if not os.path.isdir(member_path):
                continue

            logger.info(f"Đang encode hội viên: {member_name}")

            image_files = [
                f for f in os.listdir(member_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))
            ]

            if not image_files:
                logger.warning(f"Không tìm thấy ảnh trong: {member_path}")
                continue

            encoded_count = 0
            for img_file in image_files:
                img_path = os.path.join(member_path, img_file)
                embedding = self.encode_face(img_path)
                if embedding is not None:
                    known_names.append(member_name)
                    known_encodings.append(embedding)
                    encoded_count += 1

            logger.info(f"  → {member_name}: {encoded_count}/{len(image_files)} ảnh encode thành công")

        logger.info(
            f"Hoàn tất encode dataset: {len(known_encodings)} encodings "
            f"từ {len(set(known_names))} hội viên"
        )
        return {"names": known_names, "encodings": known_encodings}

    def save_encodings(self, encodings_data, file_path):
        """Lưu dict encodings ra file pickle."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump(encodings_data, f)
        logger.info(f"Đã lưu encodings → {file_path}")

    @staticmethod
    def load_encodings(file_path):
        """Đọc file pickle encodings đã lưu."""
        if not os.path.isfile(file_path):
            logger.warning(f"File encodings không tồn tại: {file_path}")
            return {"names": [], "encodings": []}

        with open(file_path, "rb") as f:
            data = pickle.load(f)

        logger.info(
            f"Đã đọc encodings từ {file_path}: "
            f"{len(data.get('encodings', []))} encodings"
        )
        return data
