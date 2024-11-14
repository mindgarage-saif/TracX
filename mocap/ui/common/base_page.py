import logging

from PyQt6.QtWidgets import QHBoxLayout, QMessageBox, QWidget

from mocap.ui.styles import PAD_X

logger = logging.getLogger(__name__)


class BasePage(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.statusBar = parent.statusBar()
        self.sidebar = parent.sidebar

        # Create an inner layout for the frame
        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
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
