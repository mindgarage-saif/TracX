from PyQt6.QtWidgets import QFrame, QSizePolicy, QTabWidget, QVBoxLayout, QWidget

from .camera_selector import CameraSelector
from .execute_button import Execute_button
from .inferencer_settings import InferencerSettings
from .setting_store import Info_storage
from .upload_layout import UploadLayout
from .visualizer_settings import VisualizerSettings


class Sidebar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("Sidebar")

        # Create an inner layout
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(16)

        # Create a tab bar for the sidebar
        self.tabBar = QTabWidget(self)

        # Add the tabs to the QTabWidget
        self.recordTab = QWidget()
        self.tabBar.addTab(self.recordTab, "Recording")
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
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(cameras)
        self.recordTab.setLayout(layout)

    def uploadTabUI(self):
        layout = QVBoxLayout()
        info_storage = Info_storage()
        label = UploadLayout(self, info_storage)
        layout.addWidget(label)

        # Inferencer and visualizer settings
        visualizerSettings = VisualizerSettings(self, info_storage)
        inferencerSettings = InferencerSettings(self, info_storage)
        motion_estimation = Execute_button(self, info_storage)

        # Let layouts handle the dynamic sizing
        visualizerSettings.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        inferencerSettings.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )

        # Add widgets to the layout
        layout.addWidget(visualizerSettings)
        layout.addWidget(inferencerSettings)
        layout.addWidget(motion_estimation)
        layout.addStretch()
        self.uploadTab.setLayout(layout)

    def setCamerasSelectedCallback(self, callback):
        self.onCamerasSelected = callback

    def handleCamerasSelected(self, cameras):
        if self.onCamerasSelected:
            self.onCamerasSelected(cameras)
