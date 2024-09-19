from PyQt6.QtWidgets import QWidget

from ..config.constants import PAD_X
from ..widgets import RecordingLayout, Sidebar
from .base import BasePage


class RecordPage(BasePage):
    def __init__(self, context: QWidget, parent: QWidget) -> None:
        super().__init__(context, parent)

        self.innerLayout.setContentsMargins(8, 0, 8, 0)

        # Create the sidebar
        sidebarWidth = int(parent.width() * 0.25)
        self.sidebar = Sidebar(self)
        self.sidebar.setFixedWidth(int(sidebarWidth))
        self.sidebar.setFixedHeight(parent.pageHeight())
        self.innerLayout.addWidget(self.sidebar)

        # Create the webcam view
        webcamWidth = self.width() - sidebarWidth - PAD_X * 5
        self.recordingLayout = RecordingLayout(
            self,
            webcamWidth,
            on_frame_fn=self.process,
        )
        self.recordingLayout.setFixedHeight(parent.pageHeight())
        self.innerLayout.addWidget(self.recordingLayout)

        # Add camera selection callback
        self.sidebar.setCamerasSelectedCallback(self.onCamerasSelected)

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
