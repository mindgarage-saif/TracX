import logging
import os

import cv2
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QVBoxLayout

from ...recording import CameraController
from .camera_view import CameraView
from .control_panel import ControlPanel

logger = logging.getLogger(__name__)

# Maximum number of cameras supported
MAX_CAMERAS = 10


class WebcamLayout(QFrame):
    def __init__(
        self,
        parent,
        parentWidth,
        on_frame_fn,
    ):
        super().__init__(parent)
        self.statusBar = parent.statusBar

        max_cam_w = parentWidth
        max_cam_h = parent.height() - 48
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

        self.setObjectName("WebcamLayout")
        self.setFixedWidth(parentWidth)
        self.setStyleSheet(
            """
            #WebcamLayout {
                background-color: black;
                border: 1px solid #0D47A1;
                border-radius: 8px;
                padding: 4px;
                color: #0D47A1;
            }
                           
            QPushButton {
                background-color: white;
                border: 1px solid #0D47A1;
                border-radius: 8px;
                padding: 4px;
                color: #0D47A1;
            }
        """
        )

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)

        # Create a grid layout for individual WebcamLayouts
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(16)

        # Detect available cameras and dynamically adjust the grid size
        camera_ids = self.get_available_cameras()
        num_cameras = min(len(camera_ids), MAX_CAMERAS)
        self.cam_views = []

        # Determine the grid size dynamically
        rows = int((num_cameras**0.5) + 0.5)  # Round up for rows
        cols = (num_cameras // rows) + (
            num_cameras % rows > 0
        )  # Calculate the number of columns needed

        # Create and add the webcam views to the grid layout
        self.camera = CameraController()
        self.camera.on_frame_fn = on_frame_fn
        for i in range(num_cameras):
            row = i // cols
            col = i % cols

            cam_h_ = size[0] // rows
            cam_w_ = size[1] // cols
            cam_view = CameraView((cam_h_, cam_w_), flip=True)
            cam_view.setFixedHeight(
                cam_h_ - 16
            )  # Adjust height for grid
            cam_view.setFixedWidth(
                cam_w_ - 16
            )  # Adjust width for grid
            self.gridLayout.addWidget(cam_view, row, col)
            self.cam_views.append(cam_view)
            self.camera.add_source(camera_ids.pop(0), cam_view)

        self.innerLayout.addLayout(self.gridLayout)
        self.innerLayout.addStretch()

        # Create the control panel
        self.controlPanel = ControlPanel(self.camera, parent=parent)
        self.innerLayout.addWidget(self.controlPanel)

    def check_camera(self, camera_id):
        if isinstance(camera_id, int) or camera_id.isdigit():
            camera = cv2.VideoCapture(int(camera_id))
            if not camera.isOpened():
                return False
            camera.release()
            return True

        if isinstance(camera_id, str):
            return os.path.exists(camera_id)

        return False

    def get_available_cameras(self):
        cameras = []
        for i in range(MAX_CAMERAS):
            if self.check_camera(i):
                cameras.append(i)

        return cameras
