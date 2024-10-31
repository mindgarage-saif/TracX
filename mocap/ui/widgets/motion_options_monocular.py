from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mocap.ui.tasks import MotionTaskConfig, VisualizeTaskConfig

from ..config.constants import PAD_X, PAD_Y
from .buttons import EstimateMotionButton, VisualizeMotionButton


class LabelledWidget(QWidget):
    """Utility widget with a label and a child widget, for cleaner UI sections."""

    def __init__(self, label_text, widget, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(label_text)
        label.setProperty("class", "h2")
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)


class ModelSelection(QWidget):
    SUPPORTED_MODELS = ["Baseline", "MotionBERT", "RTMPose3D"]

    def __init__(self, parent, cfg):
        super().__init__(parent)
        self.cfg = cfg
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.modelComboBox = QComboBox(self)
        self.modelComboBox.addItems(self.SUPPORTED_MODELS)
        layout.addWidget(self.modelComboBox)
        self.setLayout(layout)

    def on_model_changed(self, callback):
        def callback_wrapper():
            selected_model = self.modelComboBox.currentText()
            self.cfg.model = selected_model
            callback(selected_model)

        self.modelComboBox.currentIndexChanged.connect(callback_wrapper)


class SkeletonSelection(QWidget):
    SUPPORTED_SKELETONS = [
        "COCO_17",
        "COCO_133",
        "DFKI_Body43",
        "DFKI_Spine17",
        "HALPE_26",
    ]
    MODEL_SKELETON_MAP = {
        "Baseline": ["HALPE_26"],
        "MotionBERT": ["HALPE_26"],
        "RTMPose3D": ["HALPE_26"],
    }

    def __init__(self, parent, cfg):
        super().__init__(parent)
        self.cfg = cfg
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.skeletonComboBox = QComboBox(self)
        self.skeletonComboBox.addItems(self.SUPPORTED_SKELETONS)
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


class MotionOptionsMonocular(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.cfg = MotionTaskConfig()
        self.cfg.mode = "monocular"
        self.cfg.engine = "Custom"

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        main_layout.setSpacing(PAD_Y)
        self.setStyleSheet("QComboBox { border: 2px solid #ccc; border-radius: 8px; }")

        model_layout = QHBoxLayout()
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.setSpacing(PAD_X)
        model_widget = QWidget(self)
        model_widget.setProperty("class", "empty")
        model_widget.setLayout(model_layout)

        # Model Selection
        self.model_selection = ModelSelection(self, self.cfg)
        self.model_selection.on_model_changed(self.model_changed)
        model_layout.addWidget(LabelledWidget("Select a Model", self.model_selection))

        # Skeleton Selection
        self.skeleton_selection = SkeletonSelection(self, self.cfg)
        model_layout.addWidget(
            LabelledWidget("Select a Skeleton", self.skeleton_selection)
        )

        # # Video Options
        # self.video_options = VideoOptions(self.params, self)
        # main_layout.addWidget(LabelledWidget(
        #     "Video Options", self.video_options))

        # Button Bar
        button_bar = self.create_button_bar()

        main_layout.addWidget(model_widget)
        main_layout.addWidget(button_bar)

        self.model_changed()

    def create_button_bar(self):
        button_bar = QWidget(self)
        button_bar.setProperty("class", "empty")
        layout = QHBoxLayout(button_bar)
        layout.setContentsMargins(0, 0, 0, 0)

        # Estimate Motion Button
        self.estimate_button = EstimateMotionButton(
            self.cfg, self.onMotionMonocularEstimated
        )
        layout.addWidget(self.estimate_button)

        # Download Button
        self.download_button = QPushButton("Download Motion", self)
        self.download_button.setEnabled(False)
        layout.addWidget(self.download_button)

        self.visualize_cfg = VisualizeTaskConfig()
        self.visualize_button = VisualizeMotionButton(
            self.visualize_cfg,
            self.onVisualizationsCreated,
        )
        layout.addWidget(self.visualize_button)

        return button_bar

    def onMotionMonocularEstimated(self, status, result):
        self.download_button.setEnabled(status)

    def onVisualizationsCreated(self, status, result):
        print("Saving visualizations:", status, result)

    def model_changed(self):
        selected_model = self.model_selection.modelComboBox.currentText()
        self.skeleton_selection.update_skeleton_options(selected_model)
