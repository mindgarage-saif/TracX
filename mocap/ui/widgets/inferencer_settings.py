from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .model_browser import ModelBrowser


class InferencerSettings(QWidget):
    def __init__(self, parent,info_storage):
        super().__init__(parent)
        self.setObjectName("InferencerSettings")

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.setLayout(self.innerLayout)

        # Section heading (centered, bold, larger font, white text)
        heading = QLabel("Configure Motion Estimation", self)
        heading.setProperty("class", "h2")
        self.innerLayout.addWidget(heading)

        # Backend
        label = QLabel("Select a Backend", self)
        label.setToolTip(
            "Default backend uses our custom pipeline for motion capture. "
            "Pose2Sim: https://github.com/perfanalytics/pose2sim"
        )
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        self.defaultBackend = QRadioButton("Default", self)
        self.defaultBackend.setChecked(True)  # Set the default selected button
        self.pose2simBackend = QRadioButton("Pose2Sim", self)

        row = QWidget(self)
        rowLayout = QHBoxLayout(row)
        rowLayout.addWidget(self.defaultBackend)
        rowLayout.addWidget(self.pose2simBackend)
        rowLayout.addStretch()
        self.innerLayout.addWidget(row)

        self.backend = QButtonGroup(self)
        self.backend.addButton(self.defaultBackend)
        self.backend.addButton(self.pose2simBackend)

        self.innerLayout.addSpacing(16)

        # Model selection area
        label = QLabel("Select a Model", self)
        label.setToolTip("More details on model performance are available in the documentation.")
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        self.modelSelectionArea = QWidget(self)
        self.modelList = QVBoxLayout(self.modelSelectionArea)
        self.innerLayout.addWidget(self.modelSelectionArea)

        # Initialize models
        self.baselineModel = QRadioButton("Baseline", self)
        self.motionbertModel = QRadioButton("MotionBERT", self)
        self.v2vModel = QRadioButton("V2V-PoseNet", self)

        self.openposeModel = QRadioButton("OpenSim", self)
        self.rtmposeModel = QRadioButton("RTMPose", self)
        self.openposeModel.hide()
        self.rtmposeModel.hide()

        # Set Default models initially
        self.baselineModel.setChecked(True)
        self.model = QButtonGroup(self)
        self.model.addButton(self.baselineModel)
        self.model.addButton(self.motionbertModel)
        self.model.addButton(self.v2vModel)
        self.updateModelList('Default')

        # Connect backend change signal
        self.defaultBackend.toggled.connect(self.onBackendChanged)
        self.pose2simBackend.toggled.connect(self.onBackendChanged)


    def updateModelList(self, backend):
        # Clear current model list layout
        for i in reversed(range(self.modelList.count())):
            widget = self.modelList.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Clear model button group
        self.model = QButtonGroup(self)

        # Add models based on backend
        if backend == 'Default':
            self.modelList.addWidget(self.baselineModel)
            self.modelList.addWidget(self.motionbertModel)
            self.modelList.addWidget(self.v2vModel)
            self.baselineModel.setChecked(True)  # Set baseline as the default selection
            self.model.addButton(self.baselineModel)
            self.model.addButton(self.motionbertModel)
            self.model.addButton(self.v2vModel)
        elif backend == 'Pose2Sim':
            self.modelList.addWidget(self.openposeModel)
            self.modelList.addWidget(self.rtmposeModel)
            self.openposeModel.setChecked(True)  # Set OpenSim as the default selection
            self.model.addButton(self.openposeModel)
            self.model.addButton(self.rtmposeModel)
            self.openposeModel.show()
            self.rtmposeModel.show()

        # Update the UI
        self.modelList.addStretch()

    def onBackendChanged(self):
        if self.defaultBackend.isChecked():
            self.updateModelList('Default')
        elif self.pose2simBackend.isChecked():
            self.updateModelList('Pose2Sim')
