import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.constants import MAX_VIDEOS, MIN_VIDEOS, SUPPORTED_VIDEO_FORMATS

from .video_list import VideoList


class VideoUploaderWidget(QFrame):
    """Widget for uploading experiment videos."""

    def __init__(
        self,
        parent: QWidget,
        minNumVideos=MIN_VIDEOS,
        numMaxVideos=MAX_VIDEOS,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setObjectName("DragDropWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(300)
        self.setAcceptDrops(True)
        self.min_num_videos = minNumVideos
        self.num_max_videos = numMaxVideos
        self.label = QLabel(
            f"Select or drop {self.min_num_videos}-{self.num_max_videos} videos here",
            self,
        )
        self.label.setProperty("class", "body")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedHeight(300)
        layout.addWidget(self.label)

        self.preview = VideoList(self, preview_size=200)
        self.preview.setFixedHeight(268)
        self.preview.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.preview.hide()
        layout.addWidget(self.preview)
        layout.addStretch()

        # Callback.
        self.onVideosSelected = lambda files: None

        self.isEnabled = True

    def setEnabled(self, enabled):
        self.isEnabled = enabled

    def previewSelected(self, selectedVideos):
        """Show the list of selected files."""
        if not selectedVideos:
            self.label.show()
            self.preview.hide()
            return

        self.preview.populate_list(selectedVideos)
        self.label.hide()
        self.preview.show()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag-enter event."""
        if not self.isEnabled:
            return

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        if not self.isEnabled:
            return

        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.onFilesSelected(files)

    def mousePressEvent(self, event):
        """Open file dialog when the drag-drop area is clicked."""
        if not self.isEnabled:
            return

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov)")
        if dialog.exec():
            self.onFilesSelected(dialog.selectedFiles())

    def onFilesSelected(self, files):
        """Handle the selected files."""

        def isVideoFile(file):
            fmt = os.path.splitext(file)[1]
            return fmt.lower() in SUPPORTED_VIDEO_FORMATS and os.path.isfile(file)

        files = [f for f in files if isVideoFile(f)][: self.num_max_videos]
        if len(files) >= self.min_num_videos:
            self.label.hide()
            self.onVideosSelected(files)
        else:
            self.label.setText(f"Select at least {self.min_num_videos} videos")
            self.label.show()
