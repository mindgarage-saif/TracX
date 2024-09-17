from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ..config.styles import pauseButtonStyle, startButtonStyle, stopButtonStyle


class ControlPanel(QFrame):
    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.statusBar = parent.statusBar
        self.setObjectName("ControlPanel")
        self.setStyleSheet(
            """
            #ControlPanel QLabel {
                color: white;
            }

            #ControlPanel #WebcamButton {
                border-radius: 0px;
                border: 1px solid white;
                background-color: transparent;
                color: white;
                padding: 4px;
            }

            #ControlPanel #VideoButton {
                border-radius: 0px;
                border: 1px solid white;
                background-color: transparent;
                color: white;
                padding: 4px;
            }

            #ControlPanel #CalibrateButton {
                border-radius: 0px;
                border: 1px solid white;
                background-color: transparent;
                color: white;
                padding: 4px;
            }
            
            #ControlPanel #WebcamButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            #ControlPanel #VideoButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            #ControlPanel #CalibrateButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }

            #ControlPanel #ExportMenu {
                padding: 4px;
                border-radius: 8px;
                padding: 8px;
            }
                           
            #ControlPanel #ExportMenu::drop-down {
                border-radius: 8px;
            }
                           
            #ControlPanel #TimerLabel {
                font-size: 16px;
                color: white;
            }
        """
        )
        self.setFixedHeight(96)
        self.setFixedWidth(parent.width() - 16)
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)
        self.setLayout(self.innerLayout)

        # Row 1 (Input source selection: webcam, video upload, image upload)
        self.layout1 = QHBoxLayout(self)
        self.layout1.setContentsMargins(8, 8, 8, 8)
        self.layout1.setSpacing(0)
        self.innerLayout.addLayout(self.layout1)

        # Add input source buttons
        inputSourceLabel = QLabel("Input Source:")
        self.layout1.addWidget(inputSourceLabel)
        self.layout1.addSpacing(8)
        buttonWidth = (self.width() - inputSourceLabel.sizeHint().width() - 16) // 3
        self.webcamButton = QPushButton("Webcam", self)
        self.webcamButton.setObjectName("WebcamButton")
        self.webcamButton.setFixedWidth(buttonWidth)
        self.videoButton = QPushButton("Video", self)
        self.videoButton.setObjectName("VideoButton")
        self.videoButton.setFixedWidth(buttonWidth)
        self.calibrationButton = QPushButton("Calibrate", self)
        self.calibrationButton.setObjectName("CalibrateButton")
        self.calibrationButton.setFixedWidth(buttonWidth)
        self.layout1.addWidget(self.webcamButton)
        self.layout1.addWidget(self.videoButton)
        self.layout1.addWidget(self.calibrationButton)

        # Row 2 (Play/Stop buttons, seek bar, export menu)
        self.layout2 = QHBoxLayout(self)
        self.layout2.setContentsMargins(8, 8, 8, 8)
        self.layout2.setSpacing(8)
        self.innerLayout.addLayout(self.layout2)

        # Add start/stop buttons
        self.startButton = QPushButton("Start", self)
        self.startButton.setObjectName("StartButton")
        self.startButton.setStyleSheet(startButtonStyle)
        self.startButton.setFixedWidth(64)
        self.stopButton = QPushButton("Stop", self)
        self.stopButton.setObjectName("StopButton")
        self.stopButton.setStyleSheet(stopButtonStyle)
        self.stopButton.setFixedWidth(64)
        self.layout2.addWidget(self.startButton)
        self.layout2.addWidget(self.stopButton)

        # Create export dropdown
        self.exportMenu = QComboBox(self)
        self.exportMenu.setObjectName("ExportMenu")
        self.exportMenu.addItem("Export Screenshot")
        self.exportMenu.addItem("Export Annotations")

        # Calculate width of timer label and export menu
        exportWidth = self.exportMenu.sizeHint().width() + 16
        self.exportMenu.setFixedWidth(exportWidth)

        # Add items to layout
        self.layout2.addWidget(self.exportMenu)
        self.layout2.addStretch()

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.webcamButton.clicked.connect(self.enableWebcam)
        self.videoButton.clicked.connect(self.pickVideo)
        self.calibrationButton.clicked.connect(self.startCalibration)

        # Initialize the control panel
        self.setStartCallback(self.onStart)
        self.setStopCallback(self.onStop)
        self.setExportCallback(self.onExport)
        self.onStop()

    def enableWebcam(self):
        cameras = self.camera.get_available_cameras()
        if len(cameras) == 0:
            self.statusBar.showMessage("No cameras available")
            return
        elif len(cameras) == 1:
            self.statusBar.showMessage("Using webcam 0")
            self.camera.change_camera(cameras[0])
        else:
            self.statusBar.showMessage("Using stereo cameras")
            self.camera.change_camera((cameras[0], cameras[1]))

        self.onStart()

    def pickVideo(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov *.webm)")
        file_dialog.setViewMode(QFileDialog.Detail)
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.camera.change_camera(file_path)

            if self.camera._is_video:
                pass
            else:
                self.onStart()

    def startCalibration(self):
        # Set camera to calibration mode
        self.camera.calibrate(delay=5, max_frames=100)

    def setStartCallback(self, callback):
        self.startButton.clicked.connect(callback)

    def setStopCallback(self, callback):
        self.stopButton.clicked.connect(callback)

    def setExportCallback(self, callback):
        self.exportMenu.currentIndexChanged.connect(callback)

    def onStart(self):
        self.camera.toggle_start()
        if self.camera._is_started:
            self.statusBar.showMessage("Webcam started")
            self.startButton.setText("Pause")
            self.startButton.setStyleSheet(pauseButtonStyle)
        else:
            self.statusBar.showMessage("Webcam paused")
            self.startButton.setText("Start")
            self.startButton.setStyleSheet(startButtonStyle)

        self.stopButton.setEnabled(True)

    def onStop(self):
        current_source = self.camera._camera_id
        if current_source is None:
            self.statusBar.showMessage("Select an input source to start")
        elif isinstance(current_source, int):
            self.statusBar.showMessage(f"Using webcam {current_source}")
        elif isinstance(current_source, str):
            self.statusBar.showMessage(f"Using video {current_source}")
        else:
            self.statusBar.showMessage("Invalid input source")

        self.startButton.setEnabled(True)
        self.startButton.setText("Start")
        self.startButton.setStyleSheet(startButtonStyle)
        self.camera.release()
        self.stopButton.setEnabled(False)

    def onExport(self, index):
        self.statusBar.showMessage("Exporting screenshot...")
        path = self.camera.screenshot()
        self.statusBar.showMessage(f"Screenshot saved to {path}")
