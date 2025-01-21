import cv2


def get_cam() -> cv2.VideoCapture:
    return cv2.VideoCapture(3)
