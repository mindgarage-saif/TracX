import logging
import os

from PyQt6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.constants import APP_ASSETS
from mocap.core import Experiment
from mocap.ui.common import EmptyState, Frame, VideoPlayerWidget, VideoUploaderWidget


class ExperimentDataWidget(Frame):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.experiment = None

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.innerLayout.setSpacing(0)

        # Placeholder label for "No Cameras Selected"
        self.noCamerasLabel = EmptyState(
            self,
            os.path.join(APP_ASSETS, "empty-state", "no-camera-selected.png"),
            "Get started with markerless motion analysis",
            action=["Start Webcam", "Upload a Video"],
            size=512,
        )
        self.noCamerasLabel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.innerLayout.addWidget(self.noCamerasLabel)

        # Create a placeholder for drag-and-drop area
        self.videoUploader = VideoUploaderWidget(self, minNumVideos=1, numMaxVideos=1)
        self.videoUploader.onVideosSelected = self.handleVideosSelected
        self.videoUploader.hide()

        # Delegate click event to the video uploader
        self.noCamerasLabel.setCallback(
            [
                self.startWebcam,
                self.videoUploader.mousePressEvent,
            ]
        )

        # Create a video player widget
        self.videoPlayer = VideoPlayerWidget(self)
        self.innerLayout.addWidget(self.videoPlayer)
        self.videoPlayer.hide()

        self.onUpdate = lambda status: None

    def startWebcam(self):
        self.videoPlayer.setSource(0)
        self.videoPlayer.show()
        self.noCamerasLabel.hide()

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
        logging.debug(f"Experiment videos: {experimentVideos}")
        if experimentVideos:
            # Hide the empty state and show the video viewer
            self.noCamerasLabel.hide()

            # Create a camera stream object
            logging.debug(f"Creating camera stream for {experimentVideos[0]}")
            self.videoPlayer.setSource(experimentVideos[0])
            self.videoPlayer.show()
        else:
            self.noCamerasLabel.show()
            self.videoPlayer.hide()
