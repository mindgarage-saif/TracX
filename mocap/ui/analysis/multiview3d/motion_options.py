from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mocap.core.configs import MotionTaskConfig
from mocap.core.configs.base import Engine, PoseModel
from mocap.ui.common import Frame, LabeledWidget, RadioGroup
from mocap.ui.styles import PAD_X, PAD_Y

from ..buttons import EstimateMotionButton

index_to_model = {
    0: "lightweight",
    1: "balanced",
    2: "performance",
}


class MotionOptions(Frame):
    SUPPORTED_ENGINES = Engine.__members__.keys()
    SUPPORTED_MODES = ["Lite", "Medium", "Heavy"]
    MODEL_MODE_MAP = {
        Engine.POSE2SIM: ["Lite", "Medium", "Heavy"],
        Engine.RTMLIB: ["Heavy"],
    }
    SUPPORTED_SKELTONS = PoseModel.__members__.keys()
    MODEL_SKELETON_MAP = {
        Engine.POSE2SIM: [PoseModel.COCO_17, PoseModel.COCO_133, PoseModel.HALPE_26],
        Engine.RTMLIB: [PoseModel.DFKI_BODY43, PoseModel.DFKI_SPINE17],
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.params = MotionTaskConfig()
        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.innerLayout.setSpacing(0)

        # Section heading (centered, bold, larger font, white text)
        heading = QLabel("Multiview Motion Estimation", self)
        heading.setProperty("class", "h1")
        self.innerLayout.addWidget(heading)
        self.innerLayout.addSpacing(8)

        # Skeleton to use
        skeletons = QComboBox(self)
        skeletons.addItems(self.SUPPORTED_SKELTONS)
        skeletons.currentIndexChanged.connect(self.toggle_pose_model)
        self.innerLayout.addWidget(LabeledWidget("Select a Skeleton", skeletons, self))
        self.innerLayout.addSpacing(8)

        # Motion estimation performance
        performance = RadioGroup("Performance", self)
        performance.addButton("Lite (Fast)")
        performance.addButton("Medium")
        performance.addButton("Heavy (Accurate)")
        performance.selectDefault()
        self.innerLayout.addWidget(performance)
        self.innerLayout.addSpacing(8)

        # Triangulation options
        label = QLabel("Triangulation Config", self)
        label.setToolTip("Select the options for 3D triangulation.")
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        self.correctRotationCheckbox = QCheckBox("Fix Rotation", self)
        self.correctRotationCheckbox.setProperty("class", "body")
        self.innerLayout.addWidget(self.correctRotationCheckbox)

        self.multiPersonChecked = QCheckBox("Multiple People", self)
        self.multiPersonChecked.setProperty("class", "body")
        self.innerLayout.addWidget(self.multiPersonChecked)

        self.markerAugmentationCheckbox = QCheckBox("Use Marker Augmentation", self)
        self.markerAugmentationCheckbox.setProperty("class", "body")
        self.innerLayout.addWidget(self.markerAugmentationCheckbox)

        self.correctRotationCheckbox.stateChanged.connect(self.toggleCorrectRotation)
        self.multiPersonChecked.stateChanged.connect(self.toggleSyncVideos)
        self.markerAugmentationCheckbox.stateChanged.connect(
            self.toggleMarkerAugmentation,
        )

        self.innerLayout.addSpacing(16)
        self.innerLayout.addStretch()

        # Button bar
        buttonBar = QWidget(self)
        buttonBar.setProperty("class", "empty")
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setContentsMargins(0, 0, 0, 0)

        # Create Button
        self.estimateButton = EstimateMotionButton(self.params, self.onMotionEstimated)
        buttonBarLayout.addWidget(self.estimateButton)

        self.downloadButton = QPushButton("Download Motion", self)
        self.downloadButton.setEnabled(False)
        buttonBarLayout.addWidget(self.downloadButton)

        self.innerLayout.addWidget(buttonBar)

        self.onUpdate = lambda status, result: None

    def onMotionEstimated(self, status, result):
        self.onUpdate(status, result)
        self.downloadButton.setEnabled(status)

    def toggleCorrectRotation(self):
        self.params.correct_rotation = self.correctRotationCheckbox.isChecked()

    def toggleSyncVideos(self):
        self.params.multi_person, self.multiPersonChecked.isChecked()

    def toggleMarkerAugmentation(self):
        self.params.use_marker_augmentation, self.markerAugmentationCheckbox.isChecked()

    def toggle_pose_model(self, index):
        self.params.pose2d_model = PoseModel._member_names_[index]
        # if index == 0:
        #     self.modelH26Widget.setVisible(True)
        #     self.modelH2617Widget.setVisible(False)
        #     self.params.trackedpoint = "Neck"
        #     self.model_changed()
        # else:
        #     self.modelH26Widget.setVisible(False)
        #     self.modelH2617Widget.setVisible(True)
        #     self.params.pose2d_model = PoseModel.DFKI_BODY43
        #     self.params.trackedpoint = "Thoracic1"
        #     self.model_changedH2617()

    def model_changed(self):
        if self.lightweightMode.isChecked():
            self.params.pose2d_kwargs.mode = "lightweight"
        elif self.balancedMode.isChecked():
            self.params.pose2d_kwargs.mode = "balanced"
        elif self.modelH26.isChecked():
            self.params.pose2d_kwargs.mode = "performance"
        else:
            raise ValueError("Unknown mode")

    def model_changedH2617(self):
        if self.lightweightMode17.isChecked():
            self.params.pose2d_kwargs.mode = "lightweight"
        elif self.balancedMode17.isChecked():
            self.params.pose2d_kwargs.mode = "balanced"
        elif self.performanceMode17.isChecked():
            self.params.pose2d_kwargs.mode = "performance"
        else:
            raise ValueError("Unknown mode")

    @property
    def data(self):
        return dict(
            # radius=self.radius.value(),
            # thickness=self.thickness.value(),
            # kpt_thr=self.threshold.value() / 100.0,
            draw_bbox=self.draw_bbox.isChecked(),
        )
