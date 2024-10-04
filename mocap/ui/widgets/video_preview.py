import os

import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QImage, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class VideoPreview(QWidget):
    def __init__(self, parent, path: str, thumbnail_size: int = 150):
        super().__init__(parent)
        self.path = path
        self.thumbnail_size = thumbnail_size

        # Create layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create and set up labels
        self.thumbnail_label = QLabel(self)
        self.filename_label = QLabel(self)

        # Add labels to layout
        self.layout.addWidget(self.thumbnail_label)
        self.layout.addWidget(self.filename_label)

        # Create video thumbnail and display
        self.create_thumbnail()

        # Display video file name
        self.display_filename()

    def create_thumbnail(self):
        # Capture the video
        cap = cv2.VideoCapture(self.path)
        if not cap.isOpened():
            print(f"Failed to open video: {self.path}")
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

            # Superimpose metadata on the thumbnail
            thumbnail_with_text = pixmap.copy()
            painter = QPainter(thumbnail_with_text)
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(10, 20, f"{width}x{height} px")
            painter.drawText(10, 40, f"Duration: {duration:.2f}s")
            painter.drawText(10, 60, f"FPS: {fps:.2f}")
            painter.end()

            # Set the thumbnail pixmap
            self.thumbnail_label.setPixmap(thumbnail_with_text)
            self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def display_filename(self):
        # Extract the base name of the video file
        filename = os.path.basename(self.path)
        self.filename_label.setText(filename)
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filename_label.setFont(QFont("Arial", 12))
