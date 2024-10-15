from PyQt6.QtWidgets import (
    QButtonGroup,
    QRadioButton,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)
from mocap.constants import APP_ASSETS, APP_PROJECTS, SUPPORTED_VIDEO_FORMATS
from mocap.core import Experiment, ExperimentMonocular
import json
import os
class CreateExperimentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Experiment")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(0)

        self.label = QLabel(self)
        self.label.setText("Experiment Name")
        self.label.setProperty("class", "h3")
        self.layout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.experiment_name = QLineEdit(self)
        self.experiment_name.setStyleSheet("border-radius: 0;")
        self.form_layout.addRow(self.experiment_name)

        def update_slug():
            text = self.experiment_name.text()
            text = text.lower().replace(" ", "-")
            text = text.lower().replace("_", "-")
            text = text.replace("--", "-")

            # Remove any characters that are not allowed
            allow_chars = "abcdefghijklmnopqrstuvwxyz-0123456789"
            text = "".join([c for c in text if c in allow_chars])

            if len(text) > 20:
                text = text[:20]

            self.experiment_name.setText(text)

        self.experiment_name.textChanged.connect(update_slug)

        self.layout.addLayout(self.form_layout)
        self.layout.addSpacing(8)

        # hint about size and allowed characters unique name
        self.hint = QLabel(self)
        self.hint.setText(
            "Experiment name must be unique and contain 3-20 characters. Only letters, numbers and hyphens are allowed."
        )
        self.hint.setProperty("class", "body")
        self.hint.setWordWrap(True)
        self.hint.setMaximumWidth(300)
        self.layout.addWidget(self.hint)
        self.layout.addSpacing(8)

        self.error_message = QLabel(self)
        self.error_message.setStyleSheet("color: red;")
        self.layout.addWidget(self.error_message)
        self.layout.addSpacing(8)
        self.monocular = QRadioButton("Monocular", self)
        self.pose2Sim = QRadioButton("Pose2Sim", self)
        self.pose2Sim.setChecked(True)
        self.estimation_type = QButtonGroup(self)
        self.estimation_type.addButton(self.monocular)
        self.estimation_type.addButton(self.pose2Sim)
        self.layout.addWidget(self.monocular)
        self.layout.addWidget(self.pose2Sim)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.button_box.accepted.connect(self.create_experiment)
        self.button_box.rejected.connect(self.reject)
        

        self.layout.addWidget(self.button_box)

    def create_experiment(self):
        experiment_name = self.experiment_name.text().strip()
        pose2Sim = self.pose2Sim.isChecked()
        experiments = {'experiments':[]}
        if os.path.exists(os.path.join(APP_PROJECTS, "experiments.json")):
            print("File exists", os.path.join(APP_PROJECTS, "experiments.json"))
            with open(os.path.join(APP_PROJECTS, "experiments.json"), "r") as f:
                experiments = json.load(f)
        try:
            if experiment_name == "":
                raise Exception("Experiment name cannot be empty.")
            if pose2Sim:
                estim_type = "pose2sim"
                Experiment(name=experiment_name, create=True)
            else:
                estim_type = "monocular"
                ExperimentMonocular(name=experiment_name, create=True)
            experiments['experiments'].append({'name':experiment_name,'est_type': estim_type})
            with open(os.path.join(APP_PROJECTS, "experiments.json"), "w") as f:
                json.dump(experiments, f, indent=4)
            self.accept()
        except Exception as e:
            print('error')
            self.error_message.setText(str(e))
