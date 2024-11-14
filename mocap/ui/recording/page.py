from PyQt6.QtWidgets import (
    QSizePolicy,
    QWidget,
)

from mocap.ui.common import BasePage

from .cameras.recording_layout import RecordingLayout


class RecordPage(BasePage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        # Create the webcam view
        self.recordingLayout = RecordingLayout(
            self,
            on_frame_fn=self.process,
        )
        self.recordingLayout.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.innerLayout.addWidget(self.recordingLayout)

        # Add camera selection callback
        parent.recordTab.camerasSelected.connect(self.onCamerasSelected)

    def onCamerasSelected(self, camera_ids):
        self.recordingLayout.set_cameras(camera_ids)

    def process(self, frames):
        """Process frames from the camera system.

        Args:
            frames (List[ndarray]): A list of synchronized frames from the camera system.
        """
        return frames

    def onStop(self):
        self.recordingLayout.onStop()
