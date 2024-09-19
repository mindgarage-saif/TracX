from PyQt6.QtWidgets import QFrame, QSizePolicy, QTabWidget, QVBoxLayout, QWidget

from .camera_selector import CameraSelector
from .inferencer_settings import InferencerSettings
from .upload_layout import UploadLayout
from .visualizer_settings import VisualizerSettings


class Sidebar(QFrame):
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
        self.tabBar.addTab(self.recordTab, "Video Recording")
        self.recordTabUI()

        self.uploadTab = QWidget()
        self.tabBar.addTab(self.uploadTab, "Motion Estimation")
        self.uploadTabUI()

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

        # Inferencer and visualizer settings
        visualizerSettings = VisualizerSettings(self)
        inferencerSettings = InferencerSettings(self)

        # Let layouts handle the dynamic sizing
        visualizerSettings.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        inferencerSettings.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        # Add widgets to the layout
        layout.addWidget(inferencerSettings)
        layout.addWidget(visualizerSettings)
        layout.addStretch()
        self.uploadTab.setLayout(layout)

    def setCamerasSelectedCallback(self, callback):
        self.onCamerasSelected = callback

    def handleCamerasSelected(self, cameras):
        if self.onCamerasSelected:
            self.onCamerasSelected(cameras)
