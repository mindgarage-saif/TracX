import os

from PyQt6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from TracX.core import Experiment
from TracX.ui.common import VideoUploaderWidget


class ExperimentDataWidget(QWidget):
    """Widget for viewing and uploading experiment data.

    This widget allows users to upload experiment video file using a
    drag-and-drop interface. The widget also displays information about the uploaded files.

    Args:
        parent (QWidget): The parent widget.

    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)

        # Create a placeholder for drag-and-drop area
        self.videoUploader = VideoUploaderWidget(self)
        self.videoUploader.onVideosSelected = self.handleVideosSelected
        self.innerLayout.addWidget(self.videoUploader)

        self.onUpdate = lambda status: None

    def setExperiment(self, experiment):
        """Set the experiment object.

        Args:
            experiment (Experiment): The experiment object.

        """
        self.experiment = experiment
        self.refreshUI()

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
        else:
            self.videoUploader.previewSelected([])

        if experimentVideos:
            self.onUpdate(True)
        else:
            self.onUpdate(False)
