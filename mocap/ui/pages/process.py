from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from mocap.core import Experiment

from ..widgets.execute_button import MotionEstimationButton
from ..widgets.inferencer_settings import InferencerSettings
from ..widgets.setting_store import MotionEstimationParams
from ..widgets.upload_layout import UploadLayout
from ..widgets.visualizer_settings import VisualizerSettings
from .base import BasePage


class ProcessingPage(BasePage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        # Create an empty state layout
        self.emptyState = QWidget(self)
        self.emptyState.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.innerLayout.addWidget(self.emptyState)
        self.createEmptyStateUI()

        # Create the project details layout
        self.experimentUI = QWidget(self)
        self.experimentUI.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.innerLayout.addWidget(self.experimentUI)
        self.createExperimentUI()

        # Set the initial state
        self.emptyState.show()
        self.experimentUI.hide()
        self.experiment = None

        # Connect the sidebar event
        self.sidebar.onExperimentSelected = self.showExperiment

    def createEmptyStateUI(self):
        # Create a layout for the empty state
        emptyStateLayout = QVBoxLayout(self.emptyState)
        emptyStateLayout.setContentsMargins(0, 0, 0, 0)
        emptyStateLayout.setSpacing(0)
        self.emptyState.setLayout(emptyStateLayout)

        # Add the empty state message
        self.emptyStateMessage = QLabel("No project selected")
        self.emptyStateMessage.setObjectName("EmptyStateMessage")
        emptyStateLayout.addWidget(self.emptyStateMessage)

    def createExperimentUI(self):
        # Create a layout for the processing page
        experimentUILayout = QVBoxLayout(self.experimentUI)
        experimentUILayout.setContentsMargins(0, 0, 0, 0)
        experimentUILayout.setSpacing(0)
        self.experimentUI.setLayout(experimentUILayout)

        settings = MotionEstimationParams()

        # Inferencer and visualizer settings
        uploadUI = UploadLayout(self, settings)

        self.numVideosLabel = QLabel("Number of videos: 0")
        experimentUILayout.addWidget(self.numVideosLabel)

        motionSettings = InferencerSettings(self, settings)
        simulationSettings = VisualizerSettings(self, settings)
        motionButton = MotionEstimationButton(self, settings)

        # Let layouts handle the dynamic sizing
        simulationSettings.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        motionSettings.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )

        # Add widgets to the layout
        experimentUILayout.addWidget(uploadUI)
        experimentUILayout.addWidget(simulationSettings)
        experimentUILayout.addWidget(motionSettings)
        experimentUILayout.addWidget(motionButton)
        experimentUILayout.addStretch()

    def showExperiment(self, name):
        try:
            self.experiment = Experiment(name, create=False)
            self.log(f"Loaded experiment: {self.experiment}")

            self.numVideosLabel.setText(
                f"Number of videos: {self.experiment.num_videos}"
            )

            self.emptyState.hide()
            self.experimentUI.show()

        except Exception as e:
            self.emptyState.show()
            self.experimentUI.hide()
            self.emptyStateMessage.setText(str(e))
            print(e)
