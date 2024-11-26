import logging
import os

from PyQt6.QtWidgets import QFrame, QGridLayout, QSizePolicy, QVBoxLayout, QWidget

from TracX.constants import APP_ASSETS
from TracX.recording.sync_video_player import SynchronizedVideoPlayer
from TracX.ui.common import CameraView, EmptyState

from .record_layout_controller import RecordLayoutController

logger = logging.getLogger(__name__)


class MultiCameraRecordUI(QFrame):
    def __init__(
        self,
        parent,
    ):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)

        # Create an empty state for when no cameras are selected
        self.emptyState = EmptyState(
            self,
            os.path.join(APP_ASSETS, "empty-state", "no-camera-selected.png"),
            "No Cameras Selected",
            size=512,
        )
        self.emptyState.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.innerLayout.addWidget(self.emptyState)

        # Grid layout for video views
        self.gridWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.gridWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(16)
        self.innerLayout.addWidget(self.gridWidget)

        # Create the video player
        self.player = SynchronizedVideoPlayer()

        # Create the preview widget
        self.preview = []

        # Create the controller
        self.controller = RecordLayoutController(self.player, parent=parent)
        self.innerLayout.addWidget(self.controller)

        # Show the empty state
        self.showEmpty()

    def setSource(self, source):
        """Sets the cameras dynamically and creates the grid layout."""
        self.controller.setEnabled(source is not None)
        if not source:
            self.controller.clear()
            self.controller.setEnabled(False)
            self.showEmpty()
            return

        # Create a preview for the cameras
        cam_w = self.size().width()
        cam_h = self.size().height() - 48
        cam_w = max(cam_w, 800)
        cam_h = max(cam_h, 600)
        self.createPreview(source, (cam_w, cam_h))

        # Enable the controller
        self.controller.setEnabled(True)

    def resizeEvent(self, event):
        max_cam_w = self.size().width()
        max_cam_h = self.size().height() - 48
        aspect_ratio = 4 / 3
        current_aspect_ratio = max_cam_w / max_cam_h

        if current_aspect_ratio > aspect_ratio:
            cam_h = max_cam_h
            cam_w = int(cam_h * aspect_ratio)
            if cam_w > max_cam_w:
                cam_w = max_cam_w
                cam_h = int(cam_w / aspect_ratio)
        else:
            cam_w = max_cam_w
            cam_h = int(cam_w / aspect_ratio)
            if cam_h > max_cam_h:
                cam_h = max_cam_h
                cam_w = int(cam_h * aspect_ratio)

        self.resizePreview((cam_w, cam_h))

    def createPreview(self, source, preview_size):
        # Clear any existing cameras or grid layout
        self.clear()

        camera_ids = [camera["id"] for camera in source]
        num_cameras = min(len(camera_ids), 10)
        camera_ids = camera_ids[:num_cameras]
        if num_cameras == 0:
            return

        # Determine the grid size dynamically
        rows = int((num_cameras**0.5) + 0.5)
        cols = (num_cameras // rows) + (num_cameras % rows > 0)

        # Add camera views to the grid layout
        sources = []
        for i in range(num_cameras):
            row = i // cols
            col = i % cols
            cam_h_ = preview_size[1] // rows
            cam_w_ = preview_size[0] // cols

            view = CameraView((cam_h_, cam_w_), flip=False)
            view.setFixedHeight(cam_h_ - 16)  # Adjust height for grid
            view.setFixedWidth(cam_w_ - 16)  # Adjust width for grid
            self.gridLayout.addWidget(view, row, col)
            self.preview.append(view)

            # Connect the camera to the controller
            sources.append((camera_ids.pop(0), view))

        self.player.setSources(sources)

        # Hide the empty state
        self.hideEmpty()

    def resizePreview(self, preview_size):
        num_cameras = len(self.preview)
        if num_cameras == 0:
            return

        rows = int((num_cameras**0.5) + 0.5)
        cols = (num_cameras // rows) + (num_cameras % rows > 0)
        for view in enumerate(self.preview):
            cam_h_ = (preview_size[1] // rows) - 16
            cam_w_ = (preview_size[0] // cols) - 16
            view.setFixedSize(cam_w_, cam_h_)

    def clear(self):
        """Clears the camera grid and camera views."""
        for view in self.preview:
            self.gridLayout.removeWidget(view)
            view.deleteLater()
        self.preview.clear()

    def stop(self):
        """Stop camera controller."""
        self.player.release()
        self.controller.reset()

    def showEmpty(self):
        """Show the empty state."""
        self.gridWidget.hide()
        self.controller.clear()
        self.emptyState.show()

    def hideEmpty(self):
        """Hide the empty state."""
        self.gridWidget.show()
        self.emptyState.hide()
