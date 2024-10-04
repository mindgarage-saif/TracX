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

from .buttons import EstimateMotionButton


class MotionOptions(QWidget):
    def __init__(self, parent, params):
        super().__init__(parent)
        self.params = params

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setSpacing(0)

        # Section heading (centered, bold, larger font, white text)
        heading = QLabel("Motion Estimation", self)
        heading.setProperty("class", "h1")
        self.innerLayout.addWidget(heading)
        self.innerLayout.addSpacing(16)

        # Backend
        label = QLabel("2D Detection Options", self)
        label.setToolTip(
            "Select the backend for 2D pose estimation. Pose2Sim uses RTNPose. Custom allows using your own model."
        )
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        row = QWidget(self)
        rowLayout = QHBoxLayout(row)
        rowLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(row)

        # Backend
        label = QLabel("Backend:", self)
        label.setToolTip(
            "Select the backend for 2D pose estimation. Pose2Sim uses RTNPose. Custom allows using your own model."
        )
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        rowLayout.addWidget(label)

        self.internalBackend = QRadioButton("Pose2Sim", self)
        self.internalBackend.setChecked(True)  # Set the default selected button
        self.externalBackend = QRadioButton("Custom", self)
        rowLayout.addWidget(self.internalBackend)
        rowLayout.addWidget(self.externalBackend)
        rowLayout.addStretch()

        self.backend = QButtonGroup(self)
        self.backend.addButton(self.internalBackend)
        self.backend.addButton(self.externalBackend)

        modelWidget = QWidget(self)
        self.modelWidgetLayout = QHBoxLayout(modelWidget)
        self.modelWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(modelWidget)

        label = QLabel("Mode:", self)
        label.setToolTip(
            "Select the model for 2D pose estimation. Lightweight is faster but less accurate. Performance is slower but more accurate."
        )
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        self.modelWidgetLayout.addWidget(label)

        # Initialize models
        self.lightweightMode = QRadioButton("Lightweight", self)
        self.balancedMode = QRadioButton("Balanced", self)
        self.performanceMode = QRadioButton("Performance", self)

        self.alphaPose = QRadioButton("AlphaPose", self)
        self.pocketPose = QRadioButton("PocketPose", self)
        self.alphaPose.hide()
        self.pocketPose.hide()

        # Set Default models initially
        self.lightweightMode.setChecked(True)
        self.model = QButtonGroup(self)
        self.model.addButton(self.lightweightMode)
        self.model.addButton(self.balancedMode)
        self.model.addButton(self.performanceMode)
        self.updateModelList("Pose2Sim")

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
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setContentsMargins(0, 0, 0, 0)

        # Create Button
        estimateButton = EstimateMotionButton(self, params)
        buttonBarLayout.addWidget(estimateButton)

        downloadButton = QPushButton("Download Motion", self)
        downloadButton.setEnabled(False)
        buttonBarLayout.addWidget(downloadButton)

        self.innerLayout.addWidget(buttonBar)

        # Connect backend change signal
        self.internalBackend.toggled.connect(self.onBackendChanged)
        self.externalBackend.toggled.connect(self.onBackendChanged)

    def updateModelList(self, backend):
        # Clear current model list layout
        for i in reversed(range(self.modelWidgetLayout.count())):
            widget = self.modelWidgetLayout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Also delete the stretch
        self.modelWidgetLayout.removeItem(
            self.modelWidgetLayout.itemAt(self.modelWidgetLayout.count() - 1)
        )

        label = QLabel("Mode:", self)
        label.setToolTip(
            "Select the model for 2D pose estimation. Lightweight is faster but less accurate. Performance is slower but more accurate."
        )
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        self.modelWidgetLayout.addWidget(label)

        # Clear model button group
        self.model = QButtonGroup(self)

        # Add models based on backend
        if backend == "Pose2Sim":
            self.modelWidgetLayout.addWidget(self.lightweightMode)
            self.modelWidgetLayout.addWidget(self.balancedMode)
            self.modelWidgetLayout.addWidget(self.performanceMode)
            self.lightweightMode.setChecked(
                True
            )  # Set baseline as the default selection
            self.model.addButton(self.lightweightMode)
            self.model.addButton(self.balancedMode)
            self.model.addButton(self.performanceMode)
        elif backend == "Custom":
            self.modelWidgetLayout.addWidget(self.alphaPose)
            self.modelWidgetLayout.addWidget(self.pocketPose)
            self.alphaPose.setChecked(True)  # Set OpenSim as the default selection
            self.model.addButton(self.alphaPose)
            self.model.addButton(self.pocketPose)
            self.alphaPose.show()
            self.pocketPose.show()

        self.modelWidgetLayout.addStretch()

    def onBackendChanged(self):
        if self.internalBackend.isChecked():
            self.updateModelList("Pose2Sim")
        elif self.externalBackend.isChecked():
            self.updateModelList("Custom")

    def toggleCorrectRotation(self):
        self.params.correct_rotation = self.correctRotationCheckbox.isChecked()

    def toggleSyncVideos(self):
        self.params.do_synchronization, self.syncVideosCheckbox.isChecked()

    def toggleMarkerAugmentation(self):
        self.params.use_marker_augmentation, self.markerAugmentationCheckbox.isChecked()

    def setCallback(self, callback):
        def inner_callback():
            callback(**self.data)

        # self.threshold.valueChanged.connect(inner_callback)
        # self.radius.valueChanged.connect(inner_callback)
        # self.thickness.valueChanged.connect(inner_callback)
        self.draw_bbox.stateChanged.connect(inner_callback)

    @property
    def data(self):
        return dict(
            # radius=self.radius.value(),
            # thickness=self.thickness.value(),
            # kpt_thr=self.threshold.value() / 100.0,
            draw_bbox=self.draw_bbox.isChecked(),
        )
