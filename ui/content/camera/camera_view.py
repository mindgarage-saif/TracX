from typing import Tuple

import cv2
import numpy as np
from PyQt5.QtWidgets import (QLabel, QLabel)
from PyQt5.QtGui import QImage, QPixmap


def resize_with_padding(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    h, w, c = image.shape
    target_h, target_w = target_size

    # Resize image to fit in target size while maintaining aspect ratio
    scale = min(target_w / w, target_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    # Resize image
    image = cv2.resize(image, (new_w, new_h))

    # Add padding to image
    top = (target_h - new_h) // 2
    bottom = target_h - new_h - top
    left = (target_w - new_w) // 2
    right = target_w - new_w - left

    image = cv2.copyMakeBorder(
        image, top, bottom, left, right, cv2.BORDER_CONSTANT)

    return image


class CameraView(QLabel):
    def __init__(self, size, flip=True):
        super().__init__()
        self.size = size
        self.flip = flip
        self.resize(*size)
        self.clear()

    def show(self, frame: np.ndarray):
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1) if self.flip else frame
            frame = resize_with_padding(frame, self.size)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(
                frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap(convert_to_Qt_format)
            self.setPixmap(pixmap)
        except Exception as e:
            print(e)

    def clear(self):
        # show splash image
        image = cv2.imread("assets/nocamera.jpg")
        image = cv2.flip(image, 1)
        self.show(image)
