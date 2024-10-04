import os

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.constants import APP_ASSETS
from mocap.core import Experiment

from ..widgets import (
    EmptyState,
    MotionOptions,
    PipelineParams,
    SimulationOptions,
    UploadLayout,
    VideoList,
)
from .base import BasePage


class ProcessingPage(BasePage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.params = PipelineParams()

        # Create an empty state layout
        self.emptyState = EmptyState(
            self,
            os.path.join(APP_ASSETS, "empty-state", "no-experiment-selected.png"),
            "Select or create an experiment to get started",
        )
        self.innerLayout.addWidget(self.emptyState)

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

    def createExperimentUI(self):
        # Create a layout for the processing page
        self.experimentUILayout = QVBoxLayout(self.experimentUI)
        self.experimentUILayout.setContentsMargins(0, 0, 0, 0)
        self.experimentUILayout.setSpacing(0)
        self.experimentUI.setLayout(self.experimentUILayout)

        # Inferencer and visualizer settings
        uploadUI = UploadLayout(self, self.params)
        self.experimentUILayout.addWidget(uploadUI)

        self.videoListWidget = QWidget(self)
        self.experimentUILayout.addWidget(self.videoListWidget)

        # Create a horizontal layout for the motion estimation settings
        processingFrame = QWidget(self)
        processingFrameLayout = QHBoxLayout(processingFrame)
        processingFrameLayout.setContentsMargins(0, 0, 0, 0)
        processingFrameLayout.setSpacing(8)
        self.experimentUILayout.addWidget(processingFrame)

        # Create two equal columns for the settings
        column1 = QFrame(self)
        column1.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        column1Layout = QVBoxLayout(column1)
        column1Layout.setContentsMargins(0, 0, 0, 0)
        column1Layout.setSpacing(16)

        column2 = QFrame(self)
        column2.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        column2Layout = QVBoxLayout(column2)
        column2Layout.setContentsMargins(0, 0, 0, 0)
        column2Layout.setSpacing(16)

        # Add columns to the horizontal layout with equal stretch factors
        processingFrameLayout.addWidget(column1, 1)  # Stretch factor 1
        processingFrameLayout.addWidget(column2, 1)  # Stretch factor 1

        # Add motion estimation settings in column 1
        motionOptions = MotionOptions(self, self.params)
        column1Layout.addWidget(motionOptions)

        # Add visualizer settings in column 2
        visualizationOptions = SimulationOptions(self, self.params)
        column2Layout.addWidget(visualizationOptions)

    def showExperiment(self, name):
        try:
            self.params.experiment_name = name
            self.experiment = Experiment(name, create=False)
            self.log(f"Loaded experiment: {self.experiment}")

            # oldWidget = self.videoListWidget
            # newWidget = VideoList(self, self.experiment.videos)
            # self.experimentUILayout.replaceWidget(oldWidget, newWidget)
            # self.videoListWidget = newWidget

            self.emptyState.hide()
            self.experimentUI.show()

        except Exception as e:
            print(e)
