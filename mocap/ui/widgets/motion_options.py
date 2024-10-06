from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ..config.constants import PAD_X, PAD_Y
from .buttons import EstimateMotionButton
from .frame import Frame


class MotionOptions(Frame):
    def __init__(self, parent, params):
        super().__init__(parent)
        self.params = params

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
        label = QLabel("2D Detection Options", self)
        label.setToolTip(
            "Select the model for 2D pose estimation. Lightweight is faster but less accurate. Performance is slower but more accurate."
        )
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        row = QWidget(self)
        row.setProperty("class", "empty")
        rowLayout = QHBoxLayout(row)
        rowLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(row)

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

        # Triangulation options
        self.innerLayout.addSpacing(16)
        label = QLabel("3D Triangulation Options", self)
        label.setToolTip("Select the options for 3D triangulation.")
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        self.correctRotationCheckbox = QCheckBox("Correct Rotation", self)
        self.correctRotationCheckbox.setProperty("class", "body")
        self.innerLayout.addWidget(self.correctRotationCheckbox)

        self.syncVideosCheckbox = QCheckBox("Sync Videos", self)
        self.syncVideosCheckbox.setProperty("class", "body")
        self.syncVideosCheckbox.setChecked(True)
        self.innerLayout.addWidget(self.syncVideosCheckbox)

        self.markerAugmentationCheckbox = QCheckBox("Use Marker Augmentation", self)
        self.markerAugmentationCheckbox.setProperty("class", "body")
        self.innerLayout.addWidget(self.markerAugmentationCheckbox)

        self.correctRotationCheckbox.stateChanged.connect(self.toggleCorrectRotation)
        self.syncVideosCheckbox.stateChanged.connect(self.toggleSyncVideos)
        self.markerAugmentationCheckbox.stateChanged.connect(
            self.toggleMarkerAugmentation
        )

        self.innerLayout.addSpacing(16)
        self.innerLayout.addStretch()

        # Button bar
        buttonBar = QWidget(self)
        buttonBar.setProperty("class", "empty")
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setContentsMargins(0, 0, 0, 0)

        # Create Button
        self.estimateButton = EstimateMotionButton(self, params, self.onMotionEstimated)
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
        self.params.do_synchronization, self.syncVideosCheckbox.isChecked()

    def toggleMarkerAugmentation(self):
        self.params.use_marker_augmentation, self.markerAugmentationCheckbox.isChecked()

    @property
    def data(self):
        return dict(
            # radius=self.radius.value(),
            # thickness=self.thickness.value(),
            # kpt_thr=self.threshold.value() / 100.0,
            draw_bbox=self.draw_bbox.isChecked(),
        )
