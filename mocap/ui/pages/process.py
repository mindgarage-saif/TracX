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
from mocap.core import Experiment, ExperimentMonocular
from mocap.ui.tasks import MotionTaskConfig

from ..config.constants import PAD_X, PAD_Y
from ..widgets import (
    EmptyState,
    ExperimentDataWidget,
    ExperimentMonocularDataWidget,
    LogsWidget,
    MotionOptions,
    MotionOptionsMonocular,
    SimulationOptions,
    SimulationOptionsMonocular,
)
from .base import BasePage


class ProcessingPage(BasePage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.params = MotionTaskConfig()

        # Create an empty state layout
        self.emptyState = EmptyState(
            self,
            os.path.join(APP_ASSETS, "empty-state", "no-experiment-selected.png"),
            "Select or create an experiment to get started",
        )
        self.innerLayout.addWidget(self.emptyState)
        # Create the project details layout for Monocular
        self.experimentMonocularUI = QWidget(self)
        self.experimentMonocularUI.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.innerLayout.addWidget(self.experimentMonocularUI)
        self.createExperimentMonocularUI()
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
        self.sidebar.onExperimentSelected = self.showExperiment

    def createExperimentMonocularUI(self):
        # Create a layout for the processing page
        self.experimentMonocularUILayout = QVBoxLayout(self.experimentMonocularUI)
        self.experimentMonocularUILayout.setContentsMargins(0, 0, 0, 0)
        self.experimentMonocularUILayout.setSpacing(0)
        self.experimentMonocularUI.setLayout(self.experimentMonocularUILayout)

        # Inferencer and visualizer settings
        self.experimentDataViewMonocular = ExperimentMonocularDataWidget(self)
        self.experimentMonocularUILayout.addWidget(self.experimentDataViewMonocular)
        self.experimentMonocularUILayout.addSpacing(PAD_Y)

        self.videoListWidget = QWidget(self)
        self.experimentMonocularUILayout.addWidget(self.videoListWidget)

        # Create a horizontal layout for the motion estimation settings
        processingFrame = QWidget(self)
        processingFrameLayout = QHBoxLayout(processingFrame)
        processingFrameLayout.setContentsMargins(0, 0, 0, 0)
        processingFrameLayout.setSpacing(PAD_X)
        self.experimentMonocularUILayout.addWidget(processingFrame)

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

        self.logs_viewMonocular = LogsWidget(self)
        self.logs_viewMonocular.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )

        # Add columns to the horizontal layout with equal stretch factors
        processingFrameLayout.addWidget(column1, 1)  # Stretch factor 1
        processingFrameLayout.addWidget(column2, 1)  # Stretch factor 1
        processingFrameLayout.addWidget(self.logs_viewMonocular, 2)  # Stretch factor 2

        # Add motion estimation settings in column 1
        self.motionOptionsMonocular = MotionOptionsMonocular(self)
        self.motionOptionsMonocular.downloadButton.clicked.connect(
            self.downloadMotionData,
        )
        column1Layout.addWidget(self.motionOptionsMonocular)

        # Add visualizer settings in column 2
        self.visualizationOptionsMonocular = SimulationOptionsMonocular(self)
        column2Layout.addWidget(self.visualizationOptionsMonocular)

        # Connect the update event
        self.motionOptionsMonocular.setEnabled(False)
        self.visualizationOptionsMonocular.setEnabled(False)
        self.experimentDataViewMonocular.onUpdate = (
            self.onExperimentMonocularDataUploaded
        )
        self.motionOptionsMonocular.onUpdate = self.onMotionMoncularEstimated

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

        self.videoListWidget = QWidget(self)
        self.experimentUILayout.addWidget(self.videoListWidget)

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
        self.motionOptions = MotionOptions(self)
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

    def onExperimentMonocularDataUploaded(self, status):
        self.motionOptionsMonocular.setEnabled(status)

    def onMotionEstimated(self, status, result):
        self.visualizationOptions.setEnabled(status)
        if not status:
            self.showAlert(str(result), "Motion Estimation Failed")

    def onMotionMoncularEstimated(self, status, result):
        self.visualizationOptionsMonocular.setEnabled(status)
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

    def showExperiment(self, name, est_type):
        try:
            if est_type == "pose2sim":
                self.motionOptions.params.experiment_name = name
                self.visualizationOptions.params.experiment_name = name
                self.visualizationOptions.opensim_config.experiment_name = name
                self.experiment = Experiment(name, create=False)
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
            else:
                self.motionOptionsMonocular.params.experiment_name = name
                self.visualizationOptionsMonocular.params.experiment_name = name
                self.experiment = ExperimentMonocular(name, create=False)
                self.experimentDataViewMonocular.setExperiment(self.experiment)
                self.experimentDataViewMonocular.videoUploader.previewSelected(
                    self.experiment.videos,
                )
                hasMotionData = self.experiment.get_motion_file() is not None
                self.motionOptionsMonocular.estimateMoncularButton.setEnabled(
                    not hasMotionData,
                )
                self.motionOptionsMonocular.downloadButton.setEnabled(hasMotionData)
                self.visualizationOptionsMonocular.setEnabled(hasMotionData)

                self.motionOptionsMonocular.estimateMoncularButton.log_file = (
                    self.experiment.log_file
                )
                self.visualizationOptionsMonocular.createButton.log_file = (
                    self.experiment.log_file
                )
                self.logs_viewMonocular.start_log_streaming(self.experiment.log_file)
            self.log(f"Loaded experiment: {self.experiment}")

            self.emptyState.hide()
            if est_type == "pose2sim":
                self.experimentMonocularUI.hide()
                self.experimentUI.show()
            else:
                self.experimentUI.hide()
                self.experimentMonocularUI.show()
            # self.experimentUI.show()

        except Exception as e:
            print(e)
