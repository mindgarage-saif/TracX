import os
import shutil

from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.constants import APP_ASSETS
from mocap.core import Experiment
from mocap.ui.common import (
    BasePage,
    EmptyState,
    LogsWidget,
)
from mocap.ui.styles import PAD_X, PAD_Y

from .monocular3d import MonocularAnalysisPage
from .multiview3d import ExperimentDataWidget, MultiviewMotionOptions, SimulationOptions


class AnalysisPage(BasePage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        # Create an empty state layout
        self.emptyState = EmptyState(
            self,
            os.path.join(APP_ASSETS, "empty-state", "no-experiment-selected.png"),
            "Select or create an experiment to get started",
        )
        self.innerLayout.addWidget(self.emptyState)

        # Create the project details layout for Monocular
        self.experimentMonocularUI = MonocularAnalysisPage(self)
        self.innerLayout.addWidget(self.experimentMonocularUI)

        # Create the project details layout
        self.experimentUI = QWidget(self)
        self.experimentUI.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.innerLayout.addWidget(self.experimentUI)
        self.createExperimentUI()

        # Set the initial state
        self.emptyState.show()
        self.experimentUI.hide()
        self.experimentMonocularUI.hide()
        self.experiment = None

        # Connect the sidebar event
        parent.analysisTab.experimentSelected.connect(self.showExperiment)

    def createExperimentUI(self):
        # Create a layout for the processing page
        self.experimentUILayout = QVBoxLayout(self.experimentUI)
        self.experimentUILayout.setContentsMargins(0, 0, 0, 0)
        self.experimentUILayout.setSpacing(0)
        self.experimentUI.setLayout(self.experimentUILayout)

        # Inferencer and visualizer settings
        self.experimentDataView = ExperimentDataWidget(self)
        self.experimentUILayout.addWidget(self.experimentDataView)
        self.experimentUILayout.addSpacing(PAD_Y)

        # Create a horizontal layout for the motion estimation settings
        processingFrame = QWidget(self)
        processingFrameLayout = QHBoxLayout(processingFrame)
        processingFrameLayout.setContentsMargins(0, 0, 0, 0)
        processingFrameLayout.setSpacing(PAD_X)
        self.experimentUILayout.addWidget(processingFrame)

        # Create two equal columns for the settings
        column1 = QFrame(self)
        column1.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        column1Layout = QVBoxLayout(column1)
        column1Layout.setContentsMargins(0, 0, 0, 0)
        column1Layout.setSpacing(PAD_Y)

        column2 = QFrame(self)
        column2.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        column2Layout = QVBoxLayout(column2)
        column2Layout.setContentsMargins(0, 0, 0, 0)
        column2Layout.setSpacing(PAD_Y)

        self.logs_view = LogsWidget(self)
        self.logs_view.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )

        # Add columns to the horizontal layout with equal stretch factors
        processingFrameLayout.addWidget(column1, 1)  # Stretch factor 1
        processingFrameLayout.addWidget(column2, 1)  # Stretch factor 1
        processingFrameLayout.addWidget(self.logs_view, 2)  # Stretch factor 2

        # Add motion estimation settings in column 1
        self.motionOptions = MultiviewMotionOptions(self)
        self.motionOptions.downloadButton.clicked.connect(self.downloadMotionData)
        column1Layout.addWidget(self.motionOptions)

        # Add visualizer settings in column 2
        self.visualizationOptions = SimulationOptions(self)
        column2Layout.addWidget(self.visualizationOptions)

        # Connect the update event
        self.motionOptions.setEnabled(False)
        self.visualizationOptions.setEnabled(False)
        self.experimentDataView.onUpdate = self.onExperimentDataUploaded
        self.motionOptions.onUpdate = self.onMotionEstimated

    def onExperimentDataUploaded(self, status):
        self.motionOptions.setEnabled(status)

    def onMotionEstimated(self, status, result):
        self.visualizationOptions.setEnabled(status)
        if not status:
            self.showAlert(str(result), "Motion Estimation Failed")

    def downloadMotionData(self):
        try:
            motionData = self.experiment.get_motion_file()
            self.downloadFile(motionData)
        except Exception as e:
            self.showAlert(str(e), "Download Failed")

    def downloadFile(self, file_path):
        # Show a download dialog
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.selectFile(os.path.basename(file_path))

        if file_dialog.exec():
            save_path = file_dialog.selectedFiles()[0]
            if save_path:
                shutil.copyfile(file_path, save_path)
                # TOOD: Show a success message

    def showExperiment(self, name, experiment):
        print("Selected experiment:", name, experiment)
        try:
            self.emptyState.hide()
            if not experiment["monocular"]:
                self.motionOptions.params.experiment_name = name
                self.visualizationOptions.params.experiment_name = name
                self.visualizationOptions.opensim_config.experiment_name = name
                self.experiment = Experiment.open(name)
                self.experimentDataView.setExperiment(self.experiment)
                self.experimentDataView.videoUploader.previewSelected(
                    self.experiment.videos,
                )
                hasMotionData = self.experiment.get_motion_file() is not None
                self.motionOptions.estimateButton.setEnabled(not hasMotionData)
                self.motionOptions.downloadButton.setEnabled(hasMotionData)
                self.visualizationOptions.setEnabled(hasMotionData)

                self.motionOptions.estimateButton.log_file = self.experiment.log_file
                self.visualizationOptions.createButton.log_file = (
                    self.experiment.log_file
                )
                self.visualizationOptions.downloadButton.log_file = (
                    self.experiment.log_file
                )
                self.logs_view.start_log_streaming(self.experiment.log_file)
                self.experimentMonocularUI.hide()
                self.experimentUI.show()
            else:
                self.experimentMonocularUI.load(name)
                self.experimentUI.hide()
                self.experimentMonocularUI.show()

            self.log(f"Loaded experiment: {self.experiment}")

        except Exception as e:
            self.experimentUI.hide()
            self.experimentMonocularUI.hide()
            self.emptyState.show()
            self.showAlert(str(e), "Failed to load experiment")