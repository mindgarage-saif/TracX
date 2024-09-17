import logging
from typing import Tuple

import cv2
import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel

logger = logging.getLogger(__name__)


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

    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT)

    return image, (top, bottom, left, right)


class CameraView(QLabel):

    mousePressed = pyqtSignal(int, int, bool)

    def __init__(self, size, flip=True):
        super().__init__()
        self.size = size
        self.flip = flip
        self.resize(*size)
        self.clear()

        # Frame size and padding
        # (used for converting mouse coordinates to image coordinates)
        self.frame_size = size
        self.frame_pad = (0, 0, 0, 0)

    def mousePressEvent(self, event):
        replace = event.button() == 1

        x, y = event.x(), event.y()

        # Flip coordinates if the image is flipped
        if self.flip:
            x = self.size[1] - x

        # Adjust coordinates by the frame padding
        x -= self.frame_pad[2]  # left
        y -= self.frame_pad[0]  # top

        # Rescale and convert to integer in one step
        x = int(x * self.frame_size[1] / self.size[1])
        y = int(y * self.frame_size[0] / self.size[0])

        self.mousePressed.emit(x, y, replace)

    def show(self, frame: np.ndarray):
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1) if self.flip else frame
            self.frame_size = frame.shape[:2]
            frame, pad = resize_with_padding(frame, self.size)
            self.frame_pad = pad
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(
                frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )
            pixmap = QPixmap(convert_to_Qt_format)
            self.setPixmap(pixmap)
        except Exception as e:
            logger.error(e)

    def clear(self):
        image = cv2.imread("assets/nocamera.jpg")
        image = cv2.flip(image, 1)
        self.show(image)
