import os
import shutil

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

from TracX.core import Experiment
from TracX.ui.common import (
    LogsWidget,
    Tab,
    TabbedArea,
)

from .cameras import CamerasTab
from .data_widget import ExperimentDataWidget
from .settings import Multiview3DSettingsPanel


class Multiview3DAnalysisPage(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("AnalysisPage")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tabbed area for experiment data and camera settings
        self.tabbed_area = TabbedArea(self)
        self.tabbed_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        layout.addWidget(self.tabbed_area)

        # Add pages
        self.data_tab = Tab("Videos", self.tabbed_area)
        self.tabbed_area.addTab(self.data_tab)

        self.cameras_tab = CamerasTab(self.tabbed_area)
        self.tabbed_area.addTab(self.cameras_tab)

        # Experiment data
        self.data = ExperimentDataWidget(self)
        self.data.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.data_tab.addWidget(self.data)

        # Experiment logs
        self.logs_tab = Tab("Logs", self.tabbed_area)
        self.tabbed_area.addTab(self.logs_tab)
        self.logs_view = LogsWidget(self)
        self.logs_view.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )
        self.logs_tab.addWidget(self.logs_view)

        # Experiment settings
        self.settings = Multiview3DSettingsPanel(self)
        self.settings.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Preferred,
        )
        self.settings.exportButton.clicked.connect(self.downloadMotionData)
        layout.addWidget(self.settings)

        # Events
        self.data.onUpdate = self.handleDataUpload
        self.settings.onUpdate = self.handleOptionsChanged

    def setExperiment(self, name):
        self.experiment = Experiment.open(name)
        self.cameras_tab.setExperiment(self.experiment)
        self.data.setExperiment(self.experiment)
        self.settings.setExperiment(self.experiment)
        self.data.videoUploader.previewSelected(
            self.experiment.videos,
        )
        hasMotionData = self.experiment.get_motion_file() is not None
        # self.settings.estimateButton.setEnabled(not hasMotionData)
        self.settings.exportButton.setEnabled(hasMotionData)

        self.settings.analyzeButton.log_file = self.experiment.log_file
        self.settings.visualizeButton.log_file = self.experiment.log_file
        self.logs_view.start_log_streaming(self.experiment.log_file)

    def handleDataUpload(self, status):
        self.settings.setEnabled(status)

    def handleOptionsChanged(self, status, result):
        if not status:
            self.parent().showAlert(str(result), "Motion Estimation Failed")

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
