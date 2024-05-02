import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QSplashScreen
from PyQt5.QtGui import QPixmap

from .sidebar import Sidebar
from .content import Content


class StudioWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setUnifiedTitleAndToolBarOnMac(True)

        # Compute initial screen size and window position
        screen = QApplication.desktop().screenGeometry()
        screen_width, screen_height = screen.width(), screen.height()

        # Correct aspect ratio of window size (4:3) and ensure it does not exceed screen size
        if screen_width * 3 > screen_height * 4:  # Wide screen
            width = screen_height * 4 // 3
            height = screen_height
        else:  # Tall screen
            width = screen_width
            height = screen_width * 3 // 4

        # Scale the window size to 90% of the screen size
        width = int(width * 0.9)
        height = int(height * 0.9)

        # Create a status bar
        self.statusBar().showMessage("Ready")

        # Set window size and move to center
        self.setFixedSize(width, height)
        position_x = (screen_width - width) // 2
        position_y = (screen_height - height) // 2
        self.move(position_x, position_y)

        self.setStyleSheet("""
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
        """)

        # Central widget
        central_widget = QWidget(self)
        height -= 20
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        central_widget.setFixedSize(width, height)
        print("Window size:", width, height)
        print("Screen size:", screen_width, screen_height)
        print("Position:", position_x, position_y)
        print("Central widget size:", central_widget.width(), central_widget.height())

        # # Create a toolbar with menu items
        # toolbar = QToolBar(self)
        # toolbar.setStyleSheet("color: black;")
        # toolbar.addAction("File")
        # toolbar.addAction("Edit")
        # toolbar.addAction("View")
        # toolbar.addAction("Help")
        # self.addToolBar(toolbar)

        # Layout
        window = QHBoxLayout(central_widget)
        window.setContentsMargins(16, 16, 16, 16)
        window.setSpacing(0)
        self.content = Content(self)
        self.sidebar = Sidebar(self)
        self.sidebar.inferencerSettings.setModelSelectedCallback(self.content.change_model)
        self.sidebar.visualizerSettings.setCallback(self.content.update_visualizer_params)

        print("Sidebar size:", self.sidebar.width(), self.sidebar.height())
        print("Content size:", self.content.width(), self.content.height())

        window.addWidget(self.sidebar)
        window.addWidget(self.content)
            
    def closeEvent(self, event):
        self.content.webcam_layout.controlPanel.onStop()


class Studio(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.title = "PocketPose Studio"

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
        sys.exit(self.exec_())
