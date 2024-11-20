import logging
import os

from PyQt6.QtCore import QSize, Qt, pyqtSignal
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
from mocap.core.processor import VideoProcessor
from mocap.core.rotation import rotate_video
from mocap.recording.video_player import VideoPlayer
from mocap.ui.common import CameraView
from mocap.ui.styles import PAD_X, PAD_Y

logger = logging.getLogger(__name__)


class VideoPlayerController(QWidget):
    play = pyqtSignal()
    stop = pyqtSignal()
    rotateLeft = pyqtSignal()
    rotateRight = pyqtSignal()

    def __init__(self, parent, height=32):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(height)
        self.setStyleSheet("""
            QPushButton {
                background-color: #aaa;
                border-radius: 12px;
                border: 0px;
            }
            QPushButton:hover {
                background-color: #888;
            }
            QLineEdit {
                background-color: transparent;
                border-radius: 0px;
                border: 0px;
                padding: 0;
                margin: 0;
                color: white;
            }
        """)
        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(8, 0, 8, 0)
        self.innerLayout.setSpacing(8)

        # Create icons
        def createIcon(name):
            path = os.path.join(APP_ASSETS, "icons", f"{name}.png")
            return QIcon(QPixmap(path).scaled(32, 32))

        self.playIcon = createIcon("play")
        self.pauseIcon = createIcon("pause")
        self.stopIcon = createIcon("stop")
        self.rotateLeftIcon = createIcon("rotate-left")
        self.rotateRightIcon = createIcon("rotate-right")

        self.playButton = QPushButton()
        self.playButton.setFixedSize(24, 24)
        self.playButton.setIconSize(QSize(18, 18))
        self.playButton.setIcon(self.playIcon)
        self.playButton.clicked.connect(self.play.emit)
        self.innerLayout.addWidget(self.playButton)

        self.stopButton = QPushButton(self)
        self.stopButton.setFixedSize(24, 24)
        self.stopButton.setIconSize(QSize(18, 18))
        self.stopButton.setIcon(self.stopIcon)
        self.stopButton.clicked.connect(self.stop.emit)
        self.innerLayout.addWidget(self.stopButton)

        self.lbl = QLineEdit("00:00:00")
        self.lbl.setEnabled(False)
        self.lbl.setReadOnly(True)
        self.lbl.setFixedWidth(60)
        self.lbl.setUpdatesEnabled(True)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl.selectionChanged.connect(lambda: self.lbl.setSelection(0, 0))
        self.innerLayout.addWidget(self.lbl)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.positionSlider.setEnabled(False)
        self.positionSlider.setRange(0, 100)
        self.positionSlider.setValue(0)
        self.positionSlider.setTickInterval(1)
        self.positionSlider.setStyleSheet("background: transparent;")
        self.innerLayout.addWidget(self.positionSlider)

        self.elbl = QLineEdit("00:00:00")
        self.elbl.setEnabled(False)
        self.elbl.setReadOnly(True)
        self.elbl.setFixedWidth(60)
        self.elbl.setUpdatesEnabled(True)
        self.elbl.selectionChanged.connect(lambda: self.elbl.setSelection(0, 0))
        self.innerLayout.addWidget(self.elbl)

        # Rotate left and right buttons
        self.rotateLeftButton = QPushButton(self)
        self.rotateLeftButton.setFixedSize(24, 24)
        self.rotateLeftButton.setIconSize(QSize(18, 18))
        self.rotateLeftButton.setIcon(self.rotateLeftIcon)
        self.rotateLeftButton.clicked.connect(self.rotateLeft.emit)
        self.innerLayout.addWidget(self.rotateLeftButton)

        self.rotateRightButton = QPushButton(self)
        self.rotateRightButton.setFixedSize(24, 24)
        self.rotateRightButton.setIconSize(QSize(18, 18))
        self.rotateRightButton.setIcon(self.rotateRightIcon)
        self.rotateRightButton.clicked.connect(self.rotateRight.emit)
        self.innerLayout.addWidget(self.rotateRightButton)

    def setDuration(self, duration):
        hours, remainder = divmod(int(duration), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elbl.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def setCurrentPosition(self, current_time, progress):
        hours, remainder = divmod(int(current_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.lbl.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
        self.positionSlider.setValue(int(progress * 100))

    def setPlaying(self):
        self.playButton.setIcon(self.pauseIcon)

    def setPaused(self):
        self.playButton.setIcon(self.playIcon)

    def reset(self):
        self.playButton.setIcon(self.playIcon)
        self.lbl.setText("00:00:00")
        self.positionSlider.setValue(0)

    def clear(self):
        self.lbl.setText("00:00:00")
        self.elbl.setText("00:00:00")
        self.positionSlider.setValue(0)
        self.playButton.setIcon(self.playIcon)


class VideoPlayerWidget(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.innerLayout.setSpacing(PAD_Y)

        # Grid layout for video views
        self.gridWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.gridWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.innerLayout.addWidget(self.gridWidget)

        # Rotation flag
        self.rotating = False

        # Create the video player and processor
        self.player = VideoPlayer()
        self.processor = VideoProcessor(self.player)

        # Create the preview widget
        self.createPreview(800, 600)

        # Create the controller
        self.controller = VideoPlayerController(self)
        self.innerLayout.addWidget(self.controller)

        # Connect controller signals
        self.controller.play.connect(self.play)
        self.controller.stop.connect(self.stop)
        self.controller.rotateLeft.connect(self.rotateLeft)
        self.controller.rotateRight.connect(self.rotateRight)
        self.player.progress.connect(self.controller.setCurrentPosition)
        self.processor.frame.connect(self.showFrame)

        # Show the empty state
        self.showEmpty()

    def setSource(self, source):
        self.stop()
        if not source:
            self.controller.clear()
            self.controller.setEnabled(False)
            self.showEmpty()
            return

        # Enable the controller
        self.controller.setEnabled(True)

        self.player.setSource(source)
        self.controller.setDuration(self.player.duration)

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

        self.resizePreview(cam_w, cam_h)

    def createPreview(self, cam_w, cam_h):
        self.preview = CameraView((cam_w, cam_h), flip=False)
        self.gridLayout.addWidget(self.preview, 0, 0)

    def resizePreview(self, cam_w, cam_h):
        # Resize the video player view
        self.preview.setFixedSize(cam_w, cam_h)

    def setRotating(self, rotating):
        self.rotating = rotating
        self.controller.setEnabled(not rotating)

    def rotate(self, angle):
        # Get the current video source
        video = self.player._source
        if not video:
            return

        # Stop the video player
        self.stop()
        self.controller.setEnabled(False)
        self.rotating = True

        # Rotate the video
        rotated_video = rotate_video(video, angle)
        os.remove(video)
        os.rename(rotated_video, video)

        # Reset flag and set the video source
        self.rotating = False
        self.controller.setEnabled(True)
        self.player.setSource(video)

    def rotateLeft(self):
        self.rotate(-90)

    def rotateRight(self):
        self.rotate(90)

    def play(self):
        if self.rotating:
            return

        if not self.player.running or self.player.paused:
            self.player.resume()
            self.processor.start()
            self.controller.setPlaying()
        else:
            self.player.pause()
            self.processor.pause()
            self.controller.setPaused()

        self.setFocus()

    def stop(self):
        if self.rotating:
            return

        self.player.stop()
        self.processor.stop()
        self.controller.reset()
        self.setFocus()

    def showEmpty(self):
        self.preview.clear()
        self.controller.clear()
        self.setFocus()

    def showFrame(self, frame):
        self.preview.showFrame(frame)
