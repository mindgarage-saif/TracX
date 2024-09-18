from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QStyle,  
)

from .base import BasePage


class MenuPage(BasePage):
    def __init__(self, context: QWidget, parent: QWidget) -> None:
        super().__init__(context, parent)

        # Add two buttons to the menu
        self.recordButton = QPushButton("Record")
        self.recordButton.setProperty("class", "big_button")
        self.recordButton.setFixedSize(200, 200)

        self.uploadButton = QPushButton("Upload")
        self.uploadButton.setProperty("class", "big_button")
        self.uploadButton.setFixedSize(200, 200)

        # Calculate empty space
        emptySpace = (self.width() - 200 * 2 - 16) // 2

        # Add the buttons to the layout surrounding them with empty space
        self.innerLayout.addSpacing(emptySpace)
        self.innerLayout.addWidget(self.recordButton)
        self.innerLayout.addSpacing(16)
        self.innerLayout.addWidget(self.uploadButton)
        self.innerLayout.addSpacing(emptySpace)

        # Connect the buttons to their respective functions
        self.recordButton.clicked.connect(self.record)
        self.uploadButton.clicked.connect(self.upload)


    def record(self):
        self.context.changePage("camera_selection")

    def upload(self):
        self.context.changePage("upload")
