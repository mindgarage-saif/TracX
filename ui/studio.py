import logging
import signal
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplashScreen,
    QWidget,
)

from .content import Content
from .sidebar import Sidebar

logger = logging.getLogger(__name__)


class StudioWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setUnifiedTitleAndToolBarOnMac(True)

        # Compute initial screen size and window position
        screen = QApplication.desktop().screenGeometry()
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
            #CentralWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #091a40, stop:1 #6A004E);
                color: white;
            }
            QStatusBar {
                width: 100%;
                background: black;
                color: white;
            }
        """
        )

        # Central widget
        central_widget = QWidget(self)
        height -= 20
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        central_widget.setFixedSize(width, height)

        # Layout
        window = QHBoxLayout(central_widget)
        window.setContentsMargins(16, 16, 16, 16)
        window.setSpacing(0)
        self.content = Content(self)
        self.sidebar = Sidebar(self)
        self.sidebar.inferencerSettings.setModelSelectedCallback(
            self.content.change_model
        )
        self.sidebar.visualizerSettings.setCallback(
            self.content.update_visualizer_params
        )

        window.addWidget(self.sidebar)
        window.addWidget(self.content)

    def confirmExit(self):
        if QMessageBox.question(
            self,
            'PocketPose Studio',
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        ) == QMessageBox.Yes:
            self.content.webcam_layout.controlPanel.onStop()
            return True
        else:
            return False

    def closeEvent(self, event):
        if self.confirmExit():
            event.accept()
        else:
            event.ignore()


class Studio(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.title = "PocketPose Studio"

    def sigint_handler(self, *args):
        """Handler for the SIGINT signal."""
        sys.stderr.write('\r')
        if self.window.confirmExit():
            self.quit()

    def run(self):
        # Show splash screen
        pixmap = QPixmap("assets/splash.png")
        splash = QSplashScreen(pixmap)
        splash.show()
        self.processEvents()

        # Show the main window
        self.window = StudioWindow(title=self.title)
        self.window.show()
        splash.finish(self.window)
        signal.signal(signal.SIGINT, self.sigint_handler)
        sys.exit(self.exec_())
