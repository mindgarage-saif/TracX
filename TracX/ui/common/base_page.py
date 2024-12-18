import logging

from PyQt6.QtWidgets import QHBoxLayout, QMessageBox, QWidget

from TracX.ui.styles import PAD_X, PAD_Y

logger = logging.getLogger(__name__)


class BasePage(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.statusBar = parent.statusBar()

        # Create an inner layout for the frame
        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.innerLayout.setSpacing(PAD_X)

    def log(self, message: str) -> None:
        """Logs a message to the console."""
        logger.info(message)
        self.statusBar.showMessage(message)

    def onStop(self):
        pass

    def showMessage(self, title: str, message: str, icon: QMessageBox.Icon):
        popup = QMessageBox(self)
        popup.setIcon(icon)
        popup.setWindowTitle(title)
        popup.setText(message)
        popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        popup.exec()

    def showAlert(self, message: str, title: str = "Alert"):
        self.showMessage(title, message, QMessageBox.Icon.Critical)

    def showWarning(self, message: str, title: str = "Warning"):
        self.showMessage(title, message, QMessageBox.Icon.Warning)
