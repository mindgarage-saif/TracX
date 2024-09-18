import os
import cv2
import logging

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QGridLayout

from ...recording import Camera
from .camera_view import CameraView
from .control_panel import ControlPanel

logger = logging.getLogger(__name__)

# Maximum number of cameras supported
MAX_CAMERAS = 10


class WebcamLayout(QFrame):
    def __init__(
            self, 
            parent, 
            on_frame_fn, 
        ):
        super().__init__(parent)
        self.statusBar = parent.statusBar
        aspect_ratio = 4 / 3
        cam_w = parent.width() - 48
        cam_h = int(cam_w / aspect_ratio)
        size = cam_h, cam_w

        self.setObjectName("WebcamLayout")
        self.setFixedWidth(size[1])
        self.setStyleSheet(
            """
            #WebcamLayout {
                background-color: rgba(0, 0, 0, 0.5);
                border: 1px solid whitesmoke;
                border-radius: 8px;
                padding: 4px;
                color: white;
            }
                           
            QPushButton {
                background-color: white;
                border: 1px solid black;
                border-radius: 8px;
                padding: 4px;
                color: black;
            }
        """
        )

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)

        # Create a grid layout for individual WebcamLayouts
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(16, 16, 16, 16)
        self.gridLayout.setSpacing(8)

        # Detect available cameras and dynamically adjust the grid size
        camera_ids = self.get_available_cameras()
        num_cameras = min(len(camera_ids), MAX_CAMERAS)
        self.cam_views = []

        # Determine the grid size dynamically
        rows = int((num_cameras ** 0.5) + 0.5)  # Round up for rows
        cols = (num_cameras // rows) + (num_cameras % rows > 0)  # Calculate the number of columns needed

        # Create and add the webcam views to the grid layout
        self.camera = Camera()
        self.camera.on_frame_fn = on_frame_fn
        for i in range(num_cameras):
            row = i // cols
            col = i % cols

            cam_h_ = size[0] // rows
            cam_w_ = size[1] // cols
            cam_view = CameraView((cam_h_, cam_w_), flip=True)
            cam_view.setFixedHeight((parent.height() - 48) // rows)  # Adjust height for grid
            cam_view.setFixedWidth((parent.width() - 48) // cols)  # Adjust width for grid
            self.gridLayout.addWidget(cam_view, row, col)
            self.cam_views.append(cam_view)
            self.camera.add_source(camera_ids.pop(0), cam_view)

        self.innerLayout.addLayout(self.gridLayout)
        self.innerLayout.addStretch()

        # Create the control panel
        self.controlPanel = ControlPanel(self.camera, parent=self)
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
