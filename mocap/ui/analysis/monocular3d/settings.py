from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from mocap.core.configs import MotionTaskConfig, VisualizeTaskConfig
from mocap.core.configs.base import Engine, ExperimentMode, LiftingModel, PoseModel
from mocap.ui.analysis import EstimateMotionButton, VisualizeMotionButton
from mocap.ui.common import IconButton, LabeledWidget


class ModelSelection(QWidget):
    def __init__(self, parent, cfg):
        super().__init__(parent)
        self.cfg = cfg
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.modelComboBox = QComboBox(self)
        self.modelComboBox.addItems(LiftingModel.__members__.keys())
        layout.addWidget(self.modelComboBox)
        self.setLayout(layout)

    def on_model_changed(self, callback):
        def callback_wrapper():
            selected_model = self.modelComboBox.currentText()
            self.cfg.model = selected_model
            callback()

        self.modelComboBox.currentIndexChanged.connect(callback_wrapper)


class SkeletonSelection(QWidget):
    MODEL_SKELETON_MAP = {
        LiftingModel.BASELINE: [PoseModel.HALPE_26],
        LiftingModel.MOTIONBERT: [PoseModel.HALPE_26],
    }

    def __init__(self, parent, cfg):
        super().__init__(parent)
        self.cfg = cfg
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.skeletonComboBox = QComboBox(self)
        self.skeletonComboBox.addItems(PoseModel.__members__.keys())
        layout.addWidget(self.skeletonComboBox)

        self.setLayout(layout)

    def update_skeleton_options(self, model_name):
        """Update skeleton options based on the selected model."""
        allowed_skeletons = self.MODEL_SKELETON_MAP.get(model_name, [])
        self.skeletonComboBox.clear()
        self.skeletonComboBox.addItems(allowed_skeletons)

    def on_skeleton_changed(self, callback):
        def callback_wrapper():
            selected_skeleton = self.skeletonComboBox.currentText()
            self.cfg.skeleton = selected_skeleton
            callback(selected_skeleton)

        self.skeletonComboBox.currentIndexChanged.connect(callback_wrapper)


class VideoOptions(QWidget):
    ROTATION_OPTIONS = ["90° Clockwise", "180°", "90° Counter Clockwise"]

    def __init__(self, params, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Rotated Checkbox
        self.isRotatedCheckbox = QCheckBox("Is Rotated", self)
        layout.addWidget(self.isRotatedCheckbox)

        # Rotation Options
        self.rotationOptions = QComboBox(self)
        self.rotationOptions.addItems(self.ROTATION_OPTIONS)
        self.rotationOptions.setVisible(False)  # Initially hidden
        layout.addWidget(self.rotationOptions)

        # Signal Connections
        self.isRotatedCheckbox.stateChanged.connect(self.toggle_rotation_options)
        self.rotationOptions.currentIndexChanged.connect(self.rotation_option_changed)

        self.params = params
        self.setLayout(layout)

    def toggle_rotation_options(self):
        self.params.correct_rotation = self.isRotatedCheckbox.isChecked()
        self.rotationOptions.setVisible(self.isRotatedCheckbox.isChecked())

    def rotation_option_changed(self, index):
        self.params.rotation = {0: 90, 1: 180, 2: -90}[index]


class Monocular3DSettingsPanel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.cfg = MotionTaskConfig()
        self.cfg.mode = ExperimentMode.MONOCULAR
        self.cfg.engine = Engine.RTMLIB

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        # Section heading
        heading = QLabel("Monocular 3D Analysis", self)
        heading.setProperty("class", "h1")
        main_layout.addWidget(heading)

        # Model Selection
        self.model_selection = ModelSelection(self, self.cfg)
        self.model_selection.on_model_changed(self.model_changed)
        main_layout.addWidget(LabeledWidget("Select a Model", self.model_selection))

        # Skeleton Selection
        self.skeleton_selection = SkeletonSelection(self, self.cfg)
        main_layout.addWidget(
            LabeledWidget("Select a Skeleton", self.skeleton_selection)
        )

        # # Video Options
        # self.video_options = VideoOptions(self.params, self)
        # main_layout.addWidget(LabelledWidget(
        #     "Video Options", self.video_options))

        main_layout.addStretch()

        # Button Bar
        button_bar = self.create_button_bar()
        main_layout.addWidget(button_bar)

        self.model_changed()

    def create_button_bar(self):
        button_bar = QWidget(self)
        button_bar.setProperty("class", "empty")
        layout = QHBoxLayout(button_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Estimate Motion Button
        self.estimate_button = EstimateMotionButton(self.onMotionMonocularEstimated)
        layout.addWidget(self.estimate_button)

        # Download Button
        self.downloadButton = IconButton("export.png", 24, self)
        self.downloadButton.setEnabled(False)
        layout.addWidget(self.downloadButton)

        self.visualize_cfg = VisualizeTaskConfig()
        self.visualize_button = VisualizeMotionButton(
            self.visualize_cfg,
            self.onVisualizationsCreated,
        )
        layout.addWidget(self.visualize_button)

        return button_bar

    def onMotionMonocularEstimated(self, status, result):
        self.downloadButton.setEnabled(status)

    def onVisualizationsCreated(self, status, result):
        pass

    def model_changed(self):
        selected_model = self.model_selection.modelComboBox.currentText()
        self.skeleton_selection.update_skeleton_options(selected_model)