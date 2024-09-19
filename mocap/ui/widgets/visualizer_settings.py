from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QLabel, QSlider, QVBoxLayout, QWidget


class VisualizerSettings(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("VisualizerSettings")

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)

        # Section heading (centered, bold, larger font, white text)
        heading = QLabel("Configure Simulation", self)
        heading.setProperty("class", "h3")
        self.innerLayout.addWidget(heading)

        # Keypoint threshold slider
        self.innerLayout.addWidget(QLabel("Setting 1", self))
        self.threshold = QSlider(Qt.Orientation.Horizontal, self)
        self.threshold.setMinimum(0)
        self.threshold.setMaximum(100)
        self.threshold.setValue(50)
        self.innerLayout.addWidget(self.threshold)

        # Keypoint radius slider
        self.innerLayout.addWidget(QLabel("Setting 2", self))
        self.radius = QSlider(Qt.Orientation.Horizontal, self)
        self.radius.setMinimum(1)
        self.radius.setMaximum(20)
        self.radius.setValue(5)
        self.innerLayout.addWidget(self.radius)

        # Line thickness slider
        self.innerLayout.addWidget(QLabel("Setting 3", self))
        self.thickness = QSlider(Qt.Orientation.Horizontal, self)
        self.thickness.setMinimum(1)
        self.thickness.setMaximum(10)
        self.thickness.setValue(3)
        self.innerLayout.addWidget(self.thickness)

        # Checkbox to draw bounding box
        self.draw_bbox = QCheckBox("Setting 4", self)
        self.draw_bbox.setProperty("class", "body")
        self.innerLayout.addWidget(self.draw_bbox)

        self.innerLayout.addStretch()

    def setCallback(self, callback):
        def inner_callback():
            callback(**self.data)

        self.threshold.valueChanged.connect(inner_callback)
        self.radius.valueChanged.connect(inner_callback)
        self.thickness.valueChanged.connect(inner_callback)
        self.draw_bbox.stateChanged.connect(inner_callback)

    @property
    def data(self):
        return dict(
            radius=self.radius.value(),
            thickness=self.thickness.value(),
            kpt_thr=self.threshold.value() / 100.0,
            draw_bbox=self.draw_bbox.isChecked(),
        )
