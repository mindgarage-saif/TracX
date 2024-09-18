from PyQt6.QtWidgets import (
    QWidget,
)

from .base import BasePage
from ..config.constants import PAD_X
from ..widgets import WebcamLayout


class RecordPage(BasePage):
    def __init__(self, context: QWidget, parent: QWidget) -> None:
        super().__init__(context, parent)

        self.innerLayout.setContentsMargins(8, 0, 8, 0)

        # Create the webcam view
        webcam_width = self.width() - PAD_X * 2
        self.webcam_layout = WebcamLayout(
            self,
            webcam_width,
            self.update_frame,
        )
        self.webcam_layout.setFixedHeight(parent.pageHeight())
        self.innerLayout.addWidget(self.webcam_layout)

        # Initialize model
        self.available_models = []

        # Add stretch to push the webcam feed to the top
        self.innerLayout.addStretch()

    def update_frame(self, frame):
        return frame
