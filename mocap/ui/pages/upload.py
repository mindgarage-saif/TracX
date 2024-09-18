from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
)

from .base import BasePage


class UploadPage(BasePage):
    def __init__(self, context: QWidget, parent: QWidget) -> None:
        super().__init__(context, parent)

        # Add two buttons to the menu
        self.videosButton = QPushButton("Select Videos")
        self.calibrationButton = QPushButton("Select Calibration File")
        self.innerLayout.addWidget(self.videosButton)
        self.innerLayout.addWidget(self.calibrationButton)

        # Connect the buttons to their respective functions
        self.videosButton.clicked.connect(self.selectVideos)
        self.calibrationButton.clicked.connect(self.selectCalibrationFile)

        # Add stretch to push the webcam feed to the top
        self.innerLayout.addStretch()

    def selectVideos(self):
        self.log("Video select button clicked")

    def selectCalibrationFile(self):
        self.log("Calibration file select button clicked")
        
