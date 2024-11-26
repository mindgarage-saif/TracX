import os
import shutil

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from TracX.core import Experiment
from TracX.core.cameras import CameraSystem, CameraVisualizer
from TracX.ui.common import (
    LogsWidget,
    Tab,
    TabbedArea,
)

from .data_widget import ExperimentDataWidget
from .settings import Multiview3DSettingsPanel


class CamerasTab(Tab):
    def __init__(self, parent):
        super().__init__("Cameras", parent, Qt.Orientation.Vertical)
        self.cameras = None
        self.visualizer = None
        self.canvas = None
        self.experiment = None

        calibrationSelection = QWidget(self)
        calibrationSelection.setProperty("class", "empty")
        calibrationSelection.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        calibrationLayout = QHBoxLayout(calibrationSelection)
        calibrationLayout.setContentsMargins(0, 0, 0, 0)
        self.addWidget(calibrationSelection)

        calibrationSelectionLabels = QWidget(self)
        calibrationSelectionLabels.setProperty("class", "empty")
        calibrationSelectionLabels.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        calibrationSelectionLabelsLayout = QVBoxLayout(calibrationSelectionLabels)
        calibrationSelectionLabelsLayout.setContentsMargins(0, 0, 0, 0)
        calibrationSelectionLabelsLayout.setSpacing(0)
        calibrationLayout.addWidget(calibrationSelectionLabels)
        calibrationLayout.addStretch()

        label = QLabel("Camera Calibration Parameters", self)
        label.setToolTip(
            "Calibration file must contain intrinsic and extrinsic parameters for each camera. See documentation for format details.",
        )
        label.setProperty("class", "h3")
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        calibrationSelectionLabelsLayout.addWidget(label)

        # Label to display selected calibration file
        self.calibrationLabel = QLabel("No calibration file uploaded", self)
        calibrationSelectionLabelsLayout.addWidget(self.calibrationLabel)

        # Create a button for selecting a calibration XML file
        self.calibrationButton = QPushButton("Upload Calibration File", self)
        self.calibrationButton.clicked.connect(self.selectCalibrationFile)
        calibrationLayout.addWidget(self.calibrationButton)

    def selectCalibrationFile(self):
        """Open a file dialog to select the TOML calibration file."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("TOML File (*.toml)")
        if file_dialog.exec():
            try:
                selected_file = file_dialog.selectedFiles()[0]
                self.experiment.set_camera_parameters(selected_file)
                self.refreshUI()
            except ValueError as e:
                self.calibrationLabel.setText(f"Error: {e}")
                return

    def setExperiment(self, experiment):
        self.experiment = experiment
        calib_file = self.experiment.calibration_file
        self.setCameraInfo(calib_file)

    def refreshUI(self):
        experiment: Experiment = self.experiment
        cameraParameters = experiment.get_camera_parameters()
        self.updateCalibrationFile(cameraParameters)

    def updateCalibrationFile(self, file_path: str):
        """Display the selected calibration file."""
        if file_path is not None:
            filename = os.path.basename(file_path)
            self.calibrationLabel.setText("Calibration file: " + filename)
            self.calibrationButton.setEnabled(False)
        else:
            self.calibrationLabel.setText("No calibration file uploaded")
            self.calibrationButton.setEnabled(True)

    def setCameraInfo(self, calib_file):
        if calib_file is None:
            self.cameras = None
            self.visualizer = None
            return

        self.cameras = CameraSystem(calib_file)
        self.visualizer = CameraVisualizer(self.cameras)
        fig = self.visualizer.visualize()
        self.showFigure(fig)

    def showFigure(self, fig):
        if self.canvas is not None:
            self.canvas.setParent(None)
            self.canvas.deleteLater()
            self.canvas = None

        self.canvas = FigureCanvas(fig)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.addWidget(self.canvas)


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
