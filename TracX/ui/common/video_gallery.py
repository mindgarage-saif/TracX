from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from TracX.ui.styles import PAD_X, PAD_Y

from .video_gallery_item import VideoGalleryItem
from .video_player_widget import VideoPlayerWidget


class VideoGallery(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("VideoGallery")
        # Create the main layout for the VideoList
        self.layout = QVBoxLayout()
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
        self.scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Create a container widget inside the scroll area
        self.scroll_widget = QFrame(self.scroll_area)
        self.scroll_widget.setObjectName("VideoGalleryScrollWidget")
        self.scroll_layout = QHBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.scroll_layout.setSpacing(8)
        self.scroll_widget.setLayout(self.scroll_layout)

        # Add the scroll widget to the scroll area
        self.scroll_area.setWidget(self.scroll_widget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

    def clear(self):
        self.video_player.stop()
        self.video_player.setSource(None)

        # Clear the list of VideoPreviews
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()

    def setItems(self, video_paths: list):
        self.clear()

        # Iterate through the list of video paths and create VideoPreview widgets
        for video_path in video_paths:
            preview = VideoGalleryItem(self, video_path, 64)
            preview.clicked.connect(self.video_player.setSource)
            self.scroll_layout.addWidget(preview)
