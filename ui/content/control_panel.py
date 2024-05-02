from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QLabel, QComboBox, QScrollBar


class ControlPanel(QFrame):
    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.statusBar = parent.statusBar
        self.setObjectName("ControlPanel")
        self.setStyleSheet("""
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

            #ControlPanel #ImageButton {
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
            
            #ControlPanel #ImageButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }

            #ControlPanel #StartButton {
                background-color: rgb(0, 139, 0);
                color: white;
            }
                           
            #ControlPanel #StopButton {
                background-color: rgb(139, 0, 0);
                color: white;
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
            
            #ControlPanel #SeekBar {
                background-color: transparent;
                border: 1px solid white;
                border-radius: 8px;
            }
                           
            #ControlPanel #SeekBar::handle {
                background-color: white;
                border: 1px solid black;
                border-radius: 8px;
            }
                           
            #ControlPanel #SeekBar::add-page, #ControlPanel #SeekBar::sub-page {
                background-color: transparent;
            }
                           
            #ControlPanel #SeekBar::add-line, #ControlPanel #SeekBar::sub-line {
                background-color: transparent;
            }
        """)
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
        self.imageButton = QPushButton("Image", self)
        self.imageButton.setObjectName("ImageButton")
        self.imageButton.setFixedWidth(buttonWidth)
        self.layout1.addWidget(self.webcamButton)
        self.layout1.addWidget(self.videoButton)
        self.layout1.addWidget(self.imageButton)

        # Row 2 (Play/Stop buttons, seek bar, export menu)
        self.layout2 = QHBoxLayout(self)
        self.layout2.setContentsMargins(8, 8, 8, 8)
        self.layout2.setSpacing(8)
        self.innerLayout.addLayout(self.layout2)

        # Add start/stop buttons
        self.startButton = QPushButton("Start", self)
        self.startButton.setObjectName("StartButton")
        self.startButton.setFixedWidth(64)
        self.stopButton = QPushButton("Stop", self)
        self.stopButton.setObjectName("StopButton")
        self.stopButton.setFixedWidth(64)
        self.layout2.addWidget(self.startButton)
        self.layout2.addWidget(self.stopButton)

        # Create a timer label
        self.timerLabel = QLabel("00:00:00", self)
        self.timerLabel.setObjectName("TimerLabel")

        # Create export dropdown
        self.exportMenu = QComboBox(self)
        self.exportMenu.setObjectName("ExportMenu")
        self.exportMenu.addItem("Export Screenshot")
        self.exportMenu.addItem("Export Annotations")

        # Calculate width of timer label and export menu
        timerWidth = self.timerLabel.sizeHint().width() + 16  # 16 is padding
        exportWidth = self.exportMenu.sizeHint().width() + 16
        buttonsWidth = self.startButton.width() + self.stopButton.width() + 32
        seekbarWidth = self.width() - timerWidth - exportWidth - buttonsWidth - 16
        self.timerLabel.setFixedWidth(timerWidth)
        self.exportMenu.setFixedWidth(exportWidth)

        # Create a seekbar (use a scroll bar for now)
        self.seekBar = QScrollBar(self)
        self.seekBar.setObjectName("SeekBar")
        self.seekBar.setOrientation(1)
        self.seekBar.setFixedWidth(seekbarWidth)
        self.seekBar.setRange(0, 100)
        self.seekBar.setPageStep(1)
        self.seekBar.setValue(0)
        self.seekBar.setEnabled(False)

        # Add items to layout
        self.layout2.addWidget(self.seekBar)
        self.layout2.addWidget(self.timerLabel)
        self.layout2.addWidget(self.exportMenu)
        self.layout2.addStretch()

        # Initialize the control panel
        self.setStartCallback(self.onStart)
        self.setStopCallback(self.onStop)
        self.setExportCallback(self.onExport)
        self.onStop()

    def setTime(self, time):
        self.timerLabel.setText(time)

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
        else:
            self.statusBar.showMessage("Webcam paused")
            self.startButton.setText("Start")

        self.stopButton.setEnabled(True)

    def onStop(self):
        self.statusBar.showMessage("Webcam stopped")
        self.camera.release()
        self.startButton.setText("Start")
        self.stopButton.setEnabled(False)

    def onExport(self, index):
        self.statusBar.showMessage("Exporting screenshot...")
        path = self.camera.screenshot()
        self.statusBar.showMessage(f"Screenshot saved to {path}")
