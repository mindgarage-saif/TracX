import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from TracX.constants import APP_NAME, FEATURE_RECORDING_ENABLED
from TracX.ui.analysis import AnalysisPage, AnalysisTab
from TracX.ui.common import AppBar, TabbedArea
from TracX.ui.recording import RecordPage, RecordTab
from TracX.ui.styles import PAD_X, PAD_Y

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
        aspect = 16 / 9
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
        self.setMinimumSize(width, height)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        position_x = (screen_width - width) // 2
        position_y = (screen_height - height) // 2
        self.move(position_x, position_y)

        # Central widget
        central_widget = QWidget(self)
        height -= 32
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        central_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        central_widget.setContentsMargins(0, 0, 0, 0)

        # Layout
        window = QVBoxLayout(central_widget)
        window.setContentsMargins(0, 0, 0, 0)
        window.setSpacing(0)

        # Create app bar
        self.appbar = AppBar(self, height=48)
        self.appbar.innerLayout.setContentsMargins(PAD_X, 0, PAD_X, 0)
        window.addWidget(self.appbar)

        # Studio frame
        self.studioFrame = QWidget(self)
        self.studioFrame.setObjectName("StudioFrame")
        self.studioFrame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.studioFrame.layout = QHBoxLayout(self.studioFrame)
        self.studioFrame.layout.setContentsMargins(0, 0, 0, 0)
        self.studioFrame.layout.setSpacing(0)
        window.addWidget(self.studioFrame)

        # Create the sidebar
        sidebarWidth = int(width * 0.2)
        self.sidebar = TabbedArea(self.studioFrame)
        self.sidebar.layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar.setFixedWidth(int(sidebarWidth))
        self.sidebar.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        self.studioFrame.layout.addWidget(self.sidebar)

        # Add pages
        self.pages = {}
        self.analysisTab = AnalysisTab(self.sidebar)
        self.sidebar.addTab(self.analysisTab)
        self.pages["process"] = AnalysisPage

        if FEATURE_RECORDING_ENABLED:
            self.recordTab = RecordTab(self.sidebar)
            self.sidebar.addTab(self.recordTab)
            self.pages["record"] = RecordPage

        self.pageFrame = QFrame(self.studioFrame)
        self.pageFrame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.pageFrame.layout = QHBoxLayout(self.pageFrame)
        self.pageFrame.layout.setContentsMargins(0, 0, 0, 0)
        self.pageFrame.layout.setSpacing(0)
        self.pageFrame.setLayout(self.pageFrame.layout)
        self.studioFrame.layout.addWidget(self.pageFrame)

        pages = list(self.pages.keys())
        self.sidebar.selected.connect(lambda index: self.changePage(pages[index]))

        # Set the initial page
        self.page = None
        self.pageHistory = []
        self.changePage(pages[0])

    def changePage(self, page, *args, **kwagrs):
        # Remove existing page
        if self.page is not None:
            self.page.onStop()
            self.pageFrame.layout.removeWidget(self.page)
            self.page.deleteLater()
            self.page = None

        # Add page inside the frame
        self.page = self.pages[page](self, *args, **kwagrs)
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
        return (
            QMessageBox.question(
                self,
                APP_NAME,
                "Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        )

    def closeEvent(self, event):
        if self.confirmExit():
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.close()

        if e.key() == Qt.Key.Key_Backspace or e.key() == Qt.Key.Key_B:
            self.back()

        if e.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
