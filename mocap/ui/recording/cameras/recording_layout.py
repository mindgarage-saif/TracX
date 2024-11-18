import logging
import os

from PyQt6.QtWidgets import QFrame, QGridLayout, QSizePolicy, QVBoxLayout, QWidget

from mocap.constants import APP_ASSETS
from mocap.ui.common import CameraView, EmptyState

from .control_panel import ControlPanel
from .controller_widget import ControllerWidget

logger = logging.getLogger(__name__)


class RecordingLayout(QFrame):
    def __init__(
        self,
        parent,
        on_frame_fn=None,
        cameras=None,
    ):
        super().__init__(parent)
        self.statusBar = parent.statusBar
        self.on_frame_fn = on_frame_fn
        self.cameras = cameras or []
        self.controller = ControllerWidget()
        self.controller.on_frame_fn = self.on_frame_fn

        self.setObjectName("RecordingLayout")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)

        # Placeholder label for "No Cameras Selected"
        self.noCamerasLabel = EmptyState(
            self,
            os.path.join(APP_ASSETS, "empty-state", "no-camera-selected.png"),
            "No Cameras Selected",
            size=512,
        )
        self.noCamerasLabel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.innerLayout.addWidget(self.noCamerasLabel)

        # Grid layout for webcam views
        self.gridWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.gridWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(16)
        self.gridWidget.setLayout(self.gridLayout)
        self.innerLayout.addWidget(self.gridWidget)
        self.gridWidget.hide()

        self.cam_views = []

        # Create the control panel, add after the camera grid
        self.controlPanel = ControlPanel(self.controller, parent=parent)
        self.innerLayout.addWidget(self.controlPanel)

        # If cameras are provided at initialization, populate the grid
        self.set_cameras(self.cameras)

    def set_cameras(self, cameras):
        """Sets the cameras dynamically and creates the grid layout."""
        camera_ids = [camera["id"] for camera in cameras]
        # Clear any existing cameras or grid layout
        self.clear_camera_grid()

        # Hide the "No Cameras Selected" label if cameras are available
        if camera_ids:
            self.noCamerasLabel.hide()
            self.gridWidget.show()
            self.controlPanel.show()
        else:
            self.noCamerasLabel.show()
            self.gridWidget.hide()
            self.controlPanel.hide()
            return

        num_cameras = min(len(camera_ids), 10)
        camera_ids = camera_ids[:num_cameras]

        max_cam_w = self.width()
        max_cam_h = self.parent().height() - 48
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

        size = cam_h, cam_w

        # Determine the grid size dynamically
        rows = int((num_cameras**0.5) + 0.5)  # Round up for rows
        cols = (num_cameras // rows) + (
            num_cameras % rows > 0
        )  # Calculate the number of columns needed

        # Add camera views to the grid layout
        for i in range(num_cameras):
            row = i // cols
            col = i % cols
            cam_h_ = size[0] // rows
            cam_w_ = size[1] // cols

            cam_view = CameraView((cam_h_, cam_w_), flip=True)
            cam_view.setFixedHeight(cam_h_ - 16)  # Adjust height for grid
            cam_view.setFixedWidth(cam_w_ - 16)  # Adjust width for grid
            self.gridLayout.addWidget(cam_view, row, col)
            self.cam_views.append(cam_view)

            # Connect the camera to the controller
            self.controller.add_source(camera_ids.pop(0), cam_view)

        # Add the grid layout to the inner layout
        self.innerLayout.insertLayout(1, self.gridLayout)
        self.controller.initialize()

    def clear_camera_grid(self):
        """Clears the camera grid and camera views."""
        for cam_view in self.cam_views:
            self.gridLayout.removeWidget(cam_view)
            cam_view.deleteLater()
        self.cam_views.clear()

    def onStop(self):
        """Stop camera controller."""
        self.controlPanel.onStop()
