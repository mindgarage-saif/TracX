from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from PyQt6.QtCore import Qt

from mocap.ui.tasks import MonocularMotionTaskConfig

from ..config.constants import PAD_X, PAD_Y
from .buttons import EstimateMonocularMotionButton
from .frame import Frame


class MotionOptionsMonocular(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.params = MonocularMotionTaskConfig()

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.innerLayout.setSpacing(0)

        # Section heading (centered, bold, larger font, white text)
        heading = QLabel("Motion Estimation", self)
        heading.setProperty("class", "h1")
        self.innerLayout.addWidget(heading)
        self.innerLayout.addSpacing(16)

        # Backend
        label = QLabel("2D Estimation Model", self)
        label.setToolTip(
            "Select the model for 2D pose estimation. Lightweight is faster but less accurate. Performance is slower but more accurate."
        )
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        modelWidget = QWidget(self)
        modelWidget.setProperty("class", "empty")
        self.modelWidgetLayout = QVBoxLayout(modelWidget)
        self.modelWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(modelWidget)

        # Initialize models
        self.lightweightMode = QRadioButton("Lightweight", self)
        self.balancedMode = QRadioButton("Balanced", self)
        self.performanceMode = QRadioButton("Performance", self)

        # Set Default models initially
        self.lightweightMode.setChecked(True)
        self.model = QButtonGroup(self)
        self.model.addButton(self.lightweightMode)
        self.model.addButton(self.balancedMode)
        self.model.addButton(self.performanceMode)
        self.modelWidgetLayout.addWidget(self.lightweightMode)
        self.modelWidgetLayout.addWidget(self.balancedMode)
        self.modelWidgetLayout.addWidget(self.performanceMode)
        self.model.buttonClicked.connect(self.model_changed)

        # Correct Options
        self.innerLayout.addSpacing(16)
        label = QLabel("Video Options", self)
        label.setToolTip(
            "Select the options that fit the uploaded video. Correct Rotation will correct the rotation of the video. Sync Videos will sync the videos."
        )
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)


        self.isRotatedCheckbox = QCheckBox("Is Rotated", self)
        self.isRotatedCheckbox.setProperty("class", "body")
        self.innerLayout.addWidget(self.isRotatedCheckbox)

        self.rotationLabel = QLabel("Video is rotated ...", self)
        self.rotationLabel.setVisible(False)  # Initially hidden
        self.innerLayout.addWidget(self.rotationLabel)

        # Rotation Drop down Menu
        self.rotationOptions = QComboBox(self)
        self.rotationOptions.addItems(["90° Clockwise", "180°", "90° Counter Clockwise"])
        self.rotationOptions.setVisible(False)  # Initially hidden
        self.innerLayout.addWidget(self.rotationOptions)

        self.isRotatedCheckbox.stateChanged.connect(self.toggle_rotation_options)
        self.rotationOptions.currentIndexChanged.connect(self.rotation_option_changed)

        # 3D Estimation Model
        self.innerLayout.addSpacing(16)
        label = QLabel("3D Estimation Model", self)
        label.setToolTip("Select which model to use for 3D pose estimation.")
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        model3DWidget = QWidget(self)
        model3DWidget.setProperty("class", "empty")
        self.model3DWidgetLayout = QVBoxLayout(model3DWidget)
        self.model3DWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(model3DWidget)

        self.BaseLineModel = QRadioButton("Base Line", self)
        self.MotionBert = QRadioButton("MotionBERT", self)

        self.BaseLineModel.setChecked(True)
        self.model3D = QButtonGroup(self)
        self.model3D.addButton(self.BaseLineModel)
        self.model3D.addButton(self.MotionBert)
        self.model3DWidgetLayout.addWidget(self.BaseLineModel)
        self.model3DWidgetLayout.addWidget(self.MotionBert)


        self.innerLayout.addSpacing(16)
        self.innerLayout.addStretch()

        # Button bar
        buttonBar = QWidget(self)
        buttonBar.setProperty("class", "empty")
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setContentsMargins(0, 0, 0, 0)

        # Create Button
        self.estimateMoncularButton = EstimateMonocularMotionButton(self.params, self.onMotionMonocularEstimated)
        buttonBarLayout.addWidget(self.estimateMoncularButton)

        self.downloadButton = QPushButton("Download Motion", self)
        self.downloadButton.setEnabled(False)
        buttonBarLayout.addWidget(self.downloadButton)

        self.innerLayout.addWidget(buttonBar)

        self.onUpdate = lambda status, result: None

    def onMotionMonocularEstimated(self, status, result):
        self.onUpdate(status, result)
        self.downloadButton.setEnabled(status)


    @property
    def data(self):
        return dict(
            # radius=self.radius.value(),
            # thickness=self.thickness.value(),
            # kpt_thr=self.threshold.value() / 100.0,
            draw_bbox=self.draw_bbox.isChecked(),
        )
    
    def toggle_rotation_options(self):
        self.params.correct_rotation = self.isRotatedCheckbox.isChecked()
        if self.isRotatedCheckbox.isChecked():
            self.rotationLabel.setVisible(True)
            self.rotationOptions.setVisible(True)
        else:
            self.rotationLabel.setVisible(False)
            self.rotationOptions.setVisible(False)

    def index_to_rotation_option(self, index):
        return {
            0: 90,
            1: 180,
            2: -90
        }[index]
    
    def rotation_option_changed(self, index):
        self.params.rotation = self.index_to_rotation_option(index)

    def model_changed(self):
        if self.lightweightMode.isChecked():
            self.params.model = "lightweight"
        elif self.balancedMode.isChecked():
            self.params.model = "balanced"
        elif self.performanceMode.isChecked():
            self.params.model = "performance"
        else:
            raise ValueError("Unknown model")