# from pocketpose.apis import list_models
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
)

from .model_browser import ModelBrowser


class InferencerSettings(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("InferencerSettings")
        self.setStyleSheet(
            """
            #InferencerSettings {
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
            QScrollBar {
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar:vertical {
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QComboBox {
                background-color: #6A004E;
                border: 1px solid #6A004E;
                border-radius: 8px;
                padding: 8px;
                color: white;
            }
            QComboBox:hover {
                border: 1px solid black;
            }
            QComboBox::drop-down {
                border-radius: 8px;
            }
        """
        )

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(16, 16, 16, 16)
        self.innerLayout.setSpacing(16)

        # Section heading (centered, bold, larger font, white text)
        heading = QLabel("Motion Estimation Settings", self)
        heading.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.innerLayout.addWidget(heading)

        # Pose estimation type (2D/3D)
        self.innerLayout.addWidget(QLabel("Backend", self))
        self.radio_2d = QRadioButton("Baseline", self)
        self.radio_2d.setChecked(True)  # Set the default selected button
        self.radio_3d = QRadioButton("Pose2Sim", self)
        row = QHBoxLayout(self)
        row.addWidget(self.radio_2d)
        row.addWidget(self.radio_3d)
        row.addStretch()
        self.innerLayout.addLayout(row)
        self.pose_type = QButtonGroup(self)
        self.pose_type.addButton(self.radio_2d)
        self.pose_type.addButton(self.radio_3d)

        # Keypoints type (body/face/hand/wholebody)
        self.innerLayout.addWidget(QLabel("Keypoints Type", self))
        self.check_body = QRadioButton("Body", self)
        self.check_face = QRadioButton("Face", self)
        self.check_hand = QRadioButton("Hand", self)
        self.check_wholebody = QRadioButton("Whole Body", self)
        self.check_body.setChecked(True)
        row = QHBoxLayout(self)
        row.addWidget(self.check_body)
        row.addWidget(self.check_face)
        row.addWidget(self.check_hand)
        row.addWidget(self.check_wholebody)
        row.addStretch()
        self.innerLayout.addLayout(row)
        self.keypoints_type = QButtonGroup(self)
        self.keypoints_type.addButton(self.check_body)
        self.keypoints_type.addButton(self.check_face)
        self.keypoints_type.addButton(self.check_hand)
        self.keypoints_type.addButton(self.check_wholebody)

        # Quantization radio buttons (FP32/FP16/INT8)
        self.innerLayout.addWidget(QLabel("Quantization", self))
        self.radio_fp32 = QRadioButton("FP32", self)
        self.radio_fp32.setChecked(True)
        self.radio_fp16 = QRadioButton("FP16", self)
        self.radio_int8 = QRadioButton("INT8", self)
        row = QHBoxLayout(self)
        row.addWidget(self.radio_fp32)
        row.addWidget(self.radio_fp16)
        row.addWidget(self.radio_int8)
        row.addStretch()
        self.innerLayout.addLayout(row)
        self.quantization = QButtonGroup(self)
        self.quantization.addButton(self.radio_fp32)
        self.quantization.addButton(self.radio_fp16)
        self.quantization.addButton(self.radio_int8)

        # Instantiate ModelBrowser
        self.modelBrowser = ModelBrowser(self)
        # available_models = (
        #     list_models()
        # )
        # self.modelBrowser.setModels(available_models)

        # Create a QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                background: #091a40;
                color: white;
                border-radius: 8px;
                padding: 0px;
            }
        """
        )
        # Important to make the scroll area adapt to the content
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.modelBrowser)

        # Compute height of the scroll area
        self.scroll_area_height = (
            self.height() - self.innerLayout.sizeHint().height() - 48
        )
        self.scroll_area.setFixedHeight(self.scroll_area_height)
        self.innerLayout.addWidget(self.scroll_area)

    def setModelSelectedCallback(self, callback):
        self.modelBrowser.callback = callback

    def setKeypointThresholdChangedCallback(self, callback):
        self.filter.valueChanged.connect(callback)
