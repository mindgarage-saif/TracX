from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from TracX.constants import FEATURE_MONOCULAR_2D_ANALYSIS_ENABLED, FEATURE_MONOCULAR_3D_ANALYSIS_ENABLED
from TracX.core import Experiment
from TracX.ui.common import RadioGroup
from TracX.ui.styles import PAD_X, PAD_Y


class CreateExperimentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Experiment")
        self.setContentsMargins(0, 0, 0, 0)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.innerWidget = QWidget(self)
        self.innerLayout = QVBoxLayout()
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.innerLayout.setSpacing(0)
        self.innerWidget.setLayout(self.innerLayout)
        self.layout.addWidget(self.innerWidget)

        self.motion_setup = RadioGroup(
            "Select Motion Type", self, Qt.Orientation.Horizontal
        )
        self.motion_setup.addButton("2D") if FEATURE_MONOCULAR_2D_ANALYSIS_ENABLED else None
        self.motion_setup.addButton("3D")
        self.motion_setup.addStretch()
        self.motion_setup.selectionChanged.connect(self.onMotionTypeChanged)
        self.innerLayout.addWidget(self.motion_setup)
        self.innerLayout.addSpacing(PAD_Y)

        self.camera_setup = RadioGroup(
            "Camera Configuration", self, Qt.Orientation.Horizontal
        )
        self.camera_setup.addButton("Monocular") if FEATURE_MONOCULAR_2D_ANALYSIS_ENABLED or FEATURE_MONOCULAR_3D_ANALYSIS_ENABLED else None
        self.camera_setup.addButton("Multiview")
        self.camera_setup.addStretch()
        self.innerLayout.addWidget(self.camera_setup)
        self.innerLayout.addSpacing(PAD_Y)

        self.motion_setup.selectDefault()
        self.camera_setup.selectDefault()

        self.label = QLabel(self)
        self.label.setText("Experiment Name")
        self.label.setProperty("class", "h3")
        self.innerLayout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(0, PAD_Y // 2, 0, 0)
        self.form_layout.setSpacing(0)
        self.experiment_name = QLineEdit(self)
        self.form_layout.addRow(self.experiment_name)

        def update_slug():
            text = self.experiment_name.text()
            text = text.upper().replace(" ", "_").replace("-", "_")
            text = text.replace("__", "_")

            # Remove any characters that are not allowed
            allow_chars = "abcdefghijklmnopqrstuvwxyz_0123456789".upper()
            text = "".join([c for c in text if c in allow_chars])

            if len(text) > 30:
                text = text[:30]

            self.experiment_name.setText(text)

        self.experiment_name.textChanged.connect(update_slug)

        self.innerLayout.addLayout(self.form_layout)
        self.innerLayout.addSpacing(8)

        # hint about size and allowed characters unique name
        self.hint = QLabel(self)
        self.hint.setText(
            "Experiment name must be unique and contain 3-30 characters. Only letters, numbers and hyphens are allowed.",
        )
        self.hint.setProperty("class", "body")
        self.hint.setWordWrap(True)
        self.hint.setMaximumWidth(300)
        self.innerLayout.addWidget(self.hint)
        self.innerLayout.addSpacing(PAD_Y)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.button_box.accepted.connect(self.createExperiment)
        self.button_box.rejected.connect(self.reject)
        self.innerLayout.addWidget(self.button_box)

        self.error_message = QLabel(self)
        self.error_message.setFixedHeight(32)
        self.error_message.setStyleSheet(
            "color: red; background-color: #000; padding: 4px; border-radius: 0px;"
        )
        self.layout.addWidget(self.error_message)

    def onMotionTypeChanged(self, button):
        if FEATURE_MONOCULAR_2D_ANALYSIS_ENABLED:
            if button.text() == "2D":
                self.camera_setup.buttons()[0].setEnabled(True)
                self.camera_setup.buttons()[0].setChecked(True)
                self.camera_setup.buttons()[1].setEnabled(False)
            else:
                self.camera_setup.buttons()[0].setEnabled(FEATURE_MONOCULAR_3D_ANALYSIS_ENABLED)
                self.camera_setup.buttons()[1].setEnabled(True)
                self.camera_setup.buttons()[1].setChecked(True)
        
    def createExperiment(self):
        try:
            name = self.experiment_name.text().strip()
            if name == "":
                raise Exception("Experiment name cannot be empty.")

            motionType = self.motion_setup.checkedButton().text()
            cameraConfig = self.camera_setup.checkedButton().text()

            # Create a new experiment
            Experiment(
                name=name,
                create=True,
                monocular=cameraConfig == "Monocular",
                is_2d=motionType == "2D",
            )

            self.accept()

        except Exception as e:
            self.error_message.setText(str(e))
