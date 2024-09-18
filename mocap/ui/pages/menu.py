from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
)

from .base import BasePage


class MenuPage(BasePage):
    def __init__(self, context: QWidget, parent: QWidget) -> None:
        super().__init__(context, parent)

        # Add two buttons to the menu
        self.recordButton = QPushButton("Record")
        self.uploadButton = QPushButton("Upload")
        self.innerLayout.addWidget(self.recordButton)
        self.innerLayout.addWidget(self.uploadButton)

        # Connect the buttons to their respective functions
        self.recordButton.clicked.connect(self.record)
        self.uploadButton.clicked.connect(self.upload)

        # Add stretch to push the webcam feed to the top
        self.innerLayout.addStretch()

    def record(self):
        self.context.changePage("record")

    def upload(self):
        self.context.changePage("upload")
