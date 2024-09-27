from PyQt6.QtWidgets import QWidget

from ..widgets import Sidebar
from .base import BasePage


class ProcessingPage(BasePage):
    def __init__(self, context: QWidget, parent: QWidget) -> None:
        super().__init__(context, parent)

        # Create a sidebar
        self.sidebar = Sidebar(self)
        self.innerLayout.addWidget(self.sidebar)

        # Add stretch to push the webcam feed to the top
        self.innerLayout.addStretch()
