from PyQt6.QtWidgets import (
    QSizePolicy,
    QWidget,
)

from mocap.ui.common import BasePage

from .cameras.recording_layout import MultiCameraRecordUI


class RecordPage(BasePage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        # Create the webcam view
        self.videoCaptureLayout = MultiCameraRecordUI(self)
        self.videoCaptureLayout.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.innerLayout.addWidget(self.videoCaptureLayout)

        # Add camera selection callback
        parent.recordTab.camerasSelected.connect(self.onCamerasSelected)

    def onCamerasSelected(self, camera_ids):
        self.videoCaptureLayout.setSource(camera_ids)

    def onStop(self):
        self.videoCaptureLayout.stop()
