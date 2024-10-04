from PyQt6.QtWidgets import QSizePolicy, QWidget

from ..config.constants import PAD_X
from ..widgets import RecordingLayout
from .base import BasePage


class RecordPage(BasePage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        # Create the webcam view
        webcamWidth = parent.width() - PAD_X * 5
        self.recordingLayout = RecordingLayout(
            self,
            webcamWidth,
            on_frame_fn=self.process,
        )
        self.recordingLayout.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.innerLayout.addWidget(self.recordingLayout)

        # Add camera selection callback
        # self.sidebar.setCamerasSelectedCallback(self.onCamerasSelected)

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
