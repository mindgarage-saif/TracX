import os
import shutil

from PyQt6.QtWidgets import (
    QFileDialog,
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

from .monocular2d import Monocular2DAnalysisPage
from .monocular3d import Monocular3DAnalysisPage
from .multiview3d import ExperimentDataWidget, MultiviewMotionOptions


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
        self.monocular2d_analysis = Monocular2DAnalysisPage(self)
        self.innerLayout.addWidget(self.monocular2d_analysis)

        self.monocular3d_analysis = Monocular3DAnalysisPage(self)
        self.innerLayout.addWidget(self.monocular3d_analysis)

        # Create the project details layout
        self.multiview3d_analysis = QWidget(self)
        self.multiview3d_analysis.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.innerLayout.addWidget(self.multiview3d_analysis)
        self.create_multiview_analysis_page()

        # Set the initial state
        self.emptyState.show()
        self.monocular2d_analysis.hide()
        self.monocular3d_analysis.hide()
        self.multiview3d_analysis.hide()
        self.experiment = None

        # Connect the sidebar event
        parent.analysisTab.experimentSelected.connect(self.showExperiment)

    def create_multiview_analysis_page(self):
        # Create a layout for the processing page
        self.multiview3d_layout = QHBoxLayout(self.multiview3d_analysis)
        self.multiview3d_layout.setContentsMargins(0, 0, 0, 0)
        self.multiview3d_layout.setSpacing(PAD_X)

        main_column = QWidget(self)
        main_column.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout = QVBoxLayout(main_column)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(PAD_Y)
        self.multiview3d_layout.addWidget(main_column)

        # Inferencer and visualizer settings
        self.experimentDataView = ExperimentDataWidget(self)
        main_layout.addWidget(self.experimentDataView)

        self.logs_view = LogsWidget(self)
        self.logs_view.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )
        main_layout.addWidget(self.logs_view)

        # Settings for motion estimation
        self.mocap_options = MultiviewMotionOptions(self)
        self.mocap_options.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        self.mocap_options.setFixedWidth(256)
        self.mocap_options.downloadButton.clicked.connect(self.downloadMotionData)
        self.multiview3d_layout.addWidget(self.mocap_options)

        # Connect the update event
        self.mocap_options.setEnabled(False)
        self.experimentDataView.onUpdate = self.onExperimentDataUploaded
        self.mocap_options.onUpdate = self.onMotionEstimated

    def onExperimentDataUploaded(self, status):
        self.mocap_options.setEnabled(status)

    def onMotionEstimated(self, status, result):
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
        try:
            self.emptyState.hide()
            if not experiment["monocular"]:
                self.mocap_options.setExperiment(name)
                self.experiment = Experiment.open(name)
                self.experimentDataView.setExperiment(self.experiment)
                self.experimentDataView.videoUploader.previewSelected(
                    self.experiment.videos,
                )
                hasMotionData = self.experiment.get_motion_file() is not None
                self.mocap_options.estimateButton.setEnabled(not hasMotionData)
                self.mocap_options.downloadButton.setEnabled(hasMotionData)

                self.mocap_options.estimateButton.log_file = self.experiment.log_file
                self.mocap_options.createButton.log_file = self.experiment.log_file
                self.mocap_options.downloadOpenSimButton.log_file = (
                    self.experiment.log_file
                )
                self.logs_view.start_log_streaming(self.experiment.log_file)
                self.monocular2d_analysis.hide()
                self.monocular3d_analysis.hide()
                self.multiview3d_analysis.show()
            elif not experiment["is_2d"]:
                self.monocular3d_analysis.load(name)
                self.monocular2d_analysis.hide()
                self.multiview3d_analysis.hide()
                self.monocular3d_analysis.show()
            else:
                self.monocular2d_analysis.setExperiment(name)
                self.multiview3d_analysis.hide()
                self.monocular3d_analysis.hide()
                self.monocular2d_analysis.show()

            self.log(f"Loaded experiment: {self.experiment}")

        except Exception as e:
            self.multiview3d_analysis.hide()
            self.monocular3d_analysis.hide()
            self.emptyState.show()
            self.showAlert(str(e), "Failed to load experiment")
