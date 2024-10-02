from PyQt6.QtWidgets import (
    QFrame,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .camera_selector import CameraSelector
from .experiment_list import ExperimentList


class Sidebar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("Sidebar")

        # Callbacks.
        self.onCamerasSelected = None
        self.onExperimentSelected = lambda x: None
        self.onTabSelected = None

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

        # Attach the tab change event
        self.tabBar.currentChanged.connect(self.handleTabSelected)

    def handleTabSelected(self, index):
        if self.onTabSelected:
            self.onTabSelected(index)

    def handleExperimentSelected(self, experiment):
        self.onExperimentSelected(experiment)

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

        experimentList = ExperimentList(self)
        experimentList.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        experimentList.callback = self.handleExperimentSelected
        layout.addWidget(experimentList)

        createButton = QPushButton("Create Experiment")
        createButton.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(createButton)

        self.uploadTab.setLayout(layout)

    def setCamerasSelectedCallback(self, callback):
        self.onCamerasSelected = callback

    def handleCamerasSelected(self, cameras):
        if self.onCamerasSelected:
            self.onCamerasSelected(cameras)
