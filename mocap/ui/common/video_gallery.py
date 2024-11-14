from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from .video_gallery_item import VideoGalleryItem
from .video_player_widget import VideoPlayerWidget


class VideoGallery(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # Create the main layout for the VideoList
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(16)
        self.setLayout(self.layout)

        # Create a video player widget
        self.video_player = VideoPlayerWidget(self)
        self.video_player.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.layout.addWidget(self.video_player)

        # Create a scrollable area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget inside the scroll area
        self.scroll_widget = QWidget(self.scroll_area)
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setContentsMargins(16, 16, 16, 16)
        self.scroll_layout.setSpacing(8)
        self.scroll_widget.setLayout(self.scroll_layout)

        # Add the scroll widget to the scroll area
        self.scroll_area.setWidget(self.scroll_widget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

    def clear(self):
        self.video_player.stop()
        self.video_player.setVideoSource(None)

        # Clear the list of VideoPreviews
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()

    def setItems(self, video_paths: list):
        self.clear()
        self.scroll_layout.addStretch()

        # Iterate through the list of video paths and create VideoPreview widgets
        for video_path in video_paths:
            preview = VideoGalleryItem(self, video_path, 64)
            preview.clicked.connect(self.video_player.setVideoSource)
            self.scroll_layout.addWidget(preview)
