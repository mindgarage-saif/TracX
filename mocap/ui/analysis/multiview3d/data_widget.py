import os

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.core import Experiment
from mocap.ui.common import Frame, VideoUploaderWidget
from mocap.ui.styles import PAD_X, PAD_Y


class ExperimentDataWidget(Frame):
    """Widget for viewing and uploading experiment data.

    This widget allows users to upload experiment videos and camera calibration files using a
    drag-and-drop interface. The widget also displays information about the uploaded files.

    Args:
        parent (QWidget): The parent widget.

    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.setAcceptDrops(True)

        label = QLabel("Experiment Videos", self)
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        info = QLabel(
            "Select 3-10 synchronized videos of a motion sequence to estimate 3D human poses.",
            self,
        )
        info.setProperty("class", "body")
        info.setWordWrap(True)
        self.innerLayout.addWidget(info)
        self.innerLayout.addSpacing(PAD_Y)

        # Create a placeholder for drag-and-drop area
        self.videoUploader = VideoUploaderWidget(self)
        self.videoUploader.onVideosSelected = self.handleVideosSelected
        self.innerLayout.addWidget(self.videoUploader)
        self.innerLayout.addSpacing(PAD_Y)

        calibrationSelection = QWidget(self)
        calibrationSelection.setProperty("class", "empty")
        calibrationSelection.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        calibrationLayout = QHBoxLayout(calibrationSelection)
        calibrationLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(calibrationSelection)

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

        self.onUpdate = lambda status: None

    def setExperiment(self, experiment):
        """Set the experiment object.

        Args:
            experiment (Experiment): The experiment object.

        """
        self.experiment = experiment
        self.refreshUI()

    def selectCalibrationFile(self):
        """Open a file dialog to select the XML calibration file."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("XML Files (*.xml)")
        if file_dialog.exec():
            try:
                selected_file = file_dialog.selectedFiles()[0]
                self.experiment.set_camera_parameters(selected_file)
                self.refreshUI()
            except ValueError as e:
                self.calibrationLabel.setText(f"Error: {e}")
                return

    def updateCalibrationFile(self, file_path: str):
        """Display the selected calibration file."""
        if file_path is not None:
            filename = os.path.basename(file_path)
            self.calibrationLabel.setText("Calibration file: " + filename)
            self.calibrationButton.setEnabled(False)
        else:
            self.calibrationLabel.setText("No calibration file uploaded")
            self.calibrationButton.setEnabled(True)

    def handleVideosSelected(self, selectedVideos):
        """Handle the selected videos."""
        for video in selectedVideos:
            if os.path.exists(video):
                self.experiment.add_video(video)

        self.refreshUI()

    def refreshUI(self):
        """Display the selected experiment."""
        experiment: Experiment = self.experiment
        if experiment is None:
            return

        experimentVideos = experiment.videos
        if experimentVideos:
            self.videoUploader.previewSelected(experimentVideos)
            # self.videoUploader.setEnabled(False)
        else:
            self.videoUploader.previewSelected([])
            # self.videoUploader.setEnabled(True)

        cameraParameters = experiment.get_camera_parameters()
        self.updateCalibrationFile(cameraParameters)

        if experimentVideos and cameraParameters:
            # self.setEnabled(False)
            self.onUpdate(True)
        else:
            # self.setEnabled(True)
            self.onUpdate(False)
