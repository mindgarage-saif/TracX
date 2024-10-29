from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from mocap.ui.tasks import MotionTaskConfig

from ..config.constants import PAD_X, PAD_Y
from .buttons import EstimateMotionButton
from .frame import Frame

index_to_model = {
    0: "lightweight",
    1: "balanced",
    2: "performance",
}


class MotionOptions(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.params = MotionTaskConfig()
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
        label = QLabel("Select a Model for 2D estimation", self)
        label.setToolTip(
            "Select the model for 2D pose estimation. Lightweight is faster but less accurate. Performance is slower but more accurate.",
        )
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        row = QWidget(self)
        row.setProperty("class", "empty")
        rowLayout = QHBoxLayout(row)
        rowLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(row)

        # Skeleton widget options
        skeletonWidget = QWidget(self)
        skeletonWidget.setProperty("class", "empty")
        self.skeletonWidgetLayout = QVBoxLayout(skeletonWidget)
        self.skeletonWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(skeletonWidget)
        self.sekeltonOptins = QComboBox(self)
        self.sekeltonOptins.addItems(["Halpe26", "Halpe26 + 17Spine"])
        self.sekeltonOptins.setVisible(True)  # Initially hidden
        self.skeletonWidgetLayout.addWidget(self.sekeltonOptins)
        self.sekeltonOptins.currentIndexChanged.connect(self.sekelton_optins_changed)

        self.modelH26Widget = QWidget(self)
        self.modelH26Widget.setProperty("class", "empty")
        self.modelH26WidgetLayout = QVBoxLayout(self.modelH26Widget)
        self.modelH26WidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.skeletonWidgetLayout.addWidget(self.modelH26Widget)

        self.modelH2617Widget = QWidget(self)
        self.modelH2617Widget.setProperty("class", "empty")
        self.modelH2617WidgetLayout = QVBoxLayout(self.modelH2617Widget)
        self.modelH2617WidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.skeletonWidgetLayout.addWidget(self.modelH2617Widget)
        # label H26 for modes
        labelMode = QLabel("Select a Mode of the 2D Estimator", self)
        labelMode.setToolTip("Select the options for 3D triangulation.")
        labelMode.setProperty("class", "h3")
        labelMode.setWordWrap(True)
        # label H26+17 for modes
        labelMode17 = QLabel("Select a Mode of the 2D Estimator", self)
        labelMode17.setToolTip("Select the options for 3D triangulation.")
        labelMode17.setProperty("class", "h3")
        labelMode17.setWordWrap(True)

        # Initialize models
        self.lightweightMode = QRadioButton("Lightweight", self)
        self.balancedMode = QRadioButton("Balanced", self)
        self.performanceMode = QRadioButton("Performance", self)

        # Modes for the Halpe26 Model initially
        self.lightweightMode.setChecked(True)  # Default
        self.modelH26 = QButtonGroup(self)
        self.modelH26.addButton(self.lightweightMode)
        self.modelH26.addButton(self.balancedMode)
        self.modelH26.addButton(self.performanceMode)
        self.modelH26WidgetLayout.addWidget(labelMode)
        self.modelH26WidgetLayout.addWidget(self.lightweightMode)
        self.modelH26WidgetLayout.addWidget(self.balancedMode)
        self.modelH26WidgetLayout.addWidget(self.performanceMode)
        self.modelH26Widget.setVisible(True)
        self.modelH26.buttonClicked.connect(self.model_changed)

        # Modes for the Halpe26 + 17Spine Model initially
        self.lightweightMode17 = QRadioButton("Lightweight", self)
        self.balancedMode17 = QRadioButton("Balanced", self)
        self.performanceMode17 = QRadioButton("Performance", self)
        self.lightweightMode17.setDisabled(True)
        self.balancedMode17.setDisabled(True)
        # Modes for the Halpe26 + 17Spine Model initially

        self.performanceMode17.setChecked(True)  # Default
        self.modelH26_17 = QButtonGroup(self)
        self.modelH26_17.addButton(self.lightweightMode17)
        self.modelH26_17.addButton(self.balancedMode17)
        self.modelH26_17.addButton(self.performanceMode17)
        self.modelH2617WidgetLayout.addWidget(labelMode17)
        # not implemented right now
        self.modelH2617WidgetLayout.addWidget(self.lightweightMode17)
        self.modelH2617WidgetLayout.addWidget(self.balancedMode17)
        self.modelH2617WidgetLayout.addWidget(self.performanceMode17)
        self.modelH2617Widget.setVisible(False)  # Initially hidden
        self.modelH26_17.buttonClicked.connect(self.model_changedH2617)

        # Triangulation options
        self.innerLayout.addSpacing(16)
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

    def model_changed(self, index):
        # change the model
        self.params.model = index_to_model[index]

    def sekelton_optins_changed(self, index):
        if index == 0:
            self.modelH26Widget.setVisible(True)
            self.modelH2617Widget.setVisible(False)
            self.params.skeleton = "HALPE_26"
            self.params.trackedpoint = "Neck"
            self.model_changed()
        else:
            self.modelH26Widget.setVisible(False)
            self.modelH2617Widget.setVisible(True)
            self.params.skeleton = "CUSTOM"
            self.params.trackedpoint = "Thoracic1"
            self.model_changedH2617()

    def model_changed(self):
        if self.lightweightMode.isChecked():
            self.params.mode = "lightweight"
        elif self.balancedMode.isChecked():
            self.params.mode = "balanced"
        elif self.performanceMode.isChecked():
            self.params.mode = "performance"
        else:
            raise ValueError("Unknown model")

    def model_changedH2617(self):
        if self.lightweightMode17.isChecked():
            self.params.mode = "lightweight"
        elif self.balancedMode17.isChecked():
            self.params.mode = "balanced"
        elif self.performanceMode17.isChecked():
            self.params.mode = "performance"
        else:
            raise ValueError("Unknown model")

    @property
    def data(self):
        return dict(
            # radius=self.radius.value(),
            # thickness=self.thickness.value(),
            # kpt_thr=self.threshold.value() / 100.0,
            draw_bbox=self.draw_bbox.isChecked(),
        )
