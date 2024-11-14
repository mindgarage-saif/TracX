import logging
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from mocap.constants import APP_ASSETS
from mocap.core.rotation import rotate_video
from mocap.recording.video_player import VideoPlayer
from mocap.ui.common import CameraView
from mocap.ui.styles import PAD_X, PAD_Y

logger = logging.getLogger(__name__)


class VideoPlayerWidget(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # Make all disabled widgets text normal colored
        self.videoPlayer = None
        self.videoSource = None

        # Create icons
        self.playIcon = QIcon(
            QPixmap(os.path.join(APP_ASSETS, "icons", "play.png")).scaled(32, 32)
        )

        self.pauseIcon = QIcon(
            QPixmap(os.path.join(APP_ASSETS, "icons", "pause.png")).scaled(32, 32)
        )

        self.stopIcon = QIcon(
            QPixmap(os.path.join(APP_ASSETS, "icons", "stop.png")).scaled(32, 32)
        )

        self.rotateLeftIcon = QIcon(
            QPixmap(os.path.join(APP_ASSETS, "icons", "rotate-left.png")).scaled(32, 32)
        )

        self.rotateRightIcon = QIcon(
            QPixmap(os.path.join(APP_ASSETS, "icons", "rotate-right.png")).scaled(
                32, 32
            )
        )

        # Create an inner layout for the frame
        self.setStyleSheet("background-color: #000000;")
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.innerLayout.setSpacing(PAD_Y)

        # Grid layout for webcam views
        self.gridWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.gridWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.innerLayout.addWidget(self.gridWidget)

        self.preview = CameraView((800, 600), flip=True)
        self.gridLayout.addWidget(self.preview, 0, 0)
        self.videoPlayer = VideoPlayer()
        self.videoPlayer.frame.connect(self.preview.showFrame)
        self.videoPlayer.progress.connect(self.updatePosition)

        # Add a button bar with toggle play button
        self.buttonBar = QWidget(self)
        self.buttonBar.setFixedHeight(32)
        self.buttonBar.setObjectName("MediaControls")
        self.buttonBar.setStyleSheet("""
            #MediaControls { background-color: #aaa; }
            #MediaControls QPushButton {
                background-color: transparent;
                border-radius: 12px;
                border: 0px;
            }
            #MediaControls QPushButton:hover {
                background-color: #888;
            }
            #MediaControls QLineEdit {
                background-color: transparent;
                border-radius: 0px;
                border: 0px;
                padding: 0;
                margin: 0;
                color: black;
            }
        """)
        buttonBarLayout = QHBoxLayout(self.buttonBar)
        buttonBarLayout.setContentsMargins(8, 0, 8, 0)
        buttonBarLayout.setSpacing(8)

        self.playButton = QPushButton()
        self.playButton.setFixedSize(24, 24)
        self.playButton.setIconSize(QSize(18, 18))
        self.playButton.setIcon(self.playIcon)
        self.playButton.clicked.connect(self.play)
        buttonBarLayout.addWidget(self.playButton)

        self.stopButton = QPushButton(self)
        self.stopButton.setFixedSize(24, 24)
        self.stopButton.setIconSize(QSize(18, 18))
        self.stopButton.setIcon(self.stopIcon)
        self.stopButton.clicked.connect(self.stop)
        buttonBarLayout.addWidget(self.stopButton)

        self.lbl = QLineEdit("00:00:00")
        self.lbl.setEnabled(False)
        self.lbl.setReadOnly(True)
        self.lbl.setFixedWidth(60)
        self.lbl.setUpdatesEnabled(True)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl.selectionChanged.connect(lambda: self.lbl.setSelection(0, 0))
        buttonBarLayout.addWidget(self.lbl)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.positionSlider.setEnabled(False)
        self.positionSlider.setRange(0, 100)
        self.positionSlider.setValue(0)
        self.positionSlider.setTickInterval(1)
        self.positionSlider.setStyleSheet("background: transparent;")
        buttonBarLayout.addWidget(self.positionSlider)

        self.elbl = QLineEdit("00:00:00")
        self.elbl.setEnabled(False)
        self.elbl.setReadOnly(True)
        self.elbl.setFixedWidth(60)
        self.elbl.setUpdatesEnabled(True)
        self.elbl.selectionChanged.connect(lambda: self.elbl.setSelection(0, 0))
        buttonBarLayout.addWidget(self.elbl)

        # Rotate left and right buttons
        self.rotating = False
        self.rotateLeftButton = QPushButton(self)
        self.rotateLeftButton.setFixedSize(24, 24)
        self.rotateLeftButton.setIconSize(QSize(18, 18))
        self.rotateLeftButton.setIcon(self.rotateLeftIcon)
        self.rotateLeftButton.clicked.connect(self.rotateLeft)
        buttonBarLayout.addWidget(self.rotateLeftButton)

        self.rotateRightButton = QPushButton(self)
        self.rotateRightButton.setFixedSize(24, 24)
        self.rotateRightButton.setIconSize(QSize(18, 18))
        self.rotateRightButton.setIcon(self.rotateRightIcon)
        self.rotateRightButton.clicked.connect(self.rotateRight)
        buttonBarLayout.addWidget(self.rotateRightButton)

        self.buttonBar.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.innerLayout.addWidget(self.buttonBar)

    def resizeEvent(self, event):
        max_cam_w = self.size().width()
        max_cam_h = self.size().height() - 48
        aspect_ratio = 16 / 9
        current_aspect_ratio = max_cam_w / max_cam_h

        if current_aspect_ratio > aspect_ratio:
            cam_h = max_cam_h
            cam_w = int(cam_h * aspect_ratio)
            if cam_w > max_cam_w:
                cam_w = max_cam_w
                cam_h = int(cam_w / aspect_ratio)
        else:
            cam_w = max_cam_w
            cam_h = int(cam_w / aspect_ratio)
            if cam_h > max_cam_h:
                cam_h = max_cam_h
                cam_w = int(cam_h * aspect_ratio)

        # Resize the video player view
        self.preview.setFixedSize(cam_w, cam_h)

    def setVideoSource(self, video_source):
        self.stop()
        self.buttonBar.setEnabled(video_source is not None)
        if video_source is None:
            self.showEmpty()
            return

        self.videoPlayer.setVideoSource(video_source)
        duration_seconds = int(self.videoPlayer.duration)
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elbl.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def updatePosition(self, current_time, progress):
        hours, remainder = divmod(int(current_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.lbl.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
        self.positionSlider.setValue(int(progress * 100))

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
        self.stop()
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
        self.stop()
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
            self.playButton.setIcon(self.pauseIcon)
        else:
            self.videoPlayer.pause()
            self.playButton.setIcon(self.playIcon)

        self.setFocus()

    def stop(self):
        if self.rotating:
            return

        self.videoPlayer.stop()
        self.playButton.setIcon(self.playIcon)
        self.lbl.setText("00:00:00")
        self.positionSlider.setValue(0)
        self.setFocus()

    def showEmpty(self):
        self.preview.clear()
        self.lbl.setText("00:00:00")
        self.elbl.setText("00:00:00")
        self.positionSlider.setValue(0)
        self.playButton.setIcon(self.playIcon)
        self.setFocus()
