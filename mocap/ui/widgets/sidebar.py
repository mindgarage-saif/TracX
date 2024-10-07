from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
)

from mocap.ui.config.constants import PAD_X, PAD_Y

from .camera_selector import CameraSelector
from .dialogs import CreateExperimentDialog
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
        self.innerLayout.setSpacing(PAD_Y)

        # Create a tab bar for the sidebar
        self.tabBar = QTabWidget(self)

        self.uploadTab = QLabel()
        self.tabBar.addTab(self.uploadTab, "Motion Estimation")
        self.uploadTabUI()

        # Add the tabs to the QTabWidget
        self.recordTab = QLabel()
        self.tabBar.addTab(self.recordTab, "Recording")
        self.recordTabUI()

        # Add the tab widget to the layout
        self.innerLayout.addWidget(self.tabBar)
        self.setLayout(self.innerLayout)

        # Attach the tab change event
        self.tabBar.currentChanged.connect(self.handleTabSelected)

    def handleTabSelected(self, index):
        if index == 1:
            self.experimentList.refresh()

        if self.onTabSelected:
            self.onTabSelected(index)

    def handleExperimentSelected(self, experiment):
        self.onExperimentSelected(experiment)

    def recordTabUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        layout.setSpacing(PAD_Y)

        cameras = CameraSelector(self)
        cameras.setCameraSelectedCallback(self.handleCamerasSelected)
        cameras.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(cameras)
        self.recordTab.setLayout(layout)

    def uploadTabUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        layout.setSpacing(0)

        # Add a title to the page
        title = QLabel("Select Experiment")
        title.setProperty("class", "h3")
        layout.addWidget(title)

        # Add instructions
        instructions = QLabel(
            "Select an experiment to start motion estimation or create a new one."
        )
        instructions.setProperty("class", "body")
        instructions.setWordWrap(True)
        instructions.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        layout.addWidget(instructions)
        layout.addSpacing(PAD_Y)

        self.experimentList = ExperimentList(self)
        self.experimentList.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        self.experimentList.onItemSelected = self.handleExperimentSelected
        layout.addWidget(self.experimentList)
        layout.addSpacing(PAD_Y)

        createButton = QPushButton("New Experiment")
        createButton.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        createButton.clicked.connect(self.createExperiment)
        layout.addWidget(createButton)

        self.uploadTab.setLayout(layout)

    def createExperiment(self):
        dialog = CreateExperimentDialog(self)
        dialog.setMinimumSize(300, 100)
        dialog.setModal(True)
        dialog.exec()

        self.experimentList.refresh()

    def setCamerasSelectedCallback(self, callback):
        self.onCamerasSelected = callback

    def handleCamerasSelected(self, cameras):
        if self.onCamerasSelected:
            self.onCamerasSelected(cameras)
