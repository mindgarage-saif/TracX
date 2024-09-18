import logging

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QMainWindow,
    QMessageBox,
    QWidget,
    QFrame,
)

from .config.constants import PAD_Y
from .pages import MenuPage, RecordPage, UploadPage
from .widgets import AppBar

logger = logging.getLogger(__name__)


class StudioWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setUnifiedTitleAndToolBarOnMac(True)

        # Compute initial screen size and window position
        screen = QApplication.primaryScreen().geometry()
        screen_width, screen_height = screen.width(), screen.height()

        # Correct aspect ratio of window size (4:3) and ensure it does not exceed screen size
        aspect = 1.33  # 4:3
        if screen_width * 3 > screen_height * 4:  # Wide screen
            width = int(screen_height * aspect)
            height = screen_height
        else:  # Tall screen
            width = screen_width
            height = screen_width // aspect

        # Scale the window size to 92% of the screen size
        width = int(width * 0.92)
        height = int(height * 0.92)

        # Create a status bar
        self.statusBar().showMessage("Ready")

        # Set window size and move to center
        self.setFixedSize(width, height)
        position_x = (screen_width - width) // 2
        position_y = (screen_height - height) // 2
        self.move(position_x, position_y)

        self.setStyleSheet(
            """
            QStatusBar {
                width: 100%;
                background: #0D47A1;
                color: #E3F2FD;
            }

            #AppBar {
                background: #1976D2;
                color: #0D47A1;
            }

            #PageFrame {
                background: #E3F2FD;
                color: #0D47A1;
            }

            #CentralWidget {
                background: #0D47A1;
                color: #E3F2FD;
            }
        """
        )

        # Central widget
        central_widget = QWidget(self)
        height -= 20
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        central_widget.setFixedSize(width, height)
        central_widget.setContentsMargins(0, 0, 0, 0)

        # Layout
        window = QVBoxLayout(central_widget)
        window.setContentsMargins(0, 0, 0, 0)
        window.setSpacing(0)

        # Create app bar
        self.appbar = AppBar(self, height=32)
        self.appbar.setObjectName("AppBar")
        window.addWidget(self.appbar)

        # Add pages
        self.pages = {
            "record": RecordPage,
            "menu": MenuPage,
            "upload": UploadPage,
        }
        self.pageFrame = QFrame(self)
        self.pageFrame.setObjectName("PageFrame")
        self.pageFrame.setFixedSize(self.width(),
                                    self.height() - self.appbar.height() - PAD_Y * 2 + 4)
        self.pageFrame.layout = QHBoxLayout(self.pageFrame)
        self.pageFrame.setLayout(self.pageFrame.layout)
        window.addWidget(self.pageFrame)

        # Set the initial page
        self.page = None
        self.pageHistory = []
        self.changePage("menu")

    def changePage(self, page):
        # Remove existing page
        if self.page is not None:
            self.pageFrame.layout.removeWidget(self.page)
            self.page.deleteLater()
            self.page = None

        # Add page inside the frame
        self.page = self.pages[page](self, self)
        self.pageFrame.layout.addWidget(self.page)
        
        # Add to history
        self.pageHistory.append(page)

    def back(self):
        if len(self.pageHistory) > 1:
            self.pageHistory.pop()
            self.changePage(self.pageHistory[-1])

    def pageHeight(self):
        return self.pageFrame.height() - PAD_Y * 2

    def confirmExit(self):
        if (
            QMessageBox.question(
                self,
                "PocketPose Studio",
                "Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            return True
        else:
            return False

    def closeEvent(self, event):
        if self.confirmExit():
            event.accept()
        else:
            event.ignore()
