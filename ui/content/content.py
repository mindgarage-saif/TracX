import time

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QLabel, QWidget, QComboBox, QScrollBar
from PyQt5.QtCore import QTimer

from pocketpose import PoseInferencer
from pocketpose.registry import VISUALIZERS
from pocketpose.apis import list_models

from ..data import RuntimeParams
from ..widgets import Chip
from .camera import Camera


class ControlPanel(QFrame):
    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.statusBar = parent.statusBar
        self.setObjectName("ControlPanel")
        self.setStyleSheet("""
            #ControlPanel {
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
        self.setFixedHeight(48)
        self.setFixedWidth(parent.width() - 16)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(8)
        self.setLayout(self.layout)

        # Add start/stop buttons
        self.startButton = QPushButton("Start", self)
        self.startButton.setObjectName("StartButton")
        self.startButton.setFixedWidth(64)
        self.stopButton = QPushButton("Stop", self)
        self.stopButton.setObjectName("StopButton")
        self.stopButton.setFixedWidth(64)
        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.stopButton)

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
        self.layout.addWidget(self.seekBar)
        self.layout.addWidget(self.timerLabel)
        self.layout.addWidget(self.exportMenu)
        self.layout.addStretch()

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


class WebcamLayout(QFrame):
    def __init__(self, parent, on_frame_fn, refresh_rate=30, camera_id=0):
        super().__init__(parent)
        self.statusBar = parent.statusBar
        aspect_ratio = 4 / 3
        cam_w = parent.width() - 48
        cam_h = int(cam_w / aspect_ratio)
        size = cam_h, cam_w

        self.setObjectName("WebcamLayout")
        self.setFixedWidth(size[1])
        self.setStyleSheet("""
            #WebcamLayout {
                background-color: rgba(0, 0, 0, 0.5);
                border: 1px solid whitesmoke;
                border-radius: 8px;
                padding: 4px;
                color: white;
            }
                           
            QPushButton {
                background-color: white;
                border: 1px solid black;
                border-radius: 8px;
                padding: 4px;
                color: black;
            }
        """)

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)

        self.size = size
        self.on_frame_fn = on_frame_fn
        self.refresh_rate = refresh_rate

        # Status bar
        self.status_bar = QHBoxLayout()
        self.status_bar.setContentsMargins(8, 8, 8, 8)
        self.status_bar.setSpacing(8)
        self.innerLayout.addLayout(self.status_bar)
        self.innerLayout.addSpacing(32)

        # Set up the labels
        self.modelName = Chip("MobileNetV2")  # TODO: Show current model
        self.modelRuntime = Chip("ONNX")  # TODO: Show current runtime
        self.modelQuant = Chip("FP32")  # TODO: Show current quantization
        self.modelFLOPs = Chip("0.0 GFLOPs")
        self.modelParams = Chip("0.0 M")
        self.fpsLabel = Chip("FPS: 0")
        self.inferenceLabel = Chip("Latency: 0.0 ms")

        # Connect signals
        self.runtimeParams = RuntimeParams()
        self.runtimeParams.fpsUpdated.connect(self.update_fps_label)
        self.runtimeParams.inferenceSpeedUpdated.connect(self.update_inference_label)
        
        # Labels for stats
        self.status_bar.addWidget(self.modelName)
        self.status_bar.addWidget(self.modelRuntime)
        self.status_bar.addWidget(self.modelQuant)
        self.status_bar.addWidget(self.modelFLOPs)
        self.status_bar.addWidget(self.modelParams)
        self.status_bar.addWidget(self.fpsLabel)
        self.status_bar.addWidget(self.inferenceLabel)
        self.status_bar.addStretch()

        # Create the camera
        self.camera = Camera(size, camera_id)
        self.innerLayout.addWidget(self.camera._view)
        self.innerLayout.addStretch()

        # Create the control panel
        self.controlPanel = ControlPanel(self.camera, parent=self)
        self.innerLayout.addWidget(self.controlPanel)

        # Create a timer to update the webcam feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(refresh_rate)

    def update_fps_label(self, fps):
        self.fpsLabel.setText(f"FPS: {fps:.0f}")

    def update_inference_label(self, speed):
        self.inferenceLabel.setText(f"Latency: {speed:.1f} ms")

    def height(self):
        return self.size[0] + self.button_layout.sizeHint().height()

    def update(self):
        ret, frame = self.camera.read()
        if not ret or frame is None:
            return

        if self.on_frame_fn is not None:
            frame = self.on_frame_fn(frame)

        self.camera._view.show(frame)


class Content(QFrame):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.statusBar = parent.statusBar()
        self.setFixedWidth(int(parent.width() * 0.7))
        self.setFixedHeight(parent.height() - 20)
        self.setStyleSheet("""
        """)

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(16, 16, 16, 16)
        self.innerLayout.setSpacing(8)

        # Create the webcam view
        self.webcam_layout = WebcamLayout(
            self,
            self.update_frame,
            camera_id=0
        )
        self.webcam_layout.setFixedHeight(self.height() - 52)
        self.innerLayout.addWidget(self.webcam_layout)

        # Initialize model
        self.available_models = list_models()
        default_model = self.available_models[0]
        self.change_model(default_model)

        # Add stretch to push the webcam feed to the top
        self.innerLayout.addStretch()

    def change_model(self, model_name):
        self.current_model = model_name
        self.inferencer = PoseInferencer(self.current_model)
        self.visualizer = VISUALIZERS.build(
            "PoseVisualizer", 
            self.inferencer.model.keypoints_type
        )
        self.frame_count = 0
        self.start_time = time.time()

    def update_visualizer_params(self, radius, thickness, kpt_thr, draw_bbox):
        self.visualizer.radius = radius
        self.visualizer.thickness = thickness
        self.visualizer.kpt_thr = kpt_thr
        self.visualizer.draw_bbox = draw_bbox

    def update_frame(self, frame):
        # Perform pose inference
        keypoints = self.inferencer.infer(frame)

        # Process frame for display (resize, convert color, draw keypoints)
        frame = self.visualizer.visualize(frame, keypoints)

        # Update frame count and calculate FPS
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            fps = self.frame_count / elapsed_time
            self.webcam_layout.runtimeParams.set_fps(fps)

        # Update inference speed
        inference_speed = self.inferencer.last_inference_duration_ms
        self.webcam_layout.runtimeParams.set_inference_speed(inference_speed)

        return frame
