import os

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.core.rotation import rotate_video
from mocap.recording.video_player import VideoPlayer

from ..config.constants import PAD_X, PAD_Y
from .camera_view import CameraView
from .frame import Frame


class VideoPlayerWidget(Frame):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.videoPlayer = None

        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.cameraView = CameraView((1024, 1024))
        self.cameraView.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.innerLayout.addWidget(self.cameraView)
        self.videoPlayer = VideoPlayer(self.cameraView)

        # Add a button bar with toggle play button
        buttonBar = QWidget(self)
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setContentsMargins(0, 0, 0, 0)

        self.playButton = QPushButton("Play", self)
        self.playButton.clicked.connect(self.play)
        buttonBarLayout.addWidget(self.playButton)

        self.stopButton = QPushButton("Stop", self)
        self.stopButton.clicked.connect(self.stop)
        buttonBarLayout.addWidget(self.stopButton)

        # Rotate left and right buttons
        self.rotating = False
        self.rotateLeftButton = QPushButton("Rotate Left", self)
        self.rotateLeftButton.clicked.connect(self.rotateLeft)
        buttonBarLayout.addWidget(self.rotateLeftButton)

        self.rotateRightButton = QPushButton("Rotate Right", self)
        self.rotateRightButton.clicked.connect(self.rotateRight)
        buttonBarLayout.addWidget(self.rotateRightButton)

        buttonBar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.innerLayout.addWidget(buttonBar)

    def setVideoSource(self, video_source):
        self.videoPlayer.setVideoSource(video_source)

    def setRotating(self, rotating):
        self.rotating = rotating
        if rotating:
            self.playButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.rotateLeftButton.setEnabled(False)
            self.rotateRightButton.setEnabled(False)

        else:
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.rotateLeftButton.setEnabled(True)
            self.rotateRightButton.setEnabled(True)

    def rotateLeft(self):
        # Get the current video source
        video = self.videoPlayer._source
        if not video:
            return

        # Stop the video player
        self.videoPlayer.stop()
        self.setRotating(True)

        # Rotate the video
        rotated_video = rotate_video(video, -90)
        os.remove(video)
        os.rename(rotated_video, video)

        # Reset flag and set the video source
        self.setRotating(False)
        self.videoPlayer.setVideoSource(video)

    def rotateRight(self):
        # Get the current video source
        video = self.videoPlayer._source
        if not video:
            return

        # Stop the video player
        self.videoPlayer.stop()
        self.setRotating(True)

        # Rotate the video
        rotated_video = rotate_video(video, 90)
        os.remove(video)
        os.rename(rotated_video, video)

        # Reset flag and set the video source
        self.setRotating(False)
        self.videoPlayer.setVideoSource(video)

    def play(self):
        if self.rotating:
            return

        if not self.videoPlayer.running or self.videoPlayer.paused:
            self.videoPlayer.resume()
        else:
            self.videoPlayer.pause()

    def stop(self):
        if self.rotating:
            return

        self.videoPlayer.stop()
