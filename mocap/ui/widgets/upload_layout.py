from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class UploadLayout(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.innerLayout = QVBoxLayout(self)
        self.setAcceptDrops(True)

        label = QLabel("Select Videos", self)
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        label = QLabel("Select synchronized videos of the same motion sequence to estimate 3D human poses.")
        label.setProperty("class", "body")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        # Create a placeholder for drag-and-drop area
        self.dragDropArea = DragDropWidget(self)
        self.innerLayout.addWidget(self.dragDropArea)
        self.innerLayout.addSpacing(16)

        label = QLabel("Select Camera Calibration", self)
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        label = QLabel("Calibration file must contain intrinsic and extrinsic parameters for each camera. See documentation for format details.")
        label.setProperty("class", "body")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        # Create a button for selecting a calibration YAML file
        self.calibrationButton = QPushButton("Select Calibration File")
        self.calibrationButton.clicked.connect(self.selectCalibrationFile)
        self.innerLayout.addWidget(self.calibrationButton)

        # Label to display selected calibration file
        self.calibrationLabel = QLabel("No calibration file selected")
        self.innerLayout.addWidget(self.calibrationLabel)
        self.innerLayout.addSpacing(16)

        # Upload button (initially disabled)
        self.uploadButton = QPushButton("Upload")
        self.uploadButton.setEnabled(False)  # Initially disabled
        self.uploadButton.clicked.connect(self.uploadFiles)
        self.innerLayout.addWidget(self.uploadButton)

        self.selectedVideos = []
        self.calibrationFile = None

    def selectCalibrationFile(self):
        """Open a file dialog to select the YAML calibration file."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("YAML Files (*.yaml)")
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
        # Your file upload logic goes here
        print(f"Uploading videos: {self.selectedVideos}")
        print(f"Using calibration file: {self.calibrationFile}")

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
        self.setFixedHeight(128)
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
        self.label.setText(f"Selected {len(files)} videos")

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
