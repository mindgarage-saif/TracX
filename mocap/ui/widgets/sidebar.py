from PyQt6.QtWidgets import QLabel, QSizePolicy, QTabWidget, QVBoxLayout, QWidget

from .camera_selector import CameraSelector
from .inferencer_settings import InferencerSettings
from .visualizer_settings import VisualizerSettings
from .upload_layout import UploadLayout


class Sidebar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Create an inner layout
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(16)

        # Create a tab bar for the sidebar
        self.tabBar = QTabWidget(self)
        self.tabBar.setStyleSheet(
            """
            QTabBar::tab {
                background-color: #2c2c2c;
                color: #ffffff;
                padding: 8px;
                font-size: 16px;
            }
            QTabBar::tab:selected {
                background-color: #3c3c3c;
            }
            """
        )

        # Add the tabs to the QTabWidget
        self.recordTab = QWidget()
        self.tabBar.addTab(self.recordTab, "1. Record")
        self.recordTabUI()

        self.uploadTab = QWidget()
        self.tabBar.addTab(self.uploadTab, "2. Upload")
        self.uploadTabUI()

        self.processTab = QWidget()
        self.tabBar.addTab(self.processTab, "3. Process")
        self.processTabUI()

        # Add the tab widget to the layout
        self.innerLayout.addWidget(self.tabBar)
        self.setLayout(self.innerLayout)

        # Callbacks.
        self.onCamerasSelected = None

    def recordTabUI(self):
        layout = QVBoxLayout()
        cameras = CameraSelector(self)
        cameras.setCameraSelectedCallback(self.handleCamerasSelected)
        cameras.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(cameras)
        self.recordTab.setLayout(layout)

    def uploadTabUI(self):
        layout = QVBoxLayout()
        label = UploadLayout(self)
        layout.addWidget(label)
        self.uploadTab.setLayout(layout)

    def processTabUI(self):
        layout = QVBoxLayout()

        # Inferencer and visualizer settings
        visualizerSettings = VisualizerSettings(self)
        inferencerSettings = InferencerSettings(self)

        # Let layouts handle the dynamic sizing
        visualizerSettings.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        inferencerSettings.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Add widgets to the layout
        layout.addWidget(inferencerSettings)
        layout.addWidget(visualizerSettings)

        self.processTab.setLayout(layout)

    def setCamerasSelectedCallback(self, callback):
        self.onCamerasSelected = callback

    def handleCamerasSelected(self, cameras):
        if self.onCamerasSelected:
            self.onCamerasSelected(cameras)
