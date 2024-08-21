from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QFrame, QLabel, QSlider, QVBoxLayout


class VisualizerSettings(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedWidth(parent.width())
        self.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 100);
                border-radius: 8px;
            }
            QLabel {
                background-color: transparent;
                font-size: 14px;
                color: white;
            }
            QSlider {
                background-color: transparent;
                color: black;
            }
            QCheckBox {
                background-color: transparent;
                color: black;
            }
        """
        )

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(16, 16, 16, 16)
        self.innerLayout.setSpacing(8)

        # Section heading (centered, bold, larger font, white text)
        heading = QLabel("Visualizer Parameters", self)
        heading.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.innerLayout.addWidget(heading)

        # Keypoint threshold slider
        self.innerLayout.addWidget(QLabel("Keypoint Threshold: ", self))
        self.threshold = QSlider(Qt.Horizontal, self)
        self.threshold.setMinimum(0)
        self.threshold.setMaximum(100)
        self.threshold.setValue(50)
        self.innerLayout.addWidget(self.threshold)

        # Keypoint radius slider
        self.innerLayout.addWidget(QLabel("Keypoint Radius: ", self))
        self.radius = QSlider(Qt.Horizontal, self)
        self.radius.setMinimum(1)
        self.radius.setMaximum(20)
        self.radius.setValue(5)
        self.innerLayout.addWidget(self.radius)

        # Line thickness slider
        self.innerLayout.addWidget(QLabel("Line Thickness: ", self))
        self.thickness = QSlider(Qt.Horizontal, self)
        self.thickness.setMinimum(1)
        self.thickness.setMaximum(10)
        self.thickness.setValue(3)
        self.innerLayout.addWidget(self.thickness)

        # Checkbox to draw bounding box
        self.draw_bbox = QCheckBox("Show Bounding Box", self)
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
