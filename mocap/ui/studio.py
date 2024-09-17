import logging
import time

from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from .widgets import Sidebar, WebcamLayout

logger = logging.getLogger(__name__)


class Content(QFrame):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.statusBar = parent.statusBar()
        self.setFixedWidth(int(parent.width() * 0.7))
        self.setFixedHeight(parent.height() - 20)
        self.setStyleSheet(
            """
        """
        )

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(16, 16, 16, 16)
        self.innerLayout.setSpacing(8)

        # Create the webcam view
        self.webcam_layout = WebcamLayout(
            self,
            self.update_frame,
        )
        self.webcam_layout.setFixedHeight(self.height() - 52)
        self.innerLayout.addWidget(self.webcam_layout)

        # Initialize model
        self.available_models = []

        # Add stretch to push the webcam feed to the top
        self.innerLayout.addStretch()

    def change_model(self, model_name):
        self.current_model = model_name
        self.frame_count = 0
        self.start_time = time.time()

    def update_visualizer_params(self, radius, thickness, kpt_thr, draw_bbox):
        self.visualizer.radius = radius
        self.visualizer.thickness = thickness
        self.visualizer.kpt_thr = kpt_thr
        self.visualizer.draw_bbox = draw_bbox

    def update_frame(self, frame, vis, first_frame=False, is_video=False):
        return frame


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
        # self.sidebar.inferencerSettings.setModelSelectedCallback(
        #     self.content.change_model
        # )
        # self.sidebar.visualizerSettings.setCallback(
        #     self.content.update_visualizer_params
        # )

        window.addWidget(self.sidebar)
        window.addWidget(self.content)

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
            self.content.webcam_layout.controlPanel.onStop()
            return True
        else:
            return False

    def closeEvent(self, event):
        if self.confirmExit():
            event.accept()
        else:
            event.ignore()
