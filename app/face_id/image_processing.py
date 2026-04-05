"""Các hàm tiện ích xử lý hình ảnh cho Face ID."""
import cv2


def draw_bbox(frame, bbox, name="Unknown", confidence=0.0):
    """Vẽ bounding box và tên lên frame."""
    top, right, bottom, left = bbox

    color = (0, 0, 255) if name == "Unknown" else (0, 200, 0)

    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

    label = f"{name} ({confidence:.0%})" if name != "Unknown" else "Unknown"
    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    label_w, label_h = label_size

    cv2.rectangle(
        frame,
        (left, bottom),
        (left + label_w + 10, bottom + label_h + 14),
        color, cv2.FILLED
    )
    cv2.putText(
        frame, label,
        (left + 5, bottom + label_h + 8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
        (255, 255, 255), 1, cv2.LINE_AA
    )
    return frame


def resize_frame(frame, scale=0.5):
    """Thu nhỏ frame để tăng tốc xử lý."""
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    return cv2.resize(frame, (width, height))


def convert_bgr_to_rgb(frame):
    """Chuyển BGR (OpenCV) sang RGB (face_recognition)."""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
