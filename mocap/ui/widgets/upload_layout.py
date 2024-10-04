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

from .video_list import VideoList


# from Pose2Sim_with_2d import main
class UploadLayout(QFrame):
    def __init__(self, parent: QWidget, params) -> None:
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
        self.dragDropArea = DragDropWidget(self)
        self.innerLayout.addWidget(self.dragDropArea)
        self.innerLayout.addSpacing(16)

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

        label = QLabel("Select Camera Calibration", self)
        label.setToolTip(
            "Calibration file must contain intrinsic and extrinsic parameters for each camera. See documentation for format details."
        )
        label.setProperty("class", "h3")
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        calibrationSelectionLabelsLayout.addWidget(label)

        # Label to display selected calibration file
        self.calibrationLabel = QLabel("No calibration file selected")
        calibrationSelectionLabelsLayout.addWidget(self.calibrationLabel)

        # Create a button for selecting a calibration YAML file
        self.calibrationButton = QPushButton("Select Calibration File")
        self.calibrationButton.clicked.connect(self.selectCalibrationFile)
        calibrationLayout.addWidget(self.calibrationButton)
        self.innerLayout.addSpacing(16)

        # Upload button (initially disabled)
        self.uploadButton = QPushButton("Upload")
        self.uploadButton.setEnabled(False)  # Initially disabled
        self.uploadButton.clicked.connect(self.uploadFiles)
        self.innerLayout.addWidget(self.uploadButton)

        self.selectedVideos = []
        self.calibrationFile = None
        self.params = params

    def selectCalibrationFile(self):
        """Open a file dialog to select the XML calibration file."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("XML Files (*.xml)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.calibrationFile = selected_files[0]
            self.calibrationLabel.setText(f"Selected: {self.calibrationFile}")

        self.updateUploadButtonState()

    def updateUploadButtonState(self):
        """Enable the Upload button if both videos and calibration file are selected."""
        if self.selectedVideos and self.calibrationFile:
            self.uploadButton.setEnabled(True)
        else:
            self.uploadButton.setEnabled(False)

    def uploadFiles(self):
        """Handle the file upload logic."""
        self.params.video_files = self.selectedVideos
        self.params.calibration_file = self.calibrationFile

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag-enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        video_files = [f for f in files if f.lower().endswith((".mp4", ".avi", ".mov"))]
        if video_files:
            self.dragDropArea.setFileList(video_files)
            self.selectedVideos = video_files

        self.updateUploadButtonState()


class DragDropWidget(QFrame):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setObjectName("DragDropWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(250)
        self.setAcceptDrops(True)

        self.layout = QVBoxLayout(self)
        self.label = QLabel("Drag and drop your videos here or click to browse")
        self.label.setProperty("class", "body")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        # Store the list of selected files
        self.fileList = []

    def setFileList(self, files):
        """Update the drag-and-drop area with selected files."""
        self.fileList = files
        newLabel = VideoList(self, self.fileList)
        self.layout.replaceWidget(self.label, newLabel)
        self.label = newLabel

    def mousePressEvent(self, event):
        """Open file dialog when the drag-drop area is clicked."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.setFileList(selected_files)
            self.parent().selectedVideos = selected_files

        self.parent().updateUploadButtonState()
