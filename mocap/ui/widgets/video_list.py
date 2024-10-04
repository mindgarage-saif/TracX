from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from .video_preview import VideoPreview


class VideoList(QWidget):
    def __init__(self, parent, video_paths: list):
        super().__init__(parent)

        # Create the main layout for the VideoList
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create a scrollable area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget inside the scroll area
        self.scroll_widget = QWidget(self.scroll_area)
        self.scroll_layout = QHBoxLayout(self.scroll_widget)
        self.scroll_widget.setLayout(self.scroll_layout)

        # Add the scroll widget to the scroll area
        self.scroll_area.setWidget(self.scroll_widget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

        # Populate the list with VideoPreviews
        self.populate_list(video_paths)

    def populate_list(self, video_paths: list):
        # Iterate through the list of video paths and create VideoPreview widgets
        for video_path in video_paths:
            video_preview = VideoPreview(self, video_path)
            self.scroll_layout.addWidget(video_preview)

        # Add a stretch to fill the remaining space
        self.scroll_layout.addStretch()
