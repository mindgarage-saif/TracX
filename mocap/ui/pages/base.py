import logging

from PyQt6.QtWidgets import QHBoxLayout, QWidget

logger = logging.getLogger(__name__)


class BasePage(QWidget):
    def __init__(self, context: QWidget, parent: QWidget) -> None:
        super().__init__(parent)
        self.context = context
        self.statusBar = parent.statusBar()
        self.setMinimumWidth(parent.width())
        self.setMinimumHeight(parent.pageHeight())

        # Create an inner layout for the frame
        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(8)

    def log(self, message: str) -> None:
        """
        Logs a message to the console.
        """
        logger.info(message)
        self.statusBar.showMessage(message)

    def onStop(self):
        pass
