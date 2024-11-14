from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from .video_preview import VideoPreview


class VideoList(QWidget):
    def __init__(self, parent, preview_size=200):
        super().__init__(parent)
        self.preview_size = preview_size

        # Create the main layout for the VideoList
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Create a scrollable area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        self.scroll_area.setFixedHeight(268)

        # Create a container widget inside the scroll area
        self.scroll_widget = QWidget(self.scroll_area)
        self.scroll_layout = QHBoxLayout(self.scroll_widget)
        self.scroll_widget.setLayout(self.scroll_layout)

        # Add the scroll widget to the scroll area
        self.scroll_area.setWidget(self.scroll_widget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

    def clear_list(self):
        # Clear the list of VideoPreviews
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                self.scroll_layout.removeWidget(widget)
                widget.setParent(None)

    def populate_list(self, video_paths: list):
        self.clear_list()
        # Iterate through the list of video paths and create VideoPreview widgets
        for video_path in video_paths:
            video_preview = VideoPreview(self, video_path, self.preview_size)
            self.scroll_layout.addWidget(video_preview)

        # Add a stretch to fill the remaining space
        self.scroll_layout.addStretch()
