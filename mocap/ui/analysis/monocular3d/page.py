import os
import shutil

from PyQt6.QtWidgets import (
    QFileDialog,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.core import Experiment
from mocap.ui.styles import PAD_Y

from .data_widget import ExperimentDataWidget
from .motion_options import MotionOptions


class MonocularAnalysisPage(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Experiment data
        self.data = ExperimentDataWidget(self)
        layout.addWidget(self.data)
        layout.addSpacing(PAD_Y)
        self.data.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )

        # Experiment settings
        self.settings = MotionOptions(self)
        self.settings.downloadButton.clicked.connect(self.downloadMotionData)
        layout.addWidget(self.settings)

        # Connect the update event
        self.data.onUpdate = self.handleDataUpload
        self.settings.onUpdate = self.handleOptionsChanged

    def load(self, name):
        self.settings.cfg.experiment_name = name
        self.settings.visualize_cfg.experiment_name = name  # FIXME: This is a hack
        self.experiment = Experiment.open(name)
        self.data.setExperiment(self.experiment)
        hasMotionData = self.experiment.get_motion_file() is not None
        self.settings.estimate_button.setEnabled(
            not hasMotionData,
        )
        self.settings.downloadButton.setEnabled(hasMotionData)

        self.settings.estimate_button.log_file = self.experiment.log_file

    def handleDataUpload(self, status):
        self.settings.setEnabled(status)

    def handleOptionsChanged(self, status, result):
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
