from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QWidget

from ..config.styles import startButtonStyle, stopButtonStyle


class ControlPanel(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.statusBar = parent.statusBar
        self.setObjectName("ControlPanel")
        self.setFixedHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(16)
        self.setLayout(self.innerLayout)

        # Add start/stop buttons
        self.startButton = QPushButton("Record", self)
        self.startButton.setObjectName("StartButton")
        self.startButton.setStyleSheet(startButtonStyle)
        self.startButton.setFixedWidth(96)
        self.innerLayout.addWidget(self.startButton)

        self.startButton.setEnabled(True)

        # Initialize the control panel
        self.setStartCallback(self.onStart)
        self.onStop()

    def setStartCallback(self, callback):
        self.startButton.clicked.connect(callback)

    def onStart(self):
        self.controller.toggle_capture()
        if self.controller._camera.running:
            self.statusBar.showMessage(f"Webcam started: {self.controller._camera_id}")
            self.startButton.setText("Stop")
            self.startButton.setStyleSheet(stopButtonStyle)
        else:
            self.statusBar.showMessage("Webcam paused")
            self.startButton.setText("Record")
            self.startButton.setStyleSheet(startButtonStyle)

    def onStop(self):
        self.startButton.setEnabled(True)
        self.startButton.setText("Record")
        self.startButton.setStyleSheet(startButtonStyle)
        self.controller.release()
