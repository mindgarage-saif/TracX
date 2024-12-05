import logging
import os

import cv2
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class VideoGalleryItem(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, parent, path: str, item_height: int = 64):
        super().__init__(parent)
        self.path = path
        self.thumbnail_size = item_height

        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.emptyFrame = QFrame(self)
        self.emptyFrame.setProperty("class", "video-gallery-item")
        self.emptyFrame.setFixedHeight(item_height + 16)
        self.innerLayout = QHBoxLayout(self.emptyFrame)
        self.innerLayout.setContentsMargins(8, 8, 8, 8)
        self.innerLayout.setSpacing(16)
        self.layout.addWidget(self.emptyFrame)

        # Create and set up labels
        self.thumbnail_label = QLabel(self)

        self.info_widget = QWidget(self)
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(0)

        self.filename_label = QLabel(self)
        self.fileinfo_label = QLabel(self)
        self.info_layout.addWidget(self.filename_label)
        self.info_layout.addWidget(self.fileinfo_label)
        self.info_layout.addStretch()

        # Add labels to layout
        self.innerLayout.addWidget(self.thumbnail_label)
        self.innerLayout.addWidget(self.info_widget)
        self.innerLayout.addStretch()

        # Create video thumbnail and display
        self.create_thumbnail()

        # Connect signals
        self.thumbnail_label.mousePressEvent = self.mousePressEvent
        self.filename_label.mousePressEvent = self.mousePressEvent

    def mousePressEvent(self, event):
        self.clicked.emit(self.path)

    def create_thumbnail(self):
        # Capture the video
        cap = cv2.VideoCapture(self.path)
        if not cap.isOpened():
            logging.error(f"Failed to open video: {self.path}")
            return

        # Get video metadata
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Read the first frame for the thumbnail
        ret, frame = cap.read()
        cap.release()

        if ret:
            # Resize the frame to create a square thumbnail
            thumbnail_size = self.thumbnail_size
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            thumbnail = cv2.resize(frame, (thumbnail_size, thumbnail_size))

            # Convert the frame to a QImage
            height_, width_, channel = thumbnail.shape
            bytes_per_line = 3 * width_
            q_img = QImage(
                thumbnail.data,
                width_,
                height_,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )
            pixmap = QPixmap.fromImage(q_img)

            # Set the thumbnail pixmap
            self.thumbnail_label.setPixmap(pixmap)
            self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Extract the base name of the video file
        filename = os.path.basename(self.path)
        self.filename_label.setText(filename)
        self.filename_label.setStyleSheet(
            "color: white; font-size: 12px; font-weight: bold;"
        )

        self.fileinfo_label.setText(f"{width}x{height}\n{duration:.2f}s\n{fps:.2f} FPS")

    def deleteLater(self):
        self.thumbnail_label.deleteLater()
        self.filename_label.deleteLater()
        super().deleteLater()
