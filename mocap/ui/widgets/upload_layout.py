import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.constants import MAX_VIDEOS, MIN_VIDEOS, SUPPORTED_VIDEO_FORMATS
from mocap.core import Experiment

from .video_list import VideoList


class VideoUploaderWidget(QFrame):
    """Widget for uploading experiment videos."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setObjectName("DragDropWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(300)
        self.setAcceptDrops(True)

        self.label = QLabel(
            f"Select or drop {MIN_VIDEOS}-{MAX_VIDEOS} videos here", self
        )
        self.label.setProperty("class", "body")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedHeight(300)
        layout.addWidget(self.label)

        self.preview = VideoList(self, preview_size=200)
        self.preview.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.preview.hide()
        layout.addWidget(self.preview)
        layout.addStretch()

        # Callback.
        self.onVideosSelected = lambda files: None

        self.isEnabled = True

    def setEnabled(self, enabled):
        self.isEnabled = enabled

    def previewSelected(self, selectedVideos):
        """Show the list of selected files."""
        if not selectedVideos:
            self.label.show()
            self.preview.hide()
            return

        self.preview.populate_list(selectedVideos)
        self.label.hide()
        self.preview.show()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag-enter event."""
        if not self.isEnabled:
            return

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        if not self.isEnabled:
            return

        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.onFilesSelected(files)

    def mousePressEvent(self, event):
        """Open file dialog when the drag-drop area is clicked."""
        if not self.isEnabled:
            return

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov)")
        if dialog.exec():
            self.onFilesSelected(dialog.selectedFiles())

    def onFilesSelected(self, files):
        """Handle the selected files."""

        def isVideoFile(file):
            fmt = os.path.splitext(file)[1]
            return fmt.lower() in SUPPORTED_VIDEO_FORMATS and os.path.isfile(file)

        files = [f for f in files if isVideoFile(f)][:MAX_VIDEOS]
        if len(files) >= MIN_VIDEOS:
            self.label.hide()
            self.onVideosSelected(files)
        else:
            self.label.setText(f"Select at least {MIN_VIDEOS} videos")
            self.label.show()


class ExperimentDataWidget(QFrame):
    """Widget for viewing and uploading experiment data.

    This widget allows users to upload experiment videos and camera calibration files using a
    drag-and-drop interface. The widget also displays information about the uploaded files.

    Args:
        parent (QWidget): The parent widget.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.innerLayout = QVBoxLayout(self)
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

        # Create a placeholder for drag-and-drop area
        self.videoUploader = VideoUploaderWidget(self)
        self.videoUploader.onVideosSelected = self.handleVideosSelected
        self.innerLayout.addWidget(self.videoUploader)
        self.innerLayout.addSpacing(8)

        calibrationSelection = QWidget(self)
        calibrationSelection.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        calibrationLayout = QHBoxLayout(calibrationSelection)
        calibrationLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(calibrationSelection)

        calibrationSelectionLabels = QWidget(self)
        calibrationSelectionLabels.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        calibrationSelectionLabelsLayout = QVBoxLayout(calibrationSelectionLabels)
        calibrationSelectionLabelsLayout.setContentsMargins(0, 0, 0, 0)
        calibrationSelectionLabelsLayout.setSpacing(0)
        calibrationLayout.addWidget(calibrationSelectionLabels)
        calibrationLayout.addStretch()

        label = QLabel("Camera Calibration Parameters", self)
        label.setToolTip(
            "Calibration file must contain intrinsic and extrinsic parameters for each camera. See documentation for format details."
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

                # Show the selected calibration file
                self.updateCalibrationFile(selected_file)
                self.calibrationLabel.setText("Calibration file uploaded")
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
            self.videoUploader.setEnabled(False)
        else:
            self.videoUploader.previewSelected([])
            self.videoUploader.setEnabled(True)

        self.updateCalibrationFile(experiment.get_camera_parameters())

    def uploadFiles(self):
        """Handle the file upload logic."""
        for video in self.selectedVideos:
            self.experiment.add_video(video)
