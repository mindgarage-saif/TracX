from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QSizePolicy,
)

from TracX.ui.common import Tab
from TracX.ui.styles import PAD_X, PAD_Y

from .cameras.camera_selector import CameraSelector


class RecordTab(Tab):
    camerasSelected = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__("Recording", parent, Qt.Orientation.Vertical)
        self.layout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.layout.setSpacing(PAD_Y)

        # Create a camera selector
        cameras = CameraSelector(self)
        cameras.selected.connect(self.camerasSelected.emit)
        cameras.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )
        self.addWidget(cameras)
