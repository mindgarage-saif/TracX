from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)

from ..config.styles import pauseButtonStyle, startButtonStyle, stopButtonStyle


class ControlPanel(QWidget):
    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.statusBar = parent.statusBar
        self.setObjectName("ControlPanel")
        self.setStyleSheet(
            """
            #ControlPanel {
                background-color: rgba(13, 71, 161, 200);
            }
        """
        )
        self.setFixedHeight(48)
        self.setFixedWidth(parent.width() - 16 * 2 - 10)
        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(16)
        self.setLayout(self.innerLayout)

        # Add start/stop buttons
        self.startButton = QPushButton("Start", self)
        self.startButton.setObjectName("StartButton")
        self.startButton.setStyleSheet(startButtonStyle)
        self.startButton.setFixedWidth(96)
        self.stopButton = QPushButton("Stop", self)
        self.stopButton.setObjectName("StopButton")
        self.stopButton.setStyleSheet(stopButtonStyle)
        self.stopButton.setFixedWidth(96)
        self.innerLayout.addWidget(self.startButton)
        self.innerLayout.addWidget(self.stopButton)

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)

        # Initialize the control panel
        self.setStartCallback(self.onStart)
        self.setStopCallback(self.onStop)
        self.onStop()

    def setStartCallback(self, callback):
        self.startButton.clicked.connect(callback)

    def setStopCallback(self, callback):
        self.stopButton.clicked.connect(callback)

    def onStart(self):
        self.camera.toggle_start()
        if self.camera._is_started:
            self.statusBar.showMessage(f"Webcam started: {self.camera._camera_id}")
            self.startButton.setText("Pause")
            self.startButton.setStyleSheet(pauseButtonStyle)
        else:
            self.statusBar.showMessage("Webcam paused")
            self.startButton.setText("Start")
            self.startButton.setStyleSheet(startButtonStyle)

        self.stopButton.setEnabled(True)

    def onStop(self):
        self.startButton.setEnabled(True)
        self.startButton.setText("Start")
        self.startButton.setStyleSheet(startButtonStyle)
        self.camera.release()
        self.stopButton.setEnabled(False)
